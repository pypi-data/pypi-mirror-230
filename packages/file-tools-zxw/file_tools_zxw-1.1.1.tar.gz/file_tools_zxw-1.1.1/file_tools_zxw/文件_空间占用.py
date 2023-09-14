import os


def 文件_占用空间_获取_MB(files_path: list[str]) -> float:
    total_size = 0.0

    for item in files_path:
        file_size_bytes = os.stat(item)
        file_size_mb = file_size_bytes.st_size / (1024 * 1024)
        total_size += file_size_mb

    return total_size


if __name__ == '__main__':
    files = ["/Users/zhangxuewei/Google 云端硬盘/软件开发/润心/软件测试-性能测试/配套软件/禅道.15.4.win64.exe",
             "/Users/zhangxuewei/Google 云端硬盘/软件开发/润心/软件测试-性能测试/配套软件/禅道.15.4.win64.exe"]
    print(文件_占用空间_获取_MB(files))
