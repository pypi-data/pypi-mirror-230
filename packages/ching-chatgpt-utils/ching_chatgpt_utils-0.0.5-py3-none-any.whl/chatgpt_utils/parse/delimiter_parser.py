"""
Helpful functions for parsing ChatGPT Output
"""
import re

def extract_text_by_delimiter(target_string, delimiter):
    pattern = re.escape(delimiter) + r'(.*?)' + re.escape(delimiter)
    matches = re.findall(pattern, target_string, re.DOTALL)
    if len(matches) > 0:
        return matches[0].strip()
    return None
        