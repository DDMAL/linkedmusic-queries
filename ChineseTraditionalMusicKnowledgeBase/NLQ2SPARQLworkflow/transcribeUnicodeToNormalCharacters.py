# This script transcribes Unicode escape sequences in a text file to their corresponding characters.
import re
import sys

def replace_unicode(match):
    escape = match.group(0)
    hex_value = escape[2:]
    return chr(int(hex_value, 16))

def transcribe_unicode(text):
    return re.sub(r'\\u[0-9a-fA-F]{4}', replace_unicode, text)

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile:
        content = infile.read()
    new_content = transcribe_unicode(content)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write(new_content)
    print(f"Transcribed file saved to {output_path}")

if __name__ == "__main__":
    # If input/output filenames are given as command-line arguments, use them.
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        # Default file names (assumed present in the same folder as the script).
        input_file = "constructedDataForMusicTypeBfPlace.ttl"
        output_file = "constructedDataForMusicTypeBfPlace_transcribed.ttl"
        print(f"Using default input file: {input_file}")
        print(f"Using default output file: {output_file}")

    process_file(input_file, output_file)