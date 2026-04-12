import re

with open(r'd:\Code\Multi-SWE-bench\task9\task9_M2\crates\core\app.rs', 'r', encoding='utf-8') as f:
    app_content = f.read()

with open(r'd:\Code\Multi-SWE-bench\task9\task9_M2\crates\core\args.rs', 'r', encoding='utf-8') as f:
    args_content = f.read()

app_names = set(re.findall(r'RGArg::(?:switch|flag)\("([^"]+)"', app_content))
mapped_names = set(re.findall(r'"([^"]+)" => Some\(', args_content[args_content.index('fn long_to_name'):]))
mapped_names.discard('help')
mapped_names.discard('version')

missing = app_names - mapped_names
extra = mapped_names - app_names

if missing:
    print('In app.rs but NOT in long_to_name:')
    for n in sorted(missing):
        print(f'  {n}')
else:
    print('All app.rs args are covered in long_to_name!')

if extra:
    print('\nIn long_to_name but NOT in app.rs:')
    for n in sorted(extra):
        print(f'  {n}')
else:
    print('No extra mappings in long_to_name!')

print(f'\nApp.rs: {len(app_names)} args, Mapped: {len(mapped_names)} unique long names')
