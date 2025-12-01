from django.contrib import admin
from .models import User, SellerAbout

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)

@admin.register(SellerAbout)
class SellerAboutAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_type')
