import os
from typing import Dict, List

class DocumentationGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.docs_dir = os.path.join(output_dir, 'docs')
        os.makedirs(self.docs_dir, exist_ok=True)
    
    def generate_all_docs(self, llm_client, codebase_content: str) -> Dict[str, str]:
        """Generate all 5 documentation files"""
        
        doc_types = ['index', 'architecture', 'database', 'classes', 'web']
        generated_files = {}
        
        print("Generating documentation files...")
        
        for doc_type in doc_types:
            print(f"  Generating {doc_type}.md...")
            
            content = llm_client.generate_documentation(codebase_content, doc_type)
            
            file_path = os.path.join(self.docs_dir, f'{doc_type}.md')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            generated_files[doc_type] = file_path
            print(f"    ✓ {doc_type}.md created")
        
        # # Generate combined HTML
        # html_path = self._generate_combined_html(generated_files)
        # generated_files['html'] = html_path
        
        return generated_files
    
    def _generate_combined_html(self, doc_files: Dict[str, str]) -> str:
        """Generate combined HTML documentation"""
        
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Documentation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; background: #f8f9fa; }
        .container { max-width: 1400px; margin: 0 auto; display: flex; min-height: 100vh; }
        .sidebar { width: 280px; background: #2c3e50; color: white; padding: 20px; position: fixed; height: 100vh; overflow-y: auto; }
        .main-content { flex: 1; margin-left: 280px; padding: 40px; background: white; }
        .nav-item { display: block; padding: 10px 15px; margin: 5px 0; background: rgba(255,255,255,0.1); border-radius: 5px; text-decoration: none; color: white; cursor: pointer; }
        .nav-item:hover, .nav-item.active { background: #3498db; }
        .section { display: none; }
        .section.active { display: block; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; }
    </style>
    <script src="https://unpkg.com/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>Documentation</h2>
            <nav>
                <a href="#" class="nav-item active" onclick="showSection('index')">📋 Overview</a>
                <a href="#" class="nav-item" onclick="showSection('architecture')">📐 Architecture</a>
                <a href="#" class="nav-item" onclick="showSection('database')">🗄️ Database</a>
                <a href="#" class="nav-item" onclick="showSection('classes')">🏗️ Classes</a>
                <a href="#" class="nav-item" onclick="showSection('web')">🌐 Web</a>
            </nav>
        </div>
        
        <div class="main-content">
"""
        
        # Add content sections
        for doc_type, file_path in doc_files.items():
            if doc_type == 'html':
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                active_class = 'active' if doc_type == 'index' else ''
                html_content += f"""
            <section id="{doc_type}" class="section {active_class}">
                <div id="{doc_type}-content">
                    <pre>{content}</pre>
                </div>
            </section>
"""
            except:
                html_content += f"""
            <section id="{doc_type}" class="section">
                <div id="{doc_type}-content">
                    <p>Error loading {doc_type} content.</p>
                </div>
            </section>
"""
        
        html_content += """
        </div>
    </div>
    
    <script>
        function showSection(sectionId) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            
            document.getElementById(sectionId).classList.add('active');
            event.target.classList.add('active');
            
            if (typeof mermaid !== 'undefined') {
                mermaid.init();
            }
        }
        
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({ startOnLoad: true, theme: 'default' });
        }
    </script>
</body>
</html>"""
        
        html_path = os.path.join(self.output_dir, 'complete_documentation.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path