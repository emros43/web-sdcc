from django.contrib import admin
from .models import Katalog, Plik, Uzytkownik
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class UzytkownikInline(admin.StackedInline):
    model = Uzytkownik
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = [UzytkownikInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Plik)
admin.site.register(Katalog)
