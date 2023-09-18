import os
import shutil
import sys


def main():
    if len(sys.argv) > 1:
        match sys.argv[1]:
            case 'init':
                copy_file()


def copy_file():
    # 拷贝文件到运行目录
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # 要复制的目录名称
    directory_to_copy = 'init_builder'
    destination_dir = os.getcwd()
    print()
    source_dir = current_directory
    source_dir = os.path.join(source_dir, directory_to_copy)
    # shutil.copytree(source_dir, destination_dir)
    destination_directory = os.getcwd()
    # 使用 shutil.copytree() 复制目录内容到运行目录下
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_directory, item)

        # 判断如果是文件，则直接复制
        if os.path.isfile(source_item):
            shutil.copy2(source_item, destination_item)
        # 如果是目录，则递归复制其内容
        elif os.path.isdir(source_item) and '__' not in source_item:
            shutil.copytree(source_item, destination_item)
