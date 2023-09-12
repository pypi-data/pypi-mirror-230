from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name="theeverythinglibrary",
    version="0.3.8",
    description="Library with a module for almost everything",
    url="https://github.com/RobertArnosson/TheEverythingLibrary",
    author="Robert Arnorsson",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
    ],
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires= [
        "cryptography",
        "hashlib",
        "argon2",
        "uuid",
        "requests",
        "googletrans"
    ],
    python_requires=">=3.9",
    project_urls={
        "Documentation": "https://github.com/RobertArnosson/TheEverythingLibrary/wiki",
        "Bug Reports": "https://github.com/RobertArnosson/TheEverythingLibrary/issues",
        "Source": "https://github.com/RobertArnosson/TheEverythingLibrary",
    },
)