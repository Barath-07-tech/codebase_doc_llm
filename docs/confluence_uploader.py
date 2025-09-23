import os
import re
import subprocess
import markdown
from bs4 import BeautifulSoup
from bs4.element import CData
from atlassian import Confluence

def replace_mermaid_with_png(content, output_dir, file_prefix):
    """
    Convert all mermaid blocks in content to PNGs.
    Returns updated content and list of generated PNG paths.
    """
    # First check if mermaid-cli is installed
    try:
        mmdc_path = None
        # Check common installation paths
        possible_paths = [
            os.path.join(os.environ.get('APPDATA', ''), 'npm', 'mmdc.cmd'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'nodejs', 'node_modules', '@mermaid-js', 'mermaid-cli', 'bin', 'mmdc.js'),
            'mmdc',  # Check in PATH
        ]
        
        for path in possible_paths:
            try:
                subprocess.run([path, "--version"], capture_output=True, check=True)
                mmdc_path = path
                break
            except:
                continue
                
        if not mmdc_path:
            print("⚠️ Mermaid CLI not found. Please install it using: npm install -g @mermaid-js/mermaid-cli")
            return content, []

        matches = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
        generated_pngs = []
        
        # Create diagrams directory if it doesn't exist
        diagrams_dir = os.path.join(output_dir, 'diagrams')
        os.makedirs(diagrams_dir, exist_ok=True)

        for i, code in enumerate(matches, start=1):
            png_file = os.path.join(diagrams_dir, f"{file_prefix}_diagram_{i}.png")
            mmd_file = os.path.join(diagrams_dir, f"{file_prefix}_diagram_{i}.mmd")

            # Write temp .mmd
            with open(mmd_file, "w", encoding="utf-8") as f:
                f.write(code.strip())

            try:
                # Generate PNG with explicit paths and error handling
                result = subprocess.run(
                    [mmdc_path, "-i", mmd_file, "-o", png_file],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                generated_pngs.append(png_file)
                
                # Replace mermaid block with Confluence image macro
                ac_image = f"""<ac:image><ri:attachment ri:filename="{os.path.basename(png_file)}" /></ac:image>"""
                content = content.replace(f"```mermaid\n{code}```", ac_image)
                
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Error generating diagram: {e.stderr}")
                continue
            finally:
                # Cleanup temp file
                if os.path.exists(mmd_file):
                    try:
                        os.remove(mmd_file)
                    except:
                        pass

        return content, generated_pngs

    except Exception as e:
        print(f"⚠️ Error in Mermaid processing: {str(e)}")
        return content, []

def md_to_confluence_storage(md_content: str) -> str:
    """
    Convert Markdown content into Confluence storage format XHTML.
    """
    html_content = markdown.markdown(
        md_content,
        extensions=["fenced_code", "tables"]
    )
    soup = BeautifulSoup(html_content, "html.parser")

    # Handle fenced code blocks
    for pre in soup.find_all("pre"):
        code = pre.code
        if code:
            lang = None
            if code.has_attr("class"):
                classes = code["class"]
                lang = classes[0].replace("language-", "") if classes else None

            # Skip mermaid/plantuml (handled earlier)
            if lang in ("mermaid", "plantuml"):
                continue

            # Build Confluence macro
            code_macro = soup.new_tag("ac:structured-macro", **{"ac:name": "code"})
            if lang:
                param = soup.new_tag("ac:parameter", **{"ac:name": "language"})
                param.string = lang
                code_macro.append(param)

            # Add plain-text-body with CDATA preserved
            body = soup.new_tag("ac:plain-text-body")
            body.append(CData("\n" + code.get_text() + "\n"))
            code_macro.append(body)

            pre.replace_with(code_macro)

    return str(soup)

def convert_links(content, parent_page_title, child_pages):
    """
    Convert markdown links to Confluence links
    """
    def replacer(match):
        text = match.group(1)
        link = match.group(2)
        if link.endswith(".md"):
            child_title = link.replace(".md", "").capitalize()
            if child_title in child_pages:
                return f"[{text}|{parent_page_title}^{child_title}]"
        return match.group(0)

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replacer, content)

def publish_to_confluence(confluence_url, space_key, docs_folder, username, api_token):
    """
    Publish documentation to Confluence
    """
    confluence = Confluence(
        url=confluence_url,
        username=username,
        password=api_token
    )

    parent_page_id = None

    # Ensure index.md is processed first
    md_files = sorted([f for f in os.listdir(docs_folder) if f.endswith(".md")])
    if "index.md" in md_files:
        md_files.remove("index.md")
        md_files = ["index.md"] + md_files

    for filename in md_files:
        file_path = os.path.join(docs_folder, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_prefix = os.path.splitext(filename)[0]

        # Convert mermaid -> PNG + replace with <ac:image>
        content, generated_pngs = replace_mermaid_with_png(content, os.path.dirname(file_path), file_prefix)

        # Convert Markdown -> Confluence storage
        page_body = md_to_confluence_storage(content)

        if filename == "index.md":
            parent_title = content.splitlines()[0].lstrip("# ").strip() or "Project Documentation"
            page_title = parent_title
            parent_page = confluence.create_page(
                space=space_key,
                title=page_title,
                body=page_body,
                type="page",
                representation="storage"
            )
            parent_page_id = parent_page["id"]
            target_page_id = parent_page_id
            print(f"📤 Published parent page: {page_title} (ID: {parent_page_id})")
        else:
            child_suffix = filename.replace(".md", "").capitalize()
            if parent_title:
                page_title = f"{parent_title} - {child_suffix}"
            else:
                page_title = child_suffix
            if parent_page_id:
                child_page = confluence.create_page(
                    space=space_key,
                    title=page_title,
                    body=page_body,
                    parent_id=parent_page_id,
                    type="page",
                    representation="storage"
                )
                target_page_id = child_page["id"]
                print(f"📤 Published child page: {page_title} (ID: {target_page_id})")
            else:
                print(f"⚠️ Skipped {page_title}, parent page not created yet!")
                continue

        # Attach all PNGs
        for png in generated_pngs:
            confluence.attach_file(png, page_id=target_page_id)
            print(f"🖼️ Attached diagram: {os.path.basename(png)}")