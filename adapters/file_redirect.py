# adapters/wrappers/file_redirect.py

import builtins
import os

FILESYSTEM_DIR = './autoexec/filesystem'

def custom_open(filepath, *args, **kwargs):
    # Check if the filepath is a relative path and starts with './' or is just a filename
    if filepath.startswith('./') or not os.path.isabs(filepath):
        # Redirect to the filesystem directory
        filepath = os.path.join(FILESYSTEM_DIR, os.path.basename(filepath))

    # Call the original open function with the modified file path
    return builtins.open(filepath, *args, **kwargs)