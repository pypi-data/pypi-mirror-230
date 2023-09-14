import os


def get项目根目录(projectName: str = "pyAutoWeigh"):
    """
    :param projectName:
    :return: /Users/zhangxuewei/Documents/GitHub/pyAutoWeigh/
    """
    # 获取当前文件的目录
    cur_path = os.path.abspath(os.path.dirname(__file__))
    print(cur_path)
    # 获取根目录
    root_path = cur_path[:cur_path.rindex(f"{projectName}") + len(f"{projectName}")] + "/"
    print(f"proj = {root_path}")
    return root_path


if __name__ == '__main__':
    get项目根目录(projectName="pyAutoWeigh")
