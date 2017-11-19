#Python 3
"""
Author: Justin Whatley
Developper Intern - Wintership 2018 Challenge
https://backend-challenge-winter-2017.herokuapp.com/

"""
import json
import urllib.request

def generate_required_key_list(validation_list):
    """
    Creates a list of all the keys required for a particular customer to ensure that they are not omitted in the customer
    data fields
    :param validation_list: initial validation object
    :return: list of the required keys
    """
    requirement_list = []
    for obj in validation_list:
        for key, value in obj.items():
            if value['required']:
                requirement_list.append(key)
    return requirement_list

def update_invalid_customer(invalid_customer, customer, customer_key):
    """
    Adds a new value to the list of invalid fields for a particular customer
    :param invalid_customer: invalid_customer object
    :param customer: customer object
    :param customer_key: the field in question that was found to be invalid
    :return: updated invalid customer object
    """
    invalid_customer['id'] = str(customer['id'])
    invalid_field_keyword = 'invalid_fields'
    invalid_customer = add_key_helper(invalid_customer, invalid_field_keyword, customer_key)
    return invalid_customer

def update_invalid_customers(response, invalid_customer):
    """
    Adds a new invalid_customer object to the list of invalid_customers
    :param response: response object to be returned by the API
    :param invalid_customer: invalid customer object to be added to the list of invalid_customers
    :return: updated response object
    """
    invalid_customers_keyword = 'invalid_customers'
    response = add_key_helper(response, invalid_customers_keyword, invalid_customer)
    return response

def add_key_helper(dict, key_to_add, data_to_add):
    """
    Helper function that initializes key with an array, when necessary, and adds a new value that array
    :param dict:
    :param key_to_add:
    :param data_to_add:
    :return: the dictionary with the appropriate key/value
    """
    if key_to_add not in dict:
        dict[key_to_add] = []
        dict[key_to_add].append(data_to_add)
    else:
        dict[key_to_add].append(data_to_add)
    return dict

def process_customer_data(customers, validation_list):
    """
    :param customers: Customer data from JSON input
    :param validation_list: Validation data from JSON input
    :return: a dictionary containing invalid_customer ids and respective invalid_fields
    """

    # Puts requirements for specific items into a dictionary object
    requirement_params = {}
    for obj in validation_list:
        for key, value in obj.items():
            requirement_params[key] = value

    # Creates a list of required characteristics to ensure they've all been included
    required__key_list = generate_required_key_list(validation_list)

    response = {}
    for customer in customers:
        requirement_list_copy = list(required__key_list)
        invalid_customer = {}
        # print('\n' + str(customer))
        for customer_key, customer_value in customer.items():
            if customer_key in required__key_list:
                # Checks validity of entered fields
                is_valid = validate_data(customer_value, requirement_params[customer_key])
                # Updates invalid fields, if present
                if not is_valid:
                    invalid_customer = update_invalid_customer(invalid_customer, customer, customer_key)

            # Checks that required items are included for each customer by removing fields from the list as they appear
            # in customer data
            for requirement in required__key_list:
                if requirement == customer_key:
                    requirement_list_copy = [x for x in requirement_list_copy if not requirement]

        # Checks for missing fields that were required
        if len(requirement_list_copy) != 0:
            for requirement in requirement_list_copy:
                invalid_customer = update_invalid_customer(invalid_customer, customer, requirement)
        if invalid_customer:
            response = update_invalid_customers(response, invalid_customer)

    return response


def validate_data(value, validation_criteria):
    """
    Checks that the stored customer data meets the validation criteria set
    :param value: The value set
    :param validation_criteria: The criteria for acceptance
    :return: boolean where True indicates the value is valid and False indicates it is invalid
    """

    #if not required (or required not set), then accept null values for the category
    if 'required' in validation_criteria:
        if value is None:
            return False

    #checks that the type of the value matches what is specified
    if 'type' in validation_criteria:
        if not validate_type(value, validation_criteria['type']):
            return False

    #checks that the length of string values
    if 'length' in validation_criteria:
        # fields with this validation can be assumed to be of type String
        if type(value) is str and not validate_length(value, validation_criteria['length']):
            return False
    return True


def validate_type(value, expected_type):
    """
    Checks that the type expected matches the value set, when the value is required. If it is not required,
    null is acceptable
    :param value: the value set for a given field
    :param expected_type: the expected type of the value
    :return: boolean indicating that the value is the expected type or not
    """

    if expected_type == 'string' and type(value) is not str:
        return False
    elif expected_type == 'number' and type(value) is not int and type(value) is not float:
        return False
    elif expected_type == 'boolean' and type(value) is not bool:
        return False
    return True

def validate_length(value, expected_length):
    """
    Checks that the length of a string satisfies length requirements in the validation section
    :param value: the value set for a given field
    :param expected_length: an object containing 'min' and 'max' lengths to the string
    :return: boolean indicating that the value is the expected length or not
    """
    if 'min' in expected_length and 'max' in expected_length:
        return expected_length['min'] <= len(value) <= expected_length['max']
    elif 'min' in expected_length:
        return len(value) >= expected_length['min']
    elif 'max' in expected_length:
        return len(value) <= expected_length['max']
    return True

def exist_more_customers(pagination):
    """
    Checks whether there exists more customers (or pages to parse) based on the total number of expected customers,
    the current_page and the number of customers presented per page
    :param pagination: pagination details from JSON input
    :return: boolean indicated whether there exist more customers on the next page or not
    """
    return pagination['total'] - pagination['current_page']*pagination['per_page'] >= 0

def update_page_query_param(customer_data_url_orig, page_counter):
    """
    Updates the page query to the next page
    :param customer_data_url_orig: str original page data url
    :param page_counter: the page number to query
    :return: the page following the given url
    """
    if page_counter:
        return customer_data_url_orig + '?page=' + str(page_counter + 1)
    else:
        return customer_data_url_orig

def local_test():
    customer_data_local = "customer_page_3.json"

    # Loads page URL
    with open(customer_data_local) as url:
        page_data = json.load(url)

        # Validate customers
        api_response = process_customer_data(page_data['customers'], page_data['validations'])
        # api_response['customers'] = page_data['customers']
        # api_response['pagination'] = page_data['pagination']

        print(json.dumps(api_response))

    exit()

if __name__ == '__main__':

    # local_test()

    customer_data_url_orig = "https://backend-challenge-winter-2017.herokuapp.com/customers.json"
    validation_parameters = {}

    page_counter = 0
    while True:
        page_data = {}

        # Updates the page query parameter
        customer_data_url = update_page_query_param(customer_data_url_orig, page_counter)

        # Loads page URL
        with urllib.request.urlopen(customer_data_url) as url:
            page_data = json.loads(url.read().decode())

            # Validate customers
            api_response = process_customer_data(page_data['customers'], page_data['validations'])
            api_response['customers'] = page_data['customers']
            api_response['pagination'] = page_data['pagination']

            print(json.dumps(api_response))
            page_counter = page_counter + 1

            # Checks that there are still customers on the following page, otherwise exits the loop
            if not exist_more_customers(page_data['pagination']):
                break





