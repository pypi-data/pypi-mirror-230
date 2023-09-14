import setuptools
# Each Python project should have pyproject.toml or setup.py
# TODO: Please create pyproject.toml instead of setup.py (delete the setup.py)
# used by python -m build
# ```python -m build``` needs pyproject.toml or setup.py
# The need for setup.py is changing as of poetry 1.1.0 (including current pre-release) as we have moved away from needing to generate a setup.py file to enable editable installs - We might able to delete this file in the near future
PACKAGE_NAME = "group-profile-remote"
package_dir = PACKAGE_NAME.replace("-", "_")

with open('README.md') as f:
    readme = f.read()

setuptools.setup(
     # TODO: Please update the name and delete this line i.e. XXX-local or XXX-remote (without the -python-package suffix). Only lowercase, no underlines.
     name=PACKAGE_NAME,  
     # TODO: Please update the URL bellow
     version='0.0.8', # https://pypi.org/project/group-profile-remote/
     author="Circles",
     author_email="info@circles.life",
     # TODO: Please update the description and delete this line
     description="PyPI Package for Circles Group-Profile-Remote Python",
     # TODO: Please update the long description and delete this line    
     long_description="This is a package for sharing common Group-Profile-Remote function used in different repositories",
     long_description_content_type="text/markdown",
     url="https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
     ppackages=[package_dir],
     package_dir={package_dir: f'{package_dir}/src'},
     package_data={package_dir: ['*.py']},
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: Other/Proprietary License",
         "Operating System :: OS Independent",
     ],
     install_requires=[
        'python-dotenv>=1.0.0',
        'pytest>=7.4.0',
        'database-without-orm-local>=0.0.11',
        'logzio-python-handler>= 4.1.0',
        'user-context-remote>=0.0.23',
        'logger-local>=0.0.11',
        'url-local>=0.0.27',
    ],
 )
