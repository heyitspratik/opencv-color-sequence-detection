from flask import Flask, request, Response, jsonify, json
from PIL import Image,ImageChops
# from colorthief import ColorThief
import cv2
import os
import numpy as np
from math import sqrt

json_report =  {
    "GLU":{"negative":(144,208,182),"1/10(ir.) 100":(140,196,135),"1/4 250":(123,176,86),"1/2 500":(140,144,67),"1 1000":(129,118,54),"2 or more 2000 or more":(119,85,58)},
    "BIL":{"negative":(246,231,164),"small ++":(237,216,163),"moderate ++":(200,195,155),"large +++":(191,173,149)},
    "KET":{"negative":(215,182,151),"trace 5":(232,175,156),"small 15":(214,128,127),"moderate 40":(178,97,103),"large 80":(134,72,85),"large 160":(97,54,64)},
    "SG":{"1.000":(17,73,72),"1.005":(38,113,72),"1.01":(95,124,80),"1.015":(119,136,58),"1.020":(140,147,54),"1.025":(139,143,48),"1.030":(184,160,55)},
    "BLO":{"negative":(229,190,63),"non-hemolyzed trace":(230,189,56),"non-hemolyzed moderate":(219,201,70),"hemolyzed trace":(193,191,68),"small+":(146,171,69),"moderate++":(87,136,70),"large+++":(57,83,58)},
    "pH":{"5.0":(241,129,74),"6.0":(236,164,82),"6.5":(220,192,83),"7.0":(181,193,91),"7.5":(129,165,77),"8.0":(76,155,107),"8.5":(28,122,124)},
    "PRO":{"negative":(220,233,119),"trace":(186,211,109),"30 +":(165,193,119),"100 ++":(144,185,145),"300 +++":(112,175,154),"2000 or more ++++":(89,156,138)},
    "URO":{"normal 0.2":(254,202,152),"normal 1":(250,168,146),"2":(235,146,142),"4":(240,138,134),"8":(232,107,137)},
    "NIT":{"negative":(255,255,218),"positive":(255,239,206),"positive":(255,206,197)},
    "LEU":{"negative":(229,233,182),"trace":(216,212,183),"small +":(188,183,163),"moderate ++":(143,117,144),"large +++":(129,100,144)}
}
UPLOAD_FOLDER = 'upload'
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/greyscale/', methods=['GET', 'POST'])
def imagetype():
    if request.method == 'POST':
            im = request.files['image']
            img = Image.open(im).convert('RGB')
            img_cv = np.array(img)
            w, h = img.size
            for i in range ( h ):
                for j in range(h):
                    try:
                        r, g, b = img.getpixel((i,j))
                    except Exception as e:
                        print(e)
                        return jsonify({"data":False,"message":"Black&White"})
                    if r != g != b:
                        a = 'colored'
                        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
                        print(fm)
                        if fm < 5:
                            return jsonify({"data":False,"message":"blurry"})
                        else:
                            return jsonify({"data":True,"message":"Not blurry"})

            b = 'gray'
            return jsonify({"data":False,"message":"Black&White"})
    else:
            return jsonify('get method is not allowed!')

r_final_list= [(497, 212, 37, 17),(498, 233, 35, 15),(499, 252, 35, 18),(499, 274, 36, 16),(498, 295, 36, 18),(499, 318, 34, 13),(499, 340, 34, 16),(496, 360, 37, 18),(497, 385, 37, 15),(497, 409, 36, 14)]
def closest_color(rgb,COLORS):
    r, g, b = rgb
    color_diffs = []

    # creating a new dictionary
    my_dict = {"java": 100, "python": 112, "c": 11}

    # list out keys and values separately
    key_list = list(COLORS.keys())
    val_list = list(COLORS.values())

    # print key with val 100
    for color in COLORS.items():
        # creating a new dictionary
        # list out keys and values separately
        # print key with val 100
        # print("color_items", color)
        # print("color",color[1])
        cr, cg, cb = color[1]
        color_diff = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        color_diffs.append((color_diff, color))
        # print(color[0])
    # print("min(color_diffs)[1]",min(color_diffs)[1])
    answer = str(min(color_diffs)[1][0]).capitalize()
    return answer

@app.route('/imagecolor/', methods=['GET', 'POST'])
def imagecolor():
    list_final_box = []

    if request.method == 'POST':
            try:
                im = request.files['image']
                im.save(os.path.join(app.config['UPLOAD_FOLDER'], im.filename))
            except Exception as e:
                print(e)
                return jsonify({"data":None,"message":"Please pass the image"})

            img = Image.open(im)
            img = np.array(img)
            im_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imS = cv2.resize(im_rgb, (960, 500))

            list_ = []
            # for i, data in enumerate(r_final_list):
            #         # print(data[i])
            #         imROI = imS[int(data[1]):int(data[1] + data[3]), int(data[0]):int(data[0] + data[2])]
            #
            #         print("mean color", imROI.mean(axis=0).mean(axis=0))
            #         list_.append(imROI.mean(axis=0).mean(axis=0))
            for i, data in enumerate(r_final_list):
                imROI = imS[int(data[1]):int(data[1] + data[3]), int(data[0]):int(data[0] + data[2])]
                cv2.imwrite('data_%02d.jpg' % i, imROI)
                temp_data = imROI.mean(axis=0).mean(axis=0)
                if i == 0:
                    GLU = closest_color(temp_data, json_report["GLU"])
                if i == 1:
                    BIL = closest_color(temp_data, json_report["BIL"])
                if i == 2:
                    KET = closest_color(temp_data, json_report["KET"])
                if i == 3:
                    SG = closest_color(temp_data, json_report["SG"])
                if i == 4:
                    BLO = closest_color(temp_data, json_report["BLO"])
                if i == 5:
                    pH = closest_color(temp_data, json_report["pH"])
                if i == 6:
                    PRO = closest_color(temp_data, json_report["PRO"])
                if i == 7:
                    URP = closest_color(temp_data, json_report["URO"])
                if i == 8:
                    NIT = closest_color(temp_data, json_report["NIT"])
                if i == 9:
                    LEU = closest_color(temp_data, json_report["LEU"])

                try:
                    list_final_box.append({"GLU":GLU,"BIL":BIL,"KET":KET,"SG":SG,"BLO":BLO,"pH":pH,"PRO":PRO,"URP":URP,"NIT":NIT,"LEU":LEU})
                except Exception as e:
                    # print(e)
                    pass
            return jsonify({"data":list_final_box})
    else:
            return jsonify('get method is not allowed!')
        

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5046)
