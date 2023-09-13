from django.contrib import admin
from . import models

class AccountAdmin(admin.ModelAdmin):
    list_display = [f.name for f in models.Account._meta.fields]
admin.site.register(models.Account, AccountAdmin)