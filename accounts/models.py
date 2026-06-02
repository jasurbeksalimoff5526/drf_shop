from django.db import models
from shared.models import BaseModel
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta
from shop.settings import EMAIL_EXPIRATION_TIME, PHONE_EXPIRATION_TIME
import uuid
import random
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.


ORDINARY_USER, SELLER, ADMIN = ('ordinary_user', 'seller', 'admin')
VIA_PHONE, VIA_EMAIL = ('via_phone', 'via_email')
NEW, CODE_VERIFY, CHANGE_INFO, DONE = ('new', 'code_verify', 'change_info', 'done')


class CustomUser(AbstractUser, BaseModel):
    USER_ROLE = (
       (ORDINARY_USER, ORDINARY_USER),
       (SELLER, SELLER),
       (ADMIN, ADMIN),
    )
    AUTH_TYPE = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL),
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFY, CODE_VERIFY),
        (CHANGE_INFO, CHANGE_INFO),
        (DONE, DONE)
    )
    
    user_role = models.CharField(max_length=120, choices=USER_ROLE, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=120, choices=AUTH_TYPE)
    auth_status = models.CharField(max_length=120, choices=AUTH_STATUS, default=NEW)
    email = models.EmailField(unique=True, null=True)
    phone_number = models.CharField(max_length=13, unique=True, null=True)
    photo = models.ImageField(upload_to='users/', null=True, blank=True, default="users/default_user.png")
    
    def __str__(self):
        return self.username
    
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def create_code(self, verify_type):
        code = str(random.randint(1000, 9999))
        CodeVerify.objects.create(
            code=code,
            user = self,
            verify_type = verify_type
        )
        return code
    
    def token(self):
        refresh = RefreshToken.for_user(self)
        
        return {
            'access_token': str(refresh.access_token),
            'refresh': str(refresh)
        }
    
    
    
    def check_username(self):
        if not self.username:
            temp_username = str(uuid.uuid4()).split('-')[-1]
            while CustomUser.objects.filter(username=temp_username).exists():
                temp_username += str(random.randint(0, 10))
            self.username = temp_username
        
    def password_check(self):
        if not self.password:
            temp_password = str(uuid.uuid4()).split('-')[-1]
            self.password = temp_password
            
    def hash_pass(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
        
    def email_normalize(self):
        if self.email:
            temp_email = self.email.lower()
            self.email = temp_email
        
    def clean(self):
        self.check_username()
        self.password_check()
        self.hash_pass()
        self.email_normalize()
        
    def save(self, *args, **kwargs):
        
        self.clean()
        super().save(*args, **kwargs)
    
    

class CodeVerify(BaseModel):
    VERIFY_TYPE = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL),
    )
    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=120, choices=VERIFY_TYPE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='verify_codes', null=True)
    is_used = models.BooleanField(default=False)
    expiration_time = models.DateTimeField()
    
    
    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL: #3425234623 -> 15:10 + 5 = 15:15
            self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRATION_TIME)
        else:
            self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRATION_TIME)

        super().save(*args, **kwargs)   
    
    