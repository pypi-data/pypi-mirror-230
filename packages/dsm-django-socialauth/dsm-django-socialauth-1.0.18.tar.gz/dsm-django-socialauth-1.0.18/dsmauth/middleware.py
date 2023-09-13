import traceback
import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http.response import HttpResponse
from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTauthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _user = JWTAuthentication().authenticate(request)
        request.user = _user[0] if _user != None else request.user

class LogHeaderMiddleware(MiddlewareMixin):
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            response['X-Username'] = request.user.username
        else:
            response['X-Username'] = 'Anonymous'
        return response
    
    def process_exception(self, request, exception):
        if not settings.DEBUG:
            if exception:
                message = "**{url}**\n\n{error}\n\n````{tb}````".format(
                    url=request.build_absolute_uri(),
                    error=repr(exception),
                    tb=traceback.format_exc()
                )
                message = re.sub("\n", "\t", message)
                response = HttpResponse(
                    "<h1>Internal server error (500)</h1><p>error save to log</p>", 
                    status=500, 
                    headers={
                        'X-Error': message
                    }
                )
            return response