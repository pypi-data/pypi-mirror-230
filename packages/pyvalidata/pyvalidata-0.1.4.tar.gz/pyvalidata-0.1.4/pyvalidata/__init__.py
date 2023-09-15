from .validators import *

def pyvalidatahelp():
    """Prints the detailed documentation and usage examples for PyValidata."""
    help_text = """
    PyValidata - Python Data Validation Package

    PyValidata is a Python package designed for easy and comprehelnsive data validation. It provides a colection of functions to validate data types, ranges, string lengths, and more. Ensure the integrity and quality of your data with PyValidata, a reliable data guardian for Python developers.

    Functions work in the way as such that passing the validation will return True, and failing validation will return False. 

    ## Features

    - Data type validation: Check if data elements belong to the expected data types.
    - Numeric range validation: Validate whether numeric data falls within specified ranges.
    - String length validation: Ensure that string data meets specified length criteria.
    - Null and missing value detection: Check for null or missing values in data.
    - Pattern matching: Validate data based on specific patterns or regular expressions.
    - Email: Validate email that meets the standard format of modern day emails.
    - Password: Check if a provided password is strong enough. For a password to be strong, it must contain at least 8 characters, one uppercase letter and 1 digit. Special characters are optional(see below for more)
    - Date: Ensure that a user enters a date in the following format YYYY-MM-DD
    - URL: Validate that a URL always starts with either https or www
    - Custom validation rules: Define and apply your custom validation rules to the data.

    ## How to Use PyValidata

    PyValidata provides functions to validate various data aspects. Here's a detailed explanation of each function:

    ### `validate_data(data, data_type=None, min_value=None, max_value=None, max_length=None, min_length=None, not_null=False, pattern=None, custom_rule_func=None)`

    Validate data based on multiple validation rules.

    - `data`: The data to be validated.
    - `data_type` (optional): Specify the expected data type (e.g., int, str, float, list). If provided, the function checks if the data matches the specified data type.
    - `min_value` and `max_value` (optional): For numeric data (int or float), specify the minimum and maximum allowed values. The function raises an error if the data is outside this range.
    - `max_length` and `min_length` (optional): For string data, specify the maximum and minimum allowed lengths. The function raises an error if the string length is outside this range.
    - `not_null` (optional): If set to `True`, the function checks if the data is not `None`.
    - `pattern` (optional): For string data, specify a regular expression pattern. The function validates whether the data matches the pattern.
    - `custom_rule_func` (optional): A custom validation function that takes the data as input and returns `True` if the data is valid or `False` otherwise.

    ### Examples

    Here are some examples of how to use the `validate_data` function:

   
    # Example 1: Validate an integer within a range
    validate_data(42, data_type=int, min_value=0, max_value=100)

    # Example 2: Validate a string with a maximum length
    validate_data("Hello, world!", max_length=20)

    # Example 3: Validate a floating-point number with a minimum value
    validate_data(10.5, data_type=float, min_value=0.0)

    # Example 4: Validate if a value is not null
    validate_data(None, not_null=True)

    # Example 5: Validate an email address using a pattern
    validate_data("example@mail.com", pattern=r"^\w+@\w+\.\w+$")

    # Example 6: Validate data with a custom rule (e.g., string length >= 6)
    validate_data("example", custom_rule_func=lambda x: len(x) >= 6)
    

    



    ###validate_data_type(data, expected_type)

    This function is used to validate if the datatype of some given data is equal to the expected data type. This function accepts two required paramaters. The first one is the data itself, this could be 100,"Hello, World!" or True. The second parameter is the expected data type of the given data. This could be int, str, float or boolean.

    ###Examples
    # Example 1: 
    validate_data_type(100,str)

    This example would raise a value error, as the given data is 100, which is an integer, but the expected datatype is a str.

    # Example 2:
    validate_data_type(100,int)

    This example would pass the validation, as the given data is 100, which is an integer, and the expected datatype is also int.


    # Example 3:
    validate_data_type("True",bool)

    This example would raise a value error, as the given data is "True", which is a string, but the expected datatype was a bool.

    # Example 4:
    validate_data_type(False,bool)

    This example would pass the validation, as the given data is False, which is a boolean value, and the expected is also bool.

    



    ###validate_range(data, min_value=None, max_value=None)

    This function is used to validate if a given int or float is within a specified range. The function features one required parameter which is data, and two optional parameters. This is so users have more flexibility while validating the range, for e.g. if they only wanted to set a max value.
    
    Note: Since min_value and max_value are positional parameters, it is recommended, but not required, to specify parameter names. 

    ###Examples


    ###Example 1:
    validate_range(10, min_value=0, max_value=100)

    This example would pass the validation, since the data is 10, and it is within the range of 0-100

    ###Example 2:

    validate_range(101, min_value=0, max_value=100)

    This example will fail the validation and raise a value error, because the data is 101, which is outside the range of 0-100

    ###Example 3:

    validate_range(0, min_value=10)

    This example would fail the validation and raise a value error, because the data is 0, which is less than the minimum value of 10.




    ###validate_string_length(data, min_length=None,max_length=None)

    
    
    
    This function is used to validate if a given string is within a specified range.  The function features one required parameter, which is data, and two optional parameters. This is so users have more flexibility while validating the range, for e.g if they onl wanted to set a max value.

    Note: Since min_length and max_length are positional parameters, it is recommended, but not required, to specify parameter names.


    ###Examples



    ###Example 1:
    validate_string_length("hello",min_length=1, max_length=10)

    This example would pass validation and return True, because the length of the string "hello" is 5, which is within the range of 1-10

    ###Example 2:
    validate_stirng_length("python", min_length=10, max_value=100)

    This example would fail the validation and return True, because the length of the string "python" is 5, which is outside the range of 10-100




    ###validate_not_null(data)
    
    This function validates if the given data is equal to None or not.




    ###validate_pattern(data, pattern)

    With this function, users can validate if some given data matches a regex pattern that the user will provide.
    


    ###validate_email(email)

    This function checks if a given email is in a modern day email format.


    ###Examples

    
    ###Example 1
    validate_email(hello@example.com)

    This would pass the validation.


    ###Example 2
    validate_email(hello@example)

    This would fail the validation.

    


    ###validate_password(password,special_char=False)

    This function ensures that a given password is strong. Check the Features to see how it's determined if a password is strong or not. 

    The function accepts two parameters, one which is the password, and special_char, which is by default set to False. If special_char is set to True, then at least one special character is required.

    

    ###Examples


    ###Example 1

    validate_password("Pythonisgreat12",special_char=False)

    This function will pass the validation.


    ###Example 2

    validate_password("Pythonisgreat12",special_char=True)

    Given the same password, this function will not pass the validation because special_char is set to True, however there aren't any special char's in the password.




    ###validate_date(date)


    This function validates if a given date is in the format that is specified by the user. Accepted date formats are YYYY/MM/DD, MM/DD/YYYY,DD/MM/YYYY.




    

    ###validate_url(url)

    This function checks if a given url is in an url format. The validate_url considers the following url formats as acceptable:

    URLs with or without "http://" or "https://" prefixes.
    URLs with or without "www." before the domain name.
    URLs with alphanumeric characters, hyphens ("-"), and dots (".") in the domain name.
    URLs with domain names ending in two or more alphabetic characters (e.g., ".com", ".org", ".net").



    Note that the function does not check if the URL is reachable or if it exists. It only checks the pattern of the url.



    ###validate_custom(data, data_type=None, min_value=None, max_value=None, max_length=None, min_length=None, not_null=False, pattern=None)


    With this function, the user can set their own custom rules for some given data in order to validate if it follows their rules or not. It isn't really a new function, but rather a combination of some previous functions.




    """

    print(help_text)


