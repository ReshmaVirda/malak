import requests
import json

class Notification:
    def Notify(deviceToken, title, message, notify_status):
        serverToken = 'AAAABS5CEwQ:APA91bHqtOw8u7p_ErfllCpp2j_nTObmNifPXxjDHBSrpw1b_6Ds-_FFDlI6D1p_YjvjWTnOQZYy9boppVGgEcanHadWKoX_sZ68k1-7MT491cc7u84tG8I7-oAKHnMINdI10wdQtsQM'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }

        body = {
            'to': deviceToken,
            'notification': 
            {
                'title': title,
                'body': message,
                'sound':'default',
                'content-available': True,
            },
            'data': {
                'title': title,
                'body': message,
                'content-available': True,
                'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                'status':notify_status
            },
            'priority': 'high', 
        }
        response = requests.post("https://fcm.googleapis.com/fcm/send",headers=headers, data=json.dumps(body))
        print(response.status_code)

        print(response.json())