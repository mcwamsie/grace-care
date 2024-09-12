from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from home.models import Church, Assembly, Member


# Register your models here.
class ChurchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'active')
    search_fields = ('name', 'address')


admin.site.register(Church, ChurchAdmin)


class AssemblyAdmin(admin.ModelAdmin):
    list_display = ('name', 'church', 'location', 'active')
    list_filter = ('church',)
    search_fields = ('name', 'location')


admin.site.register(Assembly, AssemblyAdmin)


class MemberAdmin(UserAdmin):
    model = Member
    ordering = ['last_name', "first_name"]
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'assembly', "role", 'is_staff', 'is_active')
    list_filter = ('assembly', 'is_staff', 'is_active', "role")
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    readonly_fields = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password', 'role')}),
        ('Personal Info',
         {'fields': ('profilePhoto', 'first_name', 'last_name', 'phone_number', 'address', 'assembly')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        ('Important dates', {'fields': ['date_joined']}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'profilePhoto',
                'email', 'password1', 'password2', 'first_name', 'last_name',
                'sex',
                'date_of_birth',
                'phone_number',
                'address', 'role',
                'assembly'),
        }),
    )


admin.site.register(Member, MemberAdmin)
