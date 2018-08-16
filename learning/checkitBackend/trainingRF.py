'''
Description: Training SVM algorithm using Sift Descriptors
Author: J. Tejada
Version: 3.0
Date: 3/21/17
'''
import os
import cv2
import cPickle as pickle
import numpy as np
from sklearn import preprocessing, cross_validation
from django.conf import settings


class SVMClassify(object):

    def __init__(self, features, label, C=1, gamma = 0.5,):

        ####UNCOMMENT TO USE SVM
        #self.params = dict(kernel_type=cv2.SVM_LINEAR,
        #                   svm_type=cv2.SVM_C_SVC,
        #                   C=C)

        ##### random trees parameters
        self.params = dict(max_depth=100,
                           min_sample_count=1,
                           use_surrogates=False,
                           max_categories=5,
                           calc_var_importance=False,
                           nactive_vars=0,
                           max_num_of_tree_in_the_forest=100,
                           term_crit=(cv2.TERM_CRITERIA_MAX_ITER,100,0.1))
       #####

        self.le = preprocessing.LabelEncoder()
        self.le.fit(label)
        leLabels = np.array(self.le.transform(label), dtype=np.float32)

        features_train, features_test = cross_validation.train_test_split(features, test_size=0.4, random_state=0)
        labels_train, labels_test = cross_validation.train_test_split(leLabels, test_size=0.4, random_state=0)

        #result = self.training(features_train, labels_train)     ### uncomment to use svm
        result = self.trainingForest(features_train, labels_train)
        self.crossValidation(result, features_test, labels_test)
        self.model = cv2.SVM()

    def trainingForest(self, features, label):
        features = np.array(features, dtype=np.float32)
        self.model = cv2.RTrees()
        self.model.train(features, cv2.CV_ROW_SAMPLE, label, params=self.params)
        model_dir = settings.MODELS_ROOT
        svm_filename =  os.path.join(model_dir, "rf.xml")
        self.model.save(svm_filename)


    def training(self, features, label):
        npfeatures = np.array(features, dtype=np.float32)
        self.model = cv2.SVM()
        self.model.train(npfeatures, label, params=self.params)
        model_dir = settings.MODELS_ROOT
        svm_filename =  os.path.join(model_dir, "svm.xml")
        self.model.save(svm_filename)

    def predict(self, features):
        labels_nums = self.model.predict(features)
        labels_words = self.le.inverse_transform([int(x) for x in labels_nums])
        return labels_words

    def crossValidation(self, model, features_test, labels_test):
        features_test = np.array(features_test, dtype=np.float32)
        predictionResult = []
        for item in features_test:
            res = self.model.predict(item)
            predictionResult.append(res)

        accuracy = (labels_test == predictionResult).mean()
        error = (labels_test != predictionResult).mean()
        print("Accuracy: %.2f %%" % (accuracy * 100))
        print('Percent Error: %.2f %%' % (error * 100))

        '''
        confusion = np.zeros((3, 3), np.int32)
        for i, j in zip(labels_test, predictionResult):
            confusion[i, j] += 1
        print 'confusion matrix:'
        print confusion
        '''
        return

def main(feature_map_file):
    model_dir = settings.MODELS_ROOT
    svm_filename =  os.path.join(model_dir, "svm.xml")

    with open(feature_map_file, 'r') as f:
        feature_map = pickle.load(f)

    features=[]
    labels=[]
    for item in feature_map:
        features.append(item['features'])
        labels.append(item['label'])

    SVMClassify(features,labels)
    print("The Classifier File has been saved!")
    return svm_filename



if __name__=='__main__':
    main()