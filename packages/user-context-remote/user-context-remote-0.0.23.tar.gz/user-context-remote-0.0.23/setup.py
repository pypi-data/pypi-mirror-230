import setuptools
# Each Python project should have pyproject.toml or setup.py
# TODO: Please create pyproject.toml instead of setup.py (delete the setup.py)
# used by python -m build
# ```python -m build``` needs pyproject.toml or setup.py
# The need for setup.py is changing as of poetry 1.1.0 (including current pre-release) as we have moved away from needing to generate a setup.py file to enable editable installs - We might able to delete this file in the near future
PACKAGE_NAME = "user-context-remote"
package_dir = PACKAGE_NAME.replace("-", "_")

with open('README.md') as f:
    readme = f.read()

setuptools.setup(
    name='user-context-remote',
    version='0.0.23',  # https://pypi.org/project/user-context-remote/
    author="Circles",
    author_email="info@circles.life",
    # TODO: Please update the description and delete this line
    description="PyPI Package for Circles User Context Local/Remote Python",
    # TODO: Please update the long description and delete this line
    long_description="This is a package for sharing common user-context-remote functions used in different repositories",
    long_description_content_type="text/markdown",
    url="https://github.com/circles/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: Other/Proprietary License",
         "Operating System :: OS Independent",
    ],
    install_requires=[
        'python-dotenv>=0.21.1',
        'pytest>=7.4.0',
        'PyJWT>=2.8.0',
        'language-local>=0.0.4',
        'url-local>=0.0.15',
        'requests>=2.31.0',
        'httpstatus35>=0.0.1',
    ],
)
