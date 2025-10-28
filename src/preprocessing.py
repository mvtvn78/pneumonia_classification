import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
from tensorflow.keras.applications.densenet import preprocess_input as densenet_preprocess
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
# Tiền xử lý theo modeIdx, và trả về x khi tiền xử lý và ảnh gốc img
def preprocess_image_detect(img_path, modelIdx,target_size=(224, 224)):
    img = tf.keras.preprocessing.image.load_img(img_path, target_size=target_size)
    x = ""
    x = tf.keras.preprocessing.image.img_to_array(img)
    if modelIdx == 0:
        x = resnet_preprocess(x)
    elif modelIdx==1:
        x = densenet_preprocess(x)
    elif modelIdx==2:
        x = efficientnet_preprocess(x)
    x = np.expand_dims(x, axis=0)
    return x, np.array(img)
