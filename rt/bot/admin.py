from django.contrib import admin
from  .models import *


@admin.register(questions)
class questAdmin(admin.ModelAdmin):
    list_display = ('service','category','subcategory','answere')


@admin.register(Categorys)
class categoryAdmin(admin.ModelAdmin):
    list_display = ('name','answere')
