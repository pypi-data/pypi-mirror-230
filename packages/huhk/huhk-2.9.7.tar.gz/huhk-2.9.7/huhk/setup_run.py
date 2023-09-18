import os
import sys

path = os.path.dirname(os.path.dirname(sys.argv[0]))

os.chdir(path)
os.system("rmdir /q /s dist")
os.system("rmdir /q /s build")
os.system("python huhk/case_project/setup_set.py sdist bdist_wheel")
os.system("python -m twine upload dist/*")
# os.system("pip install huhk -U -i https://pypi.org/project")
