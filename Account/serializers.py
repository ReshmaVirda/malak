from locale import currency
from rest_framework import serializers
from Account.models import User, Subscription,Income,Expense,Goal, SourceIncome, Exchangerate, Location, Periodic, Tag, Transaction, Setting, Debt
from datetime import datetime, date
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

# Registration Serializer Code Start #
class UserRegistrationSerializer(serializers.ModelSerializer):
    ''' User Register by firstname, lastname, email, mobile, gender, country, birthdate, is_agree,
    registered_by,  password. Here, country and birthdate is optional fields'''
    profile_pic = serializers.ImageField(required=False, default="")
    password = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'mobile', 'country', 'birthdate', 'gender', 'registered_by', 'device_token', 'social_id', 'profile_pic', 'is_agree', 'password', 'country_code','created_at','modified_at']
        extra_kwargs={
            'password':{'write_only':True},
            'country':{'required':False},
            'birthdate':{'required':False},
            'device_token':{'required':False},
            'social_id':{'required':False},
            'profile_pic':{'required':False},
            "created_at":{'read_only':True, 'required':False},
            "modified_at":{'required':False}
        }
    
    def create(self, validate_data):
        # print(validate_data)
        return User.objects.create(**validate_data)
# Registration Serializer Code End #

# Login Serializer Code Start #
class UserLoginSerializer(serializers.ModelSerializer):
    ''' User Login by email and password and registered_by '''
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password', 'registered_by']
# Login Serializer Code End #

# Social Login Code Start #
class UserSocialLoginSerializer(serializers.ModelSerializer):
    ''' User Login by email and social_id and registered_by '''
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'social_id', 'registered_by']
# Social Login Code End #

# User Profile Serializer Code Start #
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'firstname', 'lastname', 'setup_count', 'is_setup', 'email','mobile', 'country', 'birthdate', 'gender', 'registered_by', 'device_token', 'social_id', 'subscription_id', 'profile_pic', 'is_agree', 'is_subscribed', 'country_code', 'is_active', 'is_admin']
        extra_kwargs={
            'id':{'read_only':True},
            'email':{'read_only':True},
            'is_agree':{'read_only':True},
            'is_active':{'read_only':True},
            'is_admin':{'read_only':True},
            'country_code':{"required":False},
            'registered_by':{'required':False},
            'firstname':{'required':False},
            'social_id':{'required':False},
            'lastname':{'required':False},
            'profile_pic':{'required':False},
            'subscription_id':{'required':False},
            'device_token':{'required':False},
            'birthdate':{'required':False},
            'mobile':{'required':False},
            'country':{'required':False},
            'gender':{'required':False},
            'setup_count':{'required':False},
            'is_setup':{'required':False},
            'is_subscribed':{'required':False}
        }
# User Profile Serializer Code End #

# User Change Password Serializer Code Start #
class UserChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=255, write_only=True, style={'input_type':'password'})
    new_password2 = serializers.CharField(max_length=255, write_only=True, style={'input_type':'password'})

    class Meta:
        fields = ['new_password', 'new_password2']

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password2 = attrs.get('new_password2')
        user = self.context.get('user')
        if new_password != new_password2:
            raise serializers.ValidationError("Password and Confirm Password Doesn't Match")
        user.set_password(new_password)
        user.save()
        return attrs
# User Change Password Serializer Code End #

# User Subscription Serializer Code Start #
class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'name', 'amount', 'created_at', 'modified_at']

        extra_kwargs={
            'id':{'read_only':True},
            'created_at':{'read_only':True},
            'modified_at':{'required':False},
            'name':{'required':False},
            'amount':{'required':False}
        }
    
    def create(self, validate_data):
        return Subscription.objects.create(**validate_data)
# User Subscription Serializer Code End #

# User Income Serializer Code Start #
class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['id','icon','title','amount','currency','created_at','modified_at']
        extra_kwargs = {
            "user":{'write_only':True},
            'icon':{'required':False},
            'title':{'required':False},
            'amount':{'required':False},
            "created_at":{'read_only':True, 'required':False},
            "modified_at":{'required':False},
            "currency":{"required":False}
        }

    def create(self, validated_data):
        income = Income.objects.create(
            user=self.context['request'].user, 
            icon=validated_data['icon'], 
            title=validated_data['title'],
            amount=validated_data['amount'],
            currency=validated_data['currency'])
        income.save()
        return income
