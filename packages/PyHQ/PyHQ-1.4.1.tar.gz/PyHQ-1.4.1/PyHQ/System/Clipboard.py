# PyHQ (System) - Clipboard

''' This is the "Clipboard" module. '''

'''
Copyright 2023 Aniketh Chavare

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

# Imports
import os
import platform
import pyperclip

# Function 1 - Copy
def copy(data):
    # Checking the OS
    if (platform.uname().system in ["Windows", "Linux", "Darwin"]):
        # Checking the Data Type of "data"
        if (isinstance(data, (str, int, float, bool))):
            # Copying the Data
            pyperclip.copy(data)
        else:
            raise TypeError("The 'data' argument must be a string, integer, float, or a boolean.")
    else:
        raise Exception("This function only works on Windows, Linux, and macOS.")

# Function 2 - Copy File
def copy_file(path):
    # Checking the OS
    if (platform.uname().system in ["Windows", "Linux", "Darwin"]):
        # Checking the Data Type of "path"
        if (isinstance(path, str)):
            # Checking if Path Exists
            if (os.path.exists(path)):
                # Opening the File
                try:
                    with open(path) as file:
                        # Copying the File
                        copy(file.read())
                except:
                    raise Exception("An error occurred while copying the contents of the file. Please try again.")
            else:
                raise FileNotFoundError("The file path doesn't exist.")
        else:
            raise TypeError("The 'path' argument must be a string.")
    else:
        raise Exception("This function only works on Windows, Linux, and macOS.")

# Function 3 - Paste
def paste():
    # Checking the OS
    if (platform.uname().system in ["Windows", "Linux", "Darwin"]):
        # Returning the Last Copied Item
        return pyperclip.paste()
    else:
        raise Exception("This function only works on Windows, Linux, and macOS.")