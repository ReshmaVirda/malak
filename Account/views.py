# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import User, Subscription, Income, Expense, Goal, LogsAPI, SourceIncome, Exchangerate, Location, Periodic, Setting, Transaction, Tag, Debt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from Account.serializers import LogoutSerializer, UserRegistrationSerializer, UserLoginSerializer, UserSocialLoginSerializer, UserProfileSerializer, UserChangePasswordSerializer, UserSubscriptionSerializer, IncomeSerializer,ExpenseSerializer,GoalsSerializer, SourceIncomeSerializer, ExchangerateSerializer, LocationSerializer, PeriodicSerializer, SettingSerializer, TagSerializer, DebtSerializer, TransactionSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.hashers import make_password
import json
from django.db.models import Sum
from datetime import date, datetime as dt, timedelta
import datetime
from django.core.files.storage import FileSystemStorage
from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
import csv
from io import StringIO, BytesIO
import xlwt
# Create your views here.

## Date Control ##
def Get_Dates(prefix, prefix_value, enddate, startdate=None):
    main_dict = {}
    month_dates = []
    year_dates = []
    days_date = []
    dates = []
    start_date = ""

    if startdate is not None:
        start_date = dt.strptime(str(startdate), '%Y-%m-%d').date()
    else:
        start_date = date.today()
    
    end_date = dt.strptime(str(enddate), '%Y-%m-%d').date()

    if prefix == "month":
        del dates[:]
        del month_dates[:]
        while start_date <= end_date:
            mdate = start_date + relativedelta(months=prefix_value)
            month_dates.append(mdate.strftime("%Y-%m-%d"))
            start_date = mdate
        month_dates.pop()

        for x in month_dates:
            x_date = dt.strptime(x, "%Y-%m-%d").date()
            if x_date > dt.now().date():
                dates.append(x)

    elif prefix == "year":
        del dates[:]
        del year_dates[:]
        while start_date <= end_date:
            mdate = start_date + relativedelta(years=prefix_value)
            year_dates.append(mdate.strftime("%Y-%m-%d"))
            start_date = mdate
        year_dates.pop()
    
        for x in year_dates:
            x_date = dt.strptime(x, "%Y-%m-%d").date()
            if x_date > dt.now().date():
                dates.append(x)

    elif prefix == "day":
        del dates[:]
        del days_date[:]
        while start_date <= end_date:
            mdate = start_date + relativedelta(days=prefix_value)
            days_date.append(mdate.strftime("%Y-%m-%d"))
            start_date = mdate
        days_date.pop()

        for x in days_date:
            x_date = dt.strptime(x, "%Y-%m-%d").date()
            if x_date > dt.now().date():
                dates.append(x)
        
    main_dict["Date_Days"] = ','.join(dates)
    main_dict["Date_Years"] = ','.join(dates)
    main_dict["Date_Months"] = ','.join(dates)
    
    return main_dict
## Date Control End ##

