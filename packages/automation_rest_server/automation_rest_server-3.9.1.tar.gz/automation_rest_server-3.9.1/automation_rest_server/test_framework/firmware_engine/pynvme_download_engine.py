import os
from utils.system import decorate_exception_result
from test_framework.state import State
from utils.firmware_path import FirmwareBinPath
from utils import log


class PynvmeDownload(object):

    def __init__(self):
        self.root_path = os.getcwd()
        self.logs_path = os.path.join(self.root_path, "logs", "download")
        self.fw_path_manage = FirmwareBinPath()

    def get_logs(self, key):
        log_dirs = os.listdir(self.logs_path)
        for item in log_dirs:
            if os.path.isfile(os.path.join(self.logs_path, item)):
                if key in item:
                    return os.path.join(self.logs_path, item)
        return None

    @decorate_exception_result
    def run(self, test_parameters):
        ret, logs = -1, ""
        test_parameters = self.fw_path_manage.update_perses_fw_path(test_parameters)
        fw_path = test_parameters.get("fw_path", "")
        pcie = test_parameters.get("pcie", "0000:01:00.0")
        key = test_parameters.get("key", "")
        if not fw_path:
            return State.ERROR_NOT_FOUND, "NOT find fw_path in test_parameters"
        cmd_line = f"python run.py download --fw_path {fw_path} --pcie {pcie} --key {key}"
        log.INFO(f"########Pynvme Download execute cmd: {cmd_line}")
        ret = os.system(cmd_line)
        log.INFO(f"########Pynvme Download execute return code: {ret}")
        logs = self.get_logs(key)
        return ret, logs
