import re
import datetime
import subprocess


class Util:
    def __init__(self):
        pass

    @staticmethod
    def regular_expression(data):
        match = re.match(r'\$\{([\w\.]+)\}', data)
        if match:
            parts = match.group(1).split('.')
            return parts
        else:
            print("Invalid variable format")

    @staticmethod
    def add_timestamp_to_version_name(data):
        current_time = datetime.datetime.now()
        time_str = current_time.strftime("%Y%m%d%H%M%S")
        new_version_name = str(data) + "_" + time_str
        return new_version_name

    @staticmethod
    def lowercase_first_letter(data):
        if isinstance(data, dict):
            return {k[0].lower() + k[1:]: v for k, v in data.items()}
        elif isinstance(data, str):
            return data[0].lower() + data[1:]
        else:
            return data

    @staticmethod
    def run_cli_command(command, cwd):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
        output, error = process.communicate()
        return output, error
