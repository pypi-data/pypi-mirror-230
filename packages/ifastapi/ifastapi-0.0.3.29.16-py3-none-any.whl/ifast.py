import os
import shutil
import sys


def main():
    print(sys.argv, '123333')
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

    # 遍历源文件夹中的文件，并将它们复制到运行目录下
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        if os.path.isfile(source_item):
            # 构建目标文件的路径，直接放在运行目录下
            destination_item = os.path.join(destination_dir, item)

            # 复制文件
            shutil.copy2(source_item, destination_item)
