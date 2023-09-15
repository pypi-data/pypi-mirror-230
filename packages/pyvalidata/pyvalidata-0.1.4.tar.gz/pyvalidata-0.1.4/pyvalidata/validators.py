import re
from datetime import datetime
import jwt
import xml.etree.ElementTree as ET

def validate_data_type(data, expected_type):
    if not isinstance(data, expected_type):
        print(f"Data type validation failed. Expected {expected_type.__name__}, but got {type(data).__name__}.")
        return False
    return True

def validate_range(data, min_value=None, max_value=None):
    if min_value is not None and data < min_value:
        print(f"Numeric range validation failed. Value should be greater than or equal to {min_value}.")
        return False
    if max_value is not None and data > max_value:
        print(f"Numeric range validation failed. Value should be less than or equal to {max_value}.")
        return False
    return True

def validate_string_length(data, min_length=None, max_length=None):
    if max_length is not None and len(data) > max_length:
        print(f"String length validation failed. String length should be at most {max_length} characters.")
        return False
    if min_length is not None and len(data) < min_length:
        print(f"String length validation failed. String length should be at least {min_length} characters.")
        return False
    return True

def validate_not_null(data):
    if data is None:
        print("Not-null validation failed. Value cannot be null.")
        return False
    return True

def validate_pattern(data, pattern):
    if not re.match(pattern, data):
        print("Pattern validation failed. Value does not match the specified pattern.")
        return False
    return True

def validate_email(email):
    # Using a simple regex pattern for basic email validation
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        print("Email validation failed. Invalid email format.")
        return False
    return True

def validate_password(password, require_special_char=False):
    if require_special_char:
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    else:
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$"

    if not re.match(password_pattern, password):
        raise ValueError("Invalid password format.")
    else:
        print("Password validation passed successfully.")

def validate_date(date, date_format='YYYY/MM/DD'):
   
    date_format = date_format.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
    try:
        datetime.strptime(date, date_format)
        print("Date validation passed successfully.")
        return True
    except ValueError:
        print(f"Invalid date format. Expected format: {date_format}.")
        return False

def validate_url(url):
    # Using a regex pattern for basic URL validation
    url_pattern = r"^(https?://)?(www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$"
    if not re.match(url_pattern, url):
        print("URL validation failed. Invalid URL format.")
        return False
    return True


def validate_custom(data, data_type=None, min_value=None, max_value=None, max_length=None, min_length=None, not_null=False, pattern=None):
    try:
        is_valid = True

        if data_type:
            is_valid &= validate_data_type(data, data_type)
        if isinstance(data, (int, float)):
            is_valid &= validate_range(data, min_value, max_value)
        if isinstance(data, str):
            is_valid &= validate_string_length(data, max_length, min_length)
        if not_null:
            is_valid &= validate_not_null(data)
        if pattern:
            is_valid &= validate_pattern(data, pattern)

        return is_valid

    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return False
def validate_credit_card(card_number):
    # Use a regex pattern for credit card number validation
    card_pattern = r"^(?:\d{4}-){3}\d{4}$|^\d{16}$"
    if re.match(card_pattern, card_number):
        print("Credit Card Number validation passed successfully.")
        return True
    else:
        print("Credit Card Number validation failed. Invalid format.")
        return False

def validate_phone_number(phone):
    # Use a regex pattern for phone number validation
    phone_pattern = r"^\+(?:[0-9] ?){6,14}[0-9]$"
    if re.match(phone_pattern, phone):
        print("Phone Number validation passed successfully.")
        return True
    else:
        print("Phone Number validation failed. Invalid phone number format.")
        return False

def validate_url_path(path):
    # Use a regex pattern for URL path validation
    path_pattern = r"^/[-a-zA-Z0-9._~:/?#[\]@!$&'()*+,;=%]*$"
    if re.match(path_pattern, path):
        print("URL Path validation passed successfully.")
        return True
    else:
        print("URL Path validation failed. Invalid path format.")
        return False

def validate_hex_color(color_code):
    # Use a regex pattern for hex color code validation
    color_pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    if re.match(color_pattern, color_code):
        print("Hexadecimal Color Code validation passed successfully.")
        return True
    else:
        print("Hexadecimal Color Code validation failed. Invalid format.")
        return False

def validate_jwt(token, secret_key):
    try:
        jwt.decode(token, secret_key, algorithms=["HS256"])
        print("JWT validation passed successfully.")
        return True
    except jwt.ExpiredSignatureError:
        print("JWT validation failed. Token has expired.")
        return False
    except jwt.InvalidTokenError:
        print("JWT validation failed. Invalid token.")
        return False

def validate_mac_address(mac_address):
    # Use a regex pattern for MAC address validation
    mac_pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    if re.match(mac_pattern, mac_address):
        print("MAC Address validation passed successfully.")
        return True
    else:
        print("MAC Address validation failed. Invalid MAC address format.")
        return False

def validate_xml(xml_string):
    try:
        ET.fromstring(xml_string)
        print("XML validation passed successfully.")
        return True
    except ET.ParseError:
        print("XML validation failed. Invalid XML format.")
        return False



def validate_postal_code(postal_code, country_code='US'):
    # Use regex patterns for postal code validation by country
    postal_code_patterns = {
        'US': r"^\d{5}(-\d{4})?$",
        'CA': r"^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$",
        # Add more patterns for other countries as needed
    }
    if country_code in postal_code_patterns:
        pattern = postal_code_patterns[country_code]
        if re.match(pattern, postal_code):
            print(f"Postal Code validation passed successfully for {country_code}.")
            return True
    print(f"Postal Code validation failed. Invalid format for {country_code}.")
    return False




def validate_username(username):
    # Use a regex pattern for username validation
    username_pattern = r"^[a-zA-Z0-9_]{4,20}$"
    if re.match(username_pattern, username):
        print("Username validation passed successfully.")
        return True
    else:
        print("Username validation failed. Invalid format.")
        return False

def validate_ip_address(ip):
    # Use a regex pattern for IP address validation
    ip_pattern = r"^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\." \
                r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\." \
                r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\." \
                r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$"
    
    if re.match(ip_pattern, ip):
        print("IP Address validation passed successfully.")
        return True
    else:
        print("IP Address validation failed. Invalid IP address format.")
        return False



