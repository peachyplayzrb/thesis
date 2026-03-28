import shutil
from pathlib import Path

# Paths
workspace_root = Path(r'c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main')
impl_notes_src = workspace_root / '07_implementation' / 'implementation_notes'
output_root = workspace_root / 'recommendation-implementation-standalone'

# Create output directory
output_root.mkdir(exist_ok=True)
print(f'Assembly location: {output_root}')

# 1. Copy implementation_notes folder (exclude website)
impl_notes_dst = output_root / 'implementation_notes'
if impl_notes_dst.exists():
    print('Removing existing implementation_notes directory...')
    shutil.rmtree(impl_notes_dst)

print('Copying implementation_notes folder...')
shutil.copytree(impl_notes_src, impl_notes_dst, ignore=lambda d, names: [n for n in names if n == 'website'])

# 2. Copy main.py
main_src = workspace_root / 'main_standalone.py'
main_dst = output_root / 'main.py'
shutil.copy2(main_src, main_dst)
print('Copied main.py')

# 3. Copy README
readme_src = workspace_root / 'README_STANDALONE.md'
readme_dst = output_root / 'README.md'
shutil.copy2(readme_src, readme_dst)
print('Copied README.md')

# 4. Copy requirements.txt
req_src = workspace_root / 'requirements.txt'
req_dst = output_root / 'requirements.txt'
if req_src.exists():
    shutil.copy2(req_src, req_dst)
    print('Copied requirements.txt')
else:
    print('WARNING: requirements.txt not found')

# 5. Create .gitignore
gitignore_path = output_root / '.gitignore'
gitignore_content = '''# Python
__pycache__/
.venv/
.env
*.pyc
.pytest_cache/

# Outputs
implementation_notes/bl*/outputs/

# OS
.DS_Store
*.swp
*.swo
Thumbs.db

# IDE
.vscode/
.idea/
*.code-workspace
'''
gitignore_path.write_text(gitignore_content)
print('Created .gitignore')

# Calculate size
total_size = sum(f.stat().st_size for f in output_root.rglob('*') if f.is_file())
total_mb = total_size // (1024*1024)

print('\nStandalone package assembly complete!')
print(f'Location: {output_root}')
print(f'Size: ~{total_mb} MB')
print('\nPackage contents:')
print('  - implementation_notes/ (full pipeline, no website)')
print('  - main.py (entry point)')
print('  - README.md (documentation)')
print('  - requirements.txt (Python dependencies)')
print('  - .gitignore')