# Generate Manual Token Code Start #
def get_tokens_for_user(user):
    refresh = ""
    try:
        user_data = User.objects.get(email=user).id
    except User.DoesNotExist:
        return Response({"status":False, "message":"User Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
    
    refresh = OutstandingToken.objects.filter(user_id=user_data)
    if refresh != []:
        refresh.delete()  
    
    refresh = RefreshToken.for_user(user)

    refresh_token = refresh
    access_token = refresh.access_token
    
    return {
        'refresh': str(refresh_token),
        'access': str(access_token),
    }
# Generate Manual Token Code End #

# Check Token Code Start #
def check_token(user):
    refresh = ""
    try:
        user_data = User.objects.get(email=user).id
    except User.DoesNotExist:
        return Response({"status":False, "message":"User Doesn't Exist."}, status=status.HTTP_404_NOT_FOUND)
    
    try:    
        refresh = OutstandingToken.objects.get(user_id=user_data).id
    except OutstandingToken.DoesNotExist:
        return Response({"status":False, "message":"User Haven't Any Token."}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        refresh = BlacklistedToken.objects.get(token_id=refresh)
        if refresh:
            refresh = "Token is Blacklisted."
    except BlacklistedToken.DoesNotExist:
        refresh = ""
    
    return refresh

# Check Token Code End #

# User Registration Api Code Start #            Done with logs
class UserRegistrationView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def post(self, request, format=None):
        serializer = ''
        userpassword = ""
        try:
            serializer = User.objects.get(email=request.data['email'])
        except User.DoesNotExist:
            pass

        if serializer != "":
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":"User already exist with this email"}), email=serializer.email, status=False)
            return Response({"status":False, "message":"User already exist with this email"}, status=status.HTTP_404_NOT_FOUND)
        
        if 'registered_by' in request.data and request.data["registered_by"] == "manual":
            if 'password' in request.data or request.data["password"] != "":
                userpassword = make_password(request.data['password'])
                request.data.update({"password":userpassword})
            else:
                return Response({"status":False, "message":"password is the required field cannot be blank."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if 'social_id' not in request.data or request.data["social_id"] == "":
                return Response({"status":False, "message":"social_id cannot be blank while signup with social account."}, status=status.HTTP_400_BAD_REQUEST)            

        serializer = UserRegistrationSerializer(data=request.data)#
        if serializer.is_valid(raise_exception=False):
            user = serializer.save()
            token = get_tokens_for_user(user)
            
            user = User.objects.get(email=user)
            settings = Setting.objects.create(user_id=user.id)
            country = ''
            birthdate = ''
            device_token = ''
            social_id = ''
            subscription_id = ''
            profile_pic = ''
            
            if user.country != '':
                country = user.country
            else:
                country = None

            if user.birthdate != '':
                birthdate = user.birthdate
            else:
                birthdate = None

            if user.device_token != '':
                device_token = user.device_token
            else:
                device_token = None
            
            if user.social_id != '':
                social_id = user.social_id
            else:
                social_id = None

            if user.subscription != '':
                subscription_id = user.subscription
            else:
                subscription_id = None
            
            if user.image_url != None:
                profile_pic = request.build_absolute_uri(user.image_url)
                profile_pic = profile_pic.replace('%40', '@')
            else:
                profile_pic = None
            
            User_data = {
                'id':user.id,
                'firstname':user.firstname,
                'lastname':user.lastname,
                'email':user.email,
                'mobile':user.mobile,
                'gender':user.gender,
                'country':country,
                'birthdate':birthdate,
                'is_agree':user.is_agree,
                'registered_by':user.registered_by,
                'profile_pic':profile_pic,
                'subscription_id':subscription_id,
                'social_id':social_id,
                'device_token':device_token,
                'is_verified':user.is_verified,
                'setupcount':int(user.setup_count),
                'is_setup':user.is_setup,
                'is_registered':user.is_registered,
                'is_active':user.is_active,
                'is_admin':user.is_admin,
                'country_code':user.country_code,
                'is_subscribed':user.is_subscribed,
                'access_token':token.get('access'),
                'refresh_token':token.get('refresh'),
                'settings_id':settings.id
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":True, "message":"Register Successfully"}), email=user.email, status=True)
            return Response({"status":True, "message":"Register Successfully", "data":User_data}, status=status.HTTP_201_CREATED)
        else:
            message = ''
            if 'firstname' in serializer.errors:
                message = "firstname cannot be blank."
            if 'lastname' in serializer.errors:
                message = "lastname cannot be blank."
            if 'email' in serializer.errors and serializer.errors['email'][0] == 'This field may not be blank.':
                message = "email cannot be blank."
            if 'email' in serializer.errors and serializer.errors['email'][0] == 'Enter a valid email address.':
                message = "Enter a valid email address."
            if 'mobile' in serializer.errors:
                message = "mobile cannot be blank"
            if 'gender' in serializer.errors and serializer.errors['gender'][0] == '"" is not a valid choice.':
                message = "please provide either male or female"
            if 'gender' in serializer.errors and serializer.errors['gender'][0] == "This field is required.":
                message = "gender is the required field. please provide male or female choice."
            if 'registered_by' in serializer.errors and serializer.errors['registered_by'][0] == '"" is not a valid choice.':
                message = "please provide valid choice. choices are manual, facebook, gmail and apple."
            if 'is_agree' in serializer.errors and serializer.errors['is_agree'][0] == 'Must be a valid boolean.':
                message = "is_agree cannot be blank please provide either true or false"
            if 'country_code' in serializer.errors:
                message = "please provide country_code like IN, AR"
            if 'registered_by' in serializer.errors:
                message = "please provide manual, facebook, google or apple as a choice."
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":message}), email="", status=False)
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)
# User Registration Api Code End #  

# User Login Api Code Start #                   Done with logs
class UserLoginView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def post(self, request, format=None):
        if (('email' not in request.data and request.data['email'] == "") and ('registered_by' not in request.data and request.data['registered_by'] == "")): 
            return Response({"status":False, "message":"email and registered_by cannot be blank"})
        
        if request.data["registered_by"] == "manual":
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid(raise_exception=False):
                email = serializer.data.get('email')
                password = serializer.data.get('password')
                registered_by = serializer.data.get('registered_by')
                user = authenticate(email=email, password=password, registered_by=registered_by)
        
                if user is not None:
                    if not user.is_active:
                        LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":"Your account is not active, please contact admin"}), email=email, status=False)
                        return Response({"status":False, "message":"Your account is not active, please contact admin"}, status=status.HTTP_400_BAD_REQUEST)
                    elif user is not None:
                        token = get_tokens_for_user(user)
                        try:
                            user = User.objects.get(email=serializer.data.get('email'))
                        except User.DoesNotExist:
                            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":"User Detail Not Found"}), email=email, status=False)
                            return Response({"status":False, "message":"User Detail Not Found"}, status=status.HTTP_404_NOT_FOUND)

                        country = ''
                        birthdate = ''
                        device_token = ''
                        social_id = ''
                        subscription_id = ''
                        profile_pic = ''

                        if user.country != '':
                            country = user.country
                        else:
                            country = None

                        if user.birthdate != '':
                            birthdate = user.birthdate
                        else:
                            birthdate = None

                        if user.device_token != '':
                            device_token = user.device_token
                        else:
                            device_token = None
                        
                        if user.social_id != '':
                            social_id = user.social_id
                        else:
                            social_id = None

                        if user.subscription != '':
                            subscription_id = user.subscription
                        else:
                            subscription_id = None
                        
                        if user.image_url != None:
                            profile_pic = request.build_absolute_uri(user.image_url)
                            profile_pic = profile_pic.replace('%40', '@')
                        else:
                            profile_pic = None

                        try:
                            settings = Setting.objects.get(user_id=str(user.id)).id
                        except Setting.DoesNotExist:
                            settings = "setting detail not found"
                    
                        User_data = {
                            'id':user.id,
                            'firstname':user.firstname,
                            'lastname':user.lastname,
                            'email':user.email,
                            'mobile':user.mobile,
                            'gender':user.gender,
                            'country':country,
                            'birthdate':birthdate,
                            'is_agree':user.is_agree,
                            'registered_by':user.registered_by,
                            'profile_pic':profile_pic,
                            'subscription_id':str(subscription_id),
                            'social_id':social_id,
                            'device_token':device_token,
                            'is_verified':user.is_verified,
                            'setupcount':int(user.setup_count),
                            'is_setup':user.is_setup,
                            'is_registered':user.is_registered,
                            'is_active':user.is_active,
                            'is_admin':user.is_admin,
                            'country_code':user.country_code,
                            'is_subscribed':user.is_subscribed,
                            'access_token':token.get('access'),
                            'refresh_token':token.get('refresh'),
                            'settings_id':settings
                        }
                        LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":True, "message":"Login Successfully"}), email=email, status=True)
                        return Response({"status":True, "message":"Login Successfully", "data":User_data}, status=status.HTTP_200_OK)
                    else:
                        LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":{"non_field_errors":["Email or Password is not valid"]}}), email=email, status=False)
                        return Response({"status":False, "message":"Email or Password is not valid"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":"user credential not match"}), email=request.data['email'], status=False)
                    return Response({"status":False, "message":"user credential not match"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                message = ''
                if (('password' in serializer.errors and serializer.errors['password'][0] == "This field may not be blank.") and ('email' in serializer.errors and serializer.errors['email'][0] == "This field may not be blank.")):
                    message = "please enter your email and password to login" 
                elif ('password' in serializer.errors and serializer.errors['password'][0] == "This field may not be blank."):
                    message = "Please provide your login password"
                elif ('email' in serializer.errors and serializer.errors['email'][0] == "This field may not be blank."):
                    message = "please enter your email"
                elif ('email' in serializer.errors and serializer.errors['email'][0] == "Enter a valid email address."):
                    message = "Enter a valid email address."

                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":serializer.errors}), email=request.data['email'], status=False)
                return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = User.objects.get(email=request.data.get('email'), registered_by=request.data.get('registered_by'), social_id=request.data.get('social_id'))
            except User.DoesNotExist:
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":"User Detail Not Found"}), email=request.data.get('email'), status=False)
                return Response({"status":False, "message":"User Detail Not Found"}, status=status.HTTP_404_NOT_FOUND)
            token = get_tokens_for_user(user)
            country = ''
            birthdate = ''
            device_token = ''
            social_id = ''
            subscription_id = ''
            profile_pic = ''

            if user.country != '':
                country = user.country
            else:
                country = None

            if user.birthdate != '':
                birthdate = user.birthdate
            else:
                birthdate = None

            if user.device_token != '':
                device_token = user.device_token
            else:
                device_token = None
            
            if user.social_id != '':
                social_id = user.social_id
            else:
                social_id = None

            if user.subscription != '':
                subscription_id = user.subscription
            else:
                subscription_id = None
            
            if user.image_url != None:
                profile_pic = request.build_absolute_uri(user.image_url)
                profile_pic = profile_pic.replace('%40', '@')
            else:
                profile_pic = None

            try:
                settings = Setting.objects.get(user_id=str(user.id)).id
            except Setting.DoesNotExist:
                settings = "setting detail not found"
        
            User_data = {
                'id':user.id,
                'firstname':user.firstname,
                'lastname':user.lastname,
                'email':user.email,
                'mobile':user.mobile,
                'gender':user.gender,
                'country':country,
                'birthdate':birthdate,
                'is_agree':user.is_agree,
                'registered_by':user.registered_by,
                'profile_pic':profile_pic,
                'subscription_id':str(subscription_id),
                'social_id':social_id,
                'device_token':device_token,
                'is_verified':user.is_verified,
                'setupcount':int(user.setup_count),
                'is_setup':user.is_setup,
                'is_registered':user.is_registered,
                'is_active':user.is_active,
                'is_admin':user.is_admin,
                'country_code':user.country_code,
                'is_subscribed':user.is_subscribed,
                'access_token':token.get('access'),
                'refresh_token':token.get('refresh'),
                'settings_id':settings
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_data=json.dumps(request.data), response_data=json.dumps({"status":True, "message":"Login Successfully"}), email=request.data.get('email'), status=True)
            return Response({"status":True, "message":"Login Successfully", "data":User_data}, status=status.HTTP_200_OK)
# User Login Api Code End #

# User Profile API Code Start #                 Done with logs
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserProfileSerializer(request.user)
        country = ''
        birthdate = ''
        profile_pic = ''
        subscription_id = ''
        social_id = ''
        device_token = ''

        if serializer.data.get('country') != '':
            country = serializer.data.get('country')
        else:
            country = None

        if serializer.data.get('birthdate') != '':
            birthdate = serializer.data.get('birthdate')
        else:
            birthdate = None
    
        if serializer.data.get('profile_pic') != None:
            profile_pic = request.build_absolute_uri(serializer.data.get('profile_pic'))
            profile_pic = profile_pic.replace('%40', '@')
        else:
            profile_pic = None

        if serializer.data.get('subscription') != '':
            subscription_id = serializer.data.get('subscription')
        else:
            subscription_id = None

        if serializer.data.get('social_id') != '':
            social_id = serializer.data.get('social_id')
        else:
            social_id = None

        if serializer.data.get('device_token') != '':
            device_token = serializer.data.get('device_token')
        else:
            device_token = None

        try:
            settings = Setting.objects.get(user_id=str(serializer.data.get('id'))).id
        except Setting.DoesNotExist:
            settings = "setting detail not found"

        user_profile = {
            'id':serializer.data.get('id'),
            'firstname':serializer.data.get('firstname'),
            'lastname':serializer.data.get('lastname'),
            'email':serializer.data.get('email'),
            'mobile':serializer.data.get('mobile'),
            'gender':serializer.data.get('gender'),
            'country':country,
            'birthdate':birthdate,
            'is_agree':serializer.data.get('is_agree'),
            'registered_by':serializer.data.get('registered_by'),
            'profile_pic':profile_pic,
            'subscription_id':subscription_id,
            'social_id':social_id,
            'device_token':device_token,
            'is_verified':serializer.data.get('is_verified'),
            'setupcount':int(serializer.data.get('setup_count')),
            'is_setup':serializer.data.get('is_setup'),
            'is_registered':serializer.data.get('is_registered'),
            'is_active':serializer.data.get('is_active'),
            'is_admin':serializer.data.get('is_admin'),
            'country_code':serializer.data.get('country_code'),
            'is_subscribed':serializer.data.get('is_subscribed'),
            'settings_id':settings
        }
        header = {
            "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
        }
        LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True, "message":"Fetch UserData Successfully"}), email=serializer.data.get('email'), status=True)
        return Response({"status":True, "message":"Fetch UserData Successfully", "data":user_profile}, status=status.HTTP_200_OK)
    
    def put(self, request, format=None):
        country = ''
        birthdate = ''
        profile_pic = ''
        subscription_id = ''
        social_id = ''
        device_token = ''
        try:
            user = User.objects.get(email=request.user)
        except User.DoesNotExist:
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps({"HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']}), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":"User Detail Doesn't Exist"}), email=request.user, status=False)
            return Response({"status":False, "message":"User Detail Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        
        if (('subscription' in request.data and request.data['subscription'] != "") and ('is_subscribed' in request.data and request.data['is_subscribed'] != False)):
            try:
                request.data['subscription'] = Subscription.objects.get(id=str(request.data['subscription'])).id
            except Subscription.DoesNotExist:
                return Response({"status":False, "message":"plan with id %s does not exist"%(request.data['subscription'])})
        
        serializer = UserProfileSerializer(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            if user.profile_pic != "" and request.FILES:
                profile = str(user.profile_pic).replace("%40", "@")
                fs = FileSystemStorage()
                fs.delete(profile)
            serializer.save()
            if serializer.data.get('country') != '':
                country = serializer.data.get('country')
            else:
                country = None
    
            if serializer.data.get('birthdate') != '':
                birthdate = serializer.data.get('birthdate')
            else:
                birthdate = None
        
            if serializer.data.get('profile_pic') != None:
                profile_pic = request.build_absolute_uri(serializer.data.get('profile_pic'))
                profile_pic = profile_pic.replace("%40", "@")
            else:
                profile_pic = None
    
            if serializer.data.get('subscription') != '':
                subscription_id = serializer.data.get('subscription')
            else:
                subscription_id = None
    
            if serializer.data.get('social_id') != '':
                social_id = serializer.data.get('social_id')
            else:
                social_id = None
    
            if serializer.data.get('device_token') != '':
                device_token = serializer.data.get('device_token')
            else:
                device_token = None
    
            try:
                settings = Setting.objects.get(user_id=str(serializer.data.get('id'))).id
            except Setting.DoesNotExist:
                settings = "setting detail not found"
            
            serializer = {
                'id':serializer.data.get('id'),
                'firstname':serializer.data.get('firstname'),
                'lastname':serializer.data.get('lastname'),
                'email':serializer.data.get('email'),
                'mobile':serializer.data.get('mobile'),
                'gender':serializer.data.get('gender'),
                'country':country,
                'birthdate':birthdate,
                'is_agree':serializer.data.get('is_agree'),
                'registered_by':serializer.data.get('registered_by'),
                'profile_pic':profile_pic,
                'subscription_id':subscription_id,
                'social_id':social_id,
                'device_token':device_token,
                'is_verified':serializer.data.get('is_verified'),
                'setupcount':int(serializer.data.get('setup_count')),
                'is_setup':serializer.data.get('is_setup'),
                'is_registered':serializer.data.get('is_registered'),
                'is_active':serializer.data.get('is_active'),
                'is_admin':serializer.data.get('is_admin'),
                'country_code':serializer.data.get('country_code'),
                'is_subscribed':serializer.data.get('is_subscribed'),
                'settings_id':settings
            }
            if 'profile_pic' in request.data:
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps({"HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']}), request_data=json.dumps({"profile_pic":request.data.get("profile_pic").name}), response_data=json.dumps({"status":True, "message":"Upload Profile Successfully"}), email=request.user, status=True)
                return Response({"status":True, "message":"Upload Profile Successfully", "data":serializer}, status=status.HTTP_200_OK)
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps({"HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']}), request_data=json.dumps(request.data), response_data=json.dumps({"status":True, "message":"update data Successfully"}), email=request.user, status=True)
            return Response({"status":True, "message":"update data Successfully", "data":serializer}, status=status.HTTP_200_OK)
        else:
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps({"HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']}), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":serializer.errors}), email=request.user, status=False)
            return Response({"status":False, "message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)    
# User Profile API Code End #

# User Change Password Code Start #
class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def post(self, request, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'status':True, 'message':'Password Changed Successfully'}, status=status.HTTP_200_OK)
        return Response({'status':False, 'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
# User Change Password Code End #

# Admin Subscription API Code Start #           Done with logs
class AdminSubscriptionView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ''    
        try:
            serializer = Subscription.objects.get(name=request.data['name'])
        except Subscription.DoesNotExist:
            pass

        if serializer is not None and serializer != "":
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":"Plan name already exist"}), email=request.user, status=False)
            return Response({"status":False, "message":"Plan name already exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSubscriptionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":True, "message":"Subscription Plan Created Successfully", "data":serializer.data}), email=request.user, status=True)
            return Response({"status":True, "message":"Subscription Plan Created Successfully", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            message = ''
            if 'name' in serializer.errors and serializer.errors['name'][0] == 'This field may not be blank.':
                message = "please provide plan name"
            elif 'amount' in serializer.errors:
                message = "amount cannot be blank and must be double max_length 15 digit."
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":message}), email=request.user, status=False)
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        if pk is not None and pk != "":
            try:
                subscription_data = Subscription.objects.get(id=pk)
            except Subscription.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":"Plan Detail Doesn't Exist"}), email=request.user, status=False)
                return Response({"status":False, "message":"Plan Detail Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = UserSubscriptionSerializer(subscription_data, data=request.data)
            if serializer.is_valid(raise_exception=False):
                serializer.save()
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":True, "message":"update data Successfully", "data":serializer.data}), email=request.user, status=True)
                return Response({"status":True, "message":"update data Successfully", "data":serializer.data}, status=status.HTTP_200_OK)
            else:
                message = ''
                if 'name' in serializer.errors:
                    message = "plan name cannot be blank"
                elif 'amount' in serializer.errors:
                    message = "plan amount cannot be blank"
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":serializer.errors}), email=request.user, status=False)
                return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":"Please Enter plan id in url/<id>"}), email=request.user, status=False)
            return Response({"status":False, "message":"Please Enter plan id in url/<id>"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        subscription_data = ''
        try:
            subscription_data = Subscription.objects.all()
        except Subscription.DoesNotExist:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"Subscription Plans Doesn't Exist"}), email=request.user, status=False)
            return Response({"status":False, "message":"Subscription haven't any plans"}, status=status.HTTP_404_NOT_FOUND)
        
        if pk is not None and pk != "":
            subscription_data = Subscription.objects.filter(id=pk)
            if len(subscription_data) <= 0: 
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"Subscription Plans Doesn't Exist"}), email=request.user, status=False)
                return Response({"status":False, "message":"Subscription Plans Doesn't Exist with id %s"%(pk)}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSubscriptionSerializer(subscription_data, many=True)
        header = {
            "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
        }
        LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True, "message":"Retrieve data Successfully", "data":serializer.data}), email=request.user, status=True)
        return Response({"status":True, "message":"Retrieve data Successfully", "data":serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        if pk is not None and pk != "":
            try:
                subscription_data = Subscription.objects.get(id=pk)
            except Subscription.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"Plan Detail Doesn't Exist"}), email=request.user, status=False)
                return Response({"status":False, "message":"Plan Detail Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
            
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            
            subscription_data.delete()
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True, "message":"delete plan with plan id %s Successfully"%(pk)}), email=request.user, status=True)
            return Response({"status":True, "message":"delete plan with plan id "+pk+" Successfully"}, status=status.HTTP_200_OK)
        else:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"Please Enter plan id in url/<id>"}), email=request.user, status=False)
            return Response({"status":False, "message":"Please enter plan id in url/<id>"}, status=status.HTTP_400_BAD_REQUEST)
# Admin Subscription API Code End #

# User Subscription API Code Start #            Done with logs          
class UserSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            subscription_data = Subscription.objects.all()
        except Subscription.DoesNotExist:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"Subscription Plans Doesn't Exist"}), email=request.user, status=False)
            return Response({"status":False, "message":"Subscription Plans Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            user_subscribed = User.objects.get(email=request.user).subscription
        except User.DoesNotExist:
            return Response({"status":False, "message":"User is not subscribed yet"}, status=status.HTTP_400_BAD_REQUEST)
        

        serializer = UserSubscriptionSerializer(subscription_data, many=True)

        user_subscribed = UserSubscriptionSerializer(user_subscribed, many=False)

        header = {
            "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
        }

        data = {
            "plans":serializer.data,
            "subscribed":user_subscribed.data
        }
        LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True, "message":"Retrieve data Successfully", "data":data}), email=request.user, status=True)
        return Response({"status":True, "message":"Retrieve data Successfully", "data":data}, status=status.HTTP_200_OK)
# User Subscription API Code End #

# User Income API Code Start #
class IncomeCreate(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = IncomeSerializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=True):
            if (('is_setup'in request.data and request.data['is_setup'] != "") and ('setupcount' in request.data and request.data['setupcount'] != "")):
                User.objects.filter(email=request.user).update(is_setup=request.data['is_setup'], setup_count=request.data['setupcount'])
            serializer.save()
            return Response({"status":True, "message":"Add Income Successfully", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            message = ""
            if 'amount' in serializer.errors:
                message = "please enter valid anount in double max_langth 15 digit."
            if 'title' in serializer.errors:
                message = "title cannot be blank must and it's required field."
            if 'icon' in serializer.errors:
                message = "icon cannot be blank."
            return Response({'status':False, 'message':message}, status=status.HTTP_400_BAD_REQUEST)  

    def get(self, request):
        user = request.user
        if user is not None:
            Incomes = Income.objects.filter(user=user)
            
        Incomeserializer = IncomeSerializer(Incomes, many=True)
        return Response({"status":True, "message":"Retrieve data Successfully", "data":Incomeserializer.data}, status=status.HTTP_200_OK)   

class IncomeDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Income.objects.get(pk=pk)
        except Income.DoesNotExist:
             return Response({"status":False, "message":"Income Detail Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)

        
    def get(self, request, pk, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            income = Income.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'income data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = IncomeSerializer(income)
        return Response({"status":True, "message":"Retrieve data Successfully", "data":serializer.data}, status=status.HTTP_200_OK) 


    def put(self,request,pk,format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        

        # income = self.get_object(id=pk, user_id=str(user.id))
        try:
            income = Income.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'income data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = IncomeSerializer(income, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":True, "message":"update data Successfully", "data":serializer.data}, status=status.HTTP_200_OK)
        else:
            message = ""
            if 'amount' in serializer.errors:
                message = "please enter valid anount in double max_langth 15 digit."
            if 'title' in serializer.errors:
                message = "title cannot be blank must and it's required field."
            if 'icon' in serializer.errors:
                message = "icon cannot be blank."
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)  

    def delete(self,request,pk):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        

        # income = self.get_object(id=pk, user_id=str(user.id))
        try:
            income = Income.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'income data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        ### Fetch All Transaction ###
        transactions = Transaction.objects.filter(income_from_id=income.id)
        for x in transactions:
            if x.income_to_id is not None:
                income_to_data = Income.objects.filter(id=x.income_to_id)
                update_amount = float(income_to_data[0].amount) - float(x.amount)
                income_to_data.update(amount=update_amount)

            if x.expense_id is not None:
                expense = Expense.objects.filter(id=x.expense_id)
                update_amount = float(expense[0].amount_limit) - float(x.amount)
                expense.update(amount_limit=update_amount)

            if x.goal_id is not None:
                goal_data = Goal.objects.filter(id=x.goal_id)
                update_amount = float(goal_data[0].amount) - float(x.amount)
                goal_data.update(amount=update_amount)

            if x.location_id is not None:
                location_data = Location.objects.filter(id=x.location_id)
                location_data.delete()
            
            if x.periodic_id is not None:
                periodic_data = Periodic.objects.filter(id=x.periodic_id)
                periodic_data.delete()

        transactions = Transaction.objects.filter(income_to_id=income.id)
        for x in transactions:
            if x.source_id is not None:
                source_data = SourceIncome.objects.filter(id=x.source_id)
                update_amount = float(source_data[0].amount) + float(x.amount)
                source_data.update(amount=update_amount)
            
            if x.location_id is not None:
                location_data = Location.objects.filter(id=x.location_id)
                location_data.delete()
            
            if x.periodic_id is not None:
                periodic_data = Periodic.objects.filter(id=x.periodic_id)
                periodic_data.delete()
        
        income.delete()
        return Response({"status":True,"message":"Data was successfully delete"}, status=status.HTTP_200_OK)
# User Income API Code End #  

# User Expens API Code start # 
class ExpenseCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ExpenseSerializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=True):
            if (('setupcount' in request.data and request.data['setupcount'] != "")):
                User.objects.filter(email=request.user).update(setup_count=request.data['setupcount'])
            serializer.save()
            return Response({"status":True, "message":"Add Expense Successfully", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            message = ""
            if 'amount_limit' in serializer.errors:
                message = "please enter valid anount_limit in double max_langth 15 digit."
            if 'title' in serializer.errors:
                message = "title cannot be blank must and it's required field."
            if 'icon' in serializer.errors:
                message = "icon cannot be blank."
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)  

    def get(self, request):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if user is not None:
            Expenses = Expense.objects.filter(user=user)
            
        Expenseserializer = ExpenseSerializer(Expenses, many=True)
        return Response({"status":True, "message":"Retrieve data Successfully", "data":Expenseserializer.data}, status=status.HTTP_200_OK)   

class ExpenseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Expense.objects.get(pk=pk)
        except Expense.DoesNotExist:
             return Response({"status":False, "message":"Expense Detail Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
       
    def get(self, request, pk, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        

        # income = self.get_object(id=pk, user_id=str(user.id))
        try:
            expense = Expense.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'Expense data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ExpenseSerializer(expense)
        return Response({"status":True, "message":"Retrieve data Successfully", "data":serializer.data}, status=status.HTTP_200_OK)   

    def put(self,request,pk,format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        

        # income = self.get_object(id=pk, user_id=str(user.id))
        try:
            expense = Expense.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'Expense data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ExpenseSerializer(expense,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":True, "message":"update data Successfully", "data":serializer.data}, status=status.HTTP_200_OK)
        else:
            message = ""
            if 'amount_limit' in serializer.errors:
                message = "please enter valid anount_limit in double max_langth 15 digit."
            if 'title' in serializer.errors:
                message = "title cannot be blank must and it's required field."
            if 'icon' in serializer.errors:
                message = "icon cannot be blank."
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST) 

    def delete(self,request,pk):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        

        # income = self.get_object(id=pk, user_id=str(user.id))
        try:
            expense = Expense.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'Expense data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        ### Fetch All Transaction ###
        transactions = Transaction.objects.filter(expense_id=expense.id)
        for x in transactions:
            if x.income_from_id is not None:
                income_from_id_data = Income.objects.filter(id=x.income_from_id)
                update_amount = float(income_from_id_data[0].amount) + float(x.amount)
                income_from_id_data.update(amount=update_amount)
            
            if x.location_id is not None:
                location_data = Location.objects.filter(id=x.location_id)
                location_data.delete()
            
            if x.periodic_id is not None:
                periodic_data = Periodic.objects.filter(id=x.periodic_id)
                periodic_data.delete()
        
        expense.delete()
        return Response({"status":True,"message":"Data was successfully delete"},status=status.HTTP_200_OK)      
# User Expens API Code End # 

# User Expens API Code start #
class GoalsCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = GoalsSerializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=True):
            if (('setupcount' in request.data and request.data['setupcount'] != "")):
                User.objects.filter(email=request.user).update(setup_count=request.data['setupcount'])
            serializer.save()
            return Response({"status":True, "message":"Add Goal Successfully", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            message = ""
            if 'amount' in serializer.errors:
                message = "please enter valid anount_limit in double max_langth 15 digit."
            if 'title' in serializer.errors:
                message = "title cannot be blank must and it's required field."
            if 'icon' in serializer.errors:
                message = "icon cannot be blank."
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)  

    def get(self, request):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if user is not None:
            goals = Goal.objects.filter(user=user)
            
        Goalsserializer = GoalsSerializer(goals, many=True)
        return Response({"status":True, "message":"Retrieve data Successfully", "data":Goalsserializer.data}, status=status.HTTP_200_OK)   

class GoalsDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Goal.objects.get(pk=pk)
        except Goal.DoesNotExist:
             return Response({"status":False,"message": "The data does not exist"}, status=status.HTTP_404_NOT_FOUND)

        
    def get(self, request, pk, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        

        # income = self.get_object(id=pk, user_id=str(user.id))
        try:
            Goals = Goal.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'Goal data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = GoalsSerializer(Goals)
        return Response({"status":True, "message":"Retrieve data Successfully", "data":serializer.data}, status=status.HTTP_200_OK)   


    def put(self,request,pk,format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        

        # income = self.get_object(id=pk, user_id=str(user.id))
        try:
            Goals = Goal.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'Goal data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = GoalsSerializer(Goals,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":True, "message":"update data Successfully", "data":serializer.data}, status=status.HTTP_200_OK)
        else:
            message = ""
            if 'amount' in serializer.errors:
                message = "please enter valid anount_limit in double max_langth 15 digit."
            if 'title' in serializer.errors:
                message = "title cannot be blank must and it's required field."
            if 'icon' in serializer.errors:
                message = "icon cannot be blank."
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)  


    def delete(self,request,pk):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        

        # income = self.get_object(id=pk, user_id=str(user.id))
        try:
            Goals = Goal.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'Goal data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        ### Fetch All Transaction ###
        transactions = Transaction.objects.filter(goal_id=Goals.id)
        for x in transactions:

            if x.income_from_id is not None:
                income_data = Income.objects.filter(id=x.income_from_id)
                update_amount = float(income_data[0].amount) + float(x.amount)
                income_data.update(amount=update_amount)

            if x.location_id is not None:
                location_data = Location.objects.filter(id=x.location_id)
                location_data.delete()
            
            if x.periodic_id is not None:
                periodic_data = Periodic.objects.filter(id=x.periodic_id)
                periodic_data.delete()
        
        Goals.delete()
        return Response({"status":True,"message":"Data was successfully delete"}, status=status.HTTP_200_OK)      
# User Expens API Code End # 

# User SourceIncome Serializer Code Start # 
class SourceIncomeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request , format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SourceIncomeSerializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response({"status":True, "message":"source income created", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            message = ""
            if 'amount' in serializer.errors:
                message = "please enter valid anount_limit in double max_langth 15 digit."
            if 'title' in serializer.errors:
                message = "title cannot be blank must and it's required field."
            if 'icon' in serializer.errors:
                message = "icon cannot be blank."
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if user is not None:
            sourceincome = SourceIncome.objects.filter(user=user)
            
        sourceincomeserializer = SourceIncomeSerializer(sourceincome, many=True)
        return Response({"status":True, "message":"get all source income data", "data":sourceincomeserializer.data}, status=status.HTTP_200_OK)
        
class SourceIncomeDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return SourceIncome.objects.get(pk=pk)
        except SourceIncome.DoesNotExist:
            return Response({'message': 'The data does not exist'}, status=status.HTTP_404_NOT_FOUND)

        
    def get(self, request,pk, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            sourceincome = SourceIncome.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'sourceincome data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SourceIncomeSerializer(sourceincome)
        return Response({"status":True, "message":"Retrieve data Successfully", "data":serializer.data}, status=status.HTTP_200_OK)


    def put(self,request,pk,format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=str(request.user)).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            sourceincome = SourceIncome.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'sourceincome data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SourceIncomeSerializer(sourceincome,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":True, "data":serializer.data}, status=status.HTTP_200_OK)
        else:
            message = ""
            if 'amount' in serializer.errors:
                message = "please enter valid anount_limit in double max_langth 15 digit."
            if 'title' in serializer.errors:
                message = "title cannot be blank must and it's required field."
            if 'icon' in serializer.errors:
                message = "icon cannot be blank."
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)  

    def delete(self,request,pk):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = request.user
            if user is not None:
                sourceincome = SourceIncome.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'sourceincome data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        ### Fetch All Transaction ###
        transactions = Transaction.objects.filter(source_id=sourceincome.id)
        for x in transactions:
            if x.income_to_id is not None:
                income_to_id_data = Income.objects.filter(id=x.income_to_id)
                update_amount = float(income_to_id_data[0].amount) - float(x.amount)
                income_to_id_data.update(amount=update_amount)
        
        sourceincome.delete()
        return Response({"status":True,"message":"Data was successfully delete"}, status=status.HTTP_200_OK) 
# User SourceIncome Serializer Code end #

# User Exchange API Code Start#                 Done with logs
class ExchangerateCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
           user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":"User doesn't exist"}), email=request.user, status=False)
            return Response({"status":False, "message":"User doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ''
        try:
            serializer = Exchangerate.objects.get(currency_name=request.data["currency_name"], user_id=user)
        except Exchangerate.DoesNotExist:
            pass
        
        if serializer != '':
            return Response({"status":False, "message":"you can't add same currency.Please select another one."})

        serializer = ExchangerateSerializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":True, "message":"Exchangerate created successfully", "data":serializer.data}), email=request.user, status=True)
            return Response({"status":True, "message":"Exchangerate created successfully", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            message = ''
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            if 'currency_name' in serializer.errors:
                message = "currency_name cannot be blank"
            
            if 'is_default' in serializer.errors:
                message = "Provide either true or false for is_default"
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False, "message":message}), email=request.user, status=False)
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        exchangerate = ''
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header),  response_data=json.dumps({"status":False, "message":"User doesn't exist"}), email=request.user, status=False)
            return Response({"status":False, "message":"User doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            exchangerate = Exchangerate.objects.filter(user=user)
        except Exchangerate.DoesNotExist:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header),  response_data=json.dumps({"status":False, "message":"user have not any Exchangerate data"}), email=request.user, status=False)
            return Response({"status":False, "message":"user have not any currency data"}, status=status.HTTP_404_NOT_FOUND)
        
        if pk is not None and pk != '':
            exchangerate = Exchangerate.objects.filter(user=user, id=pk)
            if len(exchangerate) <= 0:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False,"message":"Currency with id %s not found"%(pk)}), email=request.user, status=False)
                return Response({"status":False, "message":"Currency with id %s not found"%(pk)}, status=status.HTTP_404_NOT_FOUND)
        

        exchangerate_serializer = ExchangerateSerializer(exchangerate, many=True)
        header = {
            "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
        }
        LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True,"message":"Exchangerate data Fetched Succcessfully"}), email=request.user, status=True)
        return Response({"status":True, "message":"Exchangerate data Fetched Succcessfully", "data":exchangerate_serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        exchangerate = ''
        if pk is not None and pk != '':
            try:
                user = User.objects.get(email=request.user).id
            except User.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False,"message":"user not found"}), email=request.user, status=False)
                return Response({"status":False, "message":"user not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                exchangerate = Exchangerate.objects.get(user=user, id=pk)
            except Exchangerate.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False,"message":"currency with id %s not found"%(pk)}), email=request.user, status=False)
                return Response({"status":False, "message":"currency with id %s not found"%(pk)}, status=status.HTTP_404_NOT_FOUND)
        else:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False,"message":"provide Exchangerate id in url/<id>"}), email=request.user, status=False)
            return Response({"status":False, "message":"provide Exchangerate id in url/<id>"},status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ExchangerateSerializer(exchangerate, data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":True,"message":"update Exchangerate data successfully"}), email=request.user, status=True)
            return Response({"status":True,"message":"update Exchangerate data successfully", "data":serializer.data}, status=status.HTTP_200_OK)
        else:
            
            message = ''
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            if ('currency_name' in serializer.errors):
                message = "currency name can't be blank"  

            if 'is_default' in serializer.errors:
                message = "Provide either true or false for is_default"                   

            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":False,"message":message}), email=request.user, status=False)
            return Response({"status":False, "message":message},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        exchangerate = ''        
        if pk is not None and pk != '':
            try:
                user = User.objects.get(email=request.user).id
            except User.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False,"message":"user not found"}), email=request.user, status=False)
                return Response({"status":False, "message":"user not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                exchangerate = Exchangerate.objects.get(user=user, id=pk)
            except Exchangerate.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False,"message":"currency with id %s not found"%(pk)}), email=request.user, status=False)
                return Response({"status":False, "message":"currency with id %s not found"%(pk)}, status=status.HTTP_400_BAD_REQUEST)
        
            exchangerate.delete()
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True,"message":"currency with id %s was successfully delete"%(pk)}), email=request.user, status=True)
            return Response({"status":True, "message":"currency with id %s was successfully delete"%(pk)}, status=status.HTTP_200_OK)     
        else:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False,"message":"provide currency id in url/<id>"}), email=request.user, status=False)
            return Response({"status":False, "message":"provide currency id in url/<id>"},  status=status.HTTP_400_BAD_REQUEST)    
