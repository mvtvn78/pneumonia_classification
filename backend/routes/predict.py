from flask import Blueprint, jsonify, request
from handler.upload import uploadHanler
from util.getFace import getFaceIMG
import torch
import PIL.Image as Image
import torchvision.transforms as transforms
from model.meso4 import Meso4
from model.resnet50 import resnet50

PATHFILEMODELMESO = "model\\best_meso4.pth"
PATHFILEMODELRESNET = "model\\best_resnet50_T5.pth"
predict_bp = Blueprint("upload", __name__)

# model = Meso4()
# model.load_state_dict(torch.load(PATHFILEMODELMESO))
# model.eval()
# img_transformer = transforms.Compose(
#     [
#         transforms.Resize((256, 256)),
#         transforms.ToTensor(),
#         transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
#     ]
# )

# Resnet50
model = resnet50
model.load_state_dict(torch.load(PATHFILEMODELRESNET))
model.eval()
img_transformer = transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
    ]
)


@predict_bp.route("/predict", methods=["POST"])
def predictHanler():
    file = uploadHanler()
    if file == -1 or file == -2:
        return jsonify({"msg": "", "status": file})
    faceFile = getFaceIMG(file)
    org, detectFaceList = faceFile
    detectList = []
    for item in detectFaceList:
        path = f"store\\{item}"
        image = Image.open(path)
        image = img_transformer(image).float()
        image = image.unsqueeze(0)
        with torch.no_grad():
            output = model(image)
            output = torch.softmax(output, 1)
            result = output.reshape(-1).tolist()
            detectList.append(result)

    return jsonify(
        {
            "msg": "",
            "status": 0,
            "org": org,
            "detectFace": detectFaceList,
            "detectList": detectList,
        }
    )
