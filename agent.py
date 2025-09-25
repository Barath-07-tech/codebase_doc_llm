import os
import sys
import argparse
import shutil
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List


from core.token_estimator import TokenEstimator
from core.codebase_processor import CodebaseProcessor
from core.llm_client import LlamaScoutClient
from docs.doc_generator import DocumentationGenerator
from docs.confluence_uploader import publish_to_confluence

load_dotenv()

class DocumentationAgent:
    def __init__(self, llm_endpoint: str, output_dir: str = "output", max_tokens: int = 10000000):
        self.output_dir = output_dir
        self.max_tokens = max_tokens
        
        self.token_estimator = TokenEstimator()
        self.processor = CodebaseProcessor()
        self.llm_client = LlamaScoutClient()
        self.doc_generator = DocumentationGenerator(output_dir)
        
        os.makedirs(output_dir, exist_ok=True)
    
    def run(self, github_url: str) -> Dict[str, str]:
        """Main execution pipeline"""
        print("Starting AI Code Documentation Agent v3...")
        
        try:
            # Step 1: Clone repository
            print("Cloning repository...")
            repo_path = self.processor.clone_repository(github_url)
            
            # Step 2: Process codebase
            print("Processing codebase...")
            files, stats = self.processor.process_codebase(repo_path)
            
            if not files:
                raise Exception("No supported files found in repository")
            
            print(f"Found {stats['total_files']} files in {len(stats['languages'])} languages")
            
            # Step 3: Prepare content for LLM
            print("Preparing content for LLM analysis...")
            
            # Create full codebase content
            full_content = self._create_full_content(files, stats)
            content_tokens = self.token_estimator.estimate_tokens(full_content)
            
            print(f"Estimated tokens: {content_tokens:,}")
            
            # Decide whether to send full content or summary
            if content_tokens <= self.max_tokens * 0.8:  # Leave 20% buffer for response
                print("Sending full codebase to LLM...")
                llm_input = full_content
            else:
                print("Codebase too large, creating intelligent summary...")
                llm_input = self.processor.create_filtered_summary(files, stats)
                print(f"Summary tokens: {self.token_estimator.estimate_tokens(llm_input):,}")
            
            # Step 4: Generate documentation
            print("Generating documentation with Gemini 2.5 pro...")
            generated_files = self.doc_generator.generate_all_docs(self.llm_client, llm_input)
            
            # Step 5: Save metadata
            metadata_path = os.path.join(self.output_dir, 'generation_metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'repository_url': github_url,
                    'generation_time': datetime.now().isoformat(),
                    'stats': stats,
                    'token_count': content_tokens,
                    'used_full_content': content_tokens <= self.max_tokens * 0.8,
                    'generated_files': list(generated_files.keys())
                }, f, indent=2)
            
            generated_files['metadata'] = metadata_path
            
            # Cleanup
            shutil.rmtree(repo_path, ignore_errors=True)
            
            print("\nDocumentation generation complete!")
            print(f"Output directory: {self.output_dir}")
            for doc_type, file_path in generated_files.items():
                print(f"  {doc_type}: {file_path}")
            
            return generated_files
            
        except Exception as e:
            print(f"Error: {str(e)}")
            raise
    
    def _create_full_content(self, files: List[Dict], stats: Dict) -> str:
        """Create complete codebase content for LLM with security filtering"""
        
        # Security sensitive patterns to filter out
        sensitive_patterns = {
            # Environment and configuration files
            '.env', 'config.json', 'settings.json', 'appsettings.json',
            # Authentication files
            'auth', 'credentials', 'secret', 'password', 'token',
            # Virtual environments and dependencies
            'venv', 'env', 'node_modules', '__pycache__', 'vendor',
            # Build and cache
            'dist', 'build', '.next', '.nuxt', 'coverage', 'target',
            # IDE and editor files
            '.idea', '.vscode', '.vs',
            # Compiled files
            '.pyc', '.class', '.jar', '.war',
            # Key and certificate files
            '.pem', '.key', '.crt', '.cer', '.pfx', '.p12',
            # Database files
            '.db', '.sqlite', '.sqlite3',
            # Log files
            '.log', 'logs/',
            # Temporary files
            'tmp/', 'temp/', '.tmp', '.temp'
        }
        
        # Filter out sensitive files
        filtered_files = []
        skipped_count = 0
        
        for file_data in files:
            path = file_data['path'].lower()
            
            # Skip if file contains sensitive patterns
            if any(pattern in path for pattern in sensitive_patterns):
                skipped_count += 1
                continue
                
            # Skip if file might contain sensitive content
            if any(keyword in file_data['content'].lower() 
                  for keyword in ['password', 'secret', 'token', 'key', 'credential', 'auth']):
                skipped_count += 1
                continue
                
            filtered_files.append(file_data)
        
        # Update stats for filtered content
        filtered_stats = stats.copy()
        filtered_stats['total_files'] -= skipped_count
        
        content_parts = [f"""
CODEBASE ANALYSIS REQUEST

PROJECT STATISTICS (After Security Filtering):
- Total Files: {filtered_stats['total_files']} (Excluded {skipped_count} sensitive files)
- Total Lines: {stats['total_lines']}
- Languages: {', '.join(stats['languages'].keys())}

LANGUAGE BREAKDOWN:
{json.dumps(stats['languages'], indent=2)}

=== FILTERED CODEBASE CONTENT ===
Note: Security-sensitive files and content have been excluded
"""]
        
        for file_data in filtered_files:
            content_parts.append(f"""
FILE: {file_data['path']}
LANGUAGE: {file_data['language']}
LINES: {file_data['lines']}
SIZE: {file_data['size']} bytes

CONTENT:
{file_data['content']}

---END FILE---
""")
        
        return '\n'.join(content_parts)

def main():
    parser = argparse.ArgumentParser(description='AI Code Documentation Agent v3 - Llama-4-Scout Edition')
    parser.add_argument('github_url', help='GitHub repository URL')
    
    args = parser.parse_args()
    
    # Set default values
    llm_endpoint = os.getenv("LLM_ENDPOINT")  # Default Llama endpoint
    output_dir = "output"
    max_tokens = 1048576
    
    # Validate GitHub URL
    if not args.github_url.startswith(('https://github.com/', 'git@github.com:')):
        print("Error: Please provide a valid GitHub URL")
        sys.exit(1)
    
    try:
        agent = DocumentationAgent(llm_endpoint, output_dir, max_tokens)
        results = agent.run(args.github_url)
        
        print("\nGeneration completed successfully!")
        
        # Automatically upload to Confluence
        try:
                
            confluence_url = os.getenv('CONFLUENCE_URL')
            space_key = os.getenv('CONFLUENCE_SPACE_KEY')
            username = os.getenv('CONFLUENCE_USERNAME')
            api_token = os.getenv('CONFLUENCE_API_TOKEN')
            
            if all([confluence_url, space_key, username, api_token]):
                docs_folder = os.path.join('output', 'docs')
                publish_to_confluence(confluence_url, space_key, docs_folder, username, api_token)
                print("\n✅ Documentation successfully uploaded to Confluence!")
            else:
                print("\nℹ️ Skipping Confluence upload - credentials not found in .env file")
        
        except Exception as e:
            print(f"\n⚠️ Confluence upload failed: {str(e)}")
            print("Documentation was generated successfully, but could not be uploaded to Confluence.")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
