from django.urls import path,include
from .import views

urlpatterns = [

    # --------------------------------------- Student head URLS -------------------------------->
    path('studenthead/',views.sh_dashboard_func, name='sh_dashboard_url'),

    path('shotolist/',views.sh_oto_list_func, name='sh_oto_list_url'),
    path('shotodetails/<int:pkid>',views.sh_oto_detail_func, name='sh_oto_detail_url'),
    path('shgrouplist/',views.sh_group_list_func, name='sh_group_list_url'),
    path('shgroupdetails/<int:pkid>',views.sh_grp_detail_func, name='sh_grp_detail_url'),
    
    # sh my oto functions
    path('shmyotolist/',views.sh_my_oto_list_func, name='sh_my_oto_list_url'),
    # path('sh_myotoaccept/<int:pkid>',views.sh_my_oto_accept_func, name='sh_my_oto_accept_url'),
    # path('sh_myotoreject/<int:pkid>',views.sh_my_oto_reject_func, name='sh_my_oto_reject_url'),
    # path('sh_myotoworkinprogress/<int:pkid>',views.sh_my_oto_work_func, name='sh_my_oto_workinprogress_url'),
    # path('sh_myotocomplete/<int:pkid>',views.sh_my_oto_feedback_func, name='sh_my_oto_feedback_url'),

    # sh my group urls
    path('shmygrouplist/',views.sh_my_group_list_func, name='sh_my_group_list_url'),
    # path('sh_mygroupaccept/<int:pkid>',views.sh_my_group_accept_func, name='sh_my_group_accept_url'),
    # path('sh_mygroupreject/<int:pkid>',views.sh_my_group_reject_func, name='sh_my_group_reject_url'),
    # path('sh_mygroupworkinprogress/<int:pkid>',views.sh_my_group_work_func, name='sh_my_group_workinprogress_url'),
    # path('sh_mygroupcomplete/<int:pkid>',views.sh_my_group_feedback_func, name='sh_my_group_feedback_url'),

    path('shotoassign/<int:pkid>',views.sh_oto_assign_func, name='sh_oto_assign_url'),
    path('shgroupassign/<int:pkid>',views.sh_group_assign_func, name='sh_group_assign_url'),
    path('shgroupassignaccept/<int:pkid>',views.sh_group_assign_and_accept_func, name='sh_group_assign_and_accept_url'),

    path('shvolunteerlist/',views.sh_volunteer_list_func, name='sh_volunteer_list_url'),
    path('shvolunteerdetails/<int:pkid>',views.sh_volunteer_detail_func, name='sh_volunteer_detail_url'),
    path('shvolunteeradd/',views.sh_volunteer_add_func, name='sh_volunteer_add_url'),
    path('shvolunteerinactive/<int:pkid>',views.set_user_inactive_volunteer_func, name='set_user_inactive_volunteer_url'),
    path('shvolunteerupdate/<int:pkid>',views.sh_volunteer_update_func, name='sh_volunteer_update_url'),

    # --------------------------------------- Volunteer URLS ------------------------------------>
    path('volunteer/',views.vol_dashboard_func, name='vol_dashboard_url'),

    path('volotolist/',views.vol_oto_list_func, name='vol_oto_list_url'),
    path('volotodetails/<int:pkid>',views.vol_oto_detail_func, name='vol_oto_detail_url'),
   
    path('volgrouplist/',views.vol_group_list_func, name='vol_group_list_url'),
    path('volgroupdetails/<int:pkid>',views.vol_grp_detail_func, name='vol_grp_detail_url'),

    path('volotoaccept/<int:pkid>',views.vol_oto_accept_func, name='vol_oto_accept_url'),
    path('volotoreject/<int:pkid>',views.vol_oto_reject_func, name='vol_oto_reject_url'),
    path('volotoworkinprogress/<int:pkid>',views.vol_oto_work_func, name='vol_oto_workinprogress_url'),
    path('volotocomplete/<int:pkid>',views.vol_oto_feedback_func, name='vol_oto_feedback_url'),

    path('volgrouppeeraccept/<int:pkid>',views.vol_group_accept_func, name='vol_group_accept_url'),
    path('volgroupreject/<int:pkid>',views.vol_group_reject_func, name='vol_group_reject_url'),
    
    path('volgroupworkinprogress/<int:pkid>',views.vol_group_work_func, name='vol_group_work_url'),
    path('volgroupcomplete/<int:pkid>',views.vol_group_feedback_func, name='vol_group_feedback_url'),

]
