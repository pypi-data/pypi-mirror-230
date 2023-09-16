"""
Helpful functions for parsing ChatGPT Output
"""
import regex as re
import json

"""
Extract the first occuring JSON object from JSON string
"""
def extract_json_from_string(input_string, output_type = "dict"):
    try:
        json_pattern = r"\{(?:[^{}]|(?R))*\}"
        json_match = re.search(json_pattern, input_string)
        if json_match:
            json_str = json_match.group(0) 
        if output_type == "dict":
            return eval(json_str)
        if output_type == "json":
            return json.dumps(eval(json_str))
    except:
        raise ValueError