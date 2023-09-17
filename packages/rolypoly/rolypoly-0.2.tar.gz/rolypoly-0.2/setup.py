from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rolypoly",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        'docker',
    ],
    entry_points={
        'console_scripts': [
            'rolypoly=main:main',  
        ],
    },
    # Optional metadata
    author="greedydurian",
    description="A Docker image rollback tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/greedydurian/rolypoly",  
)
