# Generated by Django 4.0.6 on 2022-07-25 10:43

import Account.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Debt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(default='', max_length=1000)),
                ('name', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('paid_amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('date', models.DateField()),
                ('is_paid', models.BooleanField(default=False)),
                ('is_partial_paid', models.BooleanField(default=False)),
                ('is_completed', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(max_length=1000)),
                ('title', models.CharField(max_length=255)),
                ('spent_amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('amount_limit', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('time_range', models.CharField(max_length=255)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(max_length=1000)),
                ('title', models.CharField(max_length=255)),
                ('added_amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now=True)),
                ('is_completed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(max_length=1000)),
                ('title', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(blank=True, default='0.00', null=True)),
                ('longitude', models.FloatField(blank=True, default='0.00', null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LogsAPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('apiname', models.CharField(max_length=255)),
                ('request_header', models.CharField(default='', max_length=2000)),
                ('request_parameter', models.CharField(default='', max_length=2000)),
                ('request_data', models.CharField(max_length=5000)),
                ('response_data', models.CharField(max_length=5000)),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='Email')),
                ('status', models.BooleanField(default=False)),
                ('created_date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('android_r_token', models.TextField()),
                ('ios_r_token', models.TextField()),
                ('payload', models.TextField()),
                ('date', models.DateField()),
                ('created_date', models.DateField(auto_now_add=True)),
                ('modified_date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Periodic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('week_days', models.CharField(blank=True, max_length=5000, null=True)),
                ('prefix', models.CharField(blank=True, max_length=255, null=True)),
                ('prefix_value', models.IntegerField(blank=True, null=True)),
                ('status_days', models.CharField(blank=True, max_length=5000, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SourceIncome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('icon', models.CharField(max_length=1000)),
                ('spent_amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('created_at', models.DateField(default=datetime.date.today)),
                ('modified_at', models.DateField(default=datetime.date.today)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateField(default=datetime.date.today)),
                ('modified_at', models.DateField(default=datetime.date.today)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='Email')),
                ('mobile', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('birthdate', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('gender', models.CharField(choices=[('male', 'male'), ('female', 'female')], max_length=6)),
                ('registered_by', models.CharField(choices=[('manual', 'manual'), ('facebook', 'facebook'), ('google', 'google'), ('apple', 'apple')], max_length=10)),
                ('device_token', models.CharField(blank=True, default='', max_length=5000, null=True)),
                ('social_id', models.CharField(blank=True, default='', max_length=15000, null=True)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to=Account.models.upload_to)),
                ('setup_count', models.CharField(default=0, max_length=255)),
                ('is_setup', models.BooleanField(default=False)),
                ('is_agree', models.BooleanField(default=0)),
                ('is_registered', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_subscribed', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=True)),
                ('country_code', models.CharField(blank=True, default='', max_length=5, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('subscription', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='subscribed', to='Account.subscription')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('description', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('transaction_amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('amount', models.DecimalField(decimal_places=2, default='0.00', max_digits=15)),
                ('created_at', models.DateField()),
                ('modified_at', models.DateField()),
                ('is_completed', models.BooleanField(default=True)),
                ('debt', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='debt', to='Account.debt')),
                ('expense', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_expense', to='Account.expense')),
                ('goal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_goal', to='Account.goal')),
                ('income_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_from_income', to='Account.income')),
                ('income_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_to_income', to='Account.income')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location', to='Account.location')),
                ('periodic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='periodic', to='Account.periodic')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_source', to='Account.sourceincome')),
                ('tag', models.ManyToManyField(blank=True, related_name='tags', to='Account.tag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='tag',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_tags', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sourceincome',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_main_income', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification', models.BooleanField(default=False)),
                ('min_pass_3', models.BooleanField(default=False)),
                ('language', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('currency', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='income',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='income', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='goal',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goal', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='expense',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Exchangerate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency_name', models.CharField(max_length=255)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='currency', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='debt',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_debt', to=settings.AUTH_USER_MODEL),
        ),
    ]
