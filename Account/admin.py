# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from Account.models import User,Income,Expense,Goal, LogsAPI, Setting, Tag, Transaction, SourceIncome, Debt, Subscription, Location, Periodic, Exchangerate
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    # 
    list_display = ('id', 'email', 'mobile', 'gender', 'country', 'country_code', 'is_active', 'is_admin', 'is_superuser', 'firstname', 'lastname', 'birthdate', 'registered_by', 'device_token', 'social_id', 'subscription', 'profile_pic', 'is_subscribed', 'is_verified', 'setup_count', 'is_setup', 'created_at', 'modified_at')
    list_filter = ('is_superuser','is_admin','is_active',)
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('gender', 'mobile', 'country', 'firstname', 'lastname', 'birthdate', 'registered_by', 'device_token', 'social_id', 'subscription', 'profile_pic', 'setup_count')}),
        ('Permissions', {'fields': ('is_superuser', 'is_subscribed', 'is_verified','is_admin','is_active',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'mobile', 'gender', 'country', 'is_active','is_admin', 'is_superuser', 'firstname', 'lastname', 'birthdate', 'registered_by', 'device_token', 'social_id', 'subscription', 'profile_pic', 'is_subscribed', 'country_code', 'is_verified', 'password1', 'password2'),
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

class DebtAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'amount', 'paid_amount', 'is_paid', 'is_partial_paid', 'is_completed', 'date', 'created_at',  'modified_at')
    list_filter = ('id','name')
    search_fields = ('id','name')
    ordering = ('id','name')
    list_per_page = 10

    def has_add_permission(self, request):
        return False

admin.site.register(Debt,DebtAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'user', 'created_at',  'modified_at')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('id','name')
    list_per_page = 10

    def has_add_permission(self, request):
        return False

admin.site.register(Tag,TagAdmin)

class TransactionAdmin(admin.ModelAdmin):
    fields = ['tag']
    list_display = ('id', 'title','description', 'transaction_amount', 'amount', 'income_to', 'income_from', 'expense', 'goal', 'source', 'user', 'location','periodic', 'get_tag', 'debt', 'is_completed', 'created_at', 'modified_at')
    list_filter = ('amount','income_to', 'income_from', 'expense', 'goal', 'source',)
    search_fields = ('title','amount', 'expense', 'goal', 'source', 'created_at',)
    ordering = ('id','title',)
    list_per_page = 10

    def has_add_permission(self, request):
        return False

    def get_tag(self, obj):
        return "\n".join([t.name for t in obj.tag.all()])

admin.site.register(Transaction,TransactionAdmin)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount', 'created_at', 'modified_at')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('id','name')
    list_per_page = 10

    def has_add_permission(self, request):
        return True

admin.site.register(Subscription,SubscriptionAdmin)

class LocationAdmin(admin.ModelAdmin):
    list_display = ('id','latitude','longitude', 'created_at', 'modified_at')
    list_filter = ('id','created_at',)
    search_fields = ('created_at',)
    ordering = ('id','created_at',)
    list_per_page = 10

    def has_add_permission(self, request):
        return False

admin.site.register(Location,LocationAdmin)

class PeriodicAdmin(admin.ModelAdmin):
    list_display = ('id','start_date','end_date','week_days','status_days','prefix','prefix_value', 'created_at', 'modified_at')
    list_filter = ('id','prefix',)
    search_fields = ('created_at','id',)
    ordering = ('id','created_at',)
    list_per_page = 10

    def has_add_permission(self, request):
        return False

admin.site.register(Periodic,PeriodicAdmin)

class SourceIncomeAdmin(admin.ModelAdmin):
    list_display = ('id','icon','title','amount', 'spent_amount', 'user', 'created_at','modified_at')
    list_filter = ('id','title',)
    search_fields = ('created_at','title',)
    ordering = ('id','created_at','title',)
    list_per_page = 10

    def has_add_permission(self, request):
        return False

admin.site.register(SourceIncome,SourceIncomeAdmin)

class ExchangerateAdmin(admin.ModelAdmin):
    list_display = ('id', 'currency_name','is_default', 'created_at', 'modified_at', 'user')
    list_filter = ('id','currency_name',)
    search_fields = ('created_at','currency_name',)
    ordering = ('id','created_at','currency_name',)
    list_per_page = 10

    def has_add_permission(self, request):
        return False

admin.site.register(Exchangerate,ExchangerateAdmin)

class SettingAdmin(admin.ModelAdmin):
    list_display = ('id','notification','min_pass_3','language','currency','user','created_at','modified_at')
    list_filter = ('id','language','currency',)
    search_fields = ('language','currency',)
    ordering = ('id','language','currency',)
    list_per_page = 10

    def has_add_permission(self, request):
        return False

admin.site.register(Setting,SettingAdmin)