import re

with open("main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'fn_args = json.loads(' in line:
        indent = line[:len(line) - len(line.lstrip())]
        patch = f"{indent}import re\n"
        patch += f"{indent}m = re.search(r'(\\{{.*?\\}})', str(raw_args), re.DOTALL)\n"
        patch += f"{indent}fn_args = json.loads(m.group(1)) if m else json.loads(raw_args)\n"
        new_lines.append(patch)
    else:
        new_lines.append(line)

with open("main.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ main.py 容错补丁已成功注入！")
