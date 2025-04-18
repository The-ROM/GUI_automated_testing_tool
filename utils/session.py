import json
import os

SESSION_FILE = "data/session.json"

def save_login(username, role):
    # 确保目录存在
    os.makedirs("data", exist_ok=True)
    # 将登录信息保存为 JSON 格式
    with open(SESSION_FILE, "w") as f:
        json.dump({"username": username, "role": role}, f)

def load_login():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                content = f.read().strip()  # 读取文件内容并去除空白字符
                if not content:  # 检查文件是否为空
                    return None
                return json.loads(content)  # 解析 JSON 数据
        except json.JSONDecodeError as e:
            # 记录错误日志并返回 None
            print(f"加载 session.json 时发生错误: {e}")
            return None
    return None

def clear_login():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)