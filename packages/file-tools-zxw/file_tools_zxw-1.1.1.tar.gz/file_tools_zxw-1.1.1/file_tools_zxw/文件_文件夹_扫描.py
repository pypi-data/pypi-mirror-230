import os
from typing import List, Tuple


def 文件_扫描_fileScan(filepath: str, suffix: str = "") -> List[Tuple[str, str]]:
    """
    扫描文件夹下所有符合条件的文件
    :param filepath:扫描路径
    :param suffix:过滤后缀, 默认值为不进行后缀过滤
    :return:[(文件路径,文件名),...]
    """
    # 参数检查
    if filepath[-1] == "\\" or filepath[-1] == "/":
        raise AttributeError("parameter of filepath can not end with '\\' or '/'")

    # 执行逻辑
    fileList = []
    print("开始扫描【{0}】".format(filepath))
    if not os.path.isdir(filepath):
        print("【{0}】不是目录".format(filepath))
        exit(-1)
    for filename in os.listdir(filepath):
        if os.path.isdir(filepath + "/" + filename):
            fileList.extend(文件_扫描_fileScan(filepath + "/" + filename, suffix))
        else:
            if filename.endswith(suffix):
                fileList.append((filepath, filename))
    return fileList


def 文件夹_扫描_dirScan(filepath: str) -> list[str]:
    """
    扫描指定文件夹下所有文件夹(去重)
    :return:[文件路径,...]
    """
    dirs = 文件_扫描_fileScan(filepath=filepath, suffix="")
    dirs_files = [item[0] for item in dirs]
    #
    return list(set(dirs_files))


if __name__ == '__main__':
    path = "/Users/zhangxuewei/Documents/禅道"
    fileLists = 文件_扫描_fileScan(path, "")

    for item in fileLists:
        print(item)

    # files = 文件夹_扫描_dirScan(path)
    # print(files)
