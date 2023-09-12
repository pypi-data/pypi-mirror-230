# PyHQ (Math) - Trigonometry

''' This is the "Trigonometry" module. '''

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
import math

# Function 1 - Degrees to Radians
def degrees_to_radians(degrees):
    # Checking the Data Type of "degrees"
    if (isinstance(degrees, (int, float))):
        # Returning the Radians
        return degrees * (math.pi/180)
    else:
        raise TypeError("The 'degrees' argument must be an integer or a float.")

# Function 2 - Radians to Degrees
def radians_to_degrees(radians):
    # Checking the Data Type of "radians"
    if (isinstance(radians, (int, float))):
        # Returning the Degrees
        return radians * (180/math.pi)
    else:
        raise TypeError("The 'radians' argument must be an integer or a float.")

# Function 3 - Sin
def sin(value, unit="radians"):
    # Variables
    parameters = ["value", "unit"]

    # Parameters & Data Types
    paramaters_data = {
        "value": [(int, float), "an integer or a float"],
        "unit": [str, "a string"]
    }

    # Checking the Data Types
    for parameter in parameters:
        if (isinstance(eval(parameter), paramaters_data[parameter][0])):
            pass
        else:
            raise TypeError("The '{0}' argument must be {1}.".format(parameter, paramaters_data[parameter][1]))

    # Returning the Sin Value
    if (unit == "radians"):
        return math.sin(value)
    elif (unit == "degrees"):
        return math.sin(degrees_to_radians(value))
    else:
        raise Exception("The 'unit' argument must be either 'radians' or 'degrees'.")

# Function 4 - Cos
def cos(value, unit="radians"):
    # Variables
    parameters = ["value", "unit"]

    # Parameters & Data Types
    paramaters_data = {
        "value": [(int, float), "an integer or a float"],
        "unit": [str, "a string"]
    }

    # Checking the Data Types
    for parameter in parameters:
        if (isinstance(eval(parameter), paramaters_data[parameter][0])):
            pass
        else:
            raise TypeError("The '{0}' argument must be {1}.".format(parameter, paramaters_data[parameter][1]))

    # Returning the Cos Value
    if (unit == "radians"):
        return math.cos(value)
    elif (unit == "degrees"):
        return math.cos(degrees_to_radians(value))
    else:
        raise Exception("The 'unit' argument must be either 'radians' or 'degrees'.")

# Function 5 - Tan
def tan(value, unit="radians"):
    # Variables
    parameters = ["value", "unit"]

    # Parameters & Data Types
    paramaters_data = {
        "value": [(int, float), "an integer or a float"],
        "unit": [str, "a string"]
    }

    # Checking the Data Types
    for parameter in parameters:
        if (isinstance(eval(parameter), paramaters_data[parameter][0])):
            pass
        else:
            raise TypeError("The '{0}' argument must be {1}.".format(parameter, paramaters_data[parameter][1]))

    # Returning the Tan Value
    if (unit == "radians"):
        return math.tan(value)
    elif (unit == "degrees"):
        return math.tan(degrees_to_radians(value))
    else:
        raise Exception("The 'unit' argument must be either 'radians' or 'degrees'.")

# Function 6 - Cosec
def cosec(value, unit="radians"):
    # Variables
    parameters = ["value", "unit"]

    # Parameters & Data Types
    paramaters_data = {
        "value": [(int, float), "an integer or a float"],
        "unit": [str, "a string"]
    }

    # Checking the Data Types
    for parameter in parameters:
        if (isinstance(eval(parameter), paramaters_data[parameter][0])):
            pass
        else:
            raise TypeError("The '{0}' argument must be {1}.".format(parameter, paramaters_data[parameter][1]))

    # Returning the Cosec Value
    if (unit == "radians"):
        return 1 / sin(value)
    elif (unit == "degrees"):
        return 1 / sin(value, unit="degrees")
    else:
        raise Exception("The 'unit' argument must be either 'radians' or 'degrees'.")

# Function 7 - Sec
def sec(value, unit="radians"):
    # Variables
    parameters = ["value", "unit"]

    # Parameters & Data Types
    paramaters_data = {
        "value": [(int, float), "an integer or a float"],
        "unit": [str, "a string"]
    }

    # Checking the Data Types
    for parameter in parameters:
        if (isinstance(eval(parameter), paramaters_data[parameter][0])):
            pass
        else:
            raise TypeError("The '{0}' argument must be {1}.".format(parameter, paramaters_data[parameter][1]))

    # Returning the Sec Value
    if (unit == "radians"):
        return 1 / cos(value)
    elif (unit == "degrees"):
        return 1 / cos(value, unit="degrees")
    else:
        raise Exception("The 'unit' argument must be either 'radians' or 'degrees'.")

# Function 8 - Cot
def cot(value, unit="radians"):
    # Variables
    parameters = ["value", "unit"]

    # Parameters & Data Types
    paramaters_data = {
        "value": [(int, float), "an integer or a float"],
        "unit": [str, "a string"]
    }

    # Checking the Data Types
    for parameter in parameters:
        if (isinstance(eval(parameter), paramaters_data[parameter][0])):
            pass
        else:
            raise TypeError("The '{0}' argument must be {1}.".format(parameter, paramaters_data[parameter][1]))

    # Returning the Cot Value
    if (unit == "radians"):
        return 1 / tan(value)
    elif (unit == "degrees"):
        return 1 / tan(value, unit="degrees")
    else:
        raise Exception("The 'unit' argument must be either 'radians' or 'degrees'.")