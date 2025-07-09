import os
import yaml

DOCS_DIR = 'docs'
MKDOCS_YML = 'mkdocs.yml'
INDEX_FILE = os.path.join(DOCS_DIR, 'index.md')


def format_title(name):
    return name.replace('_', ' ').replace('-', ' ').title()


def scan_docs(dir_path, base=''):
    nav = []
    index_links = []

    for item in sorted(os.listdir(dir_path)):
        full_path = os.path.join(dir_path, item)
        rel_path = os.path.join(base, item)

        if item.startswith('.') or item.startswith('_'):
            continue

        if os.path.isdir(full_path):
            sub_nav, sub_index = scan_docs(full_path, rel_path)
            title = format_title(item)
            nav.append({title: sub_nav})
            index_links.append((title, sub_index))
        elif item.endswith('.md') and item.lower() != 'index.md':
            title = format_title(os.path.splitext(item)[0])
            file_path = rel_path.replace(os.sep, '/')
            nav.append({title: file_path})
            index_links.append((title, file_path))

    return nav, index_links


def generate_index_md(index_links, level=2):
    lines = ['# Documentation Index\n']

    def render_links(links, indent_level):
        for title, link in links:
            if isinstance(link, list):
                lines.append(f"\n{'#' * indent_level} {title}\n")
                render_links(link, indent_level + 1)
            else:
                lines.append(f"- [{title}]({link})")

    render_links(index_links, level)
    return '\n'.join(lines)


def update_mkdocs_yml(nav):
    if os.path.exists(MKDOCS_YML):
        with open(MKDOCS_YML, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}

    config['nav'] = nav

    with open(MKDOCS_YML, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)

    print(f'✅ Updated {MKDOCS_YML} with new nav structure')


def main():
    nav, index_links = scan_docs(DOCS_DIR)

    update_mkdocs_yml(nav)

    index_content = generate_index_md(index_links)
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f'✅ Generated {INDEX_FILE}')


if __name__ == '__main__':
    main()
