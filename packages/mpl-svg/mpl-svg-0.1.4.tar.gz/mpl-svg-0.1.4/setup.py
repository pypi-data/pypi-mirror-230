from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "PROJECT.md").read_text()

setup(
    name='mpl-svg',
    version='0.1.4',
    author='Anas Bouzid',
    author_email='anasbouzid@gmail.com',
    description='Reformat Matplotlib SVGs for easier access and customzation with CSS',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/bouzidanas/mpl-svg",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.6",
    install_requires=[
        # If your component has Python dependencies, list
        # them here.
        "matplotlib >= 3.2.1",
        "beautifulsoup4 >= 4.9.0",
    ],
)