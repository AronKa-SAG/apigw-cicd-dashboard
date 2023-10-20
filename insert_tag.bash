#!/bin/bash

# Check for the correct number of command-line arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input.yaml replacement_text"
    exit 1
fi

# Input file (YAML) and replacement text
input_file="$1"
replacement="$2"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Input file '$input_file' does not exist."
    exit 1
fi

# Perform the replacement and save it to a new file
output_file="${input_file%.yaml}_modified.yaml"  # Output file name

# Use `sed` to replace '@TAG@' with the replacement text
sed "s/@TAG@/$replacement/g" "$input_file" > "$output_file"

echo "Replacement completed. Modified YAML saved to '$output_file'."
