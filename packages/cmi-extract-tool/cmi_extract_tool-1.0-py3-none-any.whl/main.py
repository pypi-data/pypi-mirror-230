from extract import ExtractCols1
from helper import *
from cmi_email import cmi_email
from classify import CmiClassify
import warnings
from openpyxl import Workbook
import logging
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(filename=os.path.join(get_log_path(), "result.log"), encoding='utf-8', level=logging.INFO)

email_accounts = read_config("config.yaml")["华润"]["mailbox"]

for email_account in email_accounts:
    email = cmi_email("华润", email_account["username"], email_account["password"], email_account["host"])
    msgs = email.read_mail()
    cls = CmiClassify("华润")
    cls.classify(msgs)
fetch_out_path = read_config("config.yaml")["华润"]["fetch_attachment_path"]
file_list = get_all_file_paths(fetch_out_path)

for file in file_list:
    if os.path.isfile(file) and os.path.basename(os.path.dirname(file)) != "handled":
        extract = ExtractCols1(file, "华润")
        extract.execute()
    # else:
    #     os.remove(file)


