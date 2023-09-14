import base64
import os


def base64decode(decode_str, char_set="utf-8"):
    decoded_bytes = base64.b64decode(decode_str)
    decoded_string = decoded_bytes.decode(char_set)
    return decoded_string


def base64encode(encode_str, char_set="utf-8"):
    encoded_string = base64.b64encode(encode_str.encode(char_set)).decode(char_set)
    return encoded_string


def get_env_variable(var_name):
    result_str = os.getenv(var_name)
    return result_str
