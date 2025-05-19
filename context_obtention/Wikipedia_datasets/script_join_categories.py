# Defining file paths
input_file_path = '' # Path to the input file
output_file_path = '' # Path to the output file

def read_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().splitlines()

def write_lines(filepath, lines):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

# Read, deduplicate, and write
lines = read_lines(input_file_path)
unique_lines = list(dict.fromkeys(lines))
write_lines(output_file_path, unique_lines)