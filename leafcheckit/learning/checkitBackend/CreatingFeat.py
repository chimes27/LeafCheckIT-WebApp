'''
Description: Loading and Extracting image features using OpenCV Dense feature detector and Sift Extractor
Author: J. Tejada
Version: 4.0
Date: 3/21/2017

'''

import os
import cv2
import numpy as np
import cPickle as pickle
from django.conf import settings


class FeatureMapExtraction(object):
    def getCentroid(self, input_map):
        codebook=[]
        featureMap=[]
        codebookFvs={}
        finalFeatureMap=[]
        buff=[]
        for item in input_map:
            featureMapFvs = {}
            cur_label=item['label']
            img = cv2.imread(item['image'])
            img_resize = imageResize(img)
            colorFeat = ColorExtract().getMeanStd(img_resize)
            siftKps, siftDesc = FeatureExtraction().MainExtractor(img_resize)
            clusteredFeat = FeatureCluster().kmeansFeature(siftDesc)

            codebookFvs = colorFeat + clusteredFeat
            codebook.append(codebookFvs)

            featureMapFvs['features'] = colorFeat + clusteredFeat
            featureMapFvs['label'] = cur_label

            print "Feature extracted for: " + item['image']
            if featureMap is not None:
                featureMap.append(featureMapFvs)

        create_report(featureMap)
        return codebook, featureMap

def imageResize(input_image):
    new_size=150
    h, w = input_image.shape[0], input_image.shape[1]
    ds_factor = new_size / float(h)

    if w < h:
        ds_factor = new_size / float(w)

    new_size = (int(w * ds_factor), int(h * ds_factor))
    newImage = cv2.resize(input_image, new_size)
    return newImage


class FeatureExtraction(object):
    def MainExtractor(self,img):
        featureKeyPoints = DenseExtract().detect(img)
        featureKeyPoints, featureVectors = SiftExtract().compute(img,featureKeyPoints)
        return featureKeyPoints, featureVectors

class DenseExtract(object):
    def __init__(self, step_size=20, feature_scale=40, img_bound=4):

        self.detector = cv2.FeatureDetector_create("Dense")
        self.detector.setInt("initXyStep", step_size)
        self.detector.setInt("initFeatureScale", feature_scale)
        self.detector.setInt("initImgBound", img_bound)

    def detect(self, img):
        return self.detector.detect(img)


class SiftExtract(object):
    def compute(self, img, featureKeyPoints):
        if img is None:
            print "Not a valid image"
            raise TypeError

        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kps, des = cv2.SIFT().compute(gray_image, featureKeyPoints)
        return kps, des

class ColorExtract(object):
    def getMeanStd(self, img):
        img3 = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
        img4 = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        mean, std = cv2.meanStdDev(img)
        meanYCrCb, stdYCrCb = cv2.meanStdDev(img3)
        meanHSV, stdHSV = cv2.meanStdDev(img4)

        stat = np.append(mean,std).flatten()
        stat2 = np.append(meanYCrCb, stdYCrCb).flatten()
        stat3 = np.append(meanHSV, stdHSV).flatten()

        colors = []
        for item in stat:
            colors.append(item)
        for item in stat2:
            colors.append(item)
        for item in stat3:
            colors.append(item)
        return colors

class FeatureCluster(object):
    def kmeansFeature(self,des):   ####input descriptor from Sift
        fvs = np.array(des)

        Z = fvs.reshape((-1,1))
        Z = np.float32(Z)
        flag = cv2.KMEANS_RANDOM_CENTERS
        clusters = 8
        term_crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(Z, clusters, term_crit, 10, flag)

        centroid=[]
        for item in center:
            centroid.append(item[0])
        return centroid

def create_report(mat):
    with open('out.txt', 'w') as file:
        for item in mat:
            file.write("{}\n".format(item))
    print("Report Created")
    return



def main(input_map):
    
    print "===== Generating and calculating features ====="
    codebook, featureMap = FeatureMapExtraction().getCentroid(input_map)
    model_dir = settings.MODELS_ROOT

    if not os.path.exists(model_dir):
        os.makedirs(model_dir)


    codebookfile = os.path.join(model_dir, "codebook.pkl")
    feature_map_file = os.path.join(model_dir, "featuremap.pkl")

    print "===== Building codebook ====="
    with open(codebookfile, 'w') as f:
        pickle.dump((codebook), f)

    print "===== Building featureMap for Training ====="
    with open(feature_map_file, 'w') as f:
        pickle.dump((featureMap), f)


    print("Codebook and featureMap is already generated!")
    return feature_map_file

if __name__=='__main__':
    main()



