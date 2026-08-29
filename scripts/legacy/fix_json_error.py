with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 用更强大的容错解析覆盖原有逻辑
target = 'raw_args = tool_call["function"].get("arguments", "{}")'

new_code = '''raw_args = tool_call["function"].get("arguments", "{}")
            try:
                fn_args = json.loads(raw_args)
            except Exception:
                import re
                match = re.search(r'\{.*?\}', raw_args, re.DOTALL)
                if match:
                    try:
                        fn_args = json.loads(match.group(0))
                    except Exception:
                        fn_args = {}
                else:
                    fn_args = {}'''

if target in content:
    # 找到从 raw_args 到 try/except 这一块进行精准替换
    start_idx = content.find(target)
    end_idx = content.find('logging.info(f"🛠️ Agent 决定调用工具', start_idx)
    if start_idx != -1 and end_idx != -1:
        content = content[:start_idx] + new_code + "\n\n            " + content[end_idx:]
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 智能 JSON 解析容错机制补丁安装成功！")
    else:
        print("⚠️ 未准确定位替换区间，建议检查代码结构")
else:
    print("⚠️ 未找到匹配的目标代码")
