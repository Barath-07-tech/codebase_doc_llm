import os
import tempfile
import subprocess
from typing import Dict, List, Tuple
from pathlib import Path
import json

class CodebaseProcessor:
    def __init__(self):
        self.supported_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.jsp', '.jspx',
            '.html', '.htm', '.css', '.scss', '.sass', '.json', '.md',
            '.sql', '.xml', '.yaml', '.yml', '.properties', '.env'
        }
        
        self.ignore_patterns = {
            'node_modules', '__pycache__', '.git', '.venv', 'venv', 'env',
            'dist', 'build', '.next', '.nuxt', 'coverage', 'target',
            '.idea', '.vscode', '*.pyc', '*.class', '*.jar', '*.war'
        }
    
    def clone_repository(self, github_url: str) -> str:
        temp_dir = tempfile.mkdtemp()
        try:
            subprocess.run(['git', 'clone', github_url, temp_dir], 
                         check=True, capture_output=True, text=True)
            return temp_dir
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to clone repository: {e}")
    
    def should_ignore(self, path: str) -> bool:
        path_parts = Path(path).parts
        for part in path_parts:
            if any(pattern in part for pattern in self.ignore_patterns):
                return True
        return False
    
    def process_codebase(self, repo_path: str) -> Tuple[List[Dict], Dict]:
        files = []
        stats = {'total_files': 0, 'total_lines': 0, 'languages': {}}
        
        for root, dirs, filenames in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not self.should_ignore(os.path.join(root, d))]
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                
                if self.should_ignore(file_path):
                    continue
                
                ext = Path(filename).suffix.lower()
                if ext not in self.supported_extensions:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    rel_path = os.path.relpath(file_path, repo_path)
                    language = self._get_language(ext)
                    lines = len(content.splitlines())
                    
                    files.append({
                        'path': rel_path,
                        'language': language,
                        'content': content,
                        'lines': lines,
                        'size': len(content)
                    })
                    
                    stats['total_files'] += 1
                    stats['total_lines'] += lines
                    
                    if language not in stats['languages']:
                        stats['languages'][language] = {'files': 0, 'lines': 0}
                    stats['languages'][language]['files'] += 1
                    stats['languages'][language]['lines'] += lines
                    
                except Exception:
                    continue
        
        return files, stats
    
    def _get_language(self, ext: str) -> str:
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript', '.java': 'java',
            '.jsp': 'jsp', '.jspx': 'jsp', '.html': 'html', '.htm': 'html',
            '.css': 'css', '.scss': 'css', '.sass': 'css', '.json': 'json',
            '.md': 'markdown', '.sql': 'sql', '.xml': 'xml', '.yaml': 'yaml',
            '.yml': 'yaml', '.properties': 'properties'
        }
        return lang_map.get(ext, 'text')
      
    def create_filtered_summary(self, files: List[Dict], stats: Dict, token_limit: int = 7500) -> str:
        """Create intelligent summary with two-layer filtering if needed"""
        from core.token_estimator import TokenEstimator
        token_estimator = TokenEstimator()
        
        def create_first_layer_summary():
            # First layer filtering - similar to current logic but more focused
            important_files = []
            database_files = []
            config_files = []
            regular_files = []
            
            for file_data in files:
                path = file_data['path'].lower()
                # Prioritize main application files and database files
                if any(name in path for name in ['home.java', 'main.java', 'app.java', 'index.java']):
                    important_files.append(file_data)
                elif path.endswith('.sql'):
                    database_files.append(file_data)
                elif any(name in path for name in ['config', 'package.json', 'readme']):
                    config_files.append(file_data)
                else:
                    regular_files.append(file_data)

            summary_parts = [f"""
    PROJECT OVERVIEW:
    - Total Files: {stats['total_files']}
    - Total Lines: {stats['total_lines']}
    - Languages: {', '.join(stats['languages'].keys())}

    LANGUAGE BREAKDOWN:
    {json.dumps(stats['languages'], indent=2)}
    """]
            
            # Important files (full content)
            if important_files:
                summary_parts.append("\n=== CORE FILES (FULL CONTENT) ===")
                for file_data in important_files[:5]:
                    summary_parts.append(f"""
    FILE: {file_data['path']} ({file_data['language']})
    LINES: {file_data['lines']}
    CONTENT:
    {file_data['content']}
    ---
    """)

            # Database files (full content)
            if database_files:
                summary_parts.append("\n=== DATABASE FILES ===")
                for file_data in database_files[:3]:
                    summary_parts.append(f"""
    FILE: {file_data['path']}
    LINES: {file_data['lines']}
    CONTENT:
    {file_data['content']}
    ---
    """)

            # File structure and summaries
            summary_parts.append("\n=== FILE STRUCTURE & SUMMARIES ===")
            for file_data in regular_files:
                if file_data['language'] in ['javascript', 'typescript', 'python', 'java']:
                    func_classes = self._extract_functions_classes(file_data['content'], file_data['language'])
                    summary_parts.append(f"  - {file_data['path']}: {func_classes}")

            return '\n'.join(summary_parts)

        def create_second_layer_summary(first_layer: str):
            # Ultra-focused summary for when first layer is still too large
            critical_files = []
            
            for file_data in files:
                path = file_data['path'].lower()
                # Only include the absolute most important files
                if any(name in path for name in ['home.java', 'main.java']):
                    critical_files.append(file_data)
                    if len(critical_files) >= 2:  # Limit to top 2 most important files
                        break

            summary_parts = [f"""
    PROJECT OVERVIEW:
    - Total Files: {stats['total_files']}
    - Languages: {', '.join(stats['languages'].keys())}
    """]
            
            if critical_files:
                summary_parts.append("\n=== CRITICAL FILES ===")
                for file_data in critical_files:
                    summary_parts.append(f"""
    FILE: {file_data['path']} ({file_data['language']})
    {self._extract_functions_classes(file_data['content'], file_data['language'])}
    KEY CONTENT:
    {file_data['content'][:1000]}... (truncated)
    ---
    """)

            return '\n'.join(summary_parts)

        # Create first layer summary
        first_layer = create_first_layer_summary()
        first_layer_tokens = token_estimator.estimate_tokens(first_layer)
        
        if first_layer_tokens <= token_limit:
            print(f"First layer summary successful: {first_layer_tokens} tokens")
            return first_layer
        
        # If first layer is too large, create second layer
        print(f"First layer too large ({first_layer_tokens} tokens), creating ultra-focused summary...")
        second_layer = create_second_layer_summary(first_layer)
        second_layer_tokens = token_estimator.estimate_tokens(second_layer)
        print(f"Second layer summary created: {second_layer_tokens} tokens")
        
        return second_layer
    
