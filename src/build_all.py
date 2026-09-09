"""Полная пересборка сайта из подготовленных JSON. Данные: см. README (pull_* / fetch_* / prep_*)."""
import subprocess, shutil, os, sys
steps = ['build.py', 'realize.py', 'build2.py', 'build3.py', 'build4.py', 'inject_nav.py']
for s in steps:
    print('>>', s); subprocess.run([sys.executable, s], check=True)
os.makedirs('../site', exist_ok=True)
for f in ['index.html', 'genes.html', 'tissues.html', 'brca1.html', 'finale.html']:
    shutil.copy(f, '../site/' + f)
print('site/ updated')
