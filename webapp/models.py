import cv2

from django.db import models
from PIL import Image
from django.core.files.base import ContentFile
from django.utils import timezone
from django.template.defaultfilters import date as date_filter

from api.models import User


class Log(models.Model):
    log_image = models.ImageField(upload_to='images/')
    logged_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, related_name='logs', on_delete=models.CASCADE)

    def __str__(self):
        logged_date = date_filter(self.logged_at, "F j, Y")
        return f"Log ID: {self.id}, Logged at: {logged_date}, By: {self.user}"

    
    def save_opencv_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the OpenCV frame to PIL Image
        pil_image = Image.fromarray(rgb_frame)

        # Create a temporary buffer to save the image
        image_buffer = ContentFile(b'')
        pil_image.save(image_buffer, 'JPEG')

        # Save the image buffer to the log_image field
        self.log_image.save('image.jpg', image_buffer)
        self.save()

    def save_img(self, img):
       
        image = Image.open(img)
         # Create a temporary buffer to save the image
        image_buffer = ContentFile(b'')
        image.save(image_buffer, 'JPEG')

        # Save the image buffer to the log_image field
        self.log_image.save('image.jpg', image_buffer)
        self.save()

