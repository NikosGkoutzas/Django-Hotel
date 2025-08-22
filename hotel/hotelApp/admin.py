from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    list_display = ('first_name' , 'last_name' , 'email' , 'country_code' , 'phone_number' , 'age')
