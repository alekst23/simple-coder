#!/bin/bash

# Directory to process
dir="human_eval_output"

# Counter for files
count_bad=0
count_ok=0

# Iterate over files
for file in "$dir"/HumanEval-*-0.py
do
  if [ -f "$file" ]; then
    echo "Processing file: $file"
    # Use Python to check if the code is valid
    if python -c "compile(open('$file').read(), '$file', 'exec')"; then
      echo "$file is a valid Python script."
      count_ok=$((count_ok+1))
    else
      echo "$file is not a valid Python script."
      count_bad=$((count_bad+1))
    fi
    
  fi
done

echo "OK: $count_ok"
echo "BAD: $count_bad"
