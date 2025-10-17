import cv2
from util import generateUnique as gn


def getFaceIMG(filePath):
    face_detect = cv2.CascadeClassifier("model\haarcascade_frontalface_default.xml")
    img = cv2.imread(filePath)
    faces = face_detect.detectMultiScale(img, scaleFactor=1.3, minNeighbors=6)
    detectList = []
    try:
        i = 0
        for x, y, w, h in faces:
            detect_face = img[y : y + h, x : x + w]
            ext = filePath.split(".")[-1]
            detectFiles = f"face_{i}{gn.generateUniqueTimestamp()}.{ext}"
            detect_filePath = f"store\\{detectFiles}"
            detect_face = cv2.resize(detect_face, (224, 224))
            cv2.imwrite(detect_filePath, detect_face)
            detectList.append(detectFiles)
            i += 1
        for x, y, w, h in faces:
            cv2.rectangle(img, (x, y, w, h), (255, 0, 0), 3)
        org_file = f"org_{gn.generateUniqueTimestamp()}.{ext}"
        org_filePath = f"store\\{org_file}"
        cv2.imwrite(org_filePath, img)
        return org_file, detectList
    except:
        return filePath.split("\\")[-1], []
