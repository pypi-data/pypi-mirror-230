import os
import shutil


def 磁盘_剩余空间_GB(folder) -> tuple[float, float, float]:
    """
    获取磁盘剩余空间
    :param folder: 磁盘路径 例如 D:\\
    :return: 剩余空间,单位GB
    """
    print("当前硬盘空间检测路径:", os.path.dirname(folder))
    total, used, free = shutil.disk_usage("/")
    print("Total: %d GB" % (total // (2 ** 30)))
    print("Used: %d GB" % (used // (2 ** 30)))
    print("Free: %d GB" % (free // (2 ** 30)))
    return total / (2 ** 30), used / (2 ** 30), free / (2 ** 30)
