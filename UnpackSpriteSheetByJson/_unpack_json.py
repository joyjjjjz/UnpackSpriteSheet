# -*- coding: utf-8 -*-
# Python图像处理PIL各模块详细介绍
# https://blog.csdn.net/zhangziju/article/details/79123275
import os,sys
import json
import os
import os.path
from PIL import Image
from os import path as op

def json_to_dict(json_filename):
    json_file = open(json_filename, 'r')
    all_pic_dic = json.load(json_file)
    all_item_list = []

    toFindKeys = ['frames', 'res']
    findKey = ''
    for key in toFindKeys:
        if key in all_pic_dic:
            findKey = key
            break
    assert findKey

    for one_pic_item in all_pic_dic[findKey]:
        one_json_item = all_pic_dic[findKey][one_pic_item]
        one_item = {}
        one_item['name'] = one_pic_item.strip().lstrip().rstrip(',')
        one_item['x'] = one_json_item['x']
        one_item['y'] = one_json_item['y']
        one_item['w'] = one_json_item['w']
        one_item['h'] = one_json_item['h']
        if "sourceW" in one_json_item:
            one_item["sourceW"] = one_json_item["sourceW"]
        if "sourceH" in one_json_item:
            one_item["sourceH"] = one_json_item["sourceH"]
        all_item_list.append(one_item)

    return all_item_list
       
   

def gen_png_from_json(folder_name, json_filename, png_filename):
    big_image = Image.open(png_filename)
    all_item_list = json_to_dict(json_filename)

    print 'gen_png_from_json:' + folder_name

    #清理掉原目录
    if not os.path.isdir(folder_name):
        #os.removedirs(folder_name)
        os.mkdir(folder_name)

    for i, one_item_data in enumerate(all_item_list):
        file_name = one_item_data['name']
        x = one_item_data['x']
        y = one_item_data['y']
        w = one_item_data['w']
        h = one_item_data['h']

        #设置图像裁剪区域 (x左上，y左上，x右下,y右下)
        image_box = [x, y, x + w , y + h ]
        one_pic = big_image.crop(image_box)
        newW = one_item_data.get("sourceW", 0)
        newH = one_item_data.get("sourceH", 0)
        if newW > 0 and newH > 0 and (w != newW or h != newH):
            newImage = Image.open("di.png")
            newImage = newImage.crop([0, 0, newW, newH])
            offsetX = (newW - w) / 2
            offsetY= (newH - h) / 2
            newImage.paste(one_pic, (offsetX, offsetY))
            one_pic = newImage
        one_pic.save(folder_name + "/" + file_name + '.png') # 存储裁剪得到的图像
        
        #print one_item_data


def GetMergeFiles(srcDir, dstFiles):
    assert isinstance(dstFiles, set)
    for root, dirs, names in os.walk(srcDir):
        for d in dirs:
            srcSubdir = op.join(root, d)
            GetMergeFiles(srcSubdir, dstFiles)

        for name in names:
            path = os.path.join(root, name)
            if os.path.isfile(path):
                dstFiles.add(op.splitext(path)[0])


if __name__ == '__main__':
    # rootdir = sys.argv[1]
    rootdir = "D:/unpack_res"
    rootdir = "D:/unpack_res/resource/image/public"
    #'E:/_github/Python/TexturePacker'

    files_set = set()
    if os.path.exists(rootdir):
        GetMergeFiles(rootdir, files_set)

    succeedSet = set()
    failedSet = set()
    for absDir in files_set:
        json_filename = os.path.join(rootdir, absDir) + '.json'
        png_filename = os.path.join(rootdir, absDir) + '.png'
        jpg_filename = os.path.join(rootdir, absDir) + '.jpg'

        if not os.path.exists(json_filename):
            continue

        succeed = True
        if os.path.exists(png_filename):
            try:
                gen_png_from_json(absDir, json_filename, png_filename )
            except Exception, e:
                succeed = False
                print("{}, png error:{}".format(json_filename, e))
            finally:
                pass
        elif os.path.exists(jpg_filename):
            try:
                gen_png_from_json(absDir, json_filename, jpg_filename )
            except Exception, e:
                succeed = False
                print("{}, jpg error:{}".format(jpg_filename, e))
            finally:
                pass

        if succeed:
            succeedSet.add(json_filename)
        else:
            failedSet.add(json_filename)

    print("process succeed len:{}, detail:{}".format(len(succeedSet), '\n'.join(succeedSet)))
    print("process failed len:{}, detail:{}".format(len(failedSet), '\n'.join(failedSet)))
