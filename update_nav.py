import os
import yaml

DOCS_DIR = 'docs'
CONFIG_FILE = 'mkdocs.yml'

def title_case(name):
    """Convert file or folder name to a title-case display label."""
    return os.path.splitext(name)[0].replace('_', ' ').title()

def build_nav(path):
    nav = []
    entries = sorted(os.listdir(path))
    
    for entry in entries:
        full_path = os.path.join(path, entry)
        rel_path = os.path.relpath(full_path, DOCS_DIR)
        
        if os.path.isdir(full_path):
            children = build_nav(full_path)
            if children:
                nav.append({entry.replace('_', ' ').title(): children})
        elif entry.endswith('.md'):
            nav.append({title_case(entry): rel_path.replace('\\', '/')})
    
    return nav

def update_mkdocs_yaml():
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

    config['nav'] = build_nav(DOCS_DIR)

    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, sort_keys=False)

    print("✅ mkdocs.yml updated.")

if __name__ == '__main__':
    update_mkdocs_yaml()
