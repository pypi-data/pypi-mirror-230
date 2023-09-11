
import fitz
from PIL import Image
from io import BytesIO
import numpy as np



import time

import os
import shutil
import traceback

def get_pdf_color_page(file_path, save_pic_path, log_name, error_name, COLOR_THRESHHOLD):
    print(11111111111111111111111111111111111111111111111111111)
    file = os.path.split(file_path)[1]
    pdf = fitz.open(file_path)
    pdffolderpath = os.path.join(save_pic_path, file[:-4].strip())
    n_folder_max = 0
    print(file_path.replace("/", "\\") + "开始处理。 时间为" + str(time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))) + "\n")
    try:
        print(log_name)
    except:
        traceback.print_exc()
    with open(log_name, "a") as f:
        f.write("{}开始处理。 时间为 ：".format(file_path.replace("/", "\\"))+ str(time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))) + "\n")

    if os.path.isdir(pdffolderpath):
        print('文件夹路径' + str(pdffolderpath) + '已存在')
        with open(error_name, "a") as f:
            f.write('文件夹路径' + str(pdffolderpath) + '已存在。处理时间为 ：' + str(time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))) + "\n")
        file_list = os.listdir(pdffolderpath)
        for single_file in file_list:
            n_folder_now = int(os.path.splitext(single_file)[0])
            if n_folder_now > n_folder_max:
                n_folder_max = n_folder_now
    else:
        os.mkdir(pdffolderpath)
    try:
        n_this_pdf = pdf.pageCount
        print(pdf.pageCount)
    except:
        n_this_pdf = pdf.page_count
    # for pg in range(0, n_this_pdf):
    if n_folder_max > n_this_pdf:
        n_folder_max = 0
        shutil.rmtree(pdffolderpath)
        os.mkdir(pdffolderpath)
        print(file[:-4].strip() + '现有文件夹中最大页数超过PDF最大页数，已重置')
        with open(error_name, "a") as f:
            f.write(file[:-4].strip() + '现有文件夹中最大页数超过PDF最大页数，已重置。处理时间为 ：' + str(time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))) + "\n")

    for pg in range(n_folder_max, n_this_pdf):
        page = pdf[pg]
        pic_name = str(pg + 1).zfill(4) + '.jpg'
        with open(log_name, "a") as f:
            f.write(pdffolderpath + pic_name + "    的处理时间为:  " + str(time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())))+ "\n")
        save_pdf_pic_path = os.path.join(pdffolderpath, pic_name)
        find_save_color_pics_in_one_pdf(page, save_pdf_pic_path,COLOR_THRESHHOLD)
    with open(log_name, "a") as f:
        f.write("{}。 完成时间为 ：".format(file_path.replace("/", "\\"))+ str(time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))) + "\n")

    print(file_path + "完成处理。 时间为" + str(time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))) + "\n")



def find_save_color_pics_in_one_pdf(page, pic_path, COLOR_THRESHHOLD):
    trans = fitz.Matrix(1.0, 1.0).prerotate(0)
    # pm = page.get_pixmap(matrix=trans, alpha=False)  # 获得每一页的流对象
    pm = page.get_pixmap(matrix=trans, alpha=False, dpi=200)

    sio = pm.tobytes()
    sio2 = BytesIO(sio)
    sio2.seek(0)
    img = Image.open(sio2)
    img = np.array(img)
    IMG_SP = img.shape
    # 新版的，向内移动了一部分避免孔洞填充
    cropped = img[int(IMG_SP[0] * 10 / 143):int(IMG_SP[0] * 50 / 143),
              int(IMG_SP[1] * 15 / 100):int(IMG_SP[1] * 45 / 100)]  # 裁剪坐标为[y0:y1, x0:x1]
    sum_sig = 0
    count_sig = 0
    for i in range(0, cropped.shape[0]):
        for j in range(0, cropped.shape[1]):
            # hsl中计算黑色时，下面的取rgb最大值小于等于46就是黑色，黑色计算偏差没有意义，注意png有一个透明层会使得判断失效
            if max(cropped[i, j]) > 46:
                sig_single = max(cropped[i, j]) - min(cropped[i, j])
                if sig_single > 5:
                    sum_sig += sig_single
                    count_sig += 1
    # avg_sig = sum_sig / (cropped.shape[0] * cropped.shape[1])
    if count_sig:
        avg_sig = sum_sig / count_sig
        if count_sig / (cropped.shape[0] * cropped.shape[1]) > 0.8 and avg_sig > COLOR_THRESHHOLD:
            trans = fitz.Matrix(1.5, 1.5).prerotate(0)
            pm = page.get_pixmap(matrix=trans, alpha=False)  # 获得每一页的流对象
            pm.save(pic_path)
