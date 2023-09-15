import os
import shutil
import sys


def main():
    print(sys.argv, '123333')
    copy_file()


def copy_file():
    # 拷贝文件到运行目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(__file__)
    print(current_directory)
    print(package_dir)

    # 要复制的目录名称
    directory_to_copy = 'init_builder'
    destination_dir = os.path.join('./test1', '')
    source_dir = current_directory
    print(destination_dir)
    source_dir = os.path.join(source_dir, directory_to_copy)
    print(source_dir)
    shutil.copytree(source_dir, destination_dir)
