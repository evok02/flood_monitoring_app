from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('map')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func
    
def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            print('Working:', allowed_roles)


            return view_func(request, *args, **kwargs)     
        return wrapper_func
    return decorator