# User Income Serializer Code End #

# User Expense Serializer Code Start #
class ExpenseSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True,slug_field='email')
    class Meta:
        model = Expense
        fields = ['id','icon','title','spent_amount', 'amount_limit','time_range','currency','created_at', 'modified_at', 'user']
        extra_kwargs = {
            'id':{'read_only':True},
            "user":{'read_only':True},
            'icon':{'required':False},
            'title':{'required':False},
            'spent_amount':{"required":False},
            'amount_limit':{'required':False},
            'time_range':{'required':False},
            "created_at":{'read_only':True, 'required':False},
            "modified_at":{'required':False},
            "currency":{"required":False}
        }

    def create(self, validated_data):
        expense = Expense.objects.create(
            user=self.context['request'].user,  
            icon=validated_data['icon'],
            title=validated_data['title'],
            amount_limit=validated_data['amount_limit'],
            time_range=validated_data['time_range'],
            currency=validated_data['currency']
            )
        expense.save()
        return expense
# User Expense Serializer Code End #

# User goal Serializer Code Start #
class GoalsSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True,slug_field='email')

    class Meta:
        model = Goal
        fields = ['id','icon','title', 'added_amount', 'amount','is_completed','currency', 'created_at', 'modified_at', 'user']
        extra_kwargs = {
            'id':{'read_only':True},
            "user":{'write_only':True},
            'icon':{'required':False},
            'title':{'required':False},
            'amount':{'required':False},
            "created_at":{'read_only':True, 'required':False},
            "is_completed":{'read_only':True, 'required':False},
            "modified_at":{'required':False},
            "added_amount":{"required":False},
            "currency":{"required":False}
        }

    def create(self, validated_data):
        goals =  Goal.objects.create(
            user=self.context['request'].user,  
            icon=validated_data['icon'],
            title=validated_data['title'],
            amount=validated_data['amount'],
            currency=validated_data['currency'])
        goals.save()
        return goals   
# User goal Serializer Code End #

# User SourceIncome Serializer Code Start #        
class SourceIncomeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True, slug_field="email")
    class Meta:
        model = SourceIncome
        fields = ['id','icon','title','spent_amount', 'amount', 'currency', 'user', 'created_at','modified_at']
        extra_kwargs = {
            "id":{"read_only":True},
            "icon":{"required":False},
            "title":{"required":False},
            "spent_amount":{"required":False},
            "amount":{"required":False},
            "currency":{"required":False}
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return SourceIncome.objects.create(**validated_data) 
# User SourceIncome Serializer Code end # 

# User Currency Serializer Code Start #
class ExchangerateSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True,slug_field='email')

    class Meta:
        model = Exchangerate
        fields = ['id', 'currency_name','is_default', 'created_at', 'modified_at', 'user']
        extra_kwargs = {
            'id':{'read_only':True},
            "user":{'write_only':True},
            "created_at":{'read_only':True, 'required':False},
            "modified_at":{'required':False}
        }

    def create(self, validated_data):
        validated_data["user"] = self.context['request'].user
        return Exchangerate.objects.create(**validated_data)
# User Currency Serializer Code End #

# User Location Serializer Code Start #
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id','latitude','longitude', 'created_at', 'modified_at']

        extra_kwargs = {
            'id':{'read_only':True},
            "created_at":{'read_only':True, 'required':False},
            "modified_at":{'required':False}
        }

    def create(self, validated_data):
        location = Location.objects.create(
            latitude=float(validated_data['latitude']),
            longitude=float(validated_data['longitude']))
        location.save()
        return location
# User Location Serializer Code End #

# User Periodic Serializer Code Start #
class PeriodicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodic
        fields = ['id','start_date','end_date','week_days','status_days','prefix','prefix_value', 'created_at', 'modified_at']

        extra_kwargs = {
            'id':{'read_only':True},
            'start_date':{'required':False},
            'week_days':{'required':False},
            'status_days':{"required":False},
            "created_at":{'read_only':True, 'required':False},
            "modified_at":{'required':False}
        }

    def create(self, validated_data):
        return Periodic.objects.create(**validated_data)
# User Periodic Serializer Code End #

