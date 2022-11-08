from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [

    # ----------------------------- Basic URLS ------------------------------------------->
    path('',views.index_func, name='index_url'),
    path('noaccess',views.unauthorized_func, name='unauthorized_access_url'),

    # ---------------------------- Login and logout urls --------------------------------->
    path('login/',views.loginfunc, name='login_url'),
    path('logout/',views.logoutfunc, name='logout_url'),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/pwd_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="accounts/pwd_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/pwd_reset_complete.html'), name='password_reset_complete'),      

    # ---------------------------- OTO booking urls -------------------------------------->
    path('otobooking/',views.oto_booking_func, name='oto_booking_url'),
    # Dont delete these urls .. it is back up for sending mail with encrypted link
    # path('otostudentfeedback/<slug:uidb64>/',views.oto_s_feedback_func, name='oto_s_feedback_url'),
    path('otostudentfeedback/<int:pkid>/',views.oto_s_feedback_func, name='oto_s_feedback_url'),

    # path('otofeedback/<slug:pk>', views.oto_feedback_func, name="otofeedback_url"),
    # path('otocompleted/<int:pk>', views.oto_completed_func, name="otofeedback_url"),

    # ----------------- ----------Group booking urls--------------------------------------->
    path('grpbooking/',views.grp_booking_func, name='grp_booking_url'),
    # path('groupfeedback/<slug:uidb64>/',views.grp_s_feedback_func, name='grp_s_feedback_url'), 
    path('groupfeedback/<int:pkid>/',views.grp_s_feedback_func, name='grp_s_feedback_url'),

    path('usersessionlist/',views.usersessionlistfunc, name='usersessionlist_url'),

    #  -------------------------Feedback anf tracing urls --------------------------------->
    # path('feedbackrequest/',views.feedback_request_func, name='feedback_request_url'),
    # path('otpconfirm/',views.otp_confirm_func, name='otp_confirm_url'),
    # path('feedback/',views.feedback_func, name='feedback'),

    path('feedbackrequest/', views.feedback_verification_func, name="feedback_verification_url"),
    path('feedbackotp/<int:pkid>', views.feedback_otp_func, name="feedback_otp_url"),
    path('feedbackgroupotp/<int:pkid>', views.feedback_otp_grp_func, name="feedback_otp_grp_url"),

    
    # path('otofeedback/',views.feedback, name='oto_feedback'),
]