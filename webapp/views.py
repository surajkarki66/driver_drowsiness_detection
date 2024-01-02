import cv2
import numpy as np
import os

from keras.models import load_model
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import StreamingHttpResponse
from django.shortcuts import render

from .camera import FaceDetect
from api.models import User
from api.models import UploadedImage


def LandingPage(request):
    if request.method == 'GET':
        return render(request, 'landing_page.html')
    elif request.method == 'POST':
        return detect_drowsiness(request)

@login_required(login_url='/login')
def LiveDetectionPage(request):
    if request.method == 'GET':
        return render(request, 'live_detection.html')
    elif request.method == 'POST':
        return stop_camera(request)


camera_running = False


def gen(camera):
    while camera_running:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def start_camera(request):
    global camera_running
    camera_running = True
    return StreamingHttpResponse(gen(FaceDetect(request)), content_type='multipart/x-mixed-replace; boundary=frame')


def stop_camera(request):
    global camera_running
    camera_running = False
    return HttpResponse('Camera stopped successfully.')


def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse("Your password and confirm password are not Same!!")
        else:
            my_user = User.objects.create_user(email, uname, contact, pass1)
            my_user.save()
            return redirect('/login')

    return render(request, 'signup.html')


def LoginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pass1 = request.POST.get('pass')

        user = authenticate(request, username=email, password=pass1)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return HttpResponse("Username or Password is incorrect!!!")

    return render(request, 'login.html')


def LogoutPage(request):
    logout(request)
    return redirect('/')


def detect_drowsiness(request):
    if request.method == 'POST':
        image = request.FILES['image_data']
       
        # Save the uploaded image to the model
        uploaded_image = UploadedImage(image=image)
        uploaded_image.save()

        image_path = uploaded_image.image.path
        processed_output = classify_image(image_path)
        output = {
            "message": processed_output["message"],
            "status": processed_output["status"],
        }
        return render(request, 'landing_page.html', output)


def classify_image(url):
    img = cv2.imread(url)

    face_path = os.path.sep.join(
        [str(settings.BASE_DIR), "models/haarcascade_frontalface_alt.xml"])
    leye_path = os.path.sep.join(
        [str(settings.BASE_DIR), "models/haarcascade_lefteye_2splits.xml"])
    reye_path = os.path.sep.join(
        [str(settings.BASE_DIR), "models/haarcascade_righteye_2splits.xml"])
    modelPath = os.path.sep.join(
        [str(settings.BASE_DIR), "models/dd_detection.h5"])

    face = cv2.CascadeClassifier(face_path)
    leye = cv2.CascadeClassifier(leye_path)
    reye = cv2.CascadeClassifier(reye_path)

    model = load_model(modelPath)

    font = cv2.FONT_HERSHEY_COMPLEX_SMALL

    font = cv2.FONT_HERSHEY_COMPLEX_SMALL

    rpred = [99]
    lpred = [99]

    height, width = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face.detectMultiScale(
        gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25))
    left_eye = leye.detectMultiScale(gray)
    right_eye = reye.detectMultiScale(gray)

    cv2.rectangle(img, (0, height-50), (200, height),
                  (0, 0, 0), thickness=cv2.FILLED)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (100, 100, 100), 1)

    for (x, y, w, h) in right_eye:
        r_eye = img[y:y+h, x:x+w]

        r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
        r_eye = cv2.resize(r_eye, (24, 24))
        r_eye = r_eye/255
        r_eye = r_eye.reshape(24, 24, -1)
        r_eye = np.expand_dims(r_eye, axis=0)
        rpred = model.predict(r_eye)
        rpred = np.argmax(rpred, axis=1)
        break

    for (x, y, w, h) in left_eye:
        l_eye = img[y:y+h, x:x+w]

        l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
        l_eye = cv2.resize(l_eye, (24, 24))
        l_eye = l_eye/255
        l_eye = l_eye.reshape(24, 24, -1)
        l_eye = np.expand_dims(l_eye, axis=0)
        lpred = model.predict(l_eye)
        lpred = np.argmax(lpred, axis=1)

        break
    if (rpred[0] == 0 and lpred[0] == 0):
        cv2.putText(img, "Closed", (10, height-20), font,
                    1, (255, 255, 255), 1, cv2.LINE_AA)
        return {"status": "close", "message": "Eyes are looking sleepy or closed!"}
    
    else:

        cv2.putText(img, "Open", (10, height-20), font,
                    1, (255, 255, 255), 1, cv2.LINE_AA)
        return  {"status": "open", "message": "Eyes are open!"}
