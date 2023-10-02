import re

def get_string_instances(string, text):
    return len(re.findall(string, text))