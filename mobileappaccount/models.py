from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Custom User MAnager


class UserManager(BaseUserManager):
    def create_user(self, email, name, contact, password=None, password2=None):
        """
        Creates and saves a User with the given email, name, contact, 
         and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            contact=contact,

        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, contact, name, password=None):
        """
        Creates and saves a superuser with the given email, contact, name  and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            contact=contact,

        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# Custom User Model
class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=30,
        unique=True,

    )
    name = models.CharField(max_length=200)
    contact = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    Updated_at = models.DateField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'contact', ]

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class UploadedImage(models.Model):
    image = models.ImageField(upload_to='images/')

    uploaded_at = models.DateTimeField(auto_now_add=True)
