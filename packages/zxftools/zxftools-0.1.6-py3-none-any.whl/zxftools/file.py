import os
import shutil

# JSON
import json
def load_json(file_path):
    '''
    加载json文件
    :param path: str 文件路径
    :return: 数据
    '''
    with open(file_path, 'r') as f:
        v = json.load(f)
    return v
def save_json(v,file_path):
    with open(file_path, 'w') as f:
        assert v is not None
        file = json.dump(v, f)
    return file

import pickle
def load_variable(file_path):
    """
    从⽂件中读取变量
    :param file_path:⽂件路径txt str
    :return: 读取的变量
    """
    with open(file_path, 'rb') as f:
        r = pickle.load(f)
    return r
def save_variable(v, file_path):
    """
    将变量存储到⽂件中
    :param v: 需要存储的变量
    :param file_path: ⽂件路径txt str
    :return:
    """
    with open(file_path, 'wb') as f:
        pickle.dump(v, f)

import yaml
def load_yaml(file_path: str, encoding: str = 'utf-8'):
    """
    windows : encoding = 'utf-8'
    """
    f = open(file_path, encoding=encoding)
    return yaml.load(f, Loader=yaml.FullLoader)
def save_yaml(v: dict, file_path: str):
    f = open(file_path, 'w')
    yaml.dump(v, f)

from io import StringIO
from io import BytesIO
def load_io(f):
    return f.getvalue()
def save_io(content,type='str'):
    if type == 'str':
        f = StringIO()
    else:
        f = BytesIO()
    f.write(content)
    return f

def file_name(path):
    count = 0
    name = path.split('/')[-1]
    paths = '/'.join(path.split('/')[:-1])
    files  = os.listdir(paths)
    for file in files:
        if file.startswith(name):
            count = count + 1

    return paths+'/' + name + '_' + str(count)

#shutil
def rm(path,**kwargs):
    # 递归地删除文件
    shutil.rmtree(path,**kwargs)
def cp(src, dst, **kwargs):
    # shutil.copyfile(file1,file2)，file1，file2是两个字符串，表示两个文件路径
    shutil.copyfile(src, dst, **kwargs)
########################

#获取环境变量
