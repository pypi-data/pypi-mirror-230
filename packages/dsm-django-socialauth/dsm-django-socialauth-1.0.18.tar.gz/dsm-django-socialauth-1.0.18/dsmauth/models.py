from django.db import models
from django.contrib.auth.models import User, AnonymousUser

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    email = models.EmailField()
    image = models.ImageField(upload_to='dsmauth-image', blank=True, null=True)
    role = models.JSONField()
    permission = models.JSONField()
    
    def __str__(self) -> str:
        return f"{self.user.username}"

import requests
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from PIL import Image
from io import BytesIO
from django.core.files.images import ImageFile

def logged_in_handle(sender, user, request, **kwargs):
    if settings.DEBUG: print("logged_in_handle")
    prov = user.social_auth.filter(provider='dsmauth')
    user_data = {
        'user': user,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': [],
        'permission': []
    }
    if prov.exists():
        data = prov.last().extra_data
        headers = {
            "Authorization": f"Bearer {data.get('access_token', '')}"
        }
        _internal_ip = getattr(settings, 'OAUTH_INTERNAL_IP', None)
        _url = f"http://{_internal_ip}" if _internal_ip not in [None, "", " "] else  f"https://{settings.OAUTH_DSM_SERVER_BASEURL}"
        try:
            api = requests.get(f"{_url}/api/v1/account/me/", headers=headers).json()
        except Exception as e:
            if settings.DEBUG: print(f"logged_in_handle: {e}")
            pass
        else:
            account = Account.objects.filter(user=request.user) | Account.objects.filter(user__username=api.get('username', ''))
            user_data.update({
                'image': ImageFile(BytesIO(requests.get(api.get('profile_url')).content), name=f"{user.username}.png") if api.get('profile_url', "") != "" else None,
                'role': api.get('role', []),
                'permission': api.get('permission', [])
            })
            user = request.user
            user.is_staff = api.get('is_staff', False)
            user.is_superuser = api.get('is_superuser', False)
            user.save()
            if not account.exists(): 
                Account.objects.create(**user_data)
            else:
                account.update(**user_data)
    elif type(request.user) != AnonymousUser and Account.objects.filter(user__username=user.username).exists() == False:
        Account.objects.create(**user_data)
        
user_logged_in.connect(logged_in_handle)