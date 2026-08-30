import os

def read_file_content(filepath: str) -> str:
    """读取指定路径文件的内容"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file_content(filepath: str, content: str) -> str:
    """将修改后的内容写入指定路径文件"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: File {filepath} updated successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"