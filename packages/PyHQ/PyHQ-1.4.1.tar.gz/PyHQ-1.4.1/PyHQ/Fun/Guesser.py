# PyHQ (Fun) - Guesser

''' This is the "Guesser" module. '''

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
import json
import requests
from types import NoneType

# Function 1 - Age
def age(name, country=None):
    # Variables
    parameters = ["name", "country"]

    # Parameters & Data Types
    paramaters_data = {
        "name": [str, "a string"],
        "country": [(str, NoneType), "a string"]
    }

    # Checking the Data Types
    for parameter in parameters:
        if (isinstance(eval(parameter), paramaters_data[parameter][0])):
            pass
        else:
            raise TypeError("The '{0}' argument must be {1}.".format(parameter, paramaters_data[parameter][1]))

    # Fetching and Returning the Age
    try:
        # Checking the Value of "country"
        if (country == None):
            # Fetching the Age
            response = json.loads(requests.get("https://api.agify.io?name=" + name).text)
        else:
            # Fetching the Age
            response =  json.loads(requests.get("https://api.agify.io?name=" + name + "&country_id=" + country).text)

        # Deleting Unwanted Keys
        del response["count"]

        # Returning the Age
        return response
    except requests.ConnectionError:
        raise ConnectionError("A connection error occurred. Please try again.")
    except:
        raise Exception("Something went wrong. Please try again.")

# Function 2 - Gender
def gender(name, country=None):
    # Variables
    parameters = ["name", "country"]

    # Parameters & Data Types
    paramaters_data = {
        "name": [str, "a string"],
        "country": [(str, NoneType), "a string"]
    }

    # Checking the Data Types
    for parameter in parameters:
        if (isinstance(eval(parameter), paramaters_data[parameter][0])):
            pass
        else:
            raise TypeError("The '{0}' argument must be {1}.".format(parameter, paramaters_data[parameter][1]))

    # Fetching and Returning the Gender
    try:
        # Checking the Value of "country"
        if (country == None):
            # Fetching the Gender
            response =  json.loads(requests.get("https://api.genderize.io?name=" + name).text)
        else:
            # Fetching the Gender
            response =  json.loads(requests.get("https://api.genderize.io?name=" + name + "&country_id=" + country).text)

        # Deleting Unwanted Keys
        del response["count"]

        # Returning the Gender
        return response
    except requests.ConnectionError:
        raise ConnectionError("A connection error occurred. Please try again.")
    except:
        raise Exception("Something went wrong. Please try again.")

# Function 3 - Nation
def nation(name):
    # Checking the Data Type of "name"
    if (isinstance(name, str)):
        # Fetching and Returning the Nation
        try:
            # Fetching the Nation
            response = json.loads(requests.get("https://api.nationalize.io?name=" + name).text)

            # Deleting Unwanted Keys
            del response["count"]

            # Returning the Nation
            return response
        except requests.ConnectionError:
            raise ConnectionError("A connection error occurred. Please try again.")
        except:
            raise Exception("Something went wrong. Please try again.")
    else:
        raise TypeError("The 'name' argument must be a string.")