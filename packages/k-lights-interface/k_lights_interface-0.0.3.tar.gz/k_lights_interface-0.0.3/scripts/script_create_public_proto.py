import sys
import re
from pathlib import Path
import os
import uuid

banned_words = ["calibration", "compensation","clear_whole_external"]

current_script_directory = Path(os.path.dirname(os.path.realpath(__file__)))
input_file =current_script_directory / "../raw_proto/k_full.proto"
output_file =  current_script_directory / "../raw_proto/k_public.proto"

print(input_file)
print(output_file)
with open(input_file, 'r') as f:
    lines = f.readlines()



def remove_blocks(lines, banned_word):
    new_lines = []
    message_block = False
    brace_count = 0
    for line in lines:
        line_as_lower = line.lower()
        if re.search(f"{banned_word}.*{{", line_as_lower):
            message_block = True

        if message_block:
            brace_count += line.count('{')
            brace_count -= line.count('}')
            if brace_count == 0:
                message_block = False
                continue 
        if not message_block:
            new_lines.append(line)
    return new_lines

def replace_banned_enums(lines, search_word):
    new_lines = []
    enum_block = False
    brace_count = 0
    for line in lines:
        if re.search("enum ", line):
            enum_block = True
        if enum_block:
            brace_count += line.count('{')
            brace_count -= line.count('}')
            if brace_count == 0:
                enum_block = False
                new_lines.append(line)
                continue 
        if search_word in line.lower() and enum_block:
            uuid_str = str(uuid.uuid4())
            uuid_str = uuid_str.replace('-', '_')
            new_line = re.sub(r'.*(?=\s*=)', 'not_for_public_use' +  uuid_str, line)
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    return new_lines

def remove_lines_with_banned_words(lines, banned_word):
    new_lines = []
    for line in lines:
        if banned_word in line.lower():
            continue
        else:
            new_lines.append(line)
    return new_lines

def remove_all_comments(complete_str,banned_word):
    # combined_string = '\n'.join(lines)
    # Remove single line comments
    single_line_comment_removed = re.sub(r'//.*', '', complete_str)
    # Remove multiline comments
    multiline_comment_removed = re.sub(r'/\*.*?\*/', '', single_line_comment_removed, flags=re.DOTALL)
    new_lines = multiline_comment_removed.split('\r')

    return multiline_comment_removed

for banned_word in banned_words:
    lines = remove_blocks(lines, banned_word)

for banned_word in banned_words:
    lines = replace_banned_enums(lines, banned_word)

for banned_word in banned_words:
    lines = remove_lines_with_banned_words(lines, banned_word)


complete_str = '\n'.join(lines)
for banned_word in banned_words:
    complete_str = remove_all_comments(complete_str, banned_word)

with open(output_file, 'w') as f:
    f.write(complete_str)




