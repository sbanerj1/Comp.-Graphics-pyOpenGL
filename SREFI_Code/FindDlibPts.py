import numpy as np
import time
import sys
import dlib
import os
import glob
import numpy as np
import cv2
import random
from cv2 import cv
import math
from PIL import Image
import multiprocessing
from joblib import Parallel, delayed

def process_image(f,save_path,base_path,detector,predictor,padding,file_name):
    print("Processing file: {}".format(f))
    img_name = os.path.basename(f)
    img_dir = os.path.dirname(f)
    saveLocation = img_dir[len(base_path):]
    if len(saveLocation) > 0 and (saveLocation[0] == '/' or saveLocation[0] == '\\'):
        saveLocation = saveLocation[1:]
    save_path = os.path.join(save_path,saveLocation)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if os.path.isfile(os.path.join(save_path,img_name)):
        print "image already exists, skipping."
        return
    #print "this is",type(f)
    if os.path.isfile(f):
        img = cv2.imread(f)
        if img is not None:
            if img.shape[0] > 30 and img.shape[1] > 30:
                rfactor = 1
                img_small = cv2.resize(img, (0,0), fx=rfactor, fy=rfactor)
                faces = detector(img_small,1)
                if len(faces) == 0:
                    faces = detector(img,1)
                    rfactor = 1
                print("Number of faces detected: {}".format(len(faces)))
                if len(faces) == 0:
                    print "faking a face detection..."
                    paddingpx = 10
                    d = dlib.rectangle(paddingpx,paddingpx,paddingpx+img.shape[1]-2*paddingpx,paddingpx+img.shape[0]-2*paddingpx)
                    faces = [d]
                if len(faces) > 0:
                    d = faces[0]
                    d = dlib.rectangle(int(d.left()*(1/rfactor)),int(d.top()*(1/rfactor)),int(d.right()*(1/rfactor)),int(d.bottom()*(1/rfactor)))
                    shape = predictor(img, d)
                    print "left,top,right,bottom:", d.left(), d.top(), d.right(), d.bottom()
                    points = np.zeros((68,2),np.int32)
                    f1 = open(save_path+'/'+file_name+'.txt','w')
                    for i in xrange(0,68):
                        apoint = shape.part(i)
                        points[i,0] = float(shape.part(i).x)
                        f1.write(str(points[i,0]))
                        f1.write(',')
                        points[i,1] = float(shape.part(i).y)
                        f1.write(str(points[i, 1]))
                        f1.write('\n')
                        print i, points[i,0], points[i,1]
                    print points.shape
                    f1.close()
                    #img_left_center=[(float(str(shape.part(36)).split(",")[0][1:])+float(str(shape.part(39)).split(",")[0][1:]))/2,(float(str(shape.part(36)).split(",")[1][:-1])+float(str(shape.part(39)).split(",")[1][:-1]))/2]
                    #img_right_center=[(float(str(shape.part(42)).split(",")[0][1:])+float(str(shape.part(45)).split(",")[0][1:]))/2,(float(str(shape.part(42)).split(",")[1][:-1])+float(str(shape.part(45)).split(",")[1][:-1]))/2]
                    #img_cropped = CropFace(img,img_left_center,img_right_center,(0.2,0.2),(512,512),padding)

                    #cv2.imwrite(os.path.join(save_path,img_name),np.asarray(img_cropped))
        else:
            print "Cannot find a face in this image!"
    else:
        print "warning: cannot find original file!"

def LandmarkImage(predictor,faces_folder_path,save_path):
    detector = dlib.get_frontal_face_detector()
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    ind = 0
    failed = 0
    num_cores = 1#multiprocessing.cpu_count()
    filepaths = []
    for root, dirs, files in os.walk(faces_folder_path):
        for file in files:
            if file.endswith(ext_strng) and not file.startswith("."):
                filepaths.append(os.path.join(root,file))
                file_name = file.split('.')[0]
    base_path = faces_folder_path
    Parallel(n_jobs=num_cores)(delayed(process_image)(f,save_path,base_path,detector,predictor,.20,file_name) for f in filepaths)


faces_folder_path = sys.argv[1]
predictor_path = sys.argv[2]
save_path = sys.argv[3]
ext_strng = sys.argv[4]
# processors = sys.argv[3]
predictor = dlib.shape_predictor(predictor_path)
LandmarkImage(predictor,faces_folder_path,save_path)