from pathlib import Path
from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

def assemble_wildcard_paths(wildcard_path):
    """

    Parameters
    ----------
    wildcard_path: str
        Path within package containing wildcards

    Returns
    -------
    list[str]
        List of paths relative to package root matching the wildcard
    """
    name_package: str = 'hvac'
    path_package = Path(f'./{name_package}').resolve()
    return [str(path.relative_to(path_package))
            for path in path_package.glob(wildcard_path)]

setup(
    name='hvac',
    version='0.1.2',
    author='Tom Christiaens <tom.chr@proximus.be>',
    description='A package for HVAC engineering',
    packages=find_packages(exclude=['']),  # e.g. exclude=['docs', 'tests']
    install_requires=requirements,
    package_data={'': [*assemble_wildcard_paths('utils/**/*')]},  # e.g. '': ['*.txt', '*.rst']
    include_package_data=True,
)
