import json
import os
import platform
import signal
import subprocess
import threading
import time

import psutil
from libs.in_win import config_path, inside_windows


class ConnectGost:
    def __init__(self, config_path, localport=8080, bypass_iran=False) -> None:
        self.config_path = config_path
        self.localport = localport
        self.sni = False
        self.__profile_from_config_file()
        self.__profiler_reader()
        self.enable_loops = True
        self.gost_process = None
        self.bypass_iran = bypass_iran

    def __profile_from_config_file(self):
        with open(self.config_path, "r") as json_file:
            # Load the JSON data from the file
            self.profile = json.load(json_file)

    def __profiler_reader(self):
        self.remote_protocol = self.profile["remote_protocol"]
        self.remote_user = self.profile["remote_user"]
        self.remote_password = self.profile["remote_password"]
        self.remote_address = self.profile["remote_address"]
        self.remote_port = self.profile["remote_port"]
        try:
            self.sni = self.profile["sni"]
        except:
            pass

    def __cmd_generator(self):
        bin_address = self.bin_address_generator()
        iran = "*.filimo.*,*.ir,arvancdn.com,blubank.com,cedarmaps.com,digikalacloud.com,digikalajet.com,ebidar.com,farsimode.com,glorytoon.com,iranserver.com,ketaabonline.com,ketab.io,lioncomputer.com,livetabco.com,maryamsoft.com,mashadkala.com,mindupmarket.com,mipersia.com,nassaab.com,nassaabpro.com,persiangig.com,restfulsms.com,serveriran.net,snapp.taxi,streamg.tv,taaghche.com,taaghchecdn.com,taranevis.com,timcheh.com,tipaxco.com,turkeykala.com,upera.tv,ustclothing.com,virgool.io,parspack.com,rasm.io,pi.hole,bankino.digital,chapchi.com,quera.org,iranecar.com,netbarg.com,bale.ai,tourism-bank.com,hamrahcard.net,nextpay.org,takhfifan.com,aparatsport.com,rozmusic.com,farsgamer.com,farsgamerpay.com,fgtal.com,sedastore.com,pay98.app,zil.ink,salambaabaa.com,bazicenter.com"

        if not self.sni:
            cmd = f"{bin_address} -D -L=auto://0.0.0.0:{self.localport} -F={self.remote_protocol}://{self.remote_user}:{self.remote_password}@{self.remote_address}:{self.remote_port}"
            if self.bypass_iran:
                cmd = f'{cmd}?bypass="{iran}"'
        else:
            cmd = f'{bin_address} -D -L="auto://0.0.0.0:{self.localport}" -F="{self.remote_protocol}://{self.remote_user}:{self.remote_password}@:{self.remote_port}?host={self.sni}"'
            if self.bypass_iran:
                if cmd.endswith('"'):
                    cmd = cmd[:-1]
                cmd = f'{cmd}&bypass={iran}"'
        # else:
        #     if not self.sni:
        #         cmd = f"bin/mac/gost/igost -D -L=auto://0.0.0.0:{self.localport} -F={self.remote_protocol}://{self.remote_user}:{self.remote_password}@{self.remote_address}:{self.remote_port}"
        #     else:
        #         cmd = f'bin/mac/gost/igost -D -L="auto://0.0.0.0:{self.localport}" -F="{self.remote_protocol}://{self.remote_user}:{self.remote_password}@:{self.remote_port}?host={self.sni}"'

        return cmd

    def bin_address_generator(self):
        # if inside_windows():
        #     pf = "win"
        # elif platform.system() == "Linux":
        #     pf = "linux"

        # elif platform.system() == "Darwin":
        #     pf = "mac"

        # bin_address = f"bin\\{pf}\\gost\\gost"
        bin_address = f"{config_path()}\\bin\\gost"
        if not inside_windows():
            bin_address = bin_address.replace("\\", "/")
        return bin_address

    def kill(self):
        self.enable_loops = False
        if self.gost_process:
            # self.gost_process.kill()
            self.kills_pid(self.gost_process.pid)
            self.gost_process.terminate()
            # self.gost_process.send_signal(signal.CTRL_C_EVENT)
            kill_cmd = f"taskkill /f /pid {self.gost_process.pid}"
            print(kill_cmd)
            os.popen(kill_cmd)

        # os.popen("taskkill /f /im igost.exe").read()
        self.gost_thread.join(1)

    def connect(self):
        cmd = self.__cmd_generator()
        self.gost_thread = threading.Thread(
            target=self.__thread_run_read_gost, args=(cmd,), daemon=True
        )
        self.gost_thread.start()
        return self.gost_thread

    def __thread_run_read_gost(self, cmd):
        self.enable_loops = True
        print("thread_run_read_gost is ran")

        print("cmd before: " + cmd)

        self.gost_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        # tasklist = os.popen("tasklist").read()

        while self.enable_loops:
            line = self.gost_process.stderr.readline().strip().decode("utf-8")
            if len(line) < 3:
                time.sleep(0.5)
                continue
            print(line)

    def kills_pid(self, pid):
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()


if __name__ == "__main__":
    gi = ConnectGost("gost1.json")
    gi.connect()
    while True:
        time.sleep(5)
