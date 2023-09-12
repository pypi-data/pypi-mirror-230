# PyHQ (Math) - Statistics

''' This is the "Statistics" module. '''

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

# Function 1 - Mean
def mean(data):
    # Checking the Data Type of "data"
    if isinstance(data, (list, tuple, set)):
        # Checking the Length of "data"
        if (len(data) != 0):
            # Returning the Mean
            return sum(data) / len(data)
        else:
            raise Exception("The array can't be empty.")
    else:
        raise TypeError("The 'data' argument must be a list, tuple, or set.")

# Function 2 - Mode
def mode(data):
    # Checking the Data Type of "data"
    if isinstance(data, (list, tuple, set)):
        # Checking the Length of "data"
        if (len(data) != 0):
            # Returning the Mode
            return max(data)
        else:
            raise Exception("The array can't be empty.")
    else:
        raise TypeError("The 'data' argument must be a list, tuple, or set.")

# Function 3 - Median
def median(data):
    # Checking the Data Type of "data"
    if isinstance(data, (list, tuple, set)):
        # Checking the Length of "data"
        if (len(data) != 0):
            data.sort()
            mid = len(data) // 2

            # Returning the Median
            return (data[mid] + data[~mid]) / 2
        else:
            raise Exception("The array can't be empty.")
    else:
        raise TypeError("The 'data' argument must be a list, tuple, or set.")