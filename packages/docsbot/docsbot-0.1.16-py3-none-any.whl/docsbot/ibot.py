import sys
import os

def main():
    history = []

    print("欢迎使用聊天机器人CLI！")
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                history = f.readlines()
            print("成功导入聊天记录！")
        else:
            print(f"找不到文件：{log_file}")

    while True:
        user_input = input("\n您：")
        if user_input.lower() in ["exit", "退出"]:
            with open("chat.log", "w") as f:
                for line in history:
                    f.write(line)
            print("聊天记录已保存到 chat.log 文件中。再见！")
            break
        else:
            history.append("您：" + user_input + "\n")
            print(f"机器人：{user_input}")
            history.append(f"机器人：{user_input}\n")

if __name__ == "__main__":
    main()
