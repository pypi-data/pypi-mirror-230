import yaml

def read_prompt(path):
    raw = read_yaml(path)
    assert len(raw) > 0
    delimiters, instructions  = list(raw.keys()), list(raw.values())
    return instructions, delimiters


def read_yaml(path):
    # file containing instructions must be yaml
    file_extension = path.split(".")[-1]
    assert file_extension == "yaml" or file_extension == "yml"
    with open(path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
