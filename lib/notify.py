from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class Slack:
    def __init__(self, token, log):
        self.token = token
        self.log = log
        
    def notify(self, channel, text):
        client = WebClient(token=self.token)
        message = {
            "text": text
        }

        try:
            response = client.chat_postMessage(channel=channel, text=message["text"])
            if response['ok']:
                self.log.info("Notify test result to slack PASS")
            else:
                self.log.error("Notify test result to slack Fail")
                self.log.error(response)
        except SlackApiError as e:
            self.log.error("Notify test result to slack Fail")
            self.log.error(f"Error: {e}")
            

class Sendgrid:
    def __init__(self, token, log):
        self.token = token
        self.log = log            

    def notify(self, from_email, to_email, subject, text):
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=text
        )
        
        try:
            sg = SendGridAPIClient(self.token)
            response = sg.send(message)
            if response.status_code == 202:
                self.log.info(f"Sendgrid Notify PASS")
            else:
                self.log.error(f"Sendgrid Notify FAIL")                
        except Exception as e:
            self.log.error(f"Sendgrid Error: {e}")
        
def Process_notify(setting, subject, text, log):   
    if setting['Slack']:
        Slack_obj = Slack(setting['Addr']['Slack'], log)
        Slack_obj.notify(setting['Addr']['slack_channel'], text)
        
    if setting['Sendgrid']:
        Sendgrid_obj = Sendgrid(setting['Addr']['Sendgrid'], log)
        Sendgrid_obj.notify(setting['Addr']['from_email'], setting['Addr']['to_email'], subject, text)
        
