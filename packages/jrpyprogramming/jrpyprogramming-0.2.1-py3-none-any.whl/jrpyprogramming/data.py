import pandas as pd
import pkg_resources
from shutil import copyfile


def load(file):
    # List data sources in package
    files = pkg_resources.resource_listdir(__name__, "data")

    # Map from filename (without) extension, to file name with extension
    files_w_ext = {data.split(".")[0]: data for data in files}

    # Ensure file is available
    assert file in files_w_ext, \
        (f"Dataset {file} not found. "
          "Available files are: "
         f"{', '.join(list(files_w_ext.keys())[:-1])} "
         f"and {list(files_w_ext.keys())[-1]}.")

    # Get file with appropriate extension from list of available
    file_w_ext = files_w_ext[file]

    # Get absolute path to file
    abs_path = pkg_resources.resource_filename(__name__, f"data/{file_w_ext}")

    return pd.read_csv(abs_path)


def populate_examples():
    # Get path to files relative to package
    pkg_data = pkg_resources.resource_listdir(__name__, 'data')

    # Only list files which have a name which starts with "data"
    files = [file for file in pkg_data if file.startswith('data')]

    # Copy files to current dir
    for file in files:
        abs_path = pkg_resources.resource_filename(__name__, f'data/{file}')
        copyfile(abs_path, file)
        print(f'\nCreated file {file} in current directory.\n')
