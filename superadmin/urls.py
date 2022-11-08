from django.urls import path,include
from .import views

urlpatterns = [

    #**************************************************dept url************************************************************
    path('deptaddform/',views.deptaddformfunc, name='sa_dept_add_url'),
    path('deptlist/',views.deptlistfunc, name='sa_dept_list_url'),
    path('deptupdate/<int:pkid>',views.deptupdatefunc, name='sa_dept_update_url'),
    path('deptdelete/<int:pkid>',views.deptdeletefunc, name='sa_dept_delete_url'),

    
    #**************************************************course url************************************************************
    path('courseaddform/',views.courseaddformfunc, name='sa_course_add_url'),
    path('courselist/',views.courselistfunc, name='sa_course_list_url'),
    path('courseupdate/<int:pkid>',views.courseupdatefunc, name='sa_course_update_url'),
    path('coursedelete/<int:pkid>',views.coursedeletefunc, name='sa_course_delete_url'),

    #**************************************************campus url************************************************************
    path('campusaddform/',views.campusaddformfunc, name='sa_campus_add_url'),
    path('campuslist/',views.campuslistfunc, name='sa_campus_list_url'),
    path('campusupdate/<int:pkid>',views.campusupdatefunc, name='sa_campus_update_url'),
    path('campusdelete/<int:pkid>',views.campusdeletefunc, name='sa_campus_delete_url'),

    #**************************************************Session url************************************************************
    path('sessionaddform/',views.sa_session_add_func, name='sa_session_add_url'),
    path('sessionlist/',views.sa_session_list_func, name='sa_session_list_url'),
    path('sessionupdate/<int:pkid>',views.sa_session_update_func, name='sa_session_update_url'),
    path('sessiondelete/<int:pkid>',views.sa_session_delete_func, name='sa_session_delete_url'),

    #**************************************************super admin url************************************************************
    path('superadmindashboard/',views.sa_dashboard_func, name='sa_dashboard_url'),

    # ---------------------------------------------- Mentors -------------------------------->
    path('mentorlist/',views.sa_mentor_list_func, name='sa_mentor_list_url'),
    path('mentoradd/',views.sa_mentor_add_func, name='sa_mentor_add_url'),
    path('mentorupdate/<int:pkid>',views.sa_mentor_update_func, name='sa_mentor_update_url'),
    path('mentorinactive/<int:pkid>',views.set_user_inactive_mentor_func, name='set_user_inactive_mentor_url'),
    path('mentoractive/<int:pkid>',views.set_user_active_mentor_func, name='set_user_active_mentor_url'),


    # --------------------------------------------- One to one sessions -------------------->
    path('otolist/',views.sa_oto_list_func, name='sa_oto_list_url'),

    path('grouplist/',views.sa_group_list_func, name='sa_group_list_url'),

    path('otodetails/<int:pkid>',views.sa_oto_detail_func, name='sa_oto_detail_url'),

    path('groupdetails/<int:pkid>',views.sa_grp_detail_func, name='sa_grp_detail_url'),

]


