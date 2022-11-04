from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'kubelink',
    version = '0.0.2',
    author = 'Volodymyr Tsumanchuk',
    author_email = 'buorn2011@gmail.com',
    license = 'MIT',
    description = 'kubelink automatically sync files to kubernetes pods',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/waverage/kubelink',
    py_modules = ['main', 'app', 'app.commands', 'app.config'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        kubelink=main:main
    '''
)