# User Exchange API Code end#

# User location API Code Start#
class LocationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Location.objects.get(pk=pk)
        except Location.DoesNotExist:
             return Response({"status":False, "message":"location Detail Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)

        
    def get(self, request, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=str(request.user)).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            trans = Transaction.objects.get(user_id=user, id=request.data.get('transaction_id'))
        except Transaction.DoesNotExist:
            return Response({'status':False, 'message':'transaction data not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            location = Location.objects.get(id=trans.location_id)
        except Location.DoesNotExist:
            return Response({'status':False, 'message':'LOCATION data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        serializer = LocationSerializer(location)
        return Response({"status":True,"message":"fetch data successfully", "data":serializer.data}, status=status.HTTP_200_OK)
# User location API Code end#

# User periodic API Code Start#
class PeriodicDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Periodic.objects.get(pk=pk)
        except Periodic.DoesNotExist:
             return Response({"status":False, "message":"periodic Detail Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)

        
    def get(self, request, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            trans = Transaction.objects.get(user_id=user, id=str(request.data.get('transaction_id')))
        except Transaction.DoesNotExist:
            return Response({'status':False, 'message':'transaction data not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            periodic = Periodic.objects.get(id=trans.periodic_id)
        except Periodic.DoesNotExist:
            return Response({'status':False, 'message':'periodic data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        serializer = PeriodicSerializer(periodic)
        return Response({"status":True,"message":"fetch data successfully", "data":serializer.data}, status=status.HTTP_200_OK)
# User periodic API Code end#

# User setting API Code Start#
class SettingView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if user is not None:
            setting = Setting.objects.filter(user=user)
            
        settingserializer = SettingSerializer(setting, many=True)
        return Response({"status":True, "message":"fetch data successfully", "data":settingserializer.data}, status=status.HTTP_200_OK) 

class SettingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self,request,pk,format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({'status':False, 'message':'user data not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            setting = Setting.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'setting data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SettingSerializer(setting,data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response({"status":True, "message":"update successfully", "data":serializer.data}, status=status.HTTP_200_OK)
        else:
            message = ""
            if 'notification' in serializer.errors:
                message = "notification cannot be blank must be true or false."
            if 'min_pass_3' in serializer.errors:
                message = "min_pass_3 cannot be blank must be true or false."
            if 'language' in serializer.errors:
                message = "language cannot be blank."
            if 'currency' in serializer.errors:
                message = "language cannot be blank."

            return Response({"status":False, "message":message},status=status.HTTP_400_BAD_REQUEST)  
# User setting API Code end#

# Debt View Code Start #
class DebtView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request , format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=str(request.user))
        except:
            return Response({"status":False, "message":"User Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DebtSerializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=False):

            serializer.save()
    
            return Response({"status":True, "message":"created successfully", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            message = ""
            if 'icon' in serializer.errors:
                message = "icon cannot be blank."
            if 'name' in serializer.errors:
                message = "name cannot be blank."
            if 'amount' in serializer.errors:
                message = "amount cannot be blank must be double max_length 15 digit."
            if 'date' in serializer.errors:
                message = "provide valid date yyyy-mm-dd."
            
            return Response({"status":False,  "message":message}, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=str(request.user)).id
        except User.DoesNotExist:
            return Response({"status":False, "message":"user data not found"}, status=status.HTTP_404_NOT_FOUND)

        debt = Debt.objects.filter(user=user)
            
        debtserializer = DebtSerializer(debt, many=True)
        return Response({"status":True, "message":"fetch data successfully", "data":debtserializer.data}, status=status.HTTP_200_OK)

class DebtDetailView(APIView):
    permission_classes = [IsAuthenticated]
        
    def get(self, request,pk, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({"status":False, "message":"User Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            debt = Debt.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'debt data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DebtSerializer(debt)
        return Response({"status":True, "message":"fetch data successfuly", "data":serializer.data}, status=status.HTTP_200_OK)

    def put(self,request,pk,format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=str(request.user)).id
        except User.DoesNotExist:
            return Response({"status":False, "message":"user doesnot exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            debt = Debt.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'debt data not found'}, status=status.HTTP_404_NOT_FOUND)
    
        serializer = DebtSerializer(debt,data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response({"status":True, "message":"Update Debt Successfully", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            message = ""
            if 'icon' in serializer.errors:
                message = "icon cannot be blank."
            if 'name' in serializer.errors:
                message = "name cannot be blank."
            if 'amount' in serializer.errors:
                message = "amount cannot be blank must be double max_length 15 digit."
            if 'date' in serializer.errors:
                message = "provide valid date yyyy-mm-dd."
            
            return Response({"status":False,  "message":message}, status=status.HTTP_400_BAD_REQUEST)  

    def delete(self,request,pk):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=str(request.user)).id
        except User.DoesNotExist:
            return Response({"status":False, "message":"User Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)
        try:
            debt = Debt.objects.get(id=pk, user_id=user)
        except:
            return Response({'status':False, 'message':'debt data not found'}, status=status.HTTP_404_NOT_FOUND)
        
        transactions = Transaction.objects.filter(debt_id=debt.id)
        for x in transactions:

            if x.income_from_id is not None:
                income_data = Income.objects.filter(id=x.income_from_id)
                update_amount = float(income_data[0].amount) + float(x.amount)
                income_data.update(amount=update_amount)

            if x.location_id is not None:
                location_data = Location.objects.filter(id=x.location_id)
                location_data.delete()
            
            if x.periodic_id is not None:
                periodic_data = Periodic.objects.filter(id=x.periodic_id)
                periodic_data.delete()
        
        debt.delete()
        return Response({"status":True, "message":"data was successfully delete"}, status=status.HTTP_200_OK) 
# Debt View Code End #

# Transaction View Code Start #
class TransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,  request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        data_dict = {}
        data = {}
        status_list = []
        if request.data != {}:
            location_serializer = ''
            periodicSerializer = ''
            status_days = ""
            try:
                user = User.objects.get(email=request.user).id
            except User.DoesNotExist:
                return Response({"status":False, "message":"User doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

            if ('longitude' in request.data and 'latitude' in request.data and request.data["longitude"] != 0 and request.data["latitude"] != 0):
                
                data = {
                    "longitude":request.data['longitude'],
                    "latitude":request.data['latitude']
                }  
                location_serializer = LocationSerializer(data=data) 
                if location_serializer.is_valid(raise_exception=True):
                    location_serializer.save()
                else:
                    message = ""
                    if 'latitude' in location_serializer.errors:
                        message = "latitude cannot be blank must be double max_length 15 digit."
                    
                    if 'longitude' in location_serializer.errors:
                        message = "longitude cannot be blank must be double max_length 15 digit."
                    return Response({"status":False, "message":message},status=status.HTTP_400_BAD_REQUEST)   
        
            if ('start_date' in request.data and 'end_date' in request.data and 'prefix' in request.data and 'prefix_value' in request.data and request.data["start_date"] != 0 and request.data["end_date"] != 0 and request.data["prefix"] != 0 and request.data["prefix_value"] != 0):
                if 'week_days' in request.data and request.data["week_days"] != "":
                    dates = []
                    end_date = dt.strptime(str(request.data['end_date']), "%Y-%m-%d").date()
                    if end_date > dt.now().date():
                        Date_List = str(request.data["week_days"]).split(",")
                        for x in Date_List:
                            x_date = dt.strptime(str(x), '%Y-%m-%d').date()
                            if x_date > dt.now().date():
                                dates.append(x)

                        if "" not in dates:        
                            for x in dates:
                                x_date = dt.strptime(str(x), '%Y-%m-%d').date()
                                if x_date > dt.now().date():
                                    x = False
                                    status_list.append(str(x))

                        status_days = ','.join(status_list)
                        week_dates = ','.join(dates)
                        request.data.update({"week_days":week_dates})
                        data = {
                            "start_date":request.data['start_date'],
                            "end_date":request.data['end_date'],
                            "prefix":request.data['prefix'],
                            "prefix_value":request.data['prefix_value'],
                            "week_days":request.data["week_days"],
                            "status_days":status_days
                        }  
                    else:
                        return Response({"status":False, "message":"Recurrence should be prior to the end date"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Changes Server #
                    start_date = None
                    if request.data['start_date'] != "":
                        start_date = request.data['start_date']
                    else:
                        start_date = date.today()

                    if "month" in request.data['prefix'] and request.data['prefix_value'] != 0:
                        end_date = dt.strptime(str(request.data['end_date']), "%Y-%m-%d").date()
                        if end_date > dt.now().date():
                            del status_list[:]
                            Date_Dict = Get_Dates(prefix=request.data['prefix'], prefix_value=int(request.data['prefix_value']), enddate=request.data['end_date'], startdate=start_date)
                            Date_List = Date_Dict["Date_Months"].split(",")
                            
                            for x in Date_List:
                                x_date = dt.strptime(str(x), '%Y-%m-%d').date()
                                if x_date <= dt.now().date():
                                    Date_List.remove(x)

                            if "" not in Date_List:
                                for x in Date_List:
                                    x = False
                                    status_list.append(str(x))
                                status_days = ','.join(status_list)
                            data = {
                                "start_date":start_date,
                                "end_date":request.data['end_date'],
                                "prefix":request.data['prefix'],
                                "prefix_value":request.data['prefix_value'],
                                "week_days":Date_Dict["Date_Months"],
                                "status_days":status_days
                            }
                        else:
                            return Response({"status":False, "message":"Recurrence should be prior to the end date"}, status=status.HTTP_400_BAD_REQUEST)
                    elif "year" in request.data['prefix'] and request.data['prefix_value'] != 0:
                        end_date = dt.strptime(str(request.data['end_date']), "%Y-%m-%d").date()
                        if end_date > dt.now().date():
                            del status_list[:]
                            Date_Dict = Get_Dates(prefix=request.data['prefix'], prefix_value=int(request.data['prefix_value']), enddate=request.data['end_date'], startdate=start_date)
                            Date_List = Date_Dict["Date_Years"].split(",")
                            
                            for x in Date_List:
                                x_date = dt.strptime(str(x), '%Y-%m-%d').date()
                                if x_date <= dt.now().date():
                                    Date_List.remove(x)

                            if "" not in Date_List:
                                for x in Date_List:
                                    x = False
                                    status_list.append(str(x))
                                status_days = ','.join(status_list)
                            data = {
                                "start_date":start_date,
                                "end_date":request.data['end_date'],
                                "prefix":request.data['prefix'],
                                "prefix_value":request.data['prefix_value'],
                                "week_days":Date_Dict["Date_Years"],
                                "status_days":status_days
                            }
                        else:
                            return Response({"status":False, "message":"Recurrence should be prior to the end date"}, status=status.HTTP_400_BAD_REQUEST)

                    elif "day" in request.data['prefix'] and request.data['prefix_value'] != 0:
                        end_date = dt.strptime(str(request.data['end_date']), "%Y-%m-%d").date()
                        if end_date > dt.now().date():
                            del status_list[:]
                            Date_Dict = Get_Dates(prefix=request.data['prefix'], prefix_value=int(request.data['prefix_value']), enddate=request.data['end_date'], startdate=start_date)
                            Date_List = Date_Dict["Date_Days"].split(",")
                           
                            for x in Date_List:
                                x_date = dt.strptime(str(x), '%Y-%m-%d').date()
                                if x_date <= dt.now().date():
                                    Date_List.remove(x)
                            
                            if "" not in Date_List:
                                for x in Date_List:
                                    x = False
                                    status_list.append(str(x))
                                status_days = ','.join(status_list)
                            data = {
                                "start_date":start_date,
                                "end_date":request.data['end_date'],
                                "prefix":request.data['prefix'],
                                "prefix_value":request.data['prefix_value'],
                                "week_days":Date_Dict["Date_Days"],
                                "status_days":status_days
                            }
                        else:
                            return Response({"status":False, "message":"Recurrence should be prior to the end date"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"status":False, "message":"prefix_value cannot be blank must be integer"}, status=status.HTTP_400_BAD_REQUEST)
                # Changes on server # 
                start_date = dt.strptime(str(data["start_date"]), "%Y-%m-%d").date()
                end_date = dt.strptime(str(data["end_date"]), "%Y-%m-%d").date()
                
                if end_date > start_date and data['week_days'] != "" and data["status_days"] != "":
                    periodicSerializer = PeriodicSerializer(data=data) 
                    if periodicSerializer.is_valid(raise_exception=False):
                        periodicSerializer.save()
                    else:
                        message = ""
                        if 'start_date' in periodicSerializer.errors:
                            message = "provide valid date yyyy-mm-dd."
                        if 'end_date' in periodicSerializer.errors:
                            message = "provide valid date yyyy-mm-dd."
                        if 'week_days' in periodicSerializer.errors:
                            message = "week_days cannot be blank and must be comma saparated string like 2022-07-12,2022-07-13."
                        if 'prefix' in periodicSerializer.errors:
                            message = "prefix cannot be blank must be string choice like day,month,year,week."
                        if 'prefix_value' in periodicSerializer.errors:
                            message="prefix_value must be integer."
                        if 'status_days' in periodicSerializer.errors:
                            message = "status_days cannot be blank must be comma saparated string like false,false,false."
                        return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)

            if (('amount' in request.data and 'source' in request.data and 'income_to' in request.data) and ('income_from' not in request.data) and ('expense' not in request.data) and ('goal' not in request.data)):
                if (request.data["amount"] != "" and request.data["source"] != ""  and request.data["income_to"] != ""):
                    if 'title' not in request.data or request.data['title'] == "":
                        title = None
                    else:
                        title = request.data['title']

                    if 'description' not in request.data or request.data['description'] == "":
                        description = None
                    else:
                        description = request.data['description']

                    try:
                        source = SourceIncome.objects.get(user_id=user, id=str(request.data["source"]))
                    except SourceIncome.DoesNotExist:
                        return Response({"status":False, "message":"User haven't any source income by id %s"%(request.data["source"])}, status=status.HTTP_404_NOT_FOUND)
                    
                    try:
                        income = Income.objects.get(user_id=user, id=str(request.data["income_to"]))
                    except Income.DoesNotExist:
                        return Response({"status":False, "message":"User haven't any income by id %s"%(request.data["income_to"])}, status=status.HTTP_404_NOT_FOUND)
                    
                    source_amount = float(source.spent_amount) + float(request.data["amount"])
                    income_amount = float(income.amount) + float(request.data["amount"])

                    if location_serializer != "" and periodicSerializer == "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "source":source.id,
                            "income_to":income.id,
                            "location":location_serializer.data.get('id')
                        }
                    elif location_serializer == "" and periodicSerializer != "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "source":source.id,
                            "income_to":income.id,
                            "periodic":periodicSerializer.data.get('id')
                        }
                    elif location_serializer != "" and periodicSerializer != "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "source":source.id,
                            "income_to":income.id,
                            "location":location_serializer.data.get('id'),
                            "periodic":periodicSerializer.data.get('id')
                        }
                    else:
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "source":source.id,
                            "income_to":income.id
                        }

                    if 'tags' in request.data and request.data["tags"] != []:
                        data_dict.update({"tag":request.data["tags"]})

                    if 'created_at' in request.data and "modified_at" in request.data:
                        data_dict.update({"created_at":request.data["created_at"]})
                        data_dict.update({"modified_at":request.data["modified_at"]})

                    if 'is_completed' in request.data:
                        data_dict.update({"is_completed":request.data["is_completed"]})
                    
                    transaction_serializer = TransactionSerializer(data=data_dict, context={"user":user})
                    if transaction_serializer.is_valid(raise_exception=False):
                        transaction_id = transaction_serializer.save()
                        if len(str(transaction_id)) > 0 and transaction_id is not None:
                            SourceIncome.objects.filter(title=source.title, id=source.id, user_id=user).update(spent_amount=source_amount)
                            Income.objects.filter(title=income.title, id=income.id, user_id=user).update(amount=income_amount)
                        else:
                            return Response({"status":False, "message":" transaction fail from Source %s to Income %s"%(source.title, income.title)}, status=status.HTTP_400_BAD_REQUEST)
                        # changes on server #
                        transaction_dict = transaction_serializer.data
                        transaction_dict["income_to_name"] = income.title
                        transaction_dict["source_name"] = source.title

                        if periodicSerializer != "" and location_serializer == "":
                            transaction_dict.update({"periodic":periodicSerializer.data})
                        elif periodicSerializer == "" and location_serializer != "":
                            transaction_dict.update({"location":location_serializer.data})
                        elif periodicSerializer != "" and location_serializer != "":
                            transaction_dict.update({"periodic":periodicSerializer.data})
                            transaction_dict.update({"location":location_serializer.data})
                       
                        # changes on server #
                        return Response({"status":True, "message":"Transfer amount from source %s to income %s"%(source.title, income.title), "data":transaction_dict}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"status":False, "message":transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"status":False, "message":"amount, income_to, source are required fields. title and description is optional"}, status=status.HTTP_400_BAD_REQUEST)

            elif (('amount' in request.data and 'income_from' in request.data and 'income_to' in request.data) and ('source' not in request.data) and ('expense' not in request.data) and ('goal' not in request.data)):
                if (request.data["amount"] != "" and request.data["income_from"] != "" and request.data["income_to"] != ""):
                    
                    if 'title' not in request.data or request.data['title'] == "":
                        title = None
                    else:
                        title = request.data['title']

                    if 'description' not in request.data or request.data['description'] == "":
                        description = None
                    else:
                        description = request.data['description']
                    
                    try:
                        income_from = Income.objects.get(user_id=user, id=str(request.data['income_from']))
                    except Income.DoesNotExist:
                        return Response({"status":False, "message":"From Income detail not found by id %s"%(request.data['income_from'])}, status=status.HTTP_404_NOT_FOUND)

                    try:
                        income_to = Income.objects.get(user_id=user, id=str(request.data['income_to']))
                    except Income.DoesNotExist:
                        return Response({"status":False, "message":"To Income detail not found by id %s"%(request.data['income_to'])}, status=status.HTTP_404_NOT_FOUND)

                    income_from_amount = float(income_from.amount) - float(request.data["amount"])
                    income_to_amount = float(income_to.amount) + float(request.data["amount"])

                    if location_serializer != "" and periodicSerializer == "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income_from.id,
                            "income_to":income_to.id,
                            "location":location_serializer.data.get('id')
                        }
                    elif location_serializer == "" and periodicSerializer != "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income_from.id,
                            "income_to":income_to.id,
                            "periodic":periodicSerializer.data.get('id')
                        }
                    elif location_serializer != "" and periodicSerializer != "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income_from.id,
                            "income_to":income_to.id,
                            "location":location_serializer.data.get('id'),
                            "periodic":periodicSerializer.data.get('id')
                        }
                    else:
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income_from.id,
                            "income_to":income_to.id
                        }

                    if 'tags' in request.data and request.data["tags"] != []:
                        data_dict.update({"tag":request.data["tags"]})

                    if 'created_at' in request.data and "modified_at" in request.data:
                        data_dict.update({"created_at":request.data["created_at"]})
                        data_dict.update({"modified_at":request.data["modified_at"]})
                        
                    if 'is_completed' in request.data:
                        data_dict.update({"is_completed":request.data["is_completed"]})
                
                    transaction_serializer = TransactionSerializer(data=data_dict, context={"user":user})
                    if transaction_serializer.is_valid(raise_exception=False):
                        transaction_id = transaction_serializer.save()
                        if len(str(transaction_id)) > 0 and transaction_id is not None:
                            Income.objects.filter(title=income_from.title, id=income_from.id, user_id=user).update(amount=income_from_amount)
                            Income.objects.filter(title=income_to.title, id=income_to.id, user_id=user).update(amount=income_to_amount)
                        else:
                            return Response({"status":False, "message":" transaction fail from Income %s to Income %s"%(income_from.title, income_to.title)}, status=status.HTTP_400_BAD_REQUEST)
                        
                        # changes on server #
                        transaction_dict = transaction_serializer.data
                        transaction_dict["income_from_name"] = income_from.title
                        transaction_dict["income_to_name"] = income_to.title

                        if periodicSerializer != "" and location_serializer == "":
                            transaction_dict.update({"periodic":periodicSerializer.data})
                        elif periodicSerializer == "" and location_serializer != "":
                            transaction_dict.update({"location":location_serializer.data})
                        elif periodicSerializer != "" and location_serializer != "":
                            transaction_dict.update({"periodic":periodicSerializer.data})
                            transaction_dict.update({"location":location_serializer.data})
                        # changes on server #
                        return Response({"status":True, "message":"Transfer amount from Income %s to Income %s"%(income_from.title, income_to.title), "data":transaction_dict}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"status":False, "message":transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"status":False, "message":"amount, income_from, income_to are required fields. title and description is optional"}, status=status.HTTP_400_BAD_REQUEST)
            
            elif (('amount' in request.data and 'income_from' in request.data and 'goal' in request.data) and ('source' not in request.data) and ('expense' not in request.data) and ('income_to' not in request.data)): 
                if (request.data["amount"] != "" and request.data["income_from"] != "" and request.data["goal"] != ""):
                    
                    if 'title' not in request.data or request.data['title'] == "":
                        title = None
                    else:
                        title = request.data['title']

                    if 'description' not in request.data or request.data['description'] == "":
                        description = None
                    else:
                        description = request.data['description']
                    
                    try:
                        income = Income.objects.get(user_id=user, id=str(request.data["income_from"]))
                    except Income.DoesNotExist:
                        return Response({"status":False, "message":"Income detail not found by id %s"%(request.data["income_from"])}, status=status.HTTP_404_NOT_FOUND)

                    try:
                        goal = Goal.objects.get(user_id=user, id=str(request.data["goal"]))
                    except Goal.DoesNotExist:
                        return Response({"status":False, "message":"Goal detail not found by id %s"%(request.data["goal"])}, status=status.HTTP_404_NOT_FOUND)

                    income_amount = float(income.amount) - float(request.data["amount"])
                    goal_amount = float(goal.added_amount) + float(request.data["amount"])

                    if location_serializer != "" and periodicSerializer == "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "goal":goal.id,
                            "location":location_serializer.data.get('id')
                        }
                    elif location_serializer == "" and periodicSerializer != "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "goal":goal.id,
                            "periodic":periodicSerializer.data.get('id')
                        }
                    elif location_serializer != "" and periodicSerializer != "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "goal":goal.id,
                            "location":location_serializer.data.get('id'),
                            "periodic":periodicSerializer.data.get('id')
                        }
                    else:
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "goal":goal.id
                        }

                    if 'tags' in request.data and request.data["tags"] != []:
                        data_dict.update({"tag":request.data["tags"]})

                    if 'created_at' in request.data and "modified_at" in request.data:
                        data_dict.update({"created_at":request.data["created_at"]})
                        data_dict.update({"modified_at":request.data["modified_at"]})
                        
                    if 'is_completed' in request.data:
                        data_dict.update({"is_completed":request.data["is_completed"]})

                    transaction_serializer = TransactionSerializer(data=data_dict, context={"user":user})
                    if transaction_serializer.is_valid(raise_exception=False):
                        if goal.amount != goal.added_amount and not goal.is_completed:
                            transaction_id = transaction_serializer.save()
                            if len(str(transaction_id)) > 0 and transaction_id is not None:
                                Income.objects.filter(title=income.title, id=income.id, user_id=user).update(amount=income_amount)
                                Goal.objects.filter(title=goal.title, id=goal.id, user_id=user).update(added_amount=goal_amount)
                            else:
                                return Response({"status":False, "message":" transaction fail from Income %s to Goal %s"%(income.title, goal.title)}, status=status.HTTP_400_BAD_REQUEST)
                        
                            # changes on server #
                            transaction_dict = transaction_serializer.data
                            transaction_dict["income_from_name"] = income.title
                            transaction_dict["goal_name"] = goal.title

                            if periodicSerializer != "" and location_serializer == "":
                                transaction_dict.update({"periodic":periodicSerializer.data})
                            elif periodicSerializer == "" and location_serializer != "":
                                transaction_dict.update({"location":location_serializer.data})
                            elif periodicSerializer != "" and location_serializer != "":
                                transaction_dict.update({"periodic":periodicSerializer.data})
                                transaction_dict.update({"location":location_serializer.data})
                            # changes on server #
                            return Response({"status":True, "message":"Transfer amount from Income %s to Goal %s"%(income.title, goal.title), "data":transaction_dict}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({"status":False, "message":"Goal is Completed"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"status":False, "message":transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"status":False, "message":"amount, income_from, goal are required fields. title and description is optional"}, status=status.HTTP_400_BAD_REQUEST)
            
            elif (('amount' in request.data and 'income_from' in request.data and 'expense' in request.data) and ('source' not in request.data) and ('goal' not in request.data) and ('income_to' not in request.data)):
                if (request.data["amount"] != "" and request.data["income_from"] != "" and request.data["expense"] != ""):
                    
                    if 'title' not in request.data or request.data['title'] == "":
                        title = None
                    else:
                        title = request.data['title']

                    if 'description' not in request.data or request.data['description'] == "":
                        description = None
                    else:
                        description = request.data['description']
                    
                    try:
                        income = Income.objects.get(user_id=user, id=str(request.data["income_from"]))
                    except Income.DoesNotExist:
                        return Response({"status":False, "message":"Income doesn't exist with id %s"%(request.data["income_from"])}, status=status.HTTP_404_NOT_FOUND)

                    try:
                        expense = Expense.objects.get(user_id=user, id=str(request.data["expense"]))
                    except Expense.DoesNotExist:
                        return Response({"status":False, "message":"Expense doesn't exist with id %s"%(request.data["expense"])}, status=status.HTTP_404_NOT_FOUND)

                    income_amount = float(income.amount) - float(request.data["amount"])
                    expense_amount = float(expense.spent_amount) + float(request.data["amount"])

                    if location_serializer != "" and periodicSerializer == "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "expense":expense.id,
                            "location":location_serializer.data.get('id')
                        }
                    elif location_serializer == "" and periodicSerializer != "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "expense":expense.id,
                            "periodic":periodicSerializer.data.get('id')
                        }
                    elif location_serializer != "" and periodicSerializer != "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "expense":expense.id,
                            "location":location_serializer.data.get('id'),
                            "periodic":periodicSerializer.data.get('id')
                        }
                    else:
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "expense":expense.id
                        }
                    
                    if 'tags' in request.data and request.data["tags"] != []:
                        data_dict.update({"tag":request.data["tags"]})

                    if 'created_at' in request.data and "modified_at" in request.data:
                        data_dict.update({"created_at":request.data["created_at"]})
                        data_dict.update({"modified_at":request.data["modified_at"]})
                        
                    if 'is_completed' in request.data:
                        data_dict.update({"is_completed":request.data["is_completed"]})

                    transaction_serializer = TransactionSerializer(data=data_dict, context={"user":user})
                    if transaction_serializer.is_valid(raise_exception=False):
                        transaction_id = transaction_serializer.save()
                        if len(str(transaction_id)) > 0 and transaction_id is not None:
                            Income.objects.filter(title=income.title, id=income.id, user_id=user).update(amount=income_amount)
                            Expense.objects.filter(title=expense.title, id=expense.id, user_id=user).update(spent_amount=expense_amount)
                        else:
                            return Response({"status":False, "message":" transaction fail from Income %s to expense %s"%(income.title, expense.title)}, status=status.HTTP_400_BAD_REQUEST)
                        
                        # changes on server #
                        transaction_dict = transaction_serializer.data

                        transaction_dict["income_from_name"] = income.title
                        transaction_dict["expense_name"] = expense.title

                        if periodicSerializer != "" and location_serializer == "":
                            transaction_dict.update({"periodic":periodicSerializer.data})
                        elif periodicSerializer == "" and location_serializer != "":
                            transaction_dict.update({"location":location_serializer.data})
                        elif periodicSerializer != "" and location_serializer != "":
                            transaction_dict.update({"periodic":periodicSerializer.data})
                            transaction_dict.update({"location":location_serializer.data})
                        # changes on server #
                        return Response({"status":True, "message":"Transfer amount from Income %s to expense %s"%(income.title, expense.title), "data":transaction_dict}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"status":False, "message":transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"status":False, "message":"amount, income_from, expense are required fields. title and description is optional"}, status=status.HTTP_400_BAD_REQUEST)     
        
            elif (('amount' in request.data and 'income_from' in request.data and 'debt' in request.data) and ('source' not in request.data) and ('goal' not in request.data) and ('income_to' not in request.data) and ('expense' not in request.data)):
                if (request.data["amount"] != "" and request.data["income_from"] != "" and request.data["debt"] != ""):
                    
                    if 'title' not in request.data or request.data['title'] == "":
                        title = None
                    else:
                        title = request.data['title']

                    if 'description' not in request.data or request.data['description'] == "":
                        description = None
                    else:
                        description = request.data['description']
                    
                    try:
                        income = Income.objects.get(user_id=user, id=str(request.data["income_from"]))
                    except Income.DoesNotExist:
                        return Response({"status":False, "message":"Income doesn't exist with id %s"%(request.data["income_from"])}, status=status.HTTP_404_NOT_FOUND)

                    try:
                        debt = Debt.objects.get(user_id=user, id=str(request.data["debt"]))
                    except Debt.DoesNotExist:
                        return Response({"status":False, "message":"Debt doesn't exist with id %s"%(request.data["debt"])}, status=status.HTTP_404_NOT_FOUND)

                    income_amount = float(income.amount) - float(request.data["amount"])
                    debt_amount = ""
                    if float(debt.amount) == float(request.data["amount"]):
                        debt_amount = float(debt.paid_amount) + float(request.data["amount"])
                    else:
                        if float(request.data["amount"]) < float(debt.amount):
                            debt_amount = float(debt.paid_amount) + float(request.data["amount"])
                        else:
                            return Response({"status":False, "message":"Paid amount %s is grater then the Debt amount %s"%(request.data["amount"], debt.amount)}, status=status.HTTP_400_BAD_REQUEST)

                    if location_serializer != "" and periodicSerializer == "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "debt":debt.id,
                            "location":location_serializer.data.get('id')
                        }
                    elif location_serializer == "" and periodicSerializer != "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "debt":debt.id,
                            "periodic":periodicSerializer.data.get('id')
                        }
                    elif location_serializer != "" and periodicSerializer != "":
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "debt":debt.id,
                            "location":location_serializer.data.get('id'),
                            "periodic":periodicSerializer.data.get('id')
                        }
                    else:
                        data_dict ={
                            "title":title,
                            "description":description,
                            "amount":request.data["amount"],
                            "income_from":income.id,
                            "debt":debt.id
                        }
                    
                    if 'created_at' in request.data and "modified_at" in request.data:
                        data_dict.update({"created_at":request.data["created_at"]})
                        data_dict.update({"modified_at":request.data["modified_at"]})

                    transaction_serializer = TransactionSerializer(data=data_dict, context={"user":user})
                    if transaction_serializer.is_valid(raise_exception=False):
                        transaction_id = transaction_serializer.save()
                        if len(str(transaction_id)) > 0 and transaction_id is not None:
                            Income.objects.filter(title=income.title, id=income.id, user_id=user).update(amount=income_amount)
                            if float(debt.amount) == float(request.data["amount"]):
                                Debt.objects.filter(name=debt.name, id=debt.id, user_id=user).update(paid_amount=debt_amount)
                            else:
                                if float(request.data["amount"]) < float(debt.amount):
                                    if float(debt_amount) == float(debt.amount):
                                        Debt.objects.filter(name=debt.name, id=debt.id, user_id=user).update(paid_amount=debt_amount)
                                    Debt.objects.filter(name=debt.name, id=debt.id, user_id=user).update(paid_amount=debt_amount, is_partial_paid=True)
                        else:
                            return Response({"status":False, "message":" transaction fail from Income %s to debt %s"%(income.title, debt.name)}, status=status.HTTP_400_BAD_REQUEST)
                        
                        # changes on server #
                        transaction_dict = transaction_serializer.data
                        transaction_dict["income_from_name"] = income.title
                        transaction_dict["debt_paid_to"] = debt.name
                        # changes on server #
                        return Response({"status":True, "message":"Transfer amount from Income %s to debt %s"%(income.title, debt.name), "data":transaction_dict}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"status":False, "message":transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"status":False, "message":"amount, income_from, debt are required fields. title and description is optional"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status":False, "message":"Invalid data Passed"}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        if pk is not None and pk != "":
            goal = ''
            income_from = ''
            income_to = ''
            source = ''
            expense = ''
            debt = ''
            location = ''
            periodic = ''
            status_list = []

            try:
                user = User.objects.get(email=request.user).id
            except User.DoesNotExist:
                return Response({"status":False, "message":"User doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                transaction = Transaction.objects.get(user_id=user, id=pk)
            except Transaction.DoesNotExist:
                return Response({"status":False, "message":"Transaction detail not found with id %s"%(pk)}, status=status.HTTP_404_NOT_FOUND)

            if transaction.income_from_id is not None and transaction.income_from_id != "":
                income_from = Income.objects.filter(user_id=user, id=transaction.income_from_id) 
            
            if transaction.income_to_id is not None and transaction.income_to_id != "":
                income_to = Income.objects.filter(user_id=user, id=transaction.income_to_id)

            if transaction.goal_id is not None and transaction.goal_id != "":
                goal = Goal.objects.filter(user_id=user, id=transaction.goal_id)

            if transaction.source_id is not None and transaction.source_id != "":
                source = SourceIncome.objects.filter(user_id=user, id=transaction.source_id)

            if transaction.expense_id is not None and transaction.expense_id != "":
                expense = Expense.objects.filter(user_id=user, id=transaction.expense_id)

            if transaction.debt_id is not None and transaction.debt_id != "":
                debt = Debt.objects.filter(user_id=user, id=transaction.debt_id)

            # Server Update #
            if transaction.location_id is not None and transaction.location_id != "":
                location = Location.objects.get(id=str(transaction.location_id))
                if 'longitude' in request.data and 'latitude' in request.data:
                    if request.data["longitude"] != "" and request.data["latitude"] != "":
                        location_dict = {
                            "longitude":request.data.pop("longitude"),
                            "latitude":request.data.pop("latitude")
                        }
                        location = LocationSerializer(location, data=location_dict)
                        if location.is_valid(raise_exception=False):
                            location.save()
                        else:
                            message = ""
                            if 'latitude' in location.errors:
                                message = "latitude cannot be blank must be double."
                            
                            if 'longitude' in location.errors:
                                message = "longitude cannot be blank must be double."
                            return Response({"status":False, "message":message},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"status":False, "message":"longiude and latitude cannot be blank."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if 'longitude' in request.data and 'latitude' in request.data:
                    if request.data["longitude"] != "" and request.data["latitude"] != "":
                        location_dict = {
                            "longitude":request.data.pop("longitude"),
                            "latitude":request.data.pop("latitude")
                        }
                        location = LocationSerializer(data=location_dict)
                        if location.is_valid(raise_exception=False):
                            location.save()
                        else:
                            message = ""
                            if 'latitude' in location.errors:
                                message = "latitude cannot be blank must be double."
                            
                            if 'longitude' in location.errors:
                                message = "longitude cannot be blank must be double."
                            return Response({"status":False, "message":message},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"status":False, "message":"longiude and latitude cannot be blank."}, status=status.HTTP_400_BAD_REQUEST)
            # Server Update #

            if transaction.periodic_id is not None and transaction.periodic_id != "":
                periodic = Periodic.objects.get(id=str(transaction.periodic_id))        

            if (len(source) > 0 and len(income_to) > 0 and len(goal) <= 0 and len(income_from) <= 0 and len(expense) <= 0):
                source_amount = ''
                income_to_amount = ''
                updated_transfer_amount = ''
                amount = ''
                transaction_amount = ''
                if 'amount' in request.data:
                    transaction_amount = float(request.data["amount"])
                    if float(request.data["amount"]) > float(transaction.transaction_amount):
                        updated_transfer_amount = float(request.data["amount"]) - float(transaction.transaction_amount)
                        source_amount = float(source[0].spent_amount) + float(updated_transfer_amount)
                        income_to_amount = float(income_to[0].amount) + float(updated_transfer_amount)
                        amount = float(transaction.amount) + float(updated_transfer_amount)
                        if periodic:
                            week_days = str(periodic.week_days).split(',')
                            status_days = str(periodic.status_days).split(',')
                            for i, repeat_date in enumerate(week_days):
                                if status_days[i] == "True":
                                    amount = float(amount) + float(updated_transfer_amount)
                                    source_amount = float(source_amount) + float(updated_transfer_amount)
                                    income_to_amount = float(income_to_amount) + float(updated_transfer_amount)

                    elif float(request.data["amount"]) < float(transaction.transaction_amount):
                        updated_transfer_amount =  float(transaction.transaction_amount) - float(request.data["amount"])
                        source_amount = float(source[0].spent_amount) - float(updated_transfer_amount)
                        income_to_amount = float(income_to[0].amount) - float(updated_transfer_amount)
                        amount = float(transaction.amount) - float(updated_transfer_amount)
                        if periodic:
                            week_days = str(periodic.week_days).split(',')
                            status_days = str(periodic.status_days).split(',')
                            for i, repeat_date in enumerate(week_days):
                                if status_days[i] == "True":
                                    amount = float(amount) - float(updated_transfer_amount)
                                    source_amount = float(source_amount) - float(updated_transfer_amount)
                                    income_to_amount = float(income_to_amount) - float(updated_transfer_amount)

                    elif float(request.data["amount"]) == float(transaction.transaction_amount):
                        request.data.pop("amount")
                # Server Update #
                if transaction.location_id is None and 'latitude' in request.data and 'longitude' in request.data: # create new location
                    request.data["location"] = location.data.get('id')
                # Server Update #
                
                request.data.update({"transaction_amount":transaction_amount})
                request.data.update({"amount":amount})
                
                transaction_serializer = TransactionSerializer(transaction, data=request.data)
                if transaction_serializer.is_valid(raise_exception=False):
                    transaction_id = transaction_serializer.save()
                    if len(str(transaction_id)) > 0:
                        if ('amount' in request.data and float(request.data["amount"]) != float(transaction.transaction_amount)):
                            source.update(spent_amount=source_amount)
                            income_to.update(amount=income_to_amount)
                    else:
                        return Response({"status":False, "message":"Transaction Update Fail by id %s"%(pk)}, status=status.HTTP_304_NOT_MODIFIED)
                    return Response({"status":True, "message":"%s Transaction Amount Update from source %s to income %s"%(pk, source[0].title, income_to[0].title), "data":transaction_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"status":False, "message":transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                     
            elif (len(source) <= 0 and len(income_to) > 0 and len(goal) <= 0 and len(income_from) > 0 and len(expense) <= 0):
                income_from_amount = ''
                income_to_amount = ''
                updated_transfer_amount = ''
                amount = ''
                transaction_amount = ''
                if 'amount' in request.data:
                    transaction_amount = float(request.data["amount"])
                    if float(request.data["amount"]) > float(transaction.transaction_amount):
                        updated_transfer_amount = float(request.data["amount"]) - float(transaction.transaction_amount)
                        income_from_amount = float(income_from[0].amount) - float(updated_transfer_amount)
                        income_to_amount = float(income_to[0].amount) + float(updated_transfer_amount)
                        amount = float(transaction.amount) + float(updated_transfer_amount)
                        if periodic:
                            week_days = str(periodic.week_days).split(',')
                            status_days = str(periodic.status_days).split(',')
                            for i, repeat_date in enumerate(week_days):
                                if status_days[i] == "True":
                                    amount = float(amount) + float(updated_transfer_amount)
                                    income_from_amount = float(income_from_amount)-float(updated_transfer_amount)
                                    income_to_amount = float(income_to_amount)+float(updated_transfer_amount)

                    elif float(request.data["amount"]) < float(transaction.transaction_amount):
                        updated_transfer_amount =  float(transaction.transaction_amount) - float(request.data["amount"])
                        income_from_amount = float(income_from[0].amount) + float(updated_transfer_amount)
                        income_to_amount = float(income_to[0].amount) - float(updated_transfer_amount)
                        amount = float(transaction.amount) - float(updated_transfer_amount)
                        if periodic:
                            week_days = str(periodic.week_days).split(',')
                            status_days = str(periodic.status_days).split(',')
                            for i, repeat_date in enumerate(week_days):
                                if status_days[i] == "True":
                                    amount = float(amount) - float(updated_transfer_amount)
                                    income_from_amount = float(income_from_amount)+float(updated_transfer_amount)
                                    income_to_amount = float(income_to_amount)-float(updated_transfer_amount)
                    elif float(request.data["amount"]) == float(transaction.transaction_amount):
                        request.data.pop("amount")

                if transaction.location_id is None and 'latitude' in request.data and 'longitude' in request.data: # create new location
                    request.data["location"] = location.data.get('id')

                request.data.update({"transaction_amount":transaction_amount})
                request.data.update({"amount":amount})
                
                transaction_serializer = TransactionSerializer(transaction, data=request.data)
                if transaction_serializer.is_valid(raise_exception=False):
                    transaction_id = transaction_serializer.save()
                    if len(str(transaction_id)) > 0:
                        if ('amount' in request.data and float(request.data["amount"]) != float(transaction.transaction_amount)):
                            income_from.update(amount=income_from_amount)
                            income_to.update(amount=income_to_amount)
                    else:
                        return Response({"status":False, "message":"Transaction Update Fail by id %s"%(pk)}, status=status.HTTP_304_NOT_MODIFIED)
                    return Response({"status":True, "message":"%s Transaction Amount Update from Income %s to Income %s"%(pk, income_from[0].title, income_to[0].title), "data":transaction_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"status":False, "message":transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
            elif (len(source) <= 0 and len(income_to) <= 0 and len(goal) > 0 and len(income_from) > 0 and len(expense) <= 0):
                income_from_amount = ''
                goal_amount = ''
                updated_transfer_amount = ''
                amount = ''
                transaction_amount = ''
                if 'amount' in request.data:
                    transaction_amount = float(request.data["amount"])
                    if float(request.data["amount"]) > float(transaction.transaction_amount):
                        updated_transfer_amount = float(request.data["amount"]) - float(transaction.transaction_amount)
                        income_from_amount = float(income_from[0].amount) - float(updated_transfer_amount)
                        goal_amount = float(goal[0].added_amount) + float(updated_transfer_amount)
                        amount = float(transaction.amount) + float(updated_transfer_amount)
                        if periodic:
                            week_days = str(periodic.week_days).split(',')
                            status_days = str(periodic.status_days).split(',')
                            for i, repeat_date in enumerate(week_days):
                                if status_days[i] == "True":
                                    amount = float(amount) + float(updated_transfer_amount)
                                    income_from_amount = float(income_from_amount)-float(updated_transfer_amount)
                                    goal_amount = float(goal_amount)+float(updated_transfer_amount)
                    elif float(request.data["amount"]) < float(transaction.transaction_amount):
                        updated_transfer_amount =  float(transaction.transaction_amount) - float(request.data["amount"])
                        income_from_amount = float(income_from[0].amount) + float(updated_transfer_amount)
                        goal_amount = float(goal[0].added_amount) - float(updated_transfer_amount)
                        amount = float(transaction.amount) - float(updated_transfer_amount)
                        if periodic:
                            week_days = str(periodic.week_days).split(',')
                            status_days = str(periodic.status_days).split(',')
                            for i, repeat_date in enumerate(week_days):
                                if status_days[i] == "True":
                                    amount = float(amount) - float(updated_transfer_amount)
                                    income_from_amount = float(income_from_amount)+float(updated_transfer_amount)
                                    goal_amount = float(goal_amount)-float(updated_transfer_amount)
                    elif float(request.data["amount"]) == float(transaction.transaction_amount):
                        request.data.pop("amount")
                    
                if transaction.location_id is None and 'latitude' in request.data and 'longitude' in request.data: # create new location
                    request.data["location"] = location.data.get('id')

                request.data.update({"transaction_amount":transaction_amount})
                request.data.update({"amount":amount})
                
                transaction_serializer = TransactionSerializer(transaction, data=request.data)
                if transaction_serializer.is_valid(raise_exception=False):
                    transaction_id = transaction_serializer.save()
                    if len(str(transaction_id)) > 0:
                        if ('amount' in request.data and float(request.data["amount"]) != float(transaction.transaction_amount)):
                            income_from.update(amount=income_from_amount)
                            goal.update(added_amount=goal_amount)
                    else:
                        return Response({"status":False, "message":"Transaction Update Fail by id %s"%(pk)}, status=status.HTTP_304_NOT_MODIFIED)
                    return Response({"status":True, "message":"%s Transaction Amount Update from Income %s to Goal %s"%(pk, income_from[0].title, goal[0].title), "data":transaction_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"status":False, "message":transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            elif (len(source) <= 0 and len(income_to) <= 0 and len(goal) <= 0 and len(income_from) > 0 and len(expense) > 0):
                income_from_amount = ''
                expense_amount = ''
                updated_transfer_amount = ''
                amount = ''
                transaction_amount = ''
                if 'amount' in request.data:
                    transaction_amount = float(request.data["amount"])
                    if float(request.data["amount"]) > float(transaction.transaction_amount):   # 3 > 2
                        updated_transfer_amount = float(request.data["amount"]) - float(transaction.transaction_amount) # 1 = 3 - 2
                        income_from_amount = float(income_from[0].amount) - float(updated_transfer_amount)  # 9 = 10-1
                        expense_amount = float(expense[0].spent_amount) + float(updated_transfer_amount) # 11 = 10+1
                        amount = float(transaction.amount) + float(updated_transfer_amount) # 7 = 6+ 1
                        if periodic:
                            week_days = str(periodic.week_days).split(',')
                            status_days = str(periodic.status_days).split(',')
                            for i, repeat_date in enumerate(week_days):
                                if status_days[i] == "True":
                                    amount = float(amount) + float(updated_transfer_amount)
                                    income_from_amount = float(income_from_amount) - float(updated_transfer_amount)
                                    expense_amount = float(expense_amount) + float(updated_transfer_amount)

                    elif float(request.data["amount"]) < float(transaction.transaction_amount):
                        updated_transfer_amount =  float(transaction.transaction_amount) - float(request.data["amount"])
                        income_from_amount = float(income_from[0].amount) + float(updated_transfer_amount)
                        expense_amount = float(expense[0].spent_amount) - float(updated_transfer_amount)
                        amount = float(transaction.amount) - float(updated_transfer_amount)
                        if periodic:
                            week_days = str(periodic.week_days).split(',')
                            status_days = str(periodic.status_days).split(',')
                            for i, repeat_date in enumerate(week_days):
                                if status_days[i] == "True":
                                    amount = float(amount) - float(updated_transfer_amount)
                                    income_from_amount = float(income_from_amount) + float(updated_transfer_amount)
                                    expense_amount = float(expense_amount) - float(updated_transfer_amount)

                    elif float(request.data["amount"]) == float(transaction.transaction_amount):
                        request.data.pop("amount")
                    
                if transaction.location_id is None and 'latitude' in request.data and 'longitude' in request.data: # create new location
                    request.data["location"] = location.data.get('id')

                request.data.update({"transaction_amount":transaction_amount})
                request.data.update({"amount":amount})
        
                transaction_serializer = TransactionSerializer(transaction, data=request.data)
                if transaction_serializer.is_valid(raise_exception=False):
                    transaction_id = transaction_serializer.save()
                    if len(str(transaction_id)) > 0:
                        if ('amount' in request.data and float(request.data["amount"]) != float(transaction.transaction_amount)):
                            income_from.update(amount=income_from_amount)
                            expense.update(spent_amount=expense_amount)
                    else:
                        return Response({"status":False, "message":"Transaction Update Fail by id %s"%(pk)}, status=status.HTTP_304_NOT_MODIFIED)
                    return Response({"status":True, "message":"%s Transaction Amount Update from Income %s to Expense %s"%(pk, income_from[0].title, expense[0].title), "data":transaction_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"status":False, "message":transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
            elif (len(source) <= 0 and len(income_to) <= 0 and len(goal) <= 0 and len(income_from) > 0 and len(expense) <= 0 and len(debt) > 0):
                income_from_amount = ''
                debt_amount = ''
                updated_transfer_amount = ''
                amount = ''
                transaction_amount = ''
                if 'amount' in request.data:
                    transaction_amount = float(request.data["amount"])
                    if float(request.data["amount"]) > float(transaction.transaction_amount):
                        updated_transfer_amount = float(request.data["amount"]) - float(transaction.transaction_amount)
                        income_from_amount = float(income_from[0].amount) - float(updated_transfer_amount)
                        debt_amount = float(debt[0].paid_amount) + float(updated_transfer_amount)
                        amount = float(transaction.amount) + float(updated_transfer_amount)
                        if periodic:
                            week_days = str(periodic.week_days).split(',')
                            status_days = str(periodic.status_days).split(',')
                            for i, repeat_date in enumerate(week_days):
                                if status_days[i] == "True":
                                    amount = float(amount) + float(updated_transfer_amount)
                                    income_from_amount = float(income_from_amount) - float(updated_transfer_amount)
                                    debt_amount = float(debt_amount) + float(updated_transfer_amount)

                    elif float(request.data["amount"]) < float(transaction.transaction_amount):
                        updated_transfer_amount =  float(transaction.transaction_amount) - float(request.data["amount"])
                        income_from_amount = float(income_from[0].amount) + float(updated_transfer_amount)
                        debt_amount = float(debt[0].paid_amount) - float(updated_transfer_amount)
                        amount = float(transaction.amount) - float(updated_transfer_amount)
                        if periodic:
                            week_days = str(periodic.week_days).split(',')
                            status_days = str(periodic.status_days).split(',')
                            for i, repeat_date in enumerate(week_days):
                                if status_days[i] == "True":
                                    amount = float(amount) - float(updated_transfer_amount)
                                    income_from_amount = float(income_from_amount) + float(updated_transfer_amount)
                                    debt_amount = float(debt_amount) - float(updated_transfer_amount)

                    elif float(request.data["amount"]) == float(transaction.transaction_amount):
                        request.data.pop("amount")
                    
                if transaction.location_id is None and 'latitude' in request.data and 'longitude' in request.data: # create new location
                    request.data["location"] = location.data.get('id')
                
                request.data.update({"transaction_amount":transaction_amount})
                request.data.update({"amount":amount})
                transaction_serializer = TransactionSerializer(transaction, data=request.data)
                if transaction_serializer.is_valid(raise_exception=False):
                    transaction_id = transaction_serializer.save()
                    if len(str(transaction_id)) > 0:
                        if ('amount' in request.data and float(request.data["amount"]) != float(transaction.transaction_amount)):
                            income_from.update(amount=income_from_amount)
                            debt.update(paid_amount=debt_amount)
                    else:
                        return Response({"status":False, "message":"Transaction Update Fail by id %s"%(pk)}, status=status.HTTP_304_NOT_MODIFIED)
                    return Response({"status":True, "message":"%s Transaction Amount Update from Income %s to Debt %s"%(pk, income_from[0].title, debt[0].name), "data":transaction_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"status":False, "message":transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status":False, "message":"Please Provide Transaction Id in url/<id>"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        transcation = ''
        transaction_list = []
        main_list = []
        income_from = ""
        income_to = ""
        goal = ""
        expense = ""
        location = ""
        periodic = ""
        debt = ""

        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({"status":False, "message":"User Detail Doesn't Exist"},status=status.HTTP_404_NOT_FOUND)
        
        transcation = Transaction.objects.filter(user=user)
        if pk is not None and request.query_params == {}:
            transcation = Transaction.objects.filter(user=user, id=pk)
            
            if len(transcation) <= 0: 
                return Response({"status":False, "message":"transaction history not found"}, status=status.HTTP_404_NOT_FOUND)
        
        elif pk is None and request.query_params != {}:
            if request.query_params != {}:
                if 'income_from' in request.query_params and request.query_params["income_from"] is not None:
                    if request.query_params["income_from"] is None:
                        return Response({"status":False, "message":"Please Provide income_from id in query params like url/?income_from=1"}, status=status.HTTP_400_BAD_REQUEST)
                    transcation = Transaction.objects.filter(user=user, income_from_id=request.query_params["income_from"])
                    if len(transcation) <= 0: 
                        return Response({"status":False, "message":"transaction history not found"}, status=status.HTTP_404_NOT_FOUND)
                
                elif 'income_to' in request.query_params and request.query_params["income_to"] is not None:
                    if request.query_params["income_to"] is None:
                        return Response({"status":False, "message":"Please Provide income_to id in query params like url/?income_to=1"}, status=status.HTTP_400_BAD_REQUEST)
                    transcation = Transaction.objects.filter(user=user, income_to_id=request.query_params["income_to"])
                    if len(transcation) <= 0: 
                        return Response({"status":False, "message":"transaction history not found"}, status=status.HTTP_404_NOT_FOUND)
                
                elif 'expense' in request.query_params and request.query_params["expense"] is not None:
                    if request.query_params["expense"] is None:
                        return Response({"status":False, "message":"Please Provide expense id in query params like url/?expense=1"}, status=status.HTTP_400_BAD_REQUEST)
                    transcation = Transaction.objects.filter(user=user, expense_id=request.query_params["expense"])
                    if len(transcation) <= 0: 
                        return Response({"status":False, "message":"transaction history not found"}, status=status.HTTP_404_NOT_FOUND)
                
                elif 'goal' in request.query_params and request.query_params["goal"] is not None:
                    if request.query_params["goal"] is None:
                        return Response({"status":False, "message":"Please Provide goal id in query params like url/?goal=1"}, status=status.HTTP_400_BAD_REQUEST)
                    transcation = Transaction.objects.filter(user=user, goal_id=request.query_params["goal"])
                    if len(transcation) <= 0: 
                        return Response({"status":False, "message":"transaction history not found"}, status=status.HTTP_404_NOT_FOUND)
                    
                elif 'source' in request.query_params and request.query_params["source"] is not None:
                    if request.query_params["source"] is None:
                        return Response({"status":False, "message":"Please Provide source id in query params like url/?source=1"}, status=status.HTTP_400_BAD_REQUEST)
                    transcation = Transaction.objects.filter(user=user, source_id=request.query_params["source"])
                    if len(transcation) <= 0: 
                        return Response({"status":False, "message":"transaction history not found"}, status=status.HTTP_404_NOT_FOUND)   
            
                if 'debt' in request.query_params and request.query_params["debt"] is not None:
                    if request.query_params["debt"] is None:
                        return Response({"status":False, "message":"Please Provide debt id in query params like url/?debt=1"}, status=status.HTTP_400_BAD_REQUEST)
                    transcation = Transaction.objects.filter(user=user, debt_id=request.query_params["debt"])
                    if len(transcation) <= 0: 
                        return Response({"status":False, "message":"transaction history not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"status":False, "message":"provide source, income_to, income_from, goal, expense, debt id in request query_params like url/?source=1"})

        for x in transcation:
            transaction_list.append(x)
        transaction_serializer = TransactionSerializer(transaction_list, many=True)  

        for y in transaction_serializer.data:
            if y["income_to"] is not None:
                try:
                    income_to = Income.objects.get(id=str(y["income_to"])).title
                except Income.DoesNotExist:
                    return Response({"status":False, "message":"income detail not found"}, status=status.HTTP_404_NOT_FOUND)
                y["income_to_name"] = income_to
            if y["income_from"] is not None:
                try:
                    income_from = Income.objects.get(id=str(y["income_from"])).title
                except Income.DoesNotExist:
                    return Response({"status":False, "message":"income detail not found"}, status=status.HTTP_404_NOT_FOUND)
                y["income_from_name"] = income_from
            if y["source"] is not None:
                try:
                    source = SourceIncome.objects.get(id=str(y["source"])).title
                except SourceIncome.DoesNotExist:
                    return Response({"status":False, "message":"source detail not found"}, status=status.HTTP_404_NOT_FOUND)
                y["source_name"] = source
            if y["goal"] is not None:
                try:
                    goal = Goal.objects.get(id=str(y["goal"])).title
                except Goal.DoesNotExist:
                    return Response({"status":False, "message":"goal detail not found"}, status=status.HTTP_404_NOT_FOUND)
                y["goal_name"] = goal
            if y["expense"] is not None:
                try:
                    expense = Expense.objects.get(id=str(y["expense"])).title
                except Expense.DoesNotExist:
                    return Response({"status":False, "message":"expense detail not found"}, status=status.HTTP_404_NOT_FOUND)
                y["expense_name"] = expense
            if y["periodic"] is not None:
                periodic = Periodic.objects.get(id=str(y["periodic"]))
                y["periodic_data"] = {'id':periodic.id,'start_date':periodic.start_date,'end_date':periodic.end_date,'week_days':periodic.week_days,'status_days':str(periodic.status_days).lower(),'prefix':periodic.prefix,'prefix_value':periodic.prefix_value, 'created_at':periodic.created_at, 'modified_at':periodic.modified_at}
            if y["location"] is not None:
                location = Location.objects.get(id=str(y["location"]))
                y["location_data"] = {'id':location.id,'latitude':location.latitude,'longitude':location.longitude, 'created_at':location.created_at, 'modified_at':location.modified_at}
            if y["debt"] is not None:
                debt = Debt.objects.get(id=str(y["debt"])).name
                y["debt_name"] = debt
            
            main_list.append(y)
        data_dict = main_list
        
        return Response({"status":True, "message":"transaction data Fetched Succcessfully", "data":data_dict}, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, format=None): 
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST) 
        expense = ""
        transaction = ""
        income_to = ""
        income_from = ""
        goal = ""
        source = ""
        debt = ""
        location = ""
        periodic = ""
        if pk is not None and pk != '':
            try:
                user = User.objects.get(email=request.user).id
            except User.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False,"message":"user not found"}), email=request.user, status=False)
                return Response({"status":False, "message":"user not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                transaction = Transaction.objects.get(user=user, id=pk)
            except Transaction.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False,"message":"user have not any transaction data"}), email=request.user, status=False)
                return Response({"status":False, "message":"user have not any transaction by id %s"%(pk)}, status=status.HTTP_400_BAD_REQUEST)
        
            if transaction.income_to_id != "" and transaction.income_to_id is not None:
                income_to = Income.objects.filter(id=transaction.income_to_id)

            if transaction.income_from_id != "" and transaction.income_from_id is not None:
                income_from = Income.objects.filter(id=transaction.income_from_id)
            
            if transaction.expense_id != "" and transaction.expense_id is not None:
                expense = Expense.objects.filter(id=transaction.expense_id)    
            
            if transaction.goal_id != "" and transaction.goal_id is not None:
                goal = Goal.objects.filter(id=transaction.goal_id)

            if transaction.source_id != "" and transaction.source_id is not None:
                source = SourceIncome.objects.filter(id=transaction.source_id)  

            if transaction.debt_id is not None and transaction.debt_id != "":
                debt = Debt.objects.filter(id=str(transaction.debt_id))
            
            if transaction.location_id != "" and transaction.location_id is not None:
                location = Location.objects.filter(id=str(transaction.location_id))
                location.delete()
            
            if transaction.periodic_id != "" and transaction.periodic_id is not None:
                periodic = Periodic.objects.filter(id=str(transaction.periodic_id))
                periodic.delete()
            
            if len(income_from) > 0 and len(expense) > 0 and len(income_to) <= 0 and len(goal) <= 0 and len(source) <= 0:
        
                income_from_amount = float(income_from[0].amount) + float(transaction.amount) 
                expense_amount = float(expense[0].spent_amount) - float(transaction.amount)
                deleted_transaction = transaction.delete()   
                if len(str(deleted_transaction)) > 0:
                    income_from.update(amount=income_from_amount)
                    expense.update(spent_amount=expense_amount)

                else:
                    header = {
                        "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                    }
                    LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"transaction data was not delete by id %s"%(pk)}), email=request.user, status=True)
                    return Response({"status":False, "message":"transaction data was not delete by id %s"%(pk)}, status=status.HTTP_403_FORBIDDEN) 
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True,"message":"transaction data was successfully delete by id %s"%(pk)}), email=request.user, status=True)
                return Response({"status":True, "message":"transaction data was successfully delete by id %s"%(pk)}, status=status.HTTP_200_OK)
            
            elif len(income_from) > 0 and len(expense) <= 0 and len(income_to) > 0 and len(goal) <= 0 and len(source) <= 0:
                income_from_amount = float(income_from[0].amount) + float(transaction.amount) 
                income_to_amount = float(income_to[0].amount) - float(transaction.amount)
                
                deleted_transaction = transaction.delete()   
                if len(str(deleted_transaction)) > 0: 
                    income_from.update(amount=income_from_amount)
                    income_to.update(amount=income_to_amount)

                else:
                    header = {
                        "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                    }
                    LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"transaction data was not delete by id %s"%(pk)}), email=request.user, status=True)
                    return Response({"status":False, "message":"transaction data was not delete by id %s"%(pk)}, status=status.HTTP_403_FORBIDDEN)     
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True,"message":"transaction data was successfully delete by id %s"%(pk)}), email=request.user, status=True)
                return Response({"status":True, "message":"transaction data was successfully delete by id %s"%(pk)}, status=status.HTTP_200_OK)
            
            elif len(income_from) <= 0 and len(expense) <= 0 and len(income_to) > 0 and len(goal) <= 0 and len(source) > 0:
                
                source_amount = float(source[0].spent_amount) - float(transaction.amount) 
                income_to_amount = float(income_to[0].amount) - float(transaction.amount)
                 
                deleted_transaction = transaction.delete()   
                if len(str(deleted_transaction)) > 0:
                    source.update(spent_amount=source_amount)
                    income_to.update(amount=income_to_amount)

                else:
                    header = {
                        "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                    }
                    LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"transaction data was not delete by id %s"%(pk)}), email=request.user, status=True)
                    return Response({"status":False, "message":"transaction data was not delete by id %s"%(pk)}, status=status.HTTP_403_FORBIDDEN)         
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True,"message":"transaction data was successfully delete by id %s"%(pk)}), email=request.user, status=True)
                return Response({"status":True, "message":"transaction data was successfully delete by id %s"%(pk)}, status=status.HTTP_200_OK)
            
            elif len(income_from) > 0 and len(expense) <= 0 and len(income_to) <= 0 and len(goal) > 0 and len(source) <= 0:
               
                income_from_amount = float(income_from[0].amount) + float(transaction.amount)
                goal_amount = float(goal[0].added_amount) - float(transaction.amount)

                deleted_transaction = transaction.delete()   
                if len(str(deleted_transaction)) > 0:
                    income_from.update(amount=income_from_amount)
                    goal.update(added_amount=goal_amount) 

                else:
                    header = {
                        "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                    }
                    LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"transaction data was not delete by id %s"%(pk)}), email=request.user, status=True)
                    return Response({"status":False, "message":"transaction data was not delete by id %s"%(pk)}, status=status.HTTP_403_FORBIDDEN)   
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True,"message":"transaction data was successfully delete by id %s"%(pk)}), email=request.user, status=True)
                return Response({"status":True, "message":"transaction data was successfully delete by id %s"%(pk)}, status=status.HTTP_200_OK)

            elif len(income_from) > 0 and len(expense) <= 0 and len(income_to) <= 0 and len(goal) <= 0 and len(source) <= 0 and len(debt) > 0:
               
                income_from_amount = float(income_from[0].amount) + float(transaction.amount)
                debt_amount = float(debt[0].paid_amount) - float(transaction.amount)

                deleted_transaction = transaction.delete()   
                if len(str(deleted_transaction)) > 0:
                    income_from.update(amount=income_from_amount)
                    if float(debt[0].paid_amount) == float(0.00):
                        debt.update(paid_amount=debt_amount, is_partial_paid=False, is_paid=False, is_completed=False) 
                    else:
                        debt.update(paid_amount=debt_amount) 

                else:
                    header = {
                        "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                    }
                    LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"transaction data was not delete by id %s"%(pk)}), email=request.user, status=True)
                    return Response({"status":False, "message":"transaction data was not delete by id %s"%(pk)}, status=status.HTTP_403_FORBIDDEN)   
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True,"message":"transaction data was successfully delete by id %s"%(pk)}), email=request.user, status=True)
                return Response({"status":True, "message":"transaction data was successfully delete by id %s"%(pk)}, status=status.HTTP_200_OK)
        else:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"Please Provide Transaction id in request param like url/<id>"}), email=request.user, status=False)
            return Response({"status":False, "message":"Please Provide Transaction id in request param like url/<id>"}, status=status.HTTP_400_BAD_REQUEST)
