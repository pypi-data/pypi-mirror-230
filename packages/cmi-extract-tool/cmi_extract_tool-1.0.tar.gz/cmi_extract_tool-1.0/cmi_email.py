from helper import read_config, get_log_path
from imap_tools import MailBox, AND
import datetime
import logging
import os

class cmi_email:
    def __init__(self, project, username, password, host):
        self.userName = username
        self.password = password
        self.host = host
        self.sinceTime = (datetime.date.today() - datetime.timedelta(days=read_config("config.yaml")[project]["day_range"]))

    def read_mail(self):
        # Get date, subject and body len of all emails from INBOX folder
        msgs = []
        with MailBox(self.host).login(self.userName, self.password) as mailbox:
            mailbox.folder.set('inbox')
            for msg in mailbox.fetch(AND(date_gte=self.sinceTime)):
                msgs.append(msg)

        return msgs
