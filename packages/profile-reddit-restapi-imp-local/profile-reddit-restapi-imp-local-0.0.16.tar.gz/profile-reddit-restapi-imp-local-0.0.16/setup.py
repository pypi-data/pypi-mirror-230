import setuptools
# Each Python project should have pyproject.toml or setup.py
# TODO: Please create pyproject.toml instead of setup.py (delete the setup.py)
# used by python -m build
# ```python -m build``` needs pyproject.toml or setup.py
# The need for setup.py is changing as of poetry 1.1.0 (including current pre-release) as we have moved away from needing to generate a setup.py file to enable editable installs - We might able to delete this file in the near future
setuptools.setup(
     name='profile-reddit-restapi-imp-local',  
     version='0.0.16', # https://pypi.org/project/profile-reddit-restapi-imp-local/
     author="Circles",
     author_email="info@circles.life",
     description="PyPI Package for Circles profile-local-reddit-restapi-imp Local/Remote Python",
     # TODO: Please update the long description and delete this line    
     long_description="This is a package for sharing common XXX function used in different repositories",
     long_description_content_type="text/markdown",
     url="https://github.com/circles-zone/profile-local-reddit-restapi-imp-python-package",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: Other/Proprietary License",
         "Operating System :: OS Independent",
     ],
     install_requires=[
        'praw>=7.4.0',
        'tqdm>=4.64.1',
        'database-without-orm-local>=0.0.11',
        'importer-local>=0.0.6',
        'logzio-python-handler>=4.1.0',
        'profile-local>=0.0.11',
        'url-local>=0.0.22',
        'python-dotenv>=1.0.0',
        'logger-local>=0.0.46',
        'entity-type-local>=0.0.13',
        'source-data-local>=0.0.3'
    ]
 )
