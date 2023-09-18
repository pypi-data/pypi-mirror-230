from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

package_name = "echoss_query"

packages = [
    package
    for package in find_packages(where=".")
    if package == package_name or package.startswith(package_name + ".")
]

setup(
    name='echoss_query',
    version='0.0.7',
    url='',
    requires=['pandas','pymongo','PyMySQL','PyYAML','opensearch'],
    license='',
    author='incheolshin',
    author_email='incheolshin@12cm.co.kr',
    description='echoss AI Bigdata Solution - Query Package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={},
    python_requires= '>3.7',
)