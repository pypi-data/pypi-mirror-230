import psutil
import os


def 根据名字获取磁盘路径(目标磁盘名: str) -> str:
    # Windows操作系统下,返回全部硬盘编号['C:\','D:\']
    # Mac/Linux下，返回硬盘名字
    所有磁盘信息 = psutil.disk_partitions()
    for item in 所有磁盘信息:
        i磁盘路径 = item.mountpoint
        i磁盘名 = os.path.basename(i磁盘路径)
        i磁盘属性 = item.opts
        # print(f"{i磁盘路径} -> {i磁盘属性}")
        if i磁盘名 == 目标磁盘名:
            return i磁盘路径


def 根据硬盘编号获取磁盘路径(目标磁盘编号: str = "Z:\\") -> str:
    # Windows操作系统下,返回全部硬盘编号['C:\','D:\']
    # Mac/Linux下，返回硬盘名字
    所有磁盘信息 = psutil.disk_partitions()
    for item in 所有磁盘信息:
        i磁盘路径: str = item.mountpoint
        i磁盘名 = item.device
        # i磁盘属性 = item.opts
        print(f"{i磁盘路径} -> {item.device},{目标磁盘编号},{item.device == 目标磁盘编号}")
        if i磁盘名 == 目标磁盘编号:
            return i磁盘路径


if __name__ == '__main__':
    print(根据名字获取磁盘路径("jm_backup") is None)
    print(根据名字获取磁盘路径("BOOTCAMP") is None)
