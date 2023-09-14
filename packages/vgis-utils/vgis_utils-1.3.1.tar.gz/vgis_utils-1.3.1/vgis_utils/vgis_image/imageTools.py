# -*- coding:utf-8 -*-

import base64
import os

import cv2
import numpy as np
from PIL import Image
from PIL import ImageDraw


class ImageHelper:
    def __init__(self):
        pass

    # 获取图片的base64码,有点问题
    @staticmethod
    def convert2Base64(image_path):
        icon = open(image_path, 'rb')
        iconData = icon.read()
        iconData = base64.b64encode(iconData)
        LIMIT = 60
        liIcon = []
        while True:
            sLimit = iconData[:LIMIT]
            iconData = iconData[LIMIT:]
            liIcon.append('\'%s\'' % sLimit)
            if len(sLimit) < LIMIT:
                break
        base64_img_str = os.linesep.join(liIcon)
        return base64_img_str

    # 根据指定范围生成二值图
    @staticmethod
    def build_binary_image(input_pic_file_path, result_pic_file_path, white_region_array):
        # 生成黑色图片
        old_img = Image.open(input_pic_file_path)
        height = old_img.height
        width = old_img.width
        black_img = Image.new("RGB", (width, height))
        # 对指定区域进行白色填充
        for region in white_region_array:
            # region为x1,y1,x2,y2...xn,yn
            draw = ImageDraw.Draw(black_img)
            draw.polygon(region, fill=(255, 255, 255, 255), outline=(255, 255, 255, 255))
        black_img.save(result_pic_file_path)

    # 获取目录下所有图片路径
    @staticmethod
    def get_image_list(image_dir,
                       suffix=['jpg', 'jpeg', 'JPG', 'JPEG', 'png', 'PNG', 'bmp', 'BMP', 'GIF', 'gif']):
        '''get all vgis_image path ends with suffix'''
        if not os.path.exists(image_dir):
            print("PATH:%s not exists" % image_dir)
            return []
        imglist = []
        for root, sdirs, files in os.walk(image_dir):
            if not files:
                continue
            for filename in files:
                filepath = os.path.join(root, filename)
                if filename.split('.')[-1] in suffix:
                    imglist.append(filepath)
        return imglist

    # 按照指定大小对图片大小进行重定义
    @staticmethod
    def resize_image_by_size(input_file_path, resize_width,resize_height,out_file_path):
        img = Image.open(input_file_path)
        new_img = img.resize((resize_width, resize_height), Image.BILINEAR)
        new_img.save(out_file_path)

    # 根据百分比缩放图片
    @staticmethod
    def resize_image_by_percent():
        pass

    # 对图像进行裁切，按照两条水平线
    @staticmethod
    def clip_image_by_line():
        pass

    @staticmethod
    def add_polygon_on_tif(tif_file):
        try:
            img = cv2.imread(tif_file, -1)
            # 输出图像信息
            # print(img)
            print(img.shape)
            print(img.dtype)
            print(img.min())
            print(img.max())
            # 读取数据，显示图像
            img = cv2.imread(tif_file, -1)
            # 将数据格式进行转换
            img = np.array(img)
            # 绘制多边形
            pts = np.array([[200, 100], [200, 300], [250, 300], [500, 200], [500, 40]], np.int32)  # 构建多边形的顶点
            cv2.polylines(img, [pts], True, (255, 0, 0), 3)

            # 设置图像窗口
            cv2.namedWindow(tif_file, 1)  # 第一个参数设置窗口名字，第二个参数"1"为根据电脑显示器自动调整窗口大小
            cv2.imshow(tif_file, img)  # 显示图像

            # 设置等待时间为0毫秒（参数0表示等待时间为无限）
            cv2.waitKey(0)

            # 释放窗口
            cv2.destroyAllWindows()
        except Exception as exp:
            print(exp)
            print(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            print(exp.__traceback__.tb_lineno)  # 发生异常所在的行数



# AI样本二值图生成单元测试方法
def build_binary_image_test(image_operator):
    while_region_array = []
    while_region_array.append([11, 45, 34, 55, 67, 44, 14, 55])
    while_region_array.append([101, 450, 340, 550, 670, 440, 140, 550])
    image_operator.build_binary_image("d:\\airport.jpg", "d:\\airport_bin.jpg", while_region_array)


# # 主入口,进行测试
# if __name__ == '__main__':
#     try:
#         image_operator = ImageOperator()
#         build_binary_image_test(image_operator)
#     except Exception as tm_exp:
#         print("AI样本二值图生成失败：{}".format(str(tm_exp)))
