'''
Description: Classifying image features using trained SVM
Author: J. Tejada
Version: 2.0
Date: 9/13/16
'''
import cv2
import argparse
import cPickle as pickle
import numpy as np
import os
import CreatingFeat as cf

from sklearn import preprocessing
from Training import SVMClassify
from django.conf import settings

def main(input_img):
    media_dir = settings.MEDIA_ROOT
    imgDir = os.path.join(media_dir,input_img)
    
    model_dir = settings.MODELS_ROOT
    svmFile = os.path.join(model_dir, "svm.xml")
    featuremap = os.path.join(model_dir, "featuremap.pkl")

    with open(featuremap, 'r') as f:
        feature_map = pickle.load(f)

    labels=[]
    for item in feature_map:
        labels.append(item['label'])

    
    if not os.path.isfile(imgDir):
        testDir = os.path.join(media_dir, 'testImages')
        imgDir = os.path.join(testDir, input_img)
        if not os.path.isfile(imgDir): 
            raise IOError("The " + imgDir + "  image directory does not exist! ")
        else:
            img = cv2.imread(imgDir)
    else:
        img = cv2.imread(imgDir)

    prediction = ImageClassifier(img, svmFile, labels)
    print prediction
    return prediction

class ImageClassifier():
    def __init__(self, img, svmFile, labels):
        self.encodeLabels(labels)

        imgFeat = np.array(self.getImageFeature(img), dtype=np.float32)

        self.svm = cv2.SVM()
        
        predictedLabel = self.predict(imgFeat,svmFile)
        self.wordLabel = self.decodeLabels(predictedLabel)
        #print(predictedLabel)
    def __str__(self):
        return str(self.wordLabel)

    def predict(self, imgFeat, svmFile):
        self.svm.load(svmFile)
        predictedLabel = self.svm.predict(imgFeat)
        return predictedLabel

    def getImageFeature(self,img):
        imgArgs=[]
        resizedImg = cf.imageResize(img)
        colorFeat = cf.ColorExtract().getMeanStd(resizedImg)
        siftKps, siftDesc = cf.FeatureExtraction().MainExtractor(resizedImg)
        clusteredFeat = cf.FeatureCluster().kmeansFeature(siftDesc)

        imgFvs = colorFeat + clusteredFeat
        imgArgs.append(imgFvs)
        return imgArgs

    def encodeLabels(self,labels):
        self.le = preprocessing.LabelEncoder()
        return self.le.fit(labels)

    def decodeLabels(self,predictedLabel):
        return self.le.inverse_transform(int(predictedLabel))



if __name__ == '__main__':
    main()

    

