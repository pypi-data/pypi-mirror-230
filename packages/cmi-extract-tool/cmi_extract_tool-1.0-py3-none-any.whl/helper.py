import os
import yaml
import logging


def read_config(file_name):
    current_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(current_folder)
    config_file_path = os.path.join(parent_folder, 'config')
    config_file_name = os.path.join(config_file_path, file_name)
    with open(config_file_name, 'r', encoding='utf-8') as file:
        config_data = yaml.safe_load(file)

    return config_data


def get_log_path():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(current_folder)
    out_file_path = os.path.join(parent_folder, 'log')
    if not os.path.exists(out_file_path):
        os.makedirs(out_file_path)

    return out_file_path


def get_files_from_msg(msg, project, enterprise):
    file_path = os.path.abspath(read_config("config.yaml")[project]["fetch_attachment_path"])
    file_path = os.path.join(file_path, enterprise)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    for att in msg.attachments:
        if att.filename.split(".")[-1] == "xlsx" or att.filename.split(".")[-1] == "xls":
            with open(os.path.join(file_path, str(att.filename)), 'wb') as f:
                f.write(att.payload)
                logging.info(f'result: classified by subject, enterprise: {enterprise}, '
                             f'sender: {msg.from_}, subject: {msg.subject}')



def get_all_file_paths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.abspath(os.path.join(root, filename))
            if os.path.isfile(filepath):
                file_paths.append(filepath)

    return file_paths




