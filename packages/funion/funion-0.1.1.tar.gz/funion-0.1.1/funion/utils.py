import re


def read_a_file(file_path):
    return open(file_path, 'r', encoding="utf-8").read()



def remove_comments(input_str):
    # Remove single-line comments (// ...)
    input_str = re.sub(r'\/\/.*', '', input_str)

    # Remove multi-line comments (/* ... */)
    input_str = re.sub(r'\/\*.*?\*\/', '', input_str, flags=re.DOTALL)

    # Remove unnecessary space lines
    input_str = re.sub(r'\n\s*\n', '\n', input_str, flags=re.MULTILINE)

    return input_str


def remove_import_statements(file_content:str)->str:
    # Define the regular expression pattern to match import statements
    import_pattern = r'^\s*import\s+[^\n\r;]+[;\n\r]'
    # Remove import statements from the Solidity code
    cleaned_code = re.sub(import_pattern, '', file_content, flags=re.MULTILINE)

    return cleaned_code