# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from Account.models import User,Income,Expense,Goal, LogsAPI, Setting
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    # 
    list_display = ('id', 'email', 'mobile', 'gender', 'country', 'country_code', 'is_active', 'is_admin', 'firstname', 'lastname', 'birthdate', 'registered_by', 'device_token', 'social_id', 'subscription', 'profile_pic', 'is_subscribed', 'is_verified', 'setup_count', 'is_setup', 'created_at', 'modified_at')
    list_filter = ('is_admin',)
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('gender', 'mobile', 'country', 'firstname', 'lastname', 'birthdate', 'registered_by', 'device_token', 'social_id', 'subscription', 'profile_pic', 'setup_count')}),
        ('Permissions', {'fields': ('is_admin', 'is_subscribed', 'is_verified',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'mobile', 'gender', 'country', 'is_active', 'is_admin', 'firstname', 'lastname', 'birthdate', 'registered_by', 'device_token', 'social_id', 'subscription', 'profile_pic', 'is_subscribed', 'country_code', 'is_verified', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'id')
    ordering = ('email', 'id')
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)

class IncomeAdmin(admin.ModelAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'title', 'amount', 'icon', 'created_at', 'modified_at', 'user')
    list_filter = ('amount', 'created_at',)
    search_fields = ('title', 'id')
    ordering = ('title', 'id')
    list_per_page = 10

admin.site.register(Income, IncomeAdmin)

class ExpenseAdmin(admin.ModelAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'title', 'spent_amount', 'amount_limit', 'icon', 'time_range', 'created_at', 'modified_at', 'user')
    list_filter = ('amount_limit', 'created_at',)
    search_fields = ('title', 'id')
    ordering = ('title', 'id')
    list_per_page = 10


admin.site.register(Expense, ExpenseAdmin)

class GoalAdmin(admin.ModelAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'title', 'added_amount', 'amount', 'icon', 'created_at', 'modified_at', 'user')
    list_filter = ('title', 'created_at',)
    search_fields = ('title', 'id')
    ordering = ('title', 'id')
    list_per_page = 10

admin.site.register(Goal, GoalAdmin)

class LogAdmin(admin.ModelAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'apiname', 'request_header', 'request_parameter', 'request_data', 'response_data', 'email', 'status', 'created_date')
    list_filter = ('email', 'status',)
    search_fields = ('email', 'apiname')
    list_per_page = 10

     # This will help you to disbale add functionality
    def has_add_permission(self, request):
        return False

admin.site.register(LogsAPI, LogAdmin)

admin.site.register(Setting)