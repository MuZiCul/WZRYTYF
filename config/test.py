import os
import shutil


def move_duplicates(source_folder, destination_folder):
    # 获取源文件夹中的所有文件
    files = os.listdir(source_folder)

    for file1 in files:
        filepath1 = os.path.join(source_folder, file1)

        if os.path.isfile(filepath1):
            for file2 in files:
                filepath2 = os.path.join(source_folder, file2)

                if os.path.isfile(filepath2) and file1 != file2 and file1[:-4] in file2[:-4]:
                    # 如果file1被file2包含，则移动file1到目标文件夹
                    dest_filepath = os.path.join(destination_folder, file1)
                    shutil.move(filepath1, dest_filepath)
                    break


# 指定源文件夹和目标文件夹的路径
source_folder = 'G:/123456'
destination_folder = 'G:/tag'

# 调用函数进行文件去重和移动操作
move_duplicates(source_folder, destination_folder)
