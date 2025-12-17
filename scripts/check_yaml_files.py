import glob
import sys
import yaml

errors = []
for p in glob.glob('aibom/**/*.yaml', recursive=True):
    try:
        with open(p,'r',encoding='utf-8') as f:
            yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as e:
        errors.append((p, str(e)))
if errors:
    print('YAML ERRORS:')
    for p,e in errors:
        print(p, e)
    sys.exit(1)
else:
    print('All AIBOM YAML files are valid YAML')
