import cv2
import numpy as np
from sklearn.cluster import KMeans
img = cv2.imread('../media/IMG_0576.jpg')
#resImg = cv2.resize(img, None, fx=0.2 , fy=0.2, interpolation=cv2.INTER_CUBIC )

new_size=150
h, w = img.shape[0], img.shape[1]
ds_factor = new_size / float(h)

if w < h:
    ds_factor = new_size / float(w)

new_size = (int(w * ds_factor), int(h * ds_factor))
resImg = cv2.resize(img, new_size)


cv2.imshow('sample', resImg)
cv2.waitKey()

##################Equalized vs non-equalized##############################
'''
grayImg = cv2.cvtColor(resImg,cv2.COLOR_BGR2GRAY)
eqGray = cv2.equalizeHist(grayImg)

cv2.imshow('Gray',grayImg)
cv2.imshow('Equalized gray', eqGray)
cv2.waitKey()
'''
##################Equalized vs non-equalized##############################

'''
detector = cv2.FeatureDetector_create("Dense")
detector.setInt("initXyStep", 20)
detector.setInt("initFeatureScale", 40)
detector.setInt("initImgBound", 4)
densepoints = detector.detect(resImg, None)

img2 = cv2.drawKeypoints(resImg,densepoints,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
kp, des = cv2.SIFT().compute(gray_image, densepoints)

fvs = np.array(des)

Z = fvs.reshape((-1,1))
Z = np.float32(Z)


term_crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
ret, label, center = cv2.kmeans(Z, 32, term_crit, 10, cv2.KMEANS_RANDOM_CENTERS)
print(center.shape)

#center = center.flatten()
#centroid = center.reshape((-1,1))
#print(centroid)

mean, std = cv2.meanStdDev(resImg)
stat = np.append(mean,std).flatten()

centroid=[]
for item in center:
    centroid.append(item[0])
print centroid
colors=[]
for item in stat:
    colors.append(item)



buff = colors + centroid
print(buff)





center = np.uint8(center)
res = center[label.flatten()]

#res2 = res.reshape((resImg.shape))
cv2.imshow('Clustered',res)
cv2.waitKey(0)
#cv2.destroyAllWindows()
'''

'''
img2 = cv2.drawKeypoints(resImg,kp,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

cv2.imshow('Dense',img2)
cv2.waitKey()

'''

