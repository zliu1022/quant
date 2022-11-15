#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def code_lines_count(path):
    code_lines = 0
    comm_lines = 0
    space_lines = 0
    for root,dirs,files in os.walk(path):
        print('root {}'.format(root))
        print('dirs {}'.format(dirs))
        for item in files:
            file_abs_path = os.path.join(root,item)
            postfix = os.path.splitext(file_abs_path)[1]
            if postfix != '.py':
                continue
            print('{:15s}'.format(item), end=' ')
            cur_comm = 0
            cur_code = 0
            cur_empty = 0
            with open(file_abs_path) as fp:
                while True:
                    line = fp.readline()
                    if not line:
                        break
                    elif line.strip().startswith('#'):
                        comm_lines += 1
                        cur_comm += 1
                    elif line.strip().startswith("'''") or line.strip().startswith('"""'):
                        comm_lines += 1
                        cur_comm += 1
                        if line.count('"""') ==1 or line.count("'''") ==1:
                            while True:
                                line = fp.readline()
                                comm_lines += 1
                                cur_comm += 1
                                if ("'''" in line) or ('"""' in line):
                                    break
                    elif line.strip():
                        code_lines += 1
                        cur_code += 1
                    else:
                        space_lines +=1
                        cur_empty += 1
            print('code {:4d} comm {:4d} empty {:4d}'.format(cur_code, cur_comm, cur_empty))
        break
    print('total           code {:4d} comm {:4d} empty {:4d}'.format(code_lines, comm_lines, space_lines))
    return code_lines,comm_lines,space_lines

if __name__ == '__main__':
    abs_dir = os.getcwd()
    x,y,z = code_lines_count(abs_dir)
