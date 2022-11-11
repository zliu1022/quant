#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# algrithm 1
k_file_extension = '.py'

def get_file_list(file_path):
    file_list = [os.path.join(root, file) for root, dirs, files in os.walk(file_path) for file in files if
        file.endswith(k_file_extension)]
    print(file_list)
    print()
    return file_list

def count_code_lines(file_list):
    count_of_code_lines = 0
    count_of_blank_lines = 0
    count_of_annotation_lines = 0
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as fp:
            content_list = fp.readlines()
            for content in content_list:
                content = content.strip()
                if content == '':
                    count_of_blank_lines += 1
                elif content.startswith('#'):
                    count_of_annotation_lines += 1
                else:
                    count_of_code_lines += 1
    print(f'代码总行数：{count_of_code_lines}，代码空行：{count_of_blank_lines}，代码注释：{count_of_annotation_lines}')

# algrithm 2
def code_lines_count(path):
    code_lines = 0
    comm_lines = 0
    space_lines = 0
    for root,dirs,files in os.walk(path):
        for item in files:
            file_abs_path = os.path.join(root,item)
            postfix = os.path.splitext(file_abs_path)[1]
            if postfix != '.py':
                continue
            with open(file_abs_path) as fp:
                while True:
                    line = fp.readline()
                    if not line:
                        break
                    elif line.strip().startswith('#'):
                        comm_lines += 1
                    elif line.strip().startswith("'''") or line.strip().startswith('"""'):
                        comm_lines += 1
                        if line.count('"""') ==1 or line.count("'''") ==1:
                            while True:
                                line = fp.readline()
                                comm_lines += 1
                                if ("'''" in line) or ('"""' in line):
                                    break
                    elif line.strip():
                        code_lines += 1
                    else:
                        space_lines +=1
    return code_lines,comm_lines,space_lines

if __name__ == '__main__':
    file_path = '.'
    count_code_lines(get_file_list(file_path))

    abs_dir = os.getcwd()
    x,y,z = code_lines_count(abs_dir)
    print('code line: {} comment line: {} empty line: {}'.format(x,y,z))

