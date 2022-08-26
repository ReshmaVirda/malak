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
        ############# REMINDERS #######################
        ## Debt Reminder ##
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
                notification.objects.create(title="Debt (Reminder)", message="Your debt payment of amount %s %s is planned for today."%(str(x.currency), str(x.amount)), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)              
        
        ## Debt Settleing ##
        for y in debts:
            if float(y.paid_amount) != float(0.00):
                if float(y.amount) == float(y.paid_amount):
                    user = ''
                    try:
                        user = User.objects.get(id=y.user_id)
                    except User.DoesNotExist:
                        return "User Doesn't Exist"
                    get_notification = Notification.Notify(deviceToken=user.device_token, title="Debt (Settleing)", message="Congratulations, your debt to %s has been fully settled with amount %s %s"%(y.name, y.currency, y.paid_amount), notify_status="DEBT_SETTLED")
                    notification.objects.create(title="Debt (Settleing)", message="Congratulations, your debt to %s has been fully settled with amount %s %s"%(y.name, y.currency, y.paid_amount), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)
                else:
                    user = ''
                    try:
                        user = User.objects.get(id=y.user_id)
                    except User.DoesNotExist:
                        return "User Doesn't Exist"
                    get_notification = Notification.Notify(deviceToken=user.device_token, title="Debt (Settleing)", message="Congratulations, your debt to %s has been partially settled with amount %s %s"%(y.name, y.currency, y.paid_amount), notify_status="DEBT_SETTLED")
                    notification.objects.create(title="Debt (Settleing)", message="Congratulations, your debt to %s has been partially settled with amount %s %s"%(y.name, y.currency, y.paid_amount), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)
        
        ############# ACHIEVINGS ######################
        ## Goal ##
        goals = Goal.objects.all()
        for g in goals:
            if float(g.added_amount) == float(g.amount):
                user = ''
                try:
                    user = User.objects.get(id=g.user_id)
                except User.DoesNotExist:
                    return "User Doesn't Exist"
                get_notification = Notification.Notify(deviceToken=user.device_token, title="Goal (Achieving)", message="You have reached the goal having accumulated amount %s %s"%(g.currency, g.amount), notify_status="GOAL_ACCUMULATED")
                notification.objects.create(title="Goal (Achieving)", message="You have reached the goal having accumulated amount %s %s"%(g.currency, g.amount), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)
        
        ## Expense ##
        expenses = Expense.objects.all()
        for e in expenses:
            if float(e.amount_limit) > float(0) and float(e.spent_amount) == float(e.amount_limit):
                user = ''
                try:
                    user = User.objects.get(id=e.user_id)
                except User.DoesNotExist:
                    return "User Doesn't Exist"
                get_notification = Notification.Notify(deviceToken=user.device_token, title="Expense (Achieving)", message="You have spend the expense having accumulated amount %s %s"%(e.currency, e.amount_limit), notify_status="EXPENSE_ACCUMULATED")
                notification.objects.create(title="Expense (Achieving)", message="You have spend the expense having accumulated amount %s %s"%(e.currency, e.amount_limit), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)
        
        ## SourceIncome ##
        sources = SourceIncome.objects.all()
        for s in sources:
            if float(s.spent_amount) == float(s.amount):
                user = ''
                try:
                    user = User.objects.get(id=s.user_id)
                except User.DoesNotExist:
                    return "User Doesn't Exist"
                get_notification = Notification.Notify(deviceToken=user.device_token, title="Source (Achieving)", message="You have spend the source having accumulated amount %s %s"%(s.currency, s.amount), notify_status="SOURCE_ACCUMULATED")
                notification.objects.create(title="Source (Achieving)", message="You have spend the source having accumulated amount %s %s"%(s.currency, s.amount), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)
        
        ############# OVERDUES ########################
        ## Goal ##
        goals = Goal.objects.all()
        for g1 in goals:
            if float(g1.added_amount) > float(g1.amount):
                user = ''
                try:
                    user = User.objects.get(id=g1.user_id)
                except User.DoesNotExist:
                    return "User Doesn't Exist"
                get_notification = Notification.Notify(deviceToken=user.device_token, title="Goal (Overdue)", message="You have overdue the goal having accumulated amount %s %s"%(g1.currency, g1.amount), notify_status="GOAL_OVERDUE")
                notification.objects.create(title="Goal (Overdue)", message="You have overdue the goal having accumulated amount %s %s"%(g1.currency, g1.amount), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)
        
        ## Expense ##
        expenses = Expense.objects.all()
        for e1 in expenses:
            if float(e1.spent_amount) > float(e1.amount_limit):
                user = ''
                try:
                    user = User.objects.get(id=e1.user_id)
                except User.DoesNotExist:
                    return "User Doesn't Exist"
                get_notification = Notification.Notify(deviceToken=user.device_token, title="Expense (Overdue)", message="You have over spend the expense having accumulated amount %s %s"%(e1.currency, e1.amount_limit), notify_status="EXPENSE_OVERDUE")
                notification.objects.create(title="Expense (Overdue)", message="You have over spend the expense having accumulated amount %s %s"%(e1.currency, e1.amount_limit), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)
        
        ## SourceIncome ##
        sources = SourceIncome.objects.all()
        for s1 in sources:
            if float(s1.spent_amount) > float(s1.amount):
                user = ''
                try:
                    user = User.objects.get(id=s1.user_id)
                except User.DoesNotExist:
                    return "User Doesn't Exist"
                get_notification = Notification.Notify(deviceToken=user.device_token, title="Source (Overdue)", message="You have spend the source having accumulated amount %s %s"%(s1.currency, s1.amount), notify_status="SOURCE_OVERDUE")
                notification.objects.create(title="Source (Overdue)", message="You have over spend the source having accumulated amount %s %s"%(s1.currency, s1.amount), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)

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
                        notification.objects.create(title="Recurrence from %s to %s"%(source.title, income.title), message="Your planed payment %s %s deducted from source %s and added %s %s to income %s"%(source.currency, get_transaction.transaction_amount, source.title, income.currency, get_transaction.converted_transaction, income.title), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)    
                    
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
                        notification.objects.create(title="Recurrence from %s to %s"%(income_from.title, income_to.title), message="Your planed payment %s %s deducted from income %s and added %s %s to income %s"%(income_from.currency, get_transaction.transaction_amount, income_from.title, income_to.currency, get_transaction.converted_transaction, income_to.title), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)

                    elif ((get_transaction.income_from_id is not None and get_transaction.expense_id is not None) and (get_transaction.source_id is None and get_transaction.goal_id is None and get_transaction.income_to_id is None and get_transaction.debt is None)):
       
                        income = ''
                        expense = ''

                        try:
                            income = Income.objects.get(id=get_transaction.income_from_id)
                        except Income.DoesNotExist:
                            return "Income Doesn't Exist"

                        try:
                            expense = Expense.objects.get(id=get_transaction.expense_id)
                        except Expense.DoesNotExist:
                            return "Expnese Doesn't Exist"
                        
                        get_notification = Notification.Notify(deviceToken=user.device_token,title="Recurrence from %s to %s"%(income.title, expense.title), message="Your planed payment %s %s deducted from income %s and added %s %s to expense %s"%(income.currency, get_transaction.transaction_amount, income.title, expense.currency, get_transaction.converted_transaction, expense.title), notify_status="RECURRENCE_PLANNED")
                        notification.objects.create(title="Recurrence from %s to %s"%(income.title, expense.title), message="Your planed payment %s %s deducted from income %s and added %s %s to expense %s"%(income.currency, get_transaction.transaction_amount, income.title, expense.currency, get_transaction.converted_transaction, expense.title), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)

                    elif ((get_transaction.income_from_id is not None and get_transaction.goal_id is not None) and (get_transaction.source_id is None and get_transaction.income_to_id is None and get_transaction.expense_id is None and get_transaction.debt is None)):
                
                        income = ''
                        goal = ''

                        try:
                            income = Income.objects.get(id=get_transaction.income_from_id)
                        except Income.DoesNotExist:
                            return "Income Doesn't Exist"

                        try:
                            goal = Goal.objects.get(id=get_transaction.goal_id)
                        except Goal.DoesNotExist:
                            return "Goal Doesn't Exist"
                        
                        get_notification = Notification.Notify(deviceToken=user.device_token,title="Recurrence from %s to %s"%(income.title, goal.title), message="Your planed payment %s %s deducted from income %s and added %s %s to goal %s"%(income.currency, get_transaction.transaction_amount, income.title, goal.currency, get_transaction.converted_transaction, goal.title), notify_status="RECURRENCE_PLANNED")
                        notification.objects.create(title="Recurrence from %s to %s"%(income.title, goal.title), message="Your planed payment %s %s deducted from income %s and added %s %s to goal %s"%(income.currency, get_transaction.transaction_amount, income.title, goal.currency, get_transaction.converted_transaction, goal.title), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)

                    elif ((get_transaction.income_from_id is not None and get_transaction.debt_id is not None) and (get_transaction.source_id is None and get_transaction.goal_id is None and get_transaction.expense_id is None and get_transaction.income_to_id is None)):
                
                        income = ''
                        debt = ''

                        try:
                            income = Income.objects.get(id=get_transaction.income_from_id)
                        except Income.DoesNotExist:
                            return "Income Doesn't Exist"
                        
                        try:
                            debt = Debt.objects.get(id=get_transaction.debt_id)
                        except Debt.DoesNotExist:
                            return "Debt Doesn't Exist"

                        get_notification = Notification.Notify(deviceToken=user.device_token,title="Recurrence from %s to %s"%(income.title, debt.title), message="Your planed payment %s %s deducted from income %s and added %s %s to debt %s"%(income.currency, get_transaction.transaction_amount, income.title, debt.currency, get_transaction.converted_transaction, debt.title), notify_status="RECURRENCE_PLANNED")
                        notification.objects.create(title="Recurrence from %s to %s"%(income.title, debt.title), message="Your planed payment %s %s deducted from income %s and added %s %s to debt %s"%(income.currency, get_transaction.transaction_amount, income.title, debt.currency, get_transaction.converted_transaction, debt.title), receiver_token=user.device_token, payload=json.dumps(get_notification["data"]), user=user.id)

        return "success"