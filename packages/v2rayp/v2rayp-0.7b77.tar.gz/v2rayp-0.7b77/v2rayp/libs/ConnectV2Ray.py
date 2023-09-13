import json
import os
import platform
import subprocess
import threading
import time

import psutil
from libs.in_win import config_path, inside_windows


class ConnectV2Ray:
    def __init__(self, config_file_path, localport=7595) -> None:
        print("v2ray started!")
        self.enable_loops = False
        self.localport = localport

        self.config_file_path = config_file_path
        self.__referesh_localport_remoteport()

        self.v2ray_thread = None
        self.v2ray_process = None

    def __referesh_localport_remoteport(self):
        with open(f"{self.config_file_path}", "r") as json_file:
            # Load the JSON data from the file
            data = json.load(json_file)
        data["log"]["loglevel"] = "debug"
        data["inbounds"][0]["port"] = int(self.localport)
        try:
            data["inbounds"][1]["port"] = int(self.localport) + 1
        except:
            pass

        try:
            a = data["outbounds"][0]["settings"]["vnext"][0]["port"]
            data["outbounds"][0]["settings"]["vnext"][0]["port"] = int(a)
        except:
            a = data["outbounds"][0]["settings"]["servers"][0]["port"]
            data["outbounds"][0]["settings"]["servers"][0]["port"] = int(a)

        with open(f"{self.config_file_path}", "w") as json_file:
            # Write the JSON data to the file
            json.dump(data, json_file)

    def connect(self):
        cmd = self.cmd_generator()
        print(cmd)
        self.v2ray_thread = threading.Thread(
            target=self.thread_run_read_v2ray, args=(cmd,), daemon=True
        )
        self.v2ray_thread.start()
        return self.v2ray_thread

    def kill_pid(self, pid):
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()

    def kill(self):
        self.enable_loops = False
        if self.v2ray_process:
            self.kill_pid(self.v2ray_process.pid)
            self.v2ray_process.terminate()
            # self.v2ray_process.send_signal(signal.CTRL_C_EVENT)
            os.popen(f"taskkill /f /pid {self.v2ray_process.pid}")
            self.v2ray_process.kill()
        # os.popen("taskkill /f /im xray.exe").read()
        self.v2ray_thread.join(1)

    def cmd_generator(
        self,
    ) -> str:
        # cmd = f"bin\\v2ray\\xray.exe run -c %appdata\\roaming%\v2rayp\configs\\{self.config_filename}"
        if inside_windows():
            cmd = f"{config_path()}\\bin\\xray.exe --config={self.config_file_path}"
        else:
            cmd = f"chmod +x {config_path()}/bin/xray && {config_path()}/bin/xray --config={self.config_file_path}"

            # if platform.system() == "Darwin":
            #     cmd = f"chmod +x  && bin/mac/v2ray/xray --config={self.config_file_path}"
            # elif platform.system() == "Linux":
            #     cmd = f"chmod +x bin/mac/v2ray/xray && bin/linux/v2ray/xray --config={self.config_file_path}"

        return cmd

    def thread_run_read_v2ray(self, cmd):
        self.enable_loops = True
        print("thread_run_read_v2ray is ran")

        err_cnt = 0

        print("cmd before: " + cmd)

        # tasklist = ""
        # while "xray" not in tasklist:
        self.v2ray_process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        # tasklist = os.popen("tasklist").read()

        print("next line")
        while self.enable_loops:
            line = self.v2ray_process.stdout.readline().strip().decode("utf-8")
            if len(line) < 3:
                time.sleep(0.5)
                continue
            print(line)
            if "failed to find an available destination" in line:
                err_cnt += 1

            elif "via" in line:
                err_cnt = 0
