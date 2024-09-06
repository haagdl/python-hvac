"""Create a new venv and install all dependencies from requirements.txt and custom repos"""

# standard imports
import subprocess
import os
import shutil

# internal imports
from hvac.paths import path_project

# python version
python_version: str = '3.11'

# command prototypes
commands: list[str] = ['/bin/bash', '-c']
pip_install_str: str = (f'source {path_project + "/.venv/bin/activate"} && '
                        f'git config --global http.sslVerify false &&'
                        f'python{python_version} -m pip install')

# custom repos
paths_custom_repos: list[str] = []

# purge previous virtual environment and create new one in project directory
shutil.rmtree(os.path.join(path_project, '.venv'), ignore_errors=True)
process = subprocess.Popen(commands + [f'python{python_version} -m venv '
                                       f'{os.path.join(path_project, ".venv")}'])
process.wait()

# Install public project dependencies from requirements.txt
process = subprocess.Popen(commands + [f'{pip_install_str} -r requirements.txt'])
process.wait()

# Install custom project dependencies from private repos
paths_custom_repo: str
for paths_custom_repo in paths_custom_repos:
    process = subprocess.Popen(commands + [f'{pip_install_str} {paths_custom_repo}'])
    process.wait()