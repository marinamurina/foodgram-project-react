from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)

