from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User,rolestbl, campustbl, depttbl, coursetbl, stuhead_vol_profiletbl
from .models import sessiontbl,onetoonetickettbl,peergrouptickettbl

from .forms import UserAddForm

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name','last_name','roles', 'last_login')}),
        ('Permissions', {'fields': (
            'is_active', 
            'is_staff', 
            'is_superuser',
            'groups', 
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )

    list_display = ('email', 'first_name', 'is_staff', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(User, UserAdmin)


admin.site.register(rolestbl)
admin.site.register(campustbl)
admin.site.register(depttbl)
admin.site.register(coursetbl)
admin.site.register(stuhead_vol_profiletbl)
# admin.site.register(mentortbl)

admin.site.register(sessiontbl)
admin.site.register(onetoonetickettbl)
admin.site.register(peergrouptickettbl)