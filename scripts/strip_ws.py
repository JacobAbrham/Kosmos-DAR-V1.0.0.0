# Strip trailing whitespace from all python files under scripts/.
from pathlib import Path

files = list(Path('scripts').glob('**/*.py'))

changed = False
for P in files:
    content = P.read_text(encoding='utf-8')
    # Normalize tabs to spaces
    if '\t' in content:
        content = content.replace('\t', ' ' * 4)
    # Remove trailing whitespace from each line
    stripped = '\n'.join(line.rstrip() for line in content.splitlines()) + '\n'
    if content != stripped:
        P.write_text(stripped, encoding='utf-8')
        print('Stripped trailing whitespace in', P)
        changed = True
if not changed:
    print('No changes')