# Transaction View Code End #

# class TagView Code start #
class TagView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TagSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({"status":True, "message":"Tag Successfully Created"}), email=request.user, status=True)
            return Response({"status":True, "message":"Tag Successfully Created", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            message = ''
            if 'name' in serializer.errors:
                message = "Tag name cannot be blnak"
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data), response_data=json.dumps({'status':False, 'message':message}), email=request.user, status=False)
            return Response({"status":False, "message":message}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        tag =''
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"User Detail Doesn't Exist"}), email=request.user, status=False)
            return Response({"status":False, "message":"User Detail Doesn't Exist"},status=status.HTTP_404_NOT_FOUND)

        try:
            tag = Tag.objects.filter(user=user)
        except Tag.DoesNotExist:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"user have not any tag data"}), email=request.user, status=False)
            return Response({"status":False, "message":"user have not any tag data"},status=status.HTTP_404_NOT_FOUND)
        
        if pk is not None:
            try:
                tag = Tag.objects.filter(user=user, id=pk)
            except Tag.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"user have not any tag data by id %s"%(pk)}), email=request.user, status=False)
                return Response({"status":False, "message":"user have not any tag data by id %s"%(pk)},status=status.HTTP_404_NOT_FOUND)


        tag_serializer = TagSerializer(tag, many=True)
        header = {
            "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
        }
        LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True, "message":"tag data Fetched Succcessfully"}), email=request.user, status=True)
        return Response({"status":True, "message":"tag data Fetched Succcessfully", "data":tag_serializer.data},status=status.HTTP_200_OK)

    def put(self,request,pk=None,format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        if pk is not None:
            try:
                user = User.objects.get(email=request.user).id
            except User.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data),response_data=json.dumps({"status":False, "message":"User Detail Doesn't Exist"}), email=request.user, status=False)
                return Response({"status":False,"message":"User Detail Doesn't Exist"},status=status.HTTP_404_NOT_FOUND)
            
            try:
                tag = Tag.objects.get(id=pk, user_id=user)
            except Tag.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data),response_data=json.dumps({'status':False, 'message':'tag data not found by id %s'%(pk)}), email=request.user, status=False)
                return Response({'status':False, 'message':'tag data not found by id %s'%(pk)}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = TagSerializer(tag, data=request.data)
            if serializer.is_valid(raise_exception=False):
                serializer.save()
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data),response_data=json.dumps({"status":True, "message":"tag data updated successfuully"}), email=request.user, status=True)
                return Response({"status":True, "message":"tag data updated successfuully","data":serializer.data}, status=status.HTTP_201_CREATED)
            else:
                message = ''
                if 'name' in serializer.errors:
                    message = "Tag name cannot be blank"
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data),response_data=json.dumps({"status":False, "message":message}), email=request.user, status=False)
                return Response({"status":False,"message":message}, status=status.HTTP_400_BAD_REQUEST)  
        else:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), request_data=json.dumps(request.data),response_data=json.dumps({"status":False, "message":"Please Provide Tag Id"}), email=request.user, status=False)
            return Response({"status":False, "message":"Please Provide Tag Id"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk=None, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        if pk is not None:
            try:
                user = User.objects.get(email=request.user).id
            except User.DoesNotExist:
                return Response({"status":False, "message":"User doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
                
            try:
                tag = Tag.objects.get(id=pk, user_id=user)
            except Tag.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header),response_data=json.dumps({"status":False, "message":"tag data not found by id %s"%(pk)}), email=request.user, status=False)
                return Response({'status':False, 'message':'tag data not found by id %s'%(pk)}, status=status.HTTP_404_NOT_FOUND)
            deleted_tag = tag.delete()
            if len(str(deleted_tag)) <= 0: 
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                    }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header),response_data=json.dumps({"status":True, "message":"tag data was not delete"}), email=request.user, status=True)
                return Response({"status":False,"message":"tag data was not delete"},status=status.HTTP_403_FORBIDDEN) 
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header),response_data=json.dumps({"status":True, "message":"tag data was successfully delete"}), email=request.user, status=True)
            return Response({"status":True,"message":"tag data was successfully delete"},status=status.HTTP_200_OK) 
        else:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header),response_data=json.dumps({"status":False,"message":"Please Provide Tag Id in request like url/<id>"}), email=request.user, status=True)
            return Response({"status":False,"message":"Please Provide Tag Id in request like url/<id>"},status=status.HTTP_400_BAD_REQUEST) 
