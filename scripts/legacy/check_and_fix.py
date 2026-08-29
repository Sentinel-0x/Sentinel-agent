import os

print("========== 1. 文件存在性检查 ==========")
for fn in ["main.py", "fetcher.py", "analyzer.py", "pusher.py", ".env"]:
    status = "✅ 存在" if os.path.exists(fn) else "❌ 缺失"
    print(f"{fn.ljust(15)}: {status}")

print("\n========== 2. fetcher.py 内容查看 ==========")
if os.path.exists("fetcher.py"):
    with open("fetcher.py", "r", encoding="utf-8") as f:
        print(f.read())
else:
    print("⚠️ fetcher.py 不存在！")

print("\n========== 3. analyzer.py 内容查看 ==========")
if os.path.exists("analyzer.py"):
    with open("analyzer.py", "r", encoding="utf-8") as f:
        print(f.read())
else:
    print("⚠️ analyzer.py 不存在！")

