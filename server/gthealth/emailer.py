import smtplib

from gthealth import config

class Emailer(object):
    def __init__(self, credentials=None):
        if credentials is None:
            credentials = config.MAIL_SETTINGS
        self.server = smtplib.SMTP(credentials['server'], credentials['port'])
        self.server.ehlo()
        self.server.starttls()
        self.server.login(credentials['username'], credentials['password'])
        self.username = credentials['username']
        return

    def send_text(self, recipients, subject, text):
        message = '''\\nFrom: {}\nTo: {}\nSubject: {}\n\n{}'''.format(
            self.username, ', '.join(recipients), subject, text)
        self.server.sendmail(self.username, recipients, message)
        return

    def close(self):
        self.server.quit()
        return