import setuptools
# used by python -m build
# python -m build needs pyproject.toml or setup.py
setuptools.setup(
    name='contact-local',
    version='0.0.20',
    author="Circlez",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles contact-local Local/Remote Python",
    long_description="This is a package for sharing common contact function used in different repositories",
    long_description_content_type="text/markdown",
    url="https://github.com/circles",
    packages=setuptools.find_packages(),
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: Other/Proprietary License",
         "Operating System :: OS Independent",
    ],
)
