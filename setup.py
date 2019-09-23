from setuptools import setup, find_packages

setup(
    name="openpoti",
    version="0.1.0",
    author="Esukhia developers",
    author_email="esukhiadev@gmail.com",
    description="OpenPoti Toolkit allows state of the art for distributed standoff annotations on moving texts",
    license="Apache2",
    url="https://github.com/OpenPoti/openpoti-toolkit",
    packages=find_packages(),

    entry_points={
        "console_scripts": ["openpoti=openpoti.cli:cli"] # command=package.module:function
    },
)