# class TagView Code end #

# class HomeVIEW Code Start With Reccustion Transaction #
class HomeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        user= ''
        balance = {}
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            return Response({"status":False, "message":"User Detail Not Found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            income = Income.objects.all().filter(user_id=user, created_at__month=dt.today().month)
        except Income.DoesNotExist:
            return Response({"status":False, "message":"User Income Detail Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            expense = Expense.objects.all().filter(user_id=user, created_at__month=dt.today().month)
        except Expense.DoesNotExist:
            return Response({"status":False, "message":"User Expense Detail Not Found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            source_income = SourceIncome.objects.all().filter(user_id=user, created_at__month=dt.today().month)
        except SourceIncome.DoesNotExist:
            return Response({"status":False, "message":"User SourceIncome Detail Not Found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            goal = Goal.objects.all().filter(user_id=user, created_at__month=dt.today().month)
        except Goal.DoesNotExist:
            return Response({"status":False, "message":"User Goal Detail Not Found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            balance = SourceIncome.objects.filter(user_id=user, created_at__month=dt.today().month).aggregate(Sum('amount'))
            if balance['amount__sum'] is None:
                balance['amount__sum'] = 0
        except SourceIncome.DoesNotExist:
            balance['amount__sum'] = 0

        try:
            debt = Debt.objects.all().filter(user_id=user, created_at__month=dt.today().month)
        except Debt.DoesNotExist:
            return Response({"status":False, "message":"User Debt Detail Not Found"}, status=status.HTTP_404_NOT_FOUND)

        source_income_serializer = SourceIncomeSerializer(source_income, many=True)
        income_serializer = IncomeSerializer(income, many=True)
        expense_serializer = ExpenseSerializer(expense, many=True)
        goal_serializer = GoalsSerializer(goal, many=True)
        debt_serializer = DebtSerializer(debt, many=True)
        
        User_Data_Dict = {
            "mainincomes":source_income_serializer.data,
            "otherincomes":income_serializer.data,
            "expenses":expense_serializer.data,
            "goals":goal_serializer.data,
            "debts":debt_serializer.data,
            "balance":balance['amount__sum']
        }

        # Reccurence Transaction Code Start #
        transacion = Transaction.objects.all().filter(user_id=user)
        periodic = ''
        transacion_amount = ""
        repeat_dates = []
        repeat_status = []
        income_from = ""
        income_to = ""
        goal = ""
        source = ""
        expense = ""
        debt = ""
        if transacion != []:
            for x in transacion:
                amount = x.amount
                
                if x.income_from_id is not None and x.income_from_id != "":
                    income_from = Income.objects.filter(user_id=user, id=x.income_from_id) 
                
                if x.income_to_id is not None and x.income_to_id != "":
                    income_to = Income.objects.filter(user_id=user, id=x.income_to_id)

                if x.goal_id is not None and x.goal_id != "":
                    goal = Goal.objects.filter(user_id=user, id=x.goal_id)

                if x.source_id is not None and x.source_id != "":
                    source = SourceIncome.objects.filter(user_id=user, id=x.source_id)

                if x.expense_id is not None and x.expense_id != "":
                    expense = Expense.objects.filter(user_id=user, id=x.expense_id)

                if x.debt_id is not None and x.debt_id != "":
                    debt = Debt.objects.filter(user_id=user, id=x.debt_id)

                if x.periodic_id is not None:
                    try:
                        periodic = Periodic.objects.get(id=str(x.periodic_id))
                    except Periodic.DoesNotExist:
                        pass
                    
                    if periodic.week_days is not None  and periodic.status_days != "":
                        repeat_dates = str(periodic.week_days).split(',')
                        repeat_status = str(periodic.status_days).split(',')
                    
                    for i, repeat_date in enumerate(repeat_dates):
                        repeat = dt.strptime(str(repeat_date), "%Y-%m-%d").date()
                        if repeat <= date.today():
                            if repeat_status[i].encode('ascii').decode('UTF-8') == "False":
                                transacion_amount = float(amount) + float(x.transaction_amount)
                                amount = transacion_amount
                                repeat_status[i] = "True"
                           
                                Transaction.objects.filter(id=str(x.id), periodic_id=str(x.periodic_id)).update(amount=float(amount))
                                
                                if x.income_to_id is not None and x.income_to_id != "" and x.source_id is not None and x.source_id != "":
                                
                                    source_amount = source[0].spent_amount
                                    income_to_amount = income_to[0].amount
                            
                                    source_amount = float(source_amount) + float(x.transaction_amount)
                                    income_to_amount = float(income_to_amount) + float(x.transaction_amount)
                                            
                                    source.update(spent_amount=source_amount)
                                    income_to.update(amount=income_to_amount)
                                        
                                elif x.income_to_id is not None and x.income_to_id != "" and x.income_from_id is not None and x.income_from_id != "":

                                    income_from_amount = income_from[0].amount
                                    income_to_amount = income_to[0].amount
                                    
                                    income_from_amount = float(income_from_amount) - float(x.transaction_amount)
                                    income_to_amount = float(income_to_amount) + float(x.transaction_amount)
                                        
                                    income_from.update(amount=income_from_amount)
                                    income_to.update(amount=income_to_amount)
                                    
                                elif x.income_from_id is not None and x.income_from_id != "" and x.goal_id is not None and x.goal_id != "":

                                    income_from_amount = income_from[0].amount
                                    goal_amount = goal[0].added_amount
                            
                                    income_from_amount = float(income_from_amount) - float(x.transaction_amount)
                                    goal_amount = float(goal_amount) + float(x.transaction_amount)
                                        
                                    income_from.update(amount=income_from_amount)
                                    goal.update(added_amount=goal_amount)

                                elif x.income_from_id is not None and x.income_from_id != "" and x.expense_id is not None and x.expense_id != "":

                                    income_from_amount = income_from[0].amount
                                    expense_amount = expense[0].spent_amount
                                
                                    income_from_amount = float(income_from_amount) - float(x.transaction_amount)
                                    expense_amount = float(expense_amount) + float(x.transaction_amount)
                                        
                                    income_from.update(amount=income_from_amount)
                                    expense.update(spent_amount=expense_amount)
                            
                                elif x.income_from_id is not None and x.income_from_id != "" and x.debt_id is not None and x.debt_id != "":

                                    income_from_amount = income_from[0].amount
                                    debt_amount = debt[0].paid_amount
                                    
                                    income_from_amount = float(income_from_amount) - float(x.transaction_amount)
                                    debt_amount = float(debt_amount) + float(x.transaction_amount)
                                    
                                    income_from.update(amount=income_from_amount)
                                    debt.update(paid_amount=debt_amount)
    
                    repeat_status = ','.join(repeat_status)   
                    Periodic.objects.filter(id=str(x.periodic_id)).update(status_days=repeat_status)
        # Reccurence Transaction Code End #

        return Response({"status":True, "message":"Fetch all data successfully", "data":User_Data_Dict}, status=status.HTTP_200_OK)
# class HomeVIEW Code End #

### Report API VIEW CODE START ###
class ReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        token_check = check_token(user=request.user)
        if token_check != "":
            return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)
        transaction_data_dict = {}
        transaction_data_list = []
        try:
            user = User.objects.get(email=request.user).id
        except User.DoesNotExist:
            header = {
                "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
            }
            LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"User Detail Doesn't Exist"}), email=request.user, status=False)
            return Response({"status":False, "message":"User Detail Doesn't Exist"},status=status.HTTP_404_NOT_FOUND)
        
        
        transaction = Transaction.objects.filter(user_id=user)
        if transaction != []:
            for x in transaction:
                transaction_data_list.append(x)
        
        if 'subfilter' in request.query_params and request.query_params['subfilter'] is not None:
            if len(transaction_data_list) > 0:
                del transaction_data_list[:]
            if request.query_params['subfilter'] == "Today":
                if request.query_params["startdate"] == request.query_params["enddate"]:
                    transaction = Transaction.objects.filter(user_id=user, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                    for x in transaction:
                        transaction_data_list.append(x)
                    
            elif request.query_params['subfilter'] == "Week":
                transaction = Transaction.objects.filter(user_id=user,created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                for x in transaction:
                    transaction_data_list.append(x)
                
            elif request.query_params['subfilter'] == "Month":
                transaction = Transaction.objects.filter(user_id=user, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                for x in transaction:
                    transaction_data_list.append(x)
            
            elif request.query_params['subfilter'] == "Year":
                transaction = Transaction.objects.filter(user_id=user, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]]) 
                for x in transaction:
                    transaction_data_list.append(x)
            
            else:
                transaction = Transaction.objects.all().filter(user_id=user, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                for x in transaction:
                    transaction_data_list.append(x)
                
        if 'filter' in request.query_params and request.query_params['filter'] is not None:
            if len(transaction_data_list) > 0:
                del transaction_data_list[:]
            if request.query_params['filter'] == "income":
                income_id = Income.objects.filter(user_id=user)
                
                for income in income_id:
                    if 'subfilter' not in request.query_params:
                        transaction = Transaction.objects.filter(user_id=user, income_from_id=income.id)
                        for x in transaction:
                            transaction_data_list.append(x)
                        
                        transaction = Transaction.objects.filter(user_id=user, income_to_id=income.id)
                        for x in transaction:
                            transaction_data_list.append(x)
                    else:
                        if request.query_params['subfilter'] == "Today":
                            if request.query_params["startdate"] == request.query_params["enddate"]:
                                transaction = Transaction.objects.filter(user_id=user, income_from_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                                for x in transaction:
                                    transaction_data_list.append(x)
                                
                                transaction = Transaction.objects.filter(user_id=user, income_to_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                                for x in transaction:
                                    transaction_data_list.append(x)
                    
                            else:
                                return Response({"status":False, "message":"please provide same start and end date when user subfilter 'Today'"}, status=status.HTTP_404_NOT_FOUND)
                                
                        elif request.query_params['subfilter'] == "Week":
                            transaction = Transaction.objects.all().filter(user_id=user, income_from_id=income.id,created_at__range=[request.query_params["startdate"], request.query_params["enddate"]] )
                            for x in transaction:
                                transaction_data_list.append(x)
                            
                            transaction = Transaction.objects.filter(user_id=user, income_to_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            

                        elif request.query_params['subfilter'] == "Month":
                            transaction = Transaction.objects.all().filter(user_id=user, income_from_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            
                            transaction = Transaction.objects.filter(user_id=user, income_to_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            

                        elif request.query_params['subfilter'] == "Year":
                            transaction = Transaction.objects.all().filter(user_id=user, income_from_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            
                            transaction = Transaction.objects.filter(user_id=user, income_to_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                        
                        else:
                            transaction = Transaction.objects.all().filter(user_id=user, income_from_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            
                            transaction = Transaction.objects.all().filter(user_id=user, income_to_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                              
            
            elif request.query_params['filter'] == "goal":
                goal_id = Goal.objects.filter(user_id=user)

                for goal in goal_id:
                    if 'subfilter' not in request.query_params:
                        transaction = Transaction.objects.filter(user_id=user, goal_id=goal.id)# queryset<[]>
                        for x in transaction:
                            transaction_data_list.append(x)     
                    else:
                        if request.query_params['subfilter'] == "Today":
                            if request.query_params["startdate"] == request.query_params["enddate"]:
                                transaction = Transaction.objects.filter(user_id=user, goal_id=goal.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                                for x in transaction:
                                    transaction_data_list.append(x)
                            else:
                                return Response({"status":False, "message":"please provide same start and end date when user subfilter 'Today'"}, status=status.HTTP_404_NOT_FOUND)
                                
                        elif request.query_params['subfilter'] == "Week":
                            transaction = Transaction.objects.all().filter(user_id=user, goal_id=goal.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                    

                        elif request.query_params['subfilter'] == "Month":
                            transaction = Transaction.objects.all().filter(user_id=user, goal_id=goal.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)

                        elif request.query_params['subfilter'] == "Year":
                            transaction = Transaction.objects.all().filter(user_id=user, goal_id=goal.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                                
                        else:
                            transaction = Transaction.objects.all().filter(user_id=user, goal_id=goal.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
            
            elif request.query_params['filter'] == "expense":
                expense_id = Expense.objects.filter(user_id=user)

                for expense in expense_id:
                    if 'subfilter' not in request.query_params:
                        transaction = Transaction.objects.filter(user_id=user, expense_id=expense.id)# queryset<[]>
                        for x in transaction:
                            transaction_data_list.append(x)
                    else:
                        if request.query_params['subfilter'] == "Today":
                            if request.query_params["startdate"] == request.query_params["enddate"]:
                                transaction = Transaction.objects.all().filter(user_id=user, expense_id=expense.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                                for x in transaction:
                                    transaction_data_list.append(x)
                            else:
                                return Response({"status":False, "message":"please provide same start and end date when user subfilter 'Today'"}, status=status.HTTP_404_NOT_FOUND)
                        elif request.query_params['subfilter'] == "Week":
                            transaction = Transaction.objects.all().filter(user_id=user, expense_id=expense.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)

                        elif request.query_params['subfilter'] == "Month":
                            transaction = Transaction.objects.all().filter(user_id=user, expense_id=expense.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)

                        elif request.query_params['subfilter'] == "Year":
                            transaction = Transaction.objects.all().filter(user_id=user, expense_id=expense.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                                
                        else:
                            transaction = Transaction.objects.all().filter(user_id=user, expense_id=expense.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)

            elif request.query_params['filter'] == "source":
                source_id = SourceIncome.objects.filter(user_id=user)

                for source in source_id:
                    if 'subfilter' not in request.query_params:
                        transaction = Transaction.objects.filter(user_id=user, source_id=source.id)
                        for x in transaction:
                            transaction_data_list.append(x)
                    else:
                        if request.query_params['subfilter'] == "Today":
                            if request.query_params["startdate"] == request.query_params["enddate"]:
                                transaction = Transaction.objects.all().filter(user_id=user, source_id=source.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                                for x in transaction:
                                    transaction_data_list.append(x)
                            else:
                                return Response({"status":False, "message":"please provide same start and end date when user subfilter 'Today'"}, status=status.HTTP_404_NOT_FOUND)
                        elif request.query_params['subfilter'] == "Week":
                            transaction = Transaction.objects.all().filter(user_id=user, source_id=source.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)

                        elif request.query_params['subfilter'] == "Month":
                            transaction = Transaction.objects.all().filter(user_id=user, source_id=source.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)

                        elif request.query_params['subfilter'] == "Year":
                            transaction = Transaction.objects.all().filter(user_id=user, source_id=source.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                        
                        else:
                            transaction = Transaction.objects.all().filter(user_id=user, source_id=source.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)

            elif request.query_params['filter'] == "tag":
                tag_id = Tag.objects.filter(user_id=user)

                for tag in tag_id:
                    if 'subfilter' not in request.query_params:
                        transaction = Transaction.objects.filter(user_id=user,tag__id=tag.id)# queryset<[]>
                        for x in transaction:
                            transaction_data_list.append(x)
                        
                    else:
                        if request.query_params['subfilter'] == "Today":
                            if request.query_params["startdate"] == request.query_params["enddate"]:
                                transaction = Transaction.objects.filter(user_id=user, tag__id=tag.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                                for x in transaction:
                                    transaction_data_list.append(x)
                            else:
                                return Response({"status":False, "message":"please provide same start and end date when user subfilter 'Today'"}, status=status.HTTP_404_NOT_FOUND)    
                                
                        elif request.query_params['subfilter'] == "Week":
                            transaction = Transaction.objects.all().filter(user_id=user, tag__id=tag.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            

                        elif request.query_params['subfilter'] == "Month":
                            transaction = Transaction.objects.all().filter(user_id=user, tag__id=tag.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            

                        elif request.query_params['subfilter'] == "Year":
                            transaction = Transaction.objects.all().filter(user_id=user, tag__id=tag.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            
                        else:
                            transaction = Transaction.objects.all().filter(user_id=user, tag__id=tag.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
            
            else:
                debts = Debt.objects.filter(user_id=user)

                for debt in debts:
                    if 'subfilter' not in request.query_params:
                        transaction = Transaction.objects.filter(user_id=user,debt_id=debt.id)
                        for x in transaction:
                            transaction_data_list.append(x)    
                    else:
                        if request.query_params['subfilter'] == "Today":
                            if request.query_params["startdate"] == request.query_params["enddate"]:
                                transaction = Transaction.objects.filter(user_id=user, debt_id=debt.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                                for x in transaction:
                                    transaction_data_list.append(x)
                            else:
                                return Response({"status":False, "message":"please provide same start and end date when user subfilter 'Today'"}, status=status.HTTP_404_NOT_FOUND)    
                                
                        elif request.query_params['subfilter'] == "Week":
                            transaction = Transaction.objects.all().filter(user_id=user, debt_id=debt.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            

                        elif request.query_params['subfilter'] == "Month":
                            transaction = Transaction.objects.all().filter(user_id=user, debt_id=debt.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            

                        elif request.query_params['subfilter'] == "Year":
                            transaction = Transaction.objects.all().filter(user_id=user, debt_id=debt.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x) 

                        else:
                            transaction = Transaction.objects.all().filter(user_id=user, debt_id=debt.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                            for x in transaction:
                                transaction_data_list.append(x)
                            
        transaction_data_list = [i for n, i in enumerate(transaction_data_list) if i not in transaction_data_list[:n]]             
        
        transaction_serializer = TransactionSerializer(transaction_data_list, many=True)
        data_dict = transaction_serializer.data
        for x in data_dict:
            x["amount"] = float(x["amount"])
            if x["income_to"] is not None:
                try:
                    income_to = Income.objects.get(id=str(x["income_to"])).title
                except Income.DoesNotExist:
                    return Response({"status":False, "message":"income_to data not found"}, status=status.HTTP_404_NOT_FOUND)
                x["income_to_name"] = income_to
            if x["income_from"] is not None:
                try:
                    income_from = Income.objects.get(id=str(x["income_from"])).title
                except Income.DoesNotExist:
                    return Response({"status":False, "message":"income_from data not found"}, status=status.HTTP_404_NOT_FOUND)
                x["income_from_name"] = income_from
            if x["source"] is not None:
                try:
                    source = SourceIncome.objects.get(id=str(x["source"])).title
                except SourceIncome.DoesNotExist:
                    return Response({"status":False, "message":"source detail not found"}, status=status.HTTP_404_NOT_FOUND)
                x["source_name"] = source
            if x["goal"] is not None:
                try:
                    goal = Goal.objects.get(id=str(x["goal"])).title
                except Goal.DoesNotExist:
                    return Response({"status":False, "message":"goal detail not found"}, status=status.HTTP_404_NOT_FOUND)
                x["goal_name"] = goal
            if x["expense"] is not None:
                try:
                    expense = Expense.objects.get(id=str(x["expense"])).title
                except Expense.DoesNotExist:
                    return Response({"status":False, "message":"expense detail not found"}, status=status.HTTP_404_NOT_FOUND)
                x["expense_name"] = expense
            if x["periodic"] is not None:
                periodic = Periodic.objects.get(id=str(x["periodic"]))
                x["periodic_data"] = {'id':periodic.id,'start_date':periodic.start_date,'end_date':periodic.end_date,'week_days':periodic.week_days,'prefix':periodic.prefix,'prefix_value':periodic.prefix_value, 'created_at':periodic.created_at, 'modified_at':periodic.modified_at}
            if x["location"] is not None:
                location = Location.objects.get(id=str(x["location"]))
                x["location_data"] = {'id':location.id,'latitude':location.latitude,'longitude':location.longitude, 'created_at':location.created_at, 'modified_at':location.modified_at}
            if x["debt"] is not None:
                try:
                    debt = Debt.objects.get(id=str(x["debt"])).name
                except Debt.DoesNotExist:
                    return Response({"status":False, "message":"debt data not found"}, status=status.HTTP_404_NOT_FOUND)
                x["debt_name"] = debt
            
        header = {
            "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
        }
        
        LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":True, "message":"report data Fetched Succcessfully"}), email=request.user, status=True)
        return Response({"status":True, "message":"report data Fetched Succcessfully", "data":data_dict},status=status.HTTP_201_CREATED)
### Report API VIEW CODE END ###


########################################################################
class LogoutAPIView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status":True, "message":"User Successfully Logged Out."}, status=status.HTTP_204_NO_CONTENT)
########################################################################

# User Reset / Forgot Password API Start #
class ResetPassword(APIView):
    # User Got The Reset Password Link on Email. #
    def post(self, request):
        if 'email' in request.data and request.data["email"] != "":
            user = User.objects.get(email=request.data["email"])
            if user:
                expire = dt.now().date() + timedelta(days=1)
                uid = urlsafe_base64_encode(force_bytes({"user":user.email, "expire":str(expire)}))
                link = request.build_absolute_uri('?uid=%s'%(uid))
            
                subject = 'Password Reset Email'
                message = render_to_string('reset.html', {'name': user.firstname, "link":link})
                sender = settings.EMAIL_HOST_USER
                receiver = (request.data["email"],)
                mssg = EmailMessage(subject, message, sender, receiver)
                mssg.content_subtype = "html"
                mssg.send()
            else:
                return Response({"status":False, "message":"User doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"status":True, "message":"Email Send Successfully, Please check your Spam."}, status=status.HTTP_200_OK)
        else:
            return Response({"status":False, "message":"Please Enter Email Address."}, status=status.HTTP_400_BAD_REQUEST)
    
    # User Redirect to Reset Form. #
    def get(self, request):
        uid = request.query_params.get("uid")
        user_data = urlsafe_base64_decode(uid)
        user_data = eval(user_data)
        expire = dt.strptime(str(user_data["expire"]), "%Y-%m-%d").date()
        if dt.now().date() <= expire:
            user = user_data["user"]
            return render(request, "reset_password.html", {"user":user, "message":""})
        else:
            return render(request, "reset_password.html", {"message":"Reset Token Expiered."})  

# Reset Password Post Method #
def confirm(request):
    if request.method == "POST":
        if request.POST.get("password") != "" and request.POST.get("password2") != "":
            if request.POST["password"] == request.POST.get("password2"):
                user = User.objects.filter(email=str(request.POST.get("user")))
                if user == []:
                    return render(request, "reset_password.html", {"message":"user not found."})
                password = make_password(request.POST.get("password"))
                user.update(password=password)
                return render(request, "reset_password.html", {"message":"Password Successfully Reset."})
            else:
                return render(request, "reset_password.html", {"message":"Password and Re-password doesn't match."})
        else:
            return render(request, "reset_password.html", {"message":"Password and Re-password cannot be blank."})
# User Reset / Forgot Password API End #

# Export Data in CSV or XLS #
class Export(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        data = ""
        if 'export' in request.query_params and request.query_params["export"] != "None" and len(request.query_params["export"]) > 2:
            token_check = check_token(user=request.user)
            if token_check != "":
                return Response({"status":False, "message":"Invalid Token / Token was Blocked."}, status=status.HTTP_400_BAD_REQUEST)

            transaction_data_list = []
            data_list = []
            try:
                user = User.objects.get(email=request.user).id
            except User.DoesNotExist:
                header = {
                    "HTTP_AUTHORIZATION":request.META['HTTP_AUTHORIZATION']
                }
                LogsAPI.objects.create(apiname=str(request.get_full_path()), request_header=json.dumps(header), response_data=json.dumps({"status":False, "message":"User Detail Doesn't Exist"}), email=request.user, status=False)
                return Response({"status":False, "message":"User Detail Doesn't Exist"},status=status.HTTP_404_NOT_FOUND)
            
            
            transaction = Transaction.objects.filter(user_id=user)
            if transaction != []:
                for x in transaction:
                    transaction_data_list.append(x)
            else:
                return Response({"status":False, "message":"Transaction Data Doesn't Exist."}, status=status.HTTP_404_NOT_FOUND)
            
            if (('filter' in request.query_params and request.query_params['filter'] is None) and ('startdate' in request.query_params and request.query_params['startdate'] is not None) and ('enddate' in request.query_params and request.query_params['enddate'] is not None)):
                transaction = Transaction.objects.all().filter(user_id=user, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                for x in transaction:
                    transaction_data_list.append(x)
                 
            if 'filter' in request.query_params and request.query_params['filter'] is not None:
                if len(transaction_data_list) > 0:
                    del transaction_data_list[:]
                if request.query_params['filter'] == "income":
                    income_id = Income.objects.filter(user_id=user)
                    
                    for income in income_id:
                        transaction = Transaction.objects.all().filter(user_id=user, income_from_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                        for x in transaction:
                            transaction_data_list.append(x)
                        
                        transaction = Transaction.objects.all().filter(user_id=user, income_to_id=income.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                        for x in transaction:
                            transaction_data_list.append(x)
                        
                elif request.query_params['filter'] == "goal":
                    goal_id = Goal.objects.filter(user_id=user)

                    for goal in goal_id: 
                        transaction = Transaction.objects.all().filter(user_id=user, goal_id=goal.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                        for x in transaction:
                            transaction_data_list.append(x)
                
                elif request.query_params['filter'] == "expense":
                    expense_id = Expense.objects.filter(user_id=user)

                    for expense in expense_id:
                        transaction = Transaction.objects.all().filter(user_id=user, expense_id=expense.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                        for x in transaction:
                            transaction_data_list.append(x)

                elif request.query_params['filter'] == "source":
                    source_id = SourceIncome.objects.filter(user_id=user)

                    for source in source_id:
                        transaction = Transaction.objects.all().filter(user_id=user, source_id=source.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                        for x in transaction:
                            transaction_data_list.append(x)

                elif request.query_params['filter'] == "tag":
                    tag_id = Tag.objects.filter(user_id=user)

                    for tag in tag_id:
                        transaction = Transaction.objects.all().filter(user_id=user, tag__id=tag.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                        for x in transaction:
                            transaction_data_list.append(x)
                
                else:
                    debts = Debt.objects.filter(user_id=user)

                    for debt in debts:
                        transaction = Transaction.objects.all().filter(user_id=user, debt_id=debt.id, created_at__range=[request.query_params["startdate"], request.query_params["enddate"]])
                        for x in transaction:
                            transaction_data_list.append(x)
                                
            transaction_data_list = [i for n, i in enumerate(transaction_data_list) if i not in transaction_data_list[:n]]             
           
            transaction_serializer = TransactionSerializer(transaction_data_list, many=True)
            data_dict = transaction_serializer.data
        
            for x in data_dict:
                x["amount"] = float(x["amount"])
                if x["income_to"] is not None:
                    try:
                        income_to = Income.objects.get(id=str(x["income_to"])).title
                    except Income.DoesNotExist:
                        return Response({"status":False, "message":"income_to data not found"}, status=status.HTTP_404_NOT_FOUND)
                    x["income_to_name"] = income_to
                else:
                    x["income_to_name"] = None

                if x["income_from"] is not None:
                    try:
                        income_from = Income.objects.get(id=str(x["income_from"])).title
                    except Income.DoesNotExist:
                        return Response({"status":False, "message":"income_from data not found"}, status=status.HTTP_404_NOT_FOUND)
                    x["income_from_name"] = income_from
                else:
                    x["income_from_name"] = None

                if x["source"] is not None:
                    try:
                        source = SourceIncome.objects.get(id=str(x["source"])).title
                    except SourceIncome.DoesNotExist:
                        return Response({"status":False, "message":"source detail not found"}, status=status.HTTP_404_NOT_FOUND)
                    x["source_name"] = source
                else:
                    x["source_name"] = None
                
                if x["goal"] is not None:
                    try:
                        goal = Goal.objects.get(id=str(x["goal"])).title
                    except Goal.DoesNotExist:
                        return Response({"status":False, "message":"goal detail not found"}, status=status.HTTP_404_NOT_FOUND)
                    x["goal_name"] = goal
                else:
                    x["goal_name"] = None

                if x["expense"] is not None:
                    try:
                        expense = Expense.objects.get(id=str(x["expense"])).title
                    except Expense.DoesNotExist:
                        return Response({"status":False, "message":"expense detail not found"}, status=status.HTTP_404_NOT_FOUND)
                    x["expense_name"] = expense
                else:
                    x["expense_name"] = None
                
                if x["periodic"] is not None:
                    periodic = Periodic.objects.get(id=str(x["periodic"]))
                    x["periodic_data"] = {'id':periodic.id,'start_date':periodic.start_date,'end_date':periodic.end_date,'week_days':periodic.week_days,'prefix':periodic.prefix,'prefix_value':periodic.prefix_value, 'created_at':periodic.created_at, 'modified_at':periodic.modified_at}
                else:
                    x["periodic_data"] = None
                
                if x["location"] is not None:
                    location = Location.objects.get(id=str(x["location"]))
                    x["location_data"] = {'id':location.id,'latitude':location.latitude,'longitude':location.longitude, 'created_at':location.created_at, 'modified_at':location.modified_at}
                else:
                    x["location_data"] = None
                
                if x["debt"] is not None:
                    try:
                        debt = Debt.objects.get(id=str(x["debt"])).name
                    except Debt.DoesNotExist:
                        return Response({"status":False, "message":"debt data not found"}, status=status.HTTP_404_NOT_FOUND)
                    x["debt_name"] = debt
                else:
                    x["debt_name"] = None
            
            if request.query_params["export"] == "csv":
                del data_list[:]
                for y in data_dict:
                    if y["source"] is not None and y["income_to"] is not None and x["income_from"] is None and x["expense"] is None and x["goal"] is None and x["debt"] is None:
                        if y["periodic"] is not None:
                            data = {
                                "date":y["created_at"],
                                "type":"Source To Income.",
                                "from":y["source_name"],
                                "to":y["income_to_name"],
                                "amount":y["amount"],
                                "recurrence":y["periodic_data"]["week_days"],
                                "note":y["description"]
                            }
                        else:
                            data = {
                                "date":y["created_at"],
                                "type":"Source To Income.",
                                "from":y["source_name"],
                                "to":y["income_to_name"],
                                "amount":y["amount"],
                                "recurrence":None,
                                "note":y["description"]
                            }
                    elif y["income_from"] is not None and y["income_to"] is not None and x["source"] is None and x["expense"] is None and x["goal"] is None and x["debt"] is None:
                        if y["periodic"] is not None:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Income.",
                                "from":y["income_from_name"],
                                "to":y["income_to_name"],
                                "amount":y["amount"],
                                "recurrence":y["periodic_data"]["week_days"],
                                "note":y["description"]
                            }
                        else:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Income.",
                                "from":y["income_from_name"],
                                "to":y["income_to_name"],
                                "amount":y["amount"],
                                "recurrence":None,
                                "note":y["description"]
                            }
                    elif y["income_from"] is not None and y["expense"] is not None and x["source"] is None and x["income_to"] is None and x["goal"] is None and x["debt"] is None:
                        if y["periodic"] is not None:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Expense.",
                                "from":y["income_from_name"],
                                "to":y["expense_name"],
                                "amount":y["amount"],
                                "recurrence":y["periodic_data"]["week_days"],
                                "note":y["description"]
                            }
                        else:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Expense.",
                                "from":y["income_from_name"],
                                "to":y["expense_name"],
                                "amount":y["amount"],
                                "recurrence":None,
                                "note":y["description"]
                            }
                    elif y["income_from"] is not None and y["goal"] is not None and x["source"] is None and x["income_to"] is None and x["expense"] is None and x["debt"] is None:
                        if y["periodic"] is not None:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Goal.",
                                "from":y["income_from_name"],
                                "to":y["goal_name"],
                                "amount":y["amount"],
                                "recurrence":y["periodic_data"]["week_days"],
                                "note":y["description"]
                            }
                        else:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Goal.",
                                "from":y["income_from_name"],
                                "to":y["goal_name"],
                                "amount":y["amount"],
                                "recurrence":None,
                                "note":y["description"]
                            }
                    else:
                        if y["periodic"] is not None:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Debt.",
                                "from":y["income_from_name"],
                                "to":y["debt_name"],
                                "amount":y["amount"],
                                "recurrence":y["periodic_data"]["week_days"],
                                "note":y["description"]
                            }
                        else:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Debt.",
                                "from":y["income_from_name"],
                                "to":y["debt_name"],
                                "amount":y["amount"],
                                "recurrence":None,
                                "note":y["description"]
                            }
            
                    data_list.append(data)

                response = StringIO()
                writer = csv.writer(response)
                writer.writerow(["Date", "Type", "From", "To", "Amount", "Recurrence", "Note"])

                for x in data_list:
                    writer.writerow([x["date"], x["type"], x["from"], x["to"], x["amount"], x["recurrence"], x["note"]])
                
                # Send Email Code Start #
                email = EmailMessage()
                subject = 'Transaction Statement From Date %s To %s'%(request.query_params["startdate"], request.query_params["enddate"])
                email.subject = subject
                email.body = "Statement Attachment is Below"
                email.from_email = settings.EMAIL_HOST_USER
                email.to = [request.user,]
                email.attach('statement.csv', response.getvalue(), 'text/csv')
                email.send(fail_silently=False)
                # Send Email Code End #
            else:
                del data_list[:]
                for y in data_dict:
                    if y["source"] is not None and y["income_to"] is not None and x["income_from"] is None and x["expense"] is None and x["goal"] is None and x["debt"] is None:
                        if y["periodic"] is not None:
                            data = {
                                "date":y["created_at"],
                                "type":"Source To Income.",
                                "from":y["source_name"],
                                "to":y["income_to_name"],
                                "amount":y["amount"],
                                "recurrence":y["periodic_data"]["week_days"],
                                "note":y["description"]
                            }
                        else:
                            data = {
                                "date":y["created_at"],
                                "type":"Source To Income.",
                                "from":y["source_name"],
                                "to":y["income_to_name"],
                                "amount":y["amount"],
                                "recurrence":None,
                                "note":y["description"]
                            }
                    elif y["income_from"] is not None and y["income_to"] is not None and x["source"] is None and x["expense"] is None and x["goal"] is None and x["debt"] is None:
                        if y["periodic"] is not None:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Income.",
                                "from":y["income_from_name"],
                                "to":y["income_to_name"],
                                "amount":y["amount"],
                                "recurrence":y["periodic_data"]["week_days"],
                                "note":y["description"]
                            }
                        else:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Income.",
                                "from":y["income_from_name"],
                                "to":y["income_to_name"],
                                "amount":y["amount"],
                                "recurrence":None,
                                "note":y["description"]
                            }
                    elif y["income_from"] is not None and y["expense"] is not None and x["source"] is None and x["income_to"] is None and x["goal"] is None and x["debt"] is None:
                        if y["periodic"] is not None:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Expense.",
                                "from":y["income_from_name"],
                                "to":y["expense_name"],
                                "amount":y["amount"],
                                "recurrence":y["periodic_data"]["week_days"],
                                "note":y["description"]
                            }
                        else:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Expense.",
                                "from":y["income_from_name"],
                                "to":y["expense_name"],
                                "amount":y["amount"],
                                "recurrence":None,
                                "note":y["description"]
                            }
                    elif y["income_from"] is not None and y["goal"] is not None and x["source"] is None and x["income_to"] is None and x["expense"] is None and x["debt"] is None:
                        if y["periodic"] is not None:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Goal.",
                                "from":y["income_from_name"],
                                "to":y["goal_name"],
                                "amount":y["amount"],
                                "recurrence":y["periodic_data"]["week_days"],
                                "note":y["description"]
                            }
                        else:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Goal.",
                                "from":y["income_from_name"],
                                "to":y["goal_name"],
                                "amount":y["amount"],
                                "recurrence":None,
                                "note":y["description"]
                            }
                    else:
                        if y["periodic"] is not None:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Debt.",
                                "from":y["income_from_name"],
                                "to":y["debt_name"],
                                "amount":y["amount"],
                                "recurrence":y["periodic_data"]["week_days"],
                                "note":y["description"]
                            }
                        else:
                            data = {
                                "date":y["created_at"],
                                "type":"Income To Debt.",
                                "from":y["income_from_name"],
                                "to":y["debt_name"],
                                "amount":y["amount"],
                                "recurrence":None,
                                "note":y["description"]
                            }
                    data_list.append(tuple(data.values()))

                response = BytesIO()
                wb = xlwt.Workbook(encoding="utf-8")
                ws = wb.add_sheet("statement")
                row_num = 0
                font_style=xlwt.XFStyle()
                font_style.font.bold= True

                columns = ["Date", "Type", "From", "To", "Amount", "Recurrence", "Note"]
                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                font_style = xlwt.XFStyle()

                
                rows = data_list
                
                for row in rows:
                    row_num += 1
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, str(row[col_num]), font_style)
                wb.save(response)
                # Send Email Code Start #
                email = EmailMessage()
                subject = 'Transaction Statement From Date %s To %s'%(request.query_params["startdate"], request.query_params["enddate"])
                email.subject = subject
                email.body = "Statement Attachment is Below"
                email.from_email = settings.EMAIL_HOST_USER
                email.to = [request.user,]
                email.attach('statement.xlsx', response.getvalue(), 'application/vnd.ms-excel')
                email.send(fail_silently=False)
                # Send Email Code End #
            return Response({"status":True, "message":"Exported successfully and sent to your registered email."}, status=status.HTTP_200_OK)
        else:
            return Response({"status":False, "message":"Please provide export choice as like csv, excel."}, status=status.HTTP_400_BAD_REQUEST)