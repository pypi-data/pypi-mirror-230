import os
import yaml
import subprocess
from utils import log
from utils.system import get_ip_address
from test_framework.state import State
from utils.firmware_path import FirmwareBinPath


class PynvmeEngine(object):

    def __init__(self):
        self.local_ip = get_ip_address()
        self.working_path = os.environ["working_path"]
        self.log_path = os.path.join(self.working_path, "logs")
        self.fw_path_manage = FirmwareBinPath()

    @staticmethod
    def convert_para_2_string(parameters):
        para_list = [f"--{key} {value}" for key, value in parameters.items()]
        para_str = ' '.join(para_list)
        return para_str

    def run_test(self, test_case, parameters):
        log.INFO(f"pynvme run_test: {test_case} key {parameters['key']}")
        para_str = self.convert_para_2_string(parameters)
        command_line = "python run.py testcase -n {} {}".format(test_case, para_str)
        log.INFO("pynvme run command: {}".format(command_line))
        child1 = subprocess.Popen(command_line, shell=True)
        return_code = child1.wait()
        return return_code

    def get_logs(self, key):
        log.INFO(f"pynvme get_logs: {key} at path {self.log_path}")
        for log_folder in os.listdir(self.log_path):
            if key in log_folder:
                log_path = os.path.join(self.log_path, log_folder)
                log_file = os.path.join(log_path, "test.log")
                return log_file

    def run(self, test_case, test_path, parameters, queue):
        log.INFO("PY-NVME run")
        ret_code = self.run_test(test_case, parameters)
        logs = self.get_logs(parameters["key"])
        result = {"name": test_case, "result": ret_code, "log": logs}
        print(f"testcase: {test_case} result {result}")
        queue.put(result)
        return ret_code
