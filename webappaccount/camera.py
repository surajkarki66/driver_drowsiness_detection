import os
import cv2
import imutils
import numpy as np

from imutils.video import VideoStream
from imutils.video import FPS

from django.conf import settings
from keras.models import load_model
from pygame import mixer
from .models import Log

face_path = os.path.sep.join(
    [str(settings.BASE_DIR), "assets/haarcascade_frontalface_alt.xml"])
leye_path = os.path.sep.join(
    [str(settings.BASE_DIR), "assets/haarcascade_lefteye_2splits.xml"])
reye_path = os.path.sep.join(
    [str(settings.BASE_DIR), "assets/haarcascade_righteye_2splits.xml"])
modelPath = os.path.sep.join([str(settings.BASE_DIR), "assets/cnnCat.keras"])
sound_path = os.path.join(str(settings.BASE_DIR), "assets/alarm.wav")

face = cv2.CascadeClassifier(face_path)
leye = cv2.CascadeClassifier(leye_path)
reye = cv2.CascadeClassifier(reye_path)

lbl = ['Close', 'Open']

model = load_model(modelPath)


mixer.init()
sound = mixer.Sound(sound_path)


class FaceDetect(object):
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    score = 0
    thicc = 2
    rpred = [99]
    lpred = [99]

    def __init__(self, request):
        self.user = request.user
        # initialize the video stream, then allow the camera sensor to warm up
        self.vs = VideoStream(src=200).start()
        # start the FPS throughput estimator
        self.fps = FPS().start()

    def __del__(self):
        self.vs.stop()
        cv2.destroyAllWindows()

    def get_frame(self):
        path = os.getcwd()

        # grab the frame from the threaded video stream
        frame = self.vs.read()
        frame = cv2.flip(frame, 1)

        frame = imutils.resize(frame, width=600)
        (height, width) = frame.shape[:2]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face.detectMultiScale(
            gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25))
        left_eye = leye.detectMultiScale(gray)
        right_eye = reye.detectMultiScale(gray)

        cv2.rectangle(frame, (0, height-50), (200, height),
                      (0, 0, 0), thickness=cv2.FILLED)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (100, 100, 100), 1)

        for (x, y, w, h) in right_eye:
            r_eye = frame[y:y+h, x:x+w]
            r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
            r_eye = cv2.resize(r_eye, (24, 24))
            r_eye = r_eye/255
            r_eye = r_eye.reshape(24, 24, -1)
            r_eye = np.expand_dims(r_eye, axis=0)
            self.rpred = model.predict(r_eye)
            self.rpred = np.argmax(self.rpred, axis=1)

            break

        for (x, y, w, h) in left_eye:
            l_eye = frame[y:y+h, x:x+w]
            l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
            l_eye = cv2.resize(l_eye, (24, 24))
            l_eye = l_eye/255
            l_eye = l_eye.reshape(24, 24, -1)
            l_eye = np.expand_dims(l_eye, axis=0)
            self.lpred = model.predict(l_eye)
            self.lpred = np.argmax(self.lpred, axis=1)

            break

        if (self.rpred[0] == 0 and self.lpred[0] == 0):
            self.score = self.score+1
            cv2.putText(frame, "Closed", (10, height-20), self.font,
                        1, (255, 255, 255), 1, cv2.LINE_AA)

        else:
            self.score = self.score-1
            cv2.putText(frame, "Open", (10, height-20), self.font,
                        1, (255, 255, 255), 1, cv2.LINE_AA)

        if (self.score < 0):
            self.score = 0
        cv2.putText(frame, 'Score:'+str(self.score), (100, height-20),
                    self.font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        if (self.score > 15):
            # person is feeling sleepy so we beep the alarm
            log_instance = Log(user=self.user)
            log_instance.save_opencv_frame(frame)

            try:
                sound.play()

            except:
                pass
            if (self.thicc < 16):
                self.thicc = self.thicc+2
            else:
                self.thicc = self.thicc-2
                if (self.thicc < 2):
                    self.thicc = 2
            cv2.rectangle(frame, (0, 0), (width, height),
                          (0, 0, 255), self.thicc)

        # update the FPS counter
        self.fps.update()
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
