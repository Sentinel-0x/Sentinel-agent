import sys
import subprocess
from llama_cpp import Llama

# 1. 加载本地离线模型
print("正在加载本地 LLM 模型...")
llm = Llama(
    model_path="./models/qwen2.5-0.5b-instruct-q4_k_m.gguf",
    n_ctx=2048,
    verbose=False
)

def repair_code(error_msg):
    """调用本地模型进行代码修复"""
    prompt = f"以下 Python 代码运行报错，请修复它并仅输出正确的代码：\n{error_msg}"
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "你是一个专业的 Python 代码修复助手。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    return response["choices"][0]["message"]["content"]

# 2. 你的测试/业务代码逻辑
if __name__ == "__main__":
    try:
        # 这里放置你要运行的代码
        print("正在执行主任务...")
        # 故意触发一个错误测试自愈
        eval("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ") 
    except Exception as e:
        print("\n🤖 [Agent Self-Healing] 检测到代码运行错误，正在调用本地 LLM 进行自动修复...")
        fixed_code = repair_code(str(e))
        print("\n✅ 本地模型修复完成，建议代码如下：")
        print(fixed_code)