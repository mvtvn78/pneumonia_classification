from flask import Blueprint, jsonify, request
from handler.upload import uploadHanler
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from util import gradcamplus as grad
PATH_FILE_EFFICIENTNETB0 = "model\\EfficientNetB0.keras"
PATH_FILE_DENSENET = "model\\finet_densenet.keras"
predict_bp = Blueprint("upload", __name__)

modelEff = load_model(PATH_FILE_EFFICIENTNETB0)
modelDen = load_model(PATH_FILE_DENSENET)
last_conv_layer_name = "conv5_block16_concat"
@predict_bp.route("/predict", methods=["POST"])
def predictHanler():
    (path,file) = uploadHanler()
    if file == -1 or file == -2:
        return jsonify({"msg": "", "status": file})
    img = image.load_img(path,target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    pred = modelDen.predict(img_array)
    class_idx = np.argmax(pred, axis=1)[0]
    class_names = ['Bình thường', 'Viêm phổi vi khuẩn', 'Viêm phổi virus']
    class_idx = int(class_idx)
    print(class_names[class_idx])
    file_heat_map = grad.make_heatmap(modelDen,img_array,img,last_conv_layer_name,class_idx,class_names)
    return jsonify(
        {
            "msg": "",
            "status": 0,
            "org": file,
            "heatmap": file_heat_map,
            "pred": class_idx
        }
    )
