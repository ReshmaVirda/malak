import requests
import json

class Notification:
    def Notify(deviceToken, title, message, notify_status, for_id=None, for_name=None, for_icon=None):
        serverToken = 'AAAABS5CEwQ:APA91bHqtOw8u7p_ErfllCpp2j_nTObmNifPXxjDHBSrpw1b_6Ds-_FFDlI6D1p_YjvjWTnOQZYy9boppVGgEcanHadWKoX_sZ68k1-7MT491cc7u84tG8I7-oAKHnMINdI10wdQtsQM'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }

        body = {
            'to': deviceToken,
            'data': {
                'title': title,
                'body': message,
                'content-available': True,
                'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                'status':notify_status
            },
            'notification': 
            {
                'title': title,
                'body': message,
                'sound':'default',
                'content-available': True,
                'icon':'ic_launcher',
                'priority':'high'
            },
            'icon':'notification_icon',
            'sound':'default',
            'content-available':True,
            'priority':'high'
        }
        response = requests.post("https://fcm.googleapis.com/fcm/send",headers=headers, data=json.dumps(body))
        if response.status_code == 200:
            response = json.loads(response.text) 
        else:
            response = ""
        data_dict = dict()
        if response != "":
            data_dict["response"] = response
            data_dict["data"] = {
                "title": title,
                "body": message,
                "content-available": True,
                "click_action": "FLUTTER_NOTIFICATION_CLICK",
                "status":notify_status,
                "id":for_id,
                "name":for_name,
                "icon":for_icon
            }
        else:
            data_dict["response"] = response
            data_dict["data"] = {} 
        return data_dict