# User Tag Serializer Code Start # 
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','name','user','created_at','modified_at']
        extra_kwargs = {
            "name":{"required":False},
            "user":{"read_only":True},
            "created_at":{'read_only':True, 'required':False},
            "modified_at":{'required':False}
        }
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Tag.objects.create(**validated_data)
# User Tag Serializer Code end # 

# User Transaction Serializer Code Start #      Update
class TransactionSerializer(serializers.ModelSerializer):
    income_to = serializers.SlugRelatedField(slug_field="id", queryset=Income.objects.all(), required=False)
    income_from = serializers.SlugRelatedField(slug_field="id", queryset=Income.objects.all(), required=False)
    expense = serializers.SlugRelatedField(slug_field="id", queryset=Expense.objects.all(), required=False)
    goal = serializers.SlugRelatedField(slug_field="id", queryset=Goal.objects.all(), required=False)
    source = serializers.SlugRelatedField(slug_field="id", queryset=SourceIncome.objects.all(), required=False)
    user = serializers.SlugRelatedField(read_only=True, slug_field="email")
    debt = serializers.SlugRelatedField(slug_field="id", queryset=Debt.objects.all(), required=False)

    class Meta:
        model = Transaction
        fields = ['id', 'title','description','transaction_amount','converted_transaction','converted_amount','amount','income_to', 'income_from', 'expense', 'goal', 'source','debt', 'user', 'location','periodic', 'tag', 'is_completed', 'created_at', 'modified_at']
        extra_kwargs = {
            "id":{"read_only":True},
            "user":{'write_only':True},
            'title':{'required':False},
            'description':{'required':False},
            'amount':{'required':False},
            "created_at":{'required':False},
            "modified_at":{'required':False},
            "tag":{"required":False},
            "transaction_amount":{"required":False},
            "converted_transaction":{"required":False},
            'is_completed':{"required":False},
            "converted_amount":{"required":False}
        }

    def create(self, validated_data):
        validated_data["user_id"] = self.context["user"]
 
        tags = ""
        if 'tag' in validated_data and validated_data['tag'] is not None:
            tags = (validated_data.pop('tag'))
        
        if 'created_at' in validated_data and 'modified_at' in validated_data:
            validated_data.update({"created_at":datetime.strptime(str(validated_data["created_at"]), '%Y-%m-%d').date()})
            validated_data.update({"modified_at":datetime.strptime(str(validated_data["modified_at"]), '%Y-%m-%d').date()})
        else:
            validated_data.update({"created_at":date.today()})
            validated_data.update({"modified_at":date.today()})

        validated_data.update({"transaction_amount":validated_data["amount"]})
        validated_data.update({"converted_amount":validated_data["converted_transaction"]})
        
        if 'is_completed' not in validated_data:
            validated_data.update({"is_completed":True})
        Transaction_Data = Transaction.objects.create(**validated_data)
        
        if tags != None:
            for x in tags:
                Transaction_Data.tag.add(x)
        return Transaction_Data
# User Transaction Serializer Code End #

# User Setting Serializer Code Start #
class SettingSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True,slug_field='email')
    class Meta:
        model = Setting
        fields = ['id','notification','min_pass_3','language','currency','created_at','modified_at','user']
        extra_kwargs = {
            "notification":{"required":False},
            "min_pass_3":{"required":False},
            "language":{"required":False},
            "currency":{"required":False},
            "user":{"read_only":True}
        }


    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Setting.objects.create(**validated_data)
# User Setting Serializer Code End #

# User Debt Serializer Code Start #
class DebtSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Debt
        fields = ['id','icon','name','date','amount','paid_amount','is_paid','is_partial_paid','is_completed', 'currency','created_at','modified_at','user']
        extra_kwargs = {
            "id":{"read_only":True},
            "user":{"read_only":True},
            'icon':{"required":False},
            "name":{"required":False},
            "date":{"required":False},
            "amount":{"required":False},
            "paid_amount":{"required":False},
            "is_paid":{"required":False},
            "is_partial_paid":{"required":False},
            "is_completed":{"required":False},
            "currency":{"required":False}
        }


    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        if 'date' in validated_data:
            validated_data.update({"date":datetime.strptime(str(validated_data["date"]), '%Y-%m-%d').date()})
        return Debt.objects.create(**validated_data)
# User Debt Serializer Code End #  

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')