#     def create_filtered_summary(self, files: List[Dict], stats: Dict) -> str:
#         """Create intelligent summary when full codebase exceeds token limit"""
        
#         # Prioritize important files
#         important_files = []
#         config_files = []
#         regular_files = []
        
#         for file_data in files:
#             path = file_data['path'].lower()
#             if any(name in path for name in [ 'home','main', 'index', 'app', 'config', 'package.json', 'readme']):
#                 important_files.append(file_data)
#             elif any(ext in path for ext in ['.json', '.md', '.yml', '.yaml', '.properties']):
#                 config_files.append(file_data)
#             else:
#                 regular_files.append(file_data)
        
#         # Include full content for important files, summaries for others
#         summary_parts = []
        
#         # Project overview
#         summary_parts.append(f"""
# PROJECT OVERVIEW:
# - Total Files: {stats['total_files']}
# - Total Lines: {stats['total_lines']}
# - Languages: {', '.join(stats['languages'].keys())}

# LANGUAGE BREAKDOWN:
# {json.dumps(stats['languages'], indent=2)}
# """)
        
#         # Important files (full content)
#         if important_files:
#             summary_parts.append("\n=== IMPORTANT FILES (FULL CONTENT) ===")
#             for file_data in important_files[:10]:  # Limit to prevent overflow
#                 summary_parts.append(f"""
# FILE: {file_data['path']} ({file_data['language']})
# LINES: {file_data['lines']}
# CONTENT:
# {file_data['content']}
# ---
# """)
        
#         # File structure and summaries
#         summary_parts.append("\n=== FILE STRUCTURE & SUMMARIES ===")
        
#         # Group by directory
#         dir_structure = {}
#         for file_data in regular_files:
#             dir_name = os.path.dirname(file_data['path']) or 'root'
#             if dir_name not in dir_structure:
#                 dir_structure[dir_name] = []
#             dir_structure[dir_name].append(file_data)
        
#         for dir_name, dir_files in dir_structure.items():
#             summary_parts.append(f"\nDIRECTORY: {dir_name}")
#             for file_data in dir_files:
#                 # Create intelligent summary based on file type
#                 if file_data['language'] in ['javascript', 'typescript', 'python', 'java']:
#                     func_classes = self._extract_functions_classes(file_data['content'], file_data['language'])
#                     summary_parts.append(f"  - {file_data['path']} ({file_data['lines']} lines): {func_classes}")
#                 else:
#                     preview = file_data['content'][:200].replace('\n', ' ')
#                     summary_parts.append(f"  - {file_data['path']} ({file_data['lines']} lines): {preview}...")
        
#         return '\n'.join(summary_parts)
    
    def _extract_functions_classes(self, content: str, language: str) -> str:
        """Extract function and class names for summary"""
        import re
        
        if language == 'python':
            functions = re.findall(r'def (\w+)', content)
            classes = re.findall(r'class (\w+)', content)
        elif language in ['javascript', 'typescript']:
            functions = re.findall(r'function (\w+)|const (\w+)\s*=|(\w+):\s*function', content)
            functions = [f[0] or f[1] or f[2] for f in functions if any(f)]
            classes = re.findall(r'class (\w+)', content)
        elif language == 'java':
            functions = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+(\w+)\s*\(', content)
            classes = re.findall(r'(?:public\s+)?class (\w+)', content)
        else:
            return "Binary/config file"
        
        result = []
        if functions:
            result.append(f"Functions: {', '.join(functions[:5])}")
        if classes:
            result.append(f"Classes: {', '.join(classes[:3])}")
        
        return '; '.join(result) if result else "No functions/classes found"
