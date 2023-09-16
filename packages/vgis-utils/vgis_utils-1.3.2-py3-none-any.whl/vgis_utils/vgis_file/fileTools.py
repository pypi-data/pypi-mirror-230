"""
===================================
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: fileTools.py
@Date: Create in 2021/1/28 12:23
@Description: 对文件的操作
@ Software: PyCharm
===================================
"""
import json
import os
import shutil
import zipfile

from vgis_utils.commonTools import CommonHelper


class FileHelper:
    # 初始化
    def __init__(self):
        pass

    # 根据路径创建文件夹
    # 可以创建下面的几级目录
    @staticmethod
    def mkdir(path):
        folder = os.path.exists(path)
        # 判断是否存在文件夹如果不存在则创建为文件夹
        if not folder:
            # 创建文件时如果路径不存在会创建这个路径
            os.makedirs(path)

    # 根据路径创建文件夹
    # 可以创建下面的几级目录
    @staticmethod
    def mkdirs(path_list):
        for path in path_list:
            folder = os.path.exists(path)
            # 判断是否存在文件夹如果不存在则创建为文件夹
            if not folder:
                # 创建文件时如果路径不存在会创建这个路径
                os.makedirs(path)

    # 清空路径文件夹下所有文件
    @staticmethod
    def rmdir(img_dir):
        images = os.listdir(img_dir)
        for name in images:
            img_path = os.path.join(img_dir, name)
            os.remove(img_path)

    # 删除文件夹下的文件及子文件夹
    @staticmethod
    def rmDirAndFiles(file_dir):
        shutil.rmtree(file_dir)

    # 删除临时目录，包括其下面的文件
    @staticmethod
    def delete_tmp_dir(dir_path):
        common_utity = CommonHelper()
        for i in os.listdir(dir_path):
            file_data = dir_path + common_utity.get_dash_in_system()
            if os.path.isfile(file_data) is True:
                os.remove(file_data)
            else:
                FileHelper.delete_tmp_dir(file_data)

    # 删除文件
    @staticmethod
    def del_file(path):
        ls = os.listdir(path)
        for i in ls:
            c_path = os.path.join(path, i)
            if os.path.isdir(c_path):
                FileHelper.del_file(c_path)
            else:
                os.remove(c_path)


    # 得到文件的完整名称
    @staticmethod
    def get_file_name(orgin_file_path):
        (file_pre_path, temp_filename) = os.path.split(orgin_file_path)
        return temp_filename

    # 得到文件名称的前缀（只含名称）
    @staticmethod
    def get_file_name_prefix(orgin_file_path):
        (file_pre_path, temp_filename) = os.path.split(orgin_file_path)
        (shot_name, file_ext) = os.path.splitext(temp_filename)
        return shot_name

    # 得到文件名称的后缀
    @staticmethod
    def get_file_name_suffix(orgin_file_path):
        (file_pre_path, temp_filename) = os.path.split(orgin_file_path)
        (shot_name, file_ext) = os.path.splitext(temp_filename)
        return file_ext

    # 为文件增加副本，按照给出的后缀名
    @staticmethod
    def get_new_file_path_add_suffix(orgin_file_path, suffix_name):
        (file_pre_path, temp_filename) = os.path.split(orgin_file_path)
        (shot_name, file_ext) = os.path.splitext(temp_filename)
        common_utity = CommonHelper()
        bak_file_path = file_pre_path + common_utity.get_dash_in_system() + shot_name + "_" + suffix_name + file_ext
        return bak_file_path

    # 为文件名称增加后缀
    @staticmethod
    def add_subfix_on_file_name(file_dir_path, add_sub):
        file_names = os.listdir(file_dir_path)
        for temp in file_names:
            file = os.path.join(file_dir_path, temp)
            fname, ext = os.path.splitext(file)
            base_name = os.path.basename(fname)
            new_n = base_name + add_sub + ext
            os.rename(os.path.join(file_dir_path, temp), os.path.join(file_dir_path, new_n))

    # 在目标文件路径的同级目录下创建临时目录,并返回路径
    @staticmethod
    def make_tmp_dir_onside_file(dest_file_path):
        common_utity = CommonHelper()
        (file_pre_path, temp_filename) = os.path.split(dest_file_path)
        tmp_path = file_pre_path + common_utity.get_dash_in_system() + common_utity.get_uuid()
        # print("创建临时文件夹{}".format(tmp_path))
        os.makedirs(tmp_path)
        return tmp_path

    # 在目标文件路径下创建临时目录,并返回路径
    @staticmethod
    def make_tmp_dir_under_dir(dest_dir_path):
        common_utity = CommonHelper()
        tmp_path = dest_dir_path + common_utity.get_dash_in_system() + common_utity.get_uuid()
        # print("创建临时文件夹{}".format(tmp_path))
        os.makedirs(tmp_path)
        return tmp_path

    # 得到文件路径中的最后一级目录名
    @staticmethod
    def get_last_dir_name_in_file_path(orgin_file_path):
        (file_pre_path, temp_filename) = os.path.split(orgin_file_path)
        return FileHelper.get_last_dir_name_in_dir_path(file_pre_path)

    # 获取目录路径中的最后一级目录名
    @staticmethod
    def get_last_dir_name_in_dir_path(dir_path):
        common_utity = CommonHelper()
        last_dir_name = dir_path[dir_path.rindex(common_utity.get_dash_in_system()) + len(
            common_utity.get_dash_in_system()):]
        return last_dir_name

    # 得到文件路径中的完整目录路径
    @staticmethod
    def get_pre_path_in_file_path(orgin_file_path):
        (file_pre_path, temp_filename) = os.path.split(orgin_file_path)
        return file_pre_path

    # 查询文件夹下面是否有指定文件
    @staticmethod
    def is_has_file_in_dir(file_dir_path, file_name):
        is_find = False
        file_names = os.listdir(file_dir_path)
        for temp in file_names:
            if temp == file_name:
                is_find = True
                break
        return is_find

    # 清除文件内容
    # 主要针对文本文件类
    @staticmethod
    def clear_file_content(file_path):
        with open(file_path, "w") as file:
            file.truncate(0)

    @staticmethod
    # Copy指定格式的文件到新文件夹
    # 函数调用示例：SFileToDFile('d:\\quiz', '.txt', 'd:\\test')
    def sfile_to_dfile(sourcefile, fileclass, destinationfile):
        # 遍历目录和子目录
        for filenames in os.listdir(sourcefile):
            # 取得文件或文件名的绝对路径
            filepath = os.path.join(sourcefile, filenames)
            # 判断是否为文件夹
            if os.path.isdir(filepath):
                # 如果是文件夹，重新调用该函数
                FileHelper.sfile_to_dfile(filepath, fileclass, destinationfile)
            # 判断是否为文件
            elif os.path.isfile(filepath):
                # 如果该文件的后缀为用户指定的格式，则把该文件复制到用户指定的目录
                if filepath.endswith(fileclass):
                    # dirname = os.path.split(filepath)[-1]
                    # 给出提示信息
                    # print('Copy %s'% filepath +' To ' + destinationfile)
                    # print('Delet %s to recycle bin.' % filepath)
                    # # 删除文件
                    # send2trash.send2trash(filepath)
                    # 复制该文件到指定目录
                    shutil.copy(filepath, destinationfile)

    # 复制整个目录及子目录文件到指定文件夹
    # 指定可以忽略拷贝的文件ignore_patterns:.git
    @staticmethod
    def copy_allsubfiles(source_dir, target_dir, ignore_patterns):
        if ignore_patterns is not None:
            shutil.copytree(source_dir, target_dir, ignore=shutil.ignore_patterns(ignore_patterns))
        else:
            shutil.copytree(source_dir, target_dir)

    # 用于复制目录下本级所有文件到另一个目录
    @staticmethod
    def copy_allfiles(src, dest):
        src_files = os.listdir(src)
        # 创建输出目录
        FileHelper.mkdir(dest)

        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, dest)

    # 复制文件到另外未知
    @staticmethod
    def copy_file(source_path, target_path):
        shutil.copyfile(source_path, target_path)


    # 创建zip文件
    @staticmethod
    def make_zip(source_dir, output_filename):
        zipf = zipfile.ZipFile(output_filename, 'w')
        pre_len = len(os.path.dirname(source_dir))
        for parent, dirnames, filenames in os.walk(source_dir):
            for filename in filenames:
                pathfile = os.path.join(parent, filename)
                arcname = pathfile[pre_len:].strip(os.path.sep)  # 相对路径
                zipf.write(pathfile, arcname)
        zipf.close()

    # 获取文件夹下指定后缀的文件
    # 比如图像文件后缀：suffix=['jpg', 'jpeg', 'JPG', 'JPEG', 'png', 'bmp']
    @staticmethod
    def get_file_list(file_dir, suffix):
        '''get all files path ends with suffix'''
        if not os.path.exists(file_dir):
            print("PATH:%s not exists" % file_dir)
            return []
        filelist = []
        for root, sdirs, files in os.walk(file_dir):
            if not files:
                continue
            for filename in files:
                filepath = os.path.join(root, filename)
                if filename.split('.')[-1] in suffix:
                    filelist.append(filepath)
        return filelist


class JsonHelper:
    def __init__(self):
        pass

    # 将json文件转成json对象
    @staticmethod
    def get_json_obj_by_file(json_file):
        with open(json_file, encoding="utf-8") as f:
            try:
                data = f.read()
                if data.startswith(u'\ufeff'):
                    data = data.encode('utf8')[3:].decode('utf8')
                json_obj = json.loads(data)
                return json_obj
            except Exception as exp:
                print(exp)
                print(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
                print(exp.__traceback__.tb_lineno)  # 发生异常所在的行数
                return None
