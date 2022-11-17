from django.shortcuts import redirect
from django.http import HttpResponse

# def staff_required(view_func=None, redirect_field_name, login_url='login_url',message="Only superadmin can acces"):
#     """
#     Decorator for views that checks that the user is logged in and is
#     staff, displaying message if provided.
#     """
#     actual_decorator = user_passes_test(
#         lambda u: u.is_active and u.is_staff and u.is_authenticated,
#         login_url=login_url,
#         redirect_field_name=redirect_field_name,
#         message=message
#     )
#     if view_func:
#         return actual_decorator(view_func)
#     return actual_decorator

def superadmin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return redirect("unauthorized_access_url")
    return wrapper_func

def mentor_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active and request.user.roles.roles == "mentor":
            return view_func(request, *args, **kwargs)
        else:
            return redirect("unauthorized_access_url")
    return wrapper_func

# def mentor_only(view_func):
#     def wrapper_func(request, *args, **kwargs):
#         try:
#             print(request.user.is_authenticated and request.user.is_active and request.user.roles.roles == "mentor")

#             if request.user.is_authenticated and request.user.is_active and request.user.roles.roles == "mentor":

#                 return view_func(request, *args, **kwargs)
#             else:
#                 return redirect("unauthorized_access_url")
#         except:
#             return redirect("unauthorized_access_url")
#     return wrapper_func

def studenthead_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active and request.user.roles.roles == "studenthead":
            return view_func(request, *args, **kwargs)
        else:
            return redirect("unauthorized_access_url")
    return wrapper_func



def volunteer_only(view_func):
    def wrapper_func(request, *args, **kwargs):
       
        if request.user.is_authenticated and request.user.is_active and (request.user.roles.roles == "volunteer"):
            print("inside")
            return view_func(request, *args, **kwargs)    
        else:
            return redirect("unauthorized_access_url")
    return wrapper_func

# decorator to allow both volunteer and student headd to access ceratin functions
def vol_and_studenthead_only(view_func):
    def wrapper_func(request, *args, **kwargs):
       
        if request.user.is_authenticated and request.user.is_active and (request.user.roles.roles == "volunteer" or request.user.roles.roles == "studenthead"):
            print("inside")
            return view_func(request, *args, **kwargs)    
        else:
            return redirect("unauthorized_access_url")
    return wrapper_func



def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponse("No access ")
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func