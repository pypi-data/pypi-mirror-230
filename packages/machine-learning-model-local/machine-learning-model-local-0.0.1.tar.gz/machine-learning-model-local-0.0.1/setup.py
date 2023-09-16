import setuptools
# Each Python project should have pyproject.toml or setup.py (if both exist, we use the setup.py)
# TODO: Please create pyproject.toml instead of setup.py (delete the setup.py)
# used by python -m build
# ```python -m build``` needs pyproject.toml or setup.py
# The need for setup.py is changing as of poetry 1.1.0 (including current pre-release) as we have moved away from needing to generate a setup.py file to enable editable installs - We might able to delete this file in the near future

PACKAGE_NAME = "machine-learning-model-local"
package_dir = PACKAGE_NAME.replace("-", "_")

with open('README.md') as f:
    readme = f.read()
    
setuptools.setup(
    # TODO: Please update the name and delete this line i.e. XXX-local or XXX-remote (without the -python-package suffix). Only lowercase, no underlines.
    name=PACKAGE_NAME,
    version='0.0.1',  # update each time
    author="Circles",
    author_email="info@circlez.ai",
    # TODO: Please update the description and delete this line
    description="PyPI Package for Circles machine-learning-model-local Python",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # TODO: Please update the URL below
    url="https://github.com/circles",  # https://pypi.org/project/machine-learning-model-local/
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    # TODO: Update which packages to include with this package
    install_requires=[
        'logger-local>= 0.0.61',
        'database-without-orm-local>=0.0.90'        
    ],
)
