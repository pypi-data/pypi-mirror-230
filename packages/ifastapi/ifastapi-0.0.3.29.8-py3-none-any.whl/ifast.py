import os
import shutil
import sys


def main():
    print(sys.argv)
    copy_file()


def copy_file():
    # 拷贝文件到运行目录
    package_dir = os.path.dirname(__file__)
    # 获取包的上一级目录
    parent_dir = os.path.dirname(package_dir)

    # 要复制的目录名称
    directory_to_copy = './iFastApi/init_builder'
    destination_dir = os.path.join('./test1', '')
    source_dir = os.path.join(parent_dir, '')
    print(destination_dir)
    source_dir = os.path.join(source_dir, directory_to_copy)
    print(source_dir)
    shutil.copytree(source_dir, destination_dir)


