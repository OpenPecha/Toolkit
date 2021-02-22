import re
from pathlib import Path

from setuptools import find_packages, setup


def read(fname):
    p = Path(__file__).parent / fname
    with p.open(encoding="utf-8") as f:
        return f.read()


def get_version(prop, project):
    project = Path(__file__).parent / project / "__init__.py"
    result = re.search(
        r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), project.read_text()
    )
    return result.group(1)


setup(
    name="openpecha",
    version=get_version("__version__", "openpecha"),
    author="Esukhia developers",
    author_email="esukhiadev@gmail.com",
    description="OpenPecha Toolkit allows state of the art for distributed standoff annotations on moving texts",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="Apache2",
    url="https://github.com/OpenPoti/openpecha-toolkit",
    packages=find_packages(),
    install_requires=[
        "Click==7.1.2",
        "diff-match-patch==20181111",
        "PyYAML>=5.0.0",
        "requests==2.22.0",
        "tqdm==4.35.0",
        "PyGithub==1.43.8",
        "GitPython==3.1.0",
        "bs4",
        "pyewts",
        "rdflib==5.0.0",
    ],
    python_requires=">=3.6",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "openpecha=openpecha.cli:cli"
        ]  # command=package.module:function
    },
)
