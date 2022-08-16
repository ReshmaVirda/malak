from django.urls import re_path
from . import views


from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView
)

urlpatterns = [
    re_path(r'^logout$', views.LogoutAPIView.as_view(), name="logout"),
    re_path(r'^reset/$', views.ResetPassword.as_view(), name="reset"),
    re_path(r'^confirm/$', views.confirm, name="confirm"),
    re_path(r'^token/$', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    re_path(r'^token/refresh/$', TokenRefreshView.as_view(), name="token_obtain_pair"),
    re_path(r'^register$', views.UserRegistrationView.as_view(), name="register"),
    re_path(r'^login$', views.UserLoginView.as_view(), name="login"),
    re_path(r'^profile$', views.UserProfileView.as_view(), name="profile"),
    re_path(r'^changepassword$', views.UserChangePasswordView.as_view(), name="changepassword"),
    re_path(r'^income$', views.IncomeCreate.as_view(), name="income"),
    re_path(r'^income/(?P<pk>\d+)$', views.IncomeDetailView.as_view(), name="income"),
    re_path(r'^expense$', views.ExpenseCreate.as_view(), name="expense"),
    re_path(r'^expense/(?P<pk>\d+)$', views.ExpenseDetailView.as_view(), name="expense"),
    re_path(r'^goal$', views.GoalsCreate.as_view(), name="goal"),
    re_path(r'^goal/(?P<pk>\d+)$', views.GoalsDetailView.as_view(), name="goal"),
    re_path(r'^source$', views.SourceIncomeView.as_view(), name="source"),
    re_path(r'^source/(?P<pk>\d+)$', views.SourceIncomeDetailView.as_view(), name="source"),
    re_path(r'^home$', views.HomeView.as_view(), name="home"),
    re_path(r'^exchange-rate/$', views.ExchangerateCreate.as_view(), name="exchangerate"),
    re_path(r'^exchange-rate/(?P<pk>\d+)$', views.ExchangerateCreate.as_view(), name="exchangerate"),
    re_path(r'^location$', views.LocationDetailView.as_view(), name="location"),
    re_path(r'^periodic$', views.PeriodicDetailView.as_view(), name="periodic"),
    re_path(r'^tag/$', views.TagView.as_view(), name="tag"),
    re_path(r'^tag/(?P<pk>\d+)$', views.TagView.as_view(), name="tag"),
    re_path(r'^debt$', views.DebtView.as_view(), name="debt"),
    re_path(r'^debt/(?P<pk>\d+)$', views.DebtDetailView.as_view(), name="debt"),
    re_path(r'^setting$', views.SettingView.as_view(), name="setting"),
    re_path(r'^setting/(?P<pk>\d+)$', views.SettingDetailView.as_view(), name="setting"),
    re_path(r'^transaction/$', views.TransactionView.as_view(), name="transaction"),
    re_path(r'^transaction/(?P<pk>\d+)$', views.TransactionView.as_view(), name="transaction"),
    re_path(r'^user/subscription$', views.UserSubscriptionView.as_view(), name="user_subscription"),
    re_path(r'^admin/subscription/$', views.AdminSubscriptionView.as_view(), name="admin_subscription"),
    re_path(r'^admin/subscription/(?P<pk>\d+)$', views.AdminSubscriptionView.as_view(), name="admin_subscription"),
    re_path(r'^report$', views.ReportView.as_view(), name="report"),
    re_path(r'^export$', views.Export.as_view(), name="export"),
]