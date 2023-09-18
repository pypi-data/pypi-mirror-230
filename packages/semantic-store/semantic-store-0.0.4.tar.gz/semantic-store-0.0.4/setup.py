import os
import pkg_resources
from setuptools import setup, find_packages




setup(
    name="semantic-store",
    version="0.0.4",
    description="An in-memory vector store for semantic data storage and retrieval",
    author="Pragnesh Barik",
    packages=find_packages(where="src", exclude=["tests*"]),
    keywords=['in-memory', 'vector', 'database', 'semantic', 'search'],
    install_requires=[
        str(r)
        for r in pkg_resources.parse_requirements(
            open(os.path.join(os.path.dirname(__file__), "requirements.txt"))
        )
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    package_dir={'': 'src'},
    include_package_data=True,

)
