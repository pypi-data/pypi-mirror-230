from setuptools import setup, find_packages

setup(
    name="rolypoly",
    version="0.1",
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
    url="https://github.com/greedydurian/rolypoly",  
)
