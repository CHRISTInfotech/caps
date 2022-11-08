import django_filters
from django_filters import DateFilter
from django import forms
from accounts.models import onetoonetickettbl, User, peergrouptickettbl

# ----------------- filter form for one o one session reports
class OtoFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="request_datetime", lookup_expr='gte',widget=forms.DateInput(attrs={"class":"form-control","type":"date"}))
    end_date = DateFilter(field_name="request_datetime", lookup_expr='lte',widget=forms.DateInput(attrs={"class":"form-control","type":"date"}))

    class Meta:
        model = onetoonetickettbl
        # fields = '__all__'
        exclude = ['other_desc','name','hours','ticket_no','v_feedback','s_feedback', 'feedback_otp','accepted_date','assigned_to','assigned_count','closed_date']  

# ------------ filtering the forms for groupsession reports
class GroupFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="request_datetime", lookup_expr='gte',widget=forms.DateInput(attrs={"class":"form-control","type":"date"}))
    end_date = DateFilter(field_name="request_datetime", lookup_expr='lte',widget=forms.DateInput(attrs={"class":"form-control","type":"date"}))

    class Meta:
        model = peergrouptickettbl
        # fields = '__all__'
        exclude = [
            'other_desc','name','hours','ticket_no','v_feedback',
            's_feedback', 'feedback_otp','accepted_date',
            'assigned_to','assigned_count','closed_date',
            'sessiondate','sesstiontime','rejected_by','accepted_count',
            'assigned_date','accepted_date'
        ]          

# --------------- filter form for volunteer and student reports
class UserFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="usercreated_date", lookup_expr='gte',widget=forms.DateInput(attrs={"class":"form-control","type":"date"}))
    end_date = DateFilter(field_name="usercreated_date", lookup_expr='gte',widget=forms.DateInput(attrs={"class":"form-control","type":"date"}))

    class Meta:
        model = User
        # fields = {
        #     'first_name': ['icontains'],
        #     'last_name':['icontains'],
        #     'email':['icontains'],
        
        # }
        exclude = ['is_staff','is_superuser']
        