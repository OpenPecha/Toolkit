from pathlib import Path
from setuptools import setup, find_packages


def read(fname):
    p = Path(__file__).parent / fname
    with p.open(encoding="utf-8") as f:
        return f.read()

setup(
    name="openpoti",
    version="0.2.2",
    author="Esukhia developers",
    author_email="esukhiadev@gmail.com",
    description="OpenPoti Toolkit allows state of the art for distributed standoff annotations on moving texts",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="Apache2",
    url="https://github.com/OpenPoti/openpoti-toolkit",
    packages=["openpoti"],
    install_requires=[
        'Click==7.0',
        'diff-match-patch==20181111',
        'PyYAML==5.1.2',
        'requests==2.22.0',
        'tqdm==4.35.0',
        'PyGithub==1.43.8',
        'GitPython==3.0.2',
    ],
    python_requires=">=3.6",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": ["openpoti=openpoti.cli:cli"] # command=package.module:function
    },
)