# clean_requirements.py
input_file = "requirements.txt"
output_file = "clean_requirements.txt"

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 过滤掉带有 "@ file" 的行
clean_lines = [line for line in lines if "@ file" not in line]

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(clean_lines)

print(f"Clean requirements saved to {output_file}")