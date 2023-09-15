"""
Utility functions
"""
import os
import logging
import hashlib
import json
import time
from datetime import datetime
import traceback

from google.cloud import secretmanager
from google.cloud import storage

from google.api_core.exceptions import Conflict, NotFound

import google.api_core.exceptions as google_exceptions

from sendgrid.helpers.mail import Mail

import dotenv

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

class HttpResponseError(Exception):
    def __init__(self, status_code):
        super().__init__(f"Unexpected HTTP response: {status_code}")
        self.status_code = status_code

def create_bucket_if_not_exists(client, bucket_name, location="US"):
    """Creates a new bucket if it does not exist in Google Cloud Storage."""
    try:
        bucket = client.get_bucket(bucket_name)
        print(f"Bucket {bucket_name} already exists.")
    except NotFound:
        try:
            bucket = client.create_bucket(bucket_name, location=location)
            print(f"Bucket {bucket_name} created successfully in the {location} region.")
        except Conflict as e:
            print(f"Conflict error while creating bucket: {e}")

# Example usage
# create_bucket_if_not_exists("your_bucket_name_here", "EUROPE-WEST1")


def create_object_in_bucket(client, bucket_name, object_name, data):
    """Creates an object with data in the specified GCS bucket."""
    try:
        # Get the bucket
        bucket = client.get_bucket(bucket_name)
    except NotFound as e:
        print(f"Error: Bucket not found - {e}")
        return

    # Create a new blob and upload data
    blob = bucket.blob(object_name)
    data_as_json_str = json.dumps(data)
    blob.upload_from_string(data_as_json_str)

    print(f"Object '{object_name}' created in bucket '{bucket_name}' with data: {data}")

# Usage:
# Replace 'your_bucket_name_here' with your bucket name,
# 'your_object_name_here' with the name of the object you want to create,
# and 'your_data_here' with the data you want to store in the object.
# create_object_in_bucket('your_bucket_name_here', 'your_object_name_here', 'your_data_here')


def send_email(client, from_email, recipient_list, subject, body):
    if not isinstance(recipient_list, list):
        LOG.info(f"recipient_list is not a list: {recipient_list}")
        LOG.info(f"type(recipient_list): {type(recipient_list)}")
        LOG.info("trying to convert to list")
        new_list = recipient_list.strip('[]').split(',')
        recipient_list = [item.strip() for item in new_list]
        LOG.info(f"modified recipient_list: {recipient_list}")
    try:
        message = Mail(
            from_email=from_email,
            to_emails=recipient_list,
            subject=subject,
            plain_text_content=body
        )
        response = client.client.mail.send.post(request_body=message.get())
        if 200 <= response.status_code <= 299:
            LOG.info(f"Email sent successfully, response code: {response.status_code}")
        else:
            raise(HttpResponseError(response.status_code))
    except Exception as exc:
        # if CONFIG["DEBUG"]:
        #     raise exc
        LOG.error(f"Exception: {exc}")
        if isinstance(exc, HttpResponseError):
            if "status_code" in dir(response):
                LOG.error(f"status_code: {response.status_code}")
            if "body" in dir(response):
                LOG.error(f"body: {response.body}")
            if "headers" in dir(response):
                LOG.error(f"headers: {response.headers}")
        LOG.error(f"Stacktrace: {traceback.print_stack()}")
        LOG.error(f"Stacktrace: {traceback.format_exc()}")
        LOG.error(f"client: {client}")
        LOG.error(f"from_email: {from_email}")
        LOG.error(f"recipient_list: {recipient_list}")
        LOG.error(f"subject: {subject}")
        LOG.error(f"body: {body}")
        raise exc
# Usage:
# send_email('YOUR_SENDGRID_API_KEY', 'your-email@example.com', ['recipient1@example.com', 'recipient2@example.com'], 'Test Subject', 'Test Body')

def timestamp():
    # Format the date and time as a string in the ISO 8601 format with 'Z' as the timezone indicator
    current_time_utc = datetime.utcnow()
    timestamp_string = current_time_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return timestamp_string

class Timer():
    def __init__(self, name):
        self.name = name
        self.start_time = time.time()

    def record_elapsed_time(self, dictionary):
        current_time = time.time()
        dictionary[self.name] = current_time - self.start_time

    def log_elapsed_time(self):
        current_time = time.time()
        LOG.info(f"{self.name} elapsed time: {current_time - self.start_time}")

class ServerError(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, message="ServerError"):
        self.error = "ServerError"
        self.message = message
        super().__init__(message)

# class StripeError(ServerError):
#     """Base class for exceptions in this module."""
#     def __init__(self, message="StripeError"):
#         self.message = message
#         super().__init__(message)
#         self.error = "StripeError"

# Don't think this is used, but...
# def remove_structures(dictionary):
#     new_dict = {}
#     for key, value in dictionary.items():
#         if (isinstance(value, str)
#             or isinstance(value, int)
#             or isinstance(value, float)):
#             new_dict[key] = value
#         else:
#             new_dict[key] = (f'This backend does not support '
#                             f'{type(value)} for metadata values')
#     return new_dict


# def create_google_cloud_storage_file(bucket_name, source_file_name):
#     """Creates a new file."""
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(source_file_name)

