
import requests
import json


SENDGRID_API_USERNAME = "yoursendgridaccount"
SENDGRID_API_KEY = "yoursendgridpassword"
SENDGRID_WEB_API_SEND_EMAIL_URL = "https://api.sendgrid.com/api/mail.send.json"

def send_email(to_email, to_name, from_email, subject, text_msg, html_msg):
    """
    Sends email using sendgrid.
    :param to_email:
    :param to_name:
    :param from_email:
    :param subject:
    :param text_msg:
    :param html_msg:
    :return: True to indicate that the email has been sent.
    """
    params = {'api_user': SENDGRID_API_USERNAME, 'api_key': SENDGRID_API_KEY, 'to': to_email, 'toname': to_name, 'subject': subject}
    params['from'] = from_email
    if text_msg != "":
        params['text'] = text_msg
    if html_msg != "":
        params['html'] = html_msg

    resp = requests.post(SENDGRID_WEB_API_SEND_EMAIL_URL, params)
    print(resp.text)
    json_resp = json.loads(resp.text)
    if 'message' in json_resp and json_resp['message'] == "success":
        return True
    else:
        return False
