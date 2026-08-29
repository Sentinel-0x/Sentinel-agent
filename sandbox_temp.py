import pandas as pd

data = {
    '项目名称': ['远程工作平台', 'AI Agent开发', '社区运营'],
    '进度(%)': [80, 45, 90],
    '负责人': ['Melody', 'Agent', 'DevTeam']
}

df = pd.DataFrame(data)
print("正在生成数据分析表...")
df.to_csv("report.csv", index=False)
print("数据已被成功导出至 report.csv 文件中！")