#     if not blob.exists():
#         blob.upload_from_string('')
#         print("File {} created.".format(source_file_name))
#     else:
#         print("File {} already exists.".format(source_file_name))

def get_config(environment_variables, dotenv_list=[".env"]):
    CONFIG = {}
    if dotenv_list == [".env"]:
        dotenv_list = [".env", "dev.env"]
    for dotenv_file in dotenv_list:
        dotenv_values = dotenv.dotenv_values(dotenv_file)
        for variable in environment_variables:
            CONFIG[variable] = os.getenv(variable)
            if CONFIG[variable] is None and variable in dotenv_values:
                CONFIG[variable] = dotenv_values[variable]
    return CONFIG


def get_secret_with_retry(project, secret_name, max_retries=5, sleep_seconds=0.5):
    """Get secret from Google Secret Manager with exponential backoff retry."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            secrets_client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{project}/secrets/{secret_name}/versions/latest"
            response = secrets_client.access_secret_version(name=name)
            secret_value = response.payload.data.decode('UTF-8')
            return secret_value
        except google_exceptions.ServiceUnavailable as exp:
            print(f"Caught a 504 error: {exp}")
            retry_count += 1
            time.sleep(sleep_seconds * 2 ** retry_count)  # exponential sleep
    raise Exception(
        f"Failed to retrieve secret {secret_name} after {max_retries} retries. "
        f"Last sleep was {sleep_seconds * 2 ** retry_count} seconds.")


# def initialize_stripe(stripe_key):
#     """Initialize Stripe with the given key."""
#     import stripe
#     stripe.api_key = stripe_key
#     return stripe


# def clean_stripe_dict(stripe_object):
#     jsonEncoded = json.dumps(stripe_object, default=lambda o: '<not serializable>')
#     pythonDict = json.loads(jsonEncoded)
#     return remove_none_values_recursive(pythonDict)


# def remove_none_values_recursive(iterable):
#     if isinstance(iterable, dict):
#         new_dict = {}
#         for key, value in iterable.items():
#             value = remove_none_values_recursive(value)
#             if value is not None:
#                 new_dict[key] = value
#         if not new_dict:
#             return None
#         return new_dict

#     elif isinstance(iterable, list):
#         new_list = []
#         for value in iterable:
#             value = remove_none_values_recursive(value)
#             if value is not None:
#                 new_list.append(value)
#         if not new_list:
#             return None
#         return new_list

#     elif isinstance(iterable, tuple):
#         new_tuple = tuple(remove_none_values_recursive(value) for value in iterable if value is not None)
#         if not new_tuple:
#             return None
#         return new_tuple

#     elif isinstance(iterable, set):
#         new_set = {remove_none_values_recursive(value) for value in iterable if value is not None}
#         if not new_set:
#             return None
#         return new_set

#     else:
#         return iterable


# def replace_values_recursive(iterable, replacements):
#     if isinstance(iterable, dict):
#         new_dict = {}
#         for key, value in iterable.items():
#             if key in replacements:
#                 value = replacements[key]
#             else:
#                 value = replace_values_recursive(value, replacements)
#             if value is not None:
#                 new_dict[key] = value
#         if not new_dict:
#             return None
#         return new_dict

#     elif isinstance(iterable, list):
#         new_list = []
#         for value in iterable:
#             if key in replacements:
#                 value = replacements[key]
#             else:
#                 value = replace_values_recursive(value, replacements)
#             if value is not None:
#                 new_list.append(value)
#         if not new_list:
#             return None
#         return new_list

#     elif isinstance(iterable, tuple):
#         if key in replacements:
#             value = replacements[key]
#         else:
#             new_tuple = tuple(replace_values_recursive(value, replacements) for value in iterable if value is not None)
#         if not new_tuple:
#             return None
#         return new_tuple

#     elif isinstance(iterable, set):
#         if key in replacements:
#             value = replacements[key]
#         else:
#             new_set = {replace_values_recursive(value, replacements) for value in iterable if value is not None}
#         if not new_set:
#             return None
#         return new_set

#     else:
#         return iterable

# def filter_data(template, data):
#     if template == {}:
#         return data
#     filtered_data = {}
#     for key, value in template.items():
#         if isinstance(value, dict):
#             if data:
#                 filtered_data[key] = filter_data(value, data.get(key, None))
#             else:
#                 filtered_data[key] = None
#         else:
#             if data:
#                 filtered_data[key] = data.get(key, None)
#             else:
#                 filtered_data[key] = None
#     return filtered_data

# def filter_data(template, data):
#     if template == {}:
#         return data
#     filtered_data = {}
#     for key, value in template.items():
#         if isinstance(value, dict):
#             filtered_data[key] = filter_data(value, data.get(key)) if data else None
#         else:
#             filtered_data[key] = data.get(key) if data else None
#     return filtered_data

# def hash_dictionary(data):
#     # Convert the dictionary to a JSON string representation
#     json_str = json.dumps(data, sort_keys=True)

#     # Hash the JSON string using SHA-256 algorithm
#     hash_object = hashlib.sha256(json_str.encode())

#     # Return the hexadecimal representation of the hash
#     return hash_object.hexdigest()
