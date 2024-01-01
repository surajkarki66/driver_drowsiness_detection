import cv2
import numpy as np
import os

from django.core.mail import EmailMessage
from keras.models import load_model
from django.conf import settings
from PIL import Image as PILImage


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=os.environ.get('EMAIL_FROM'),
            to=[data['to_email']]
        )
        email.send()


def image_to_array(image_instance):
    image = PILImage.open(image_instance)
    image_array = np.array(image)

    return image_array


def classify_image(image_data):
    img = image_to_array(image_data)
    img = img.astype(np.uint8)

    leye_path = os.path.sep.join(
        [str(settings.BASE_DIR), "models/haarcascade_lefteye_2splits.xml"])
    reye_path = os.path.sep.join(
        [str(settings.BASE_DIR), "models/haarcascade_righteye_2splits.xml"])
    modelPath = os.path.sep.join(
        [str(settings.BASE_DIR), "models/dd_detection.h5"])

    leye = cv2.CascadeClassifier(leye_path)
    reye = cv2.CascadeClassifier(reye_path)

    model = load_model(modelPath)

    rpred = [99]
    lpred = [99]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    left_eye = leye.detectMultiScale(gray)
    right_eye = reye.detectMultiScale(gray)

    for (x, y, w, h) in right_eye:
        r_eye = img[y:y+h, x:x+w]
        r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
        r_eye = cv2.resize(r_eye, (24, 24))
        r_eye = r_eye/255
        r_eye = r_eye.reshape(24, 24, -1)
        r_eye = np.expand_dims(r_eye, axis=0)
        rpred = model.predict(r_eye)
        rpred = np.argmax(rpred, axis=1)

    for (x, y, w, h) in left_eye:
        l_eye = img[y:y+h, x:x+w]

        l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
        l_eye = cv2.resize(l_eye, (24, 24))
        l_eye = l_eye/255
        l_eye = l_eye.reshape(24, 24, -1)
        l_eye = np.expand_dims(l_eye, axis=0)
        lpred = model.predict(l_eye)
        lpred = np.argmax(lpred, axis=1)

    if (rpred[0] == 0 and lpred[0] == 0):
        return "Sleepy Eyes"
    else:
        return "Open Eyes"
