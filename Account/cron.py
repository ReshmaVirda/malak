import json
from django_cron import CronJobBase, Schedule
from .models import Income, Transaction, SourceIncome, Expense, Goal, Debt, Periodic, notification, User
from datetime import datetime as dt, date
from .push_notifications import Notification

class MyCronJob(CronJobBase):
    RUN_EVERY_DAYS = 1 # every 1 day

    schedule = Schedule(run_on_days=RUN_EVERY_DAYS)
    code = 'cron.MyCronJob'    # a unique code

    def do(self):
        print("hello")
        ############# REMINDERS #######################
        ## Debt ##
        debts = Debt.objects.all()
        for x in debts:
            settle_date = dt.strptime(str(x.date), "%Y-%m-%d").date()
            if date.today() == settle_date:
                user = ''
                try:
                    user = User.objects.get(id=x.user_id)
                except User.DoesNotExist:
                    return "User Doesn't Exist"

                get_notification = Notification.Notify(deviceToken=user.device_token,title="Debt (Reminder)", message="Your debt payment of amount %s %s is planned for today."%(str(x.currency), str(x.amount)), notify_status="DEBT_PLANNED")
                notification.objects.create(title="Debt (Reminder)", message="Your debt payment of amount %s %s is planned for today."%(str(x.currency), str(x.amount)), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]))              
        
        ## Reccurence ##
        reccurences = Periodic.objects.all()
        for x in reccurences:
            repeat_dates = []
            repeat_status = []
            repeat_dates = str(x.week_days).split(',')
            repeat_status = str(x.status_days).split(',')
        
            for i, repeat_date in enumerate(repeat_dates):
                repeat = dt.strptime(str(repeat_date), "%Y-%m-%d").date()
                if repeat == date.today() and repeat_status[i].encode('ascii').decode('UTF-8') == "False":
                    user = ''
                    get_transaction = ''
                    
                    try:
                        get_transaction = Transaction.objects.get(periodic_id=x.id)
                    except Transaction.DoesNotExist:
                        return "Transaction Detail Not Found"
                    
                    try:
                        user = User.objects.get(id=get_transaction.user_id)
                    except User.DoesNotExist:
                        return "User Doesn't Exist"

                    if ((get_transaction.source_id is not None and get_transaction.income_to_id is not None) and (get_transaction.income_from_id is None and get_transaction.goal_id is None and get_transaction.expense_id is None and get_transaction.debt is None)):
                        source = ''
                        income = ''

                        try:
                            source = SourceIncome.objects.get(id=get_transaction.source_id)
                        except SourceIncome.DoesNotExist:
                            return "Source Income Doesn't Exist"
                        
                        try:
                            income = Income.objects.get(id=get_transaction.income_to_id)
                        except Income.DoesNotExist:
                            return "Income Doesn't Exist"
                        
                        get_notification = Notification.Notify(deviceToken=user.device_token,title="Recurrence from %s to %s"%(source.title, income.title), message="Your planed payment %s %s deducted from source %s and added %s %s to income %s"%(source.currency, get_transaction.transaction_amount, source.title, income.currency, get_transaction.converted_transaction, income.title), notify_status="RECURRENCE_PLANNED")
                        notification.objects.create(title="Recurrence from %s to %s"%(source.title, income.title), message="Your planed payment %s %s deducted from source %s and added %s %s to income %s"%(source.currency, get_transaction.transaction_amount, source.title, income.currency, get_transaction.converted_transaction, income.title), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]))    
                    
                    elif ((get_transaction.income_from_id is not None and get_transaction.income_to_id is not None) and (get_transaction.source_id is None and get_transaction.goal_id is None and get_transaction.expense_id is None and get_transaction.debt is None)): 
                        income_from = ''
                        income_to = ''

                        try:
                            income_from = Income.objects.get(id=get_transaction.income_from_id)
                        except Income.DoesNotExist:
                            return "Income_From Doesn't Exist"

                        try:
                            income_to = Income.objects.get(id=get_transaction.income_to_id)
                        except Income.DoesNotExist:
                            return "Income_To Doesn't Exist"

                        get_notification = Notification.Notify(deviceToken=user.device_token,title="Recurrence from %s to %s"%(income_from.title, income_to.title), message="Your planed payment %s %s deducted from income %s and added %s %s to income %s"%(income_from.currency, get_transaction.transaction_amount, income_from.title, income_to.currency, get_transaction.converted_transaction, income_to.title), notify_status="RECURRENCE_PLANNED")
                        notification.objects.create(title="Recurrence from %s to %s"%(income_from.title, income_to.title), message="Your planed payment %s %s deducted from income %s and added %s %s to income %s"%(income_from.currency, get_transaction.transaction_amount, income_from.title, income_to.currency, get_transaction.converted_transaction, income_to.title), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]))

                    elif ((get_transaction.income_from_id is not None and get_transaction.expense_id is not None) and (get_transaction.source_id is None and get_transaction.goal_id is None and get_transaction.income_to_id is None and get_transaction.debt is None)):
                        get_notification = Notification.Notify(deviceToken=user.device_token,title="Debt (Reminder)", message="Your debt payment of amount %s %s is planned for today."%(str(x.currency), str(x.amount)), notify_status="DEBT_PLANNED")
                        notification.objects.create(title="Debt (Reminder)", message="Your debt payment of amount %s %s is planned for today."%(str(x.currency), str(x.amount)), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]))

                    elif ((get_transaction.income_from_id is not None and get_transaction.goal_id is not None) and (get_transaction.source_id is None and get_transaction.income_to_id is None and get_transaction.expense_id is None and get_transaction.debt is None)):
                        get_notification = Notification.Notify(deviceToken=user.device_token,title="Debt (Reminder)", message="Your debt payment of amount %s %s is planned for today."%(str(x.currency), str(x.amount)), notify_status="DEBT_PLANNED")
                        notification.objects.create(title="Debt (Reminder)", message="Your debt payment of amount %s %s is planned for today."%(str(x.currency), str(x.amount)), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]))

                    elif ((get_transaction.income_from_id is not None and get_transaction.debt_id is not None) and (get_transaction.source_id is None and get_transaction.goal_id is None and get_transaction.expense_id is None and get_transaction.income_to_id is None)):
                        get_notification = Notification.Notify(deviceToken=user.device_token,title="Debt (Reminder)", message="Your debt payment of amount %s %s is planned for today."%(str(x.currency), str(x.amount)), notify_status="DEBT_PLANNED")
                        notification.objects.create(title="Debt (Reminder)", message="Your debt payment of amount %s %s is planned for today."%(str(x.currency), str(x.amount)), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]))
        ############# SETTLEING #######################

        ############# ACHIEVINGS ######################

        ############# OVERDUES ########################
        return "success"