from helper import *
import logging


class CmiClassify:
    def __init__(self, project):
        self.classifyConfig = read_config("config.yaml")[project]["mail_rule"]
        self.project = project

    def classify(self, msgs):
        msgs_for_loop = msgs
        email_addresses = self.classifyConfig.keys()

        # walk all msgs
        for msg in msgs_for_loop:
            # walk all enterprises info
            for email_address in email_addresses:
                enterprise_count_in_one_email = len(self.classifyConfig[str(email_address)])
                # if one email contain 1 enterprise then classify by sender
                if enterprise_count_in_one_email == 1:
                    # -----------------------classify by sender-------------------------
                    if msg.from_ == email_address:
                        # get enterprise name form single element list
                        enterprise = "".join(self.classifyConfig[str(email_address)]["enterprise"])
                        # save attachments
                        get_files_from_msg(msg, self.project, enterprise)
                        # record log

                    # -------------------------------------------------------------------
                # if one email contain multi enterprises, classify by subject and attachments names
                # ----------------classify by subject and attachments names------------------
                elif enterprise_count_in_one_email > 1:
                    # get enterprise name form single element list
                    enterprises_list = self.classifyConfig[str(email_address)]["enterprise"]
                    for each_enterprise in enterprises_list:
                        if each_enterprise in msg.subject:
                            # save attachments
                            get_files_from_msg(msg, self.project, each_enterprise)

                        # walk all attachments in one email
                        for att in msg.attachments:
                            if each_enterprise in att.filename:
                                # save attachments
                                get_files_from_msg(msg, self.project, each_enterprise)

                # ----------------------------------------------------------------------------



