from django.urls import path
from .import views

urlpatterns = [

    # --------------------------------------------- Mentor URLS ---------------------------->
    path('mentor/',views.mentor_dashboard_func, name='mentor_dashboard_url'),

    path('otolist/',views.mentor_oto_list_func, name='mentor_oto_list_url'),
    path('mentorotodetails/<int:pkid>',views.mentor_oto_detail_func, name='mentor_oto_detail_url'),

    path('grouplist/',views.mentor_group_list_func, name='mentor_group_list_url'),
    path('mentorgroupdetails/<int:pkid>',views.mentor_grp_detail_func, name='mentor_grp_detail_url'),

    #  not used urls
    # path('mentorotoassign/<int:pkid>',views.mentor_oto_assign_func, name='mentor_oto_assign_url'),
    # path('mentorgroupassign/<int:pkid>',views.mentor_group_assign_func, name='mentor_group_assign_url'),

    path('mentorvolunteerlist/',views.mentor_volunteer_list_func, name='mentor_volunteer_list_url'),
    path('mentorvolunteeradd/',views.mentor_volunteer_add_func, name='mentor_volunteer_add_url'),
    path('mentorvolunteerupdate/<int:pkid>',views.mentor_volunteer_update_func, name='mentor_volunteer_update_url'),
    
    path('mentorshlist/',views.mentor_sh_list_func, name='mentor_sh_list_url'),
    path('mentorshadd/',views.mentor_sh_add_func, name='mentor_sh_add_url'),
    path('mentorshupdate/<int:pkid>',views.mentor_sh_update_func, name='mentor_sh_update_url'),

    # common method to disable the volunteer and student head and alos to chaneg roles
    path('mentoruserinactive/<int:pkid>',views.mentor_set_user_inactive_func, name='mentor_set_user_inactive_url'),
    path('mentoruseractive/<int:pkid>',views.mentor_set_user_active_func, name='mentor_set_user_active_url'),
    path('mentorchangevolroles/<int:pkid>',views.mentor_change_role_func, name="mentor_change_role_url"),

    # -------------------- MENTOR - session urls ------------------------------>
    path('mentorsessionaddform/',views.mentor_session_add_func, name='mentor_session_add_url'),
    path('mentorsessionlist/',views.mentor_session_list_func, name='mentor_session_list_url'),
    path('mentorsessionupdate/<int:pkid>',views.mentor_session_update_func, name='mentor_session_update_url'),
    path('mentorsessiondelete/<int:pkid>',views.mentor_session_delete_func, name='mentor_session_delete_url'),

    # -------------------- MENTOR - reports ------------------------------------>

    path('userreports/', views.userreports, name='userreports'),
    path('onetoonereports/',views.onetoonereports, name='onetoonereports'),
    path("peertopeerreports/",views.peertopeerreports,name="peertopeerreports"),
    path('volunteerreports/',views.volunteerreports, name='volunteerreports'),
    path('studentheadreports/',views.studentheadreports, name='studentheadreports'),
    path('sessions/',views.sessions, name='sessions'),
    path('sessionsgroup/',views.sessions_group, name='sessionsgroup'),
    path('group_studentheadreports/',views.group_studentheadreports,name="group_studentheadreports"),
    path('group_volunteerreports/',views.group_volunteerreports,name="group_volunteerreports"),

    path('otoreport/', views.oto_report_func, name='oto_report_url'),
    path('grpreport/', views.grp_report_func, name='grp_report_url'),
    path('userreport/', views.user_report_func, name='user_report_url'),
    path('userreportgen/<int:pkid>', views.user_report_gen_func, name='user_report_gen_url'),
]


