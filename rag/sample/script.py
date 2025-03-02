import random
import sys

# Input and output file paths
input_file = sys.argv[1]
# replace the input file by the output file
output_file = sys.argv[1]

# Read all lines from the input file
with open(input_file, "r") as f:
    lines = f.readlines()  # 2000 lines

# Randomly sample 10 lines
sampled_lines = random.sample(lines, 10)

# Write the sampled lines to the output file
with open(output_file, "w") as f:
    f.writelines(sampled_lines)

print(f"Sampled 10 lines from {input_file} and saved to {output_file}")
