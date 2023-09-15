Installed packages
> pip install wheel
> pip install setuptools
> pip install twine
> pip install pytest==4.4.1
> pip install pytest-runner==4.4

build library command
> python setup.py bdist_wheel
    - This command will create build, dist and <created_library_name>.egg.info folders.

Install created library command
> pip insall path/to/<root_folder_name>

To uninstall 
> pip uninsall <created_library_name>