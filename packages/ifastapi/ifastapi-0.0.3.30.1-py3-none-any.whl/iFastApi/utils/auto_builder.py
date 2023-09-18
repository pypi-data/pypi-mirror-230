import os

# 拷贝文件到运行目录
package_dir = os.path.dirname(__file__)
# 获取包的上一级目录
parent_dir = os.path.dirname(package_dir)
root_dir = './api'

# 根据api目录下 自动生成导入文件
py_files = [f for f in os.listdir(root_dir) if f.endswith('.py')]
with open(os.path.join(root_dir, '__init__.py'), 'w') as init_file:
    for py_file in py_files:
        if '__' in py_file:
            continue
        file_name = os.path.splitext(py_file)[0]
        module_name = os.path.splitext(py_file)[0].capitalize()
        import_statement = f'from .{file_name} import {module_name}\n'
        init_file.write(import_statement)
