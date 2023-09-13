import json
import os
import time

from libs.in_win import config_path, inside_windows

# Set the encoding explicitly to UTF-8
# if os.name == "nt":  # For Windows
#     import sys

#     sys.stdin.reconfigure(encoding="utf-8")
#     sys.stdout.reconfigure(encoding="utf-8")
# else:  # For Unix/Linux
#     import locale

#     locale.setlocale(locale.LC_ALL, "en_US.utf-8")


class RefereshTableContent:
    def __init__(self) -> None:
        self.json_v2ray_configs = self._referesh_v2ray_folder()
        self.json_gost_configs = self._referesh_gost_folder()
        ##############################
        self.v2ray_subscriptions = []

        if inside_windows():
            path = f"{config_path()}\\v2ray_profiles\\subscriptions"
        else:
            path = f"{config_path()}/v2ray_profiles/subscriptions"

        self.check_folder_if_not_make(path)

        self.v2ray_subscriptions = [
            file for file in os.listdir(path) if os.path.isdir(os.path.join(path, file))
        ]

        print(self.v2ray_subscriptions)
        # if inside_windows():
        #     cmd = f"dir /b /ad {config_path()}\\v2ray_profiles\\subscriptions"
        #     self.v2ray_subscriptions = os.popen(cmd).read().strip().split("\n")
        # else:
        #     cmd = f"cd {config_path()}/v2ray_profiles/subscriptions;ls -d */"
        #     self.v2ray_subscriptions = (
        #         os.popen(cmd).read().strip().replace("/", "").split()
        #     )
        for subscription_name in self.v2ray_subscriptions:
            self.json_v2ray_subscription_configs = (
                self._referesh_v2ray_subscription_folder(subscription_name)
            )
        #######################################
        self.gost_subscriptions = []
        # if inside_windows():
        #     cmd = f"dir /b /ad {config_path()}\\gost_profiles\\subscriptions"
        #     self.gost_subscriptions = os.popen(cmd).read().strip().split("\n")
        # else:
        #     cmd = f"cd {config_path()}/gost_profiles/subscriptions;ls -d */"
        #     self.gost_subscriptions = (
        #         os.popen(cmd).read().strip().replace("/", "").split()
        #     )

        if inside_windows():
            path = f"{config_path()}\\gost_profiles\\subscriptions"
        else:
            path = f"{config_path()}/gost_profiles/subscriptions"
        self.check_folder_if_not_make(path)
        self.gost_subscriptions = [
            file for file in os.listdir(path) if os.path.isdir(os.path.join(path, file))
        ]

        print(self.gost_subscriptions)

        for subscription_name in self.gost_subscriptions:
            self.json_gost_subscription_configs = (
                self._referesh_gost_subscription_folder(subscription_name)
            )

    def extract_all_rows(self):
        rows = []
        ###############################
        for subscription_name in self.v2ray_subscriptions:
            i = 0
            for json_config in self.json_v2ray_subscription_configs:
                # try:

                row = self._extract_row_from_config_v2ray(json_config)
                # except Exception as e:
                #     continue
                row["remark"] = self.list_of_v2ray_subscription_configs[i]
                row["group"] = subscription_name
                rows.append(row)
                i += 1
        ####################################
        for subscription_name in self.gost_subscriptions:
            i = 0
            for json_config in self.json_gost_subscription_configs:
                row = self._extract_row_from_config_gost(json_config)
                row["remark"] = self.list_of_gost_subscription_configs[i]
                row["group"] = subscription_name
                rows.append(row)
                i += 1
        ####################################
        i = 0
        for json_config in self.json_v2ray_configs:
            row = self._extract_row_from_config_v2ray(json_config)
            row["remark"] = self.list_of_v2ray_configs[i]
            row["group"] = ""
            rows.append(row)
            i += 1
        ###########################################
        i = 0
        for json_config in self.json_gost_configs:
            row = self._extract_row_from_config_gost(json_config)
            row["remark"] = self.list_of_gost_configs[i]
            row["group"] = ""
            rows.append(row)
            i += 1
        #############################

        return rows

    def _extract_row_from_config_gost(self, data: json):
        row_data = {
            "protocol": data["remote_protocol"],
            "network": data["remote_protocol"],
            "server_address": data["remote_address"],
            "port": data["remote_port"],
            "security": data["remote_protocol"],
            "user_security": data["remote_protocol"],
        }
        return row_data

    def _extract_row_from_config_v2ray(self, data: json):
        protocol = data["outbounds"][0]["protocol"]
        network = data["outbounds"][0]["streamSettings"]["network"]
        user_security = ""
        if "trojan" in protocol:
            server_address = data["outbounds"][0]["settings"]["servers"][0]["address"]
            port = data["outbounds"][0]["settings"]["servers"][0]["port"]
        elif ("vless" in protocol) or ("vmess" in protocol):
            server_address = data["outbounds"][0]["settings"]["vnext"][0]["address"]
            port = data["outbounds"][0]["settings"]["vnext"][0]["port"]
            user_security = data["outbounds"][0]["settings"]["vnext"][0]["users"][0][
                "security"
            ]

        try:
            security = data["outbounds"][0]["streamSettings"]["security"]
        except:
            security = "none"

        row_data = {
            "protocol": protocol,
            "network": network,
            "server_address": server_address,
            "port": port,
            "security": security,
            "user_security": user_security,
        }
        return row_data

    def _referesh_v2ray_folder(self):
        # list_of_configs = (
        #     os.popen(
        #         f"dir {config_path()}\\v2ray_profiles /a-d /B"
        #         if inside_windows()
        #         else f"ls -p {config_path()}/v2ray_profiles | grep -v /"
        #     )
        #     .read()
        #     .split("\n")
        # )
        # list_of_configs = [x for x in list_of_configs if x]
        if inside_windows():
            path = f"{config_path()}\\v2ray_profiles"
        else:
            path = f"{config_path()}/v2ray_profiles"

        self.check_folder_if_not_make(path)

        list_of_configs = [
            file
            for file in os.listdir(path)
            if os.path.isfile(os.path.join(path, file))
        ]

        self.list_of_v2ray_configs = list_of_configs
        json_configs = []
        for config in list_of_configs:
            path = f"{config_path()}\\v2ray_profiles\\{config}"
            if not inside_windows:
                path = path.replace("\\", "/")

            json_configs.append(self._read_content_of_config_file(path))
        return json_configs

    def check_folder_if_not_make(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print("Folder created successfully.")
        else:
            print("Folder already exists.")

    def _referesh_v2ray_subscription_folder(self, subscription_name):
        # list_of_configs = (
        #     os.popen(
        #         f"dir {config_path()}\\v2ray_profiles\\subscriptions\\{subscription_name} /a-d /B"
        #         if inside_windows()
        #         else f"ls -p  {config_path()}/v2ray_profiles/subscriptions/{subscription_name} | grep -v /"
        #     )
        #     .read()
        #     .split("\n")
        # )
        # list_of_configs = [x for x in list_of_configs if x]

        if inside_windows():
            path = (
                f"{config_path()}\\v2ray_profiles\\subscriptions\\{subscription_name}"
            )
        else:
            path = f"{config_path()}/v2ray_profiles/subscriptions/{subscription_name}"

        list_of_configs = [
            file
            for file in os.listdir(path)
            if os.path.isfile(os.path.join(path, file))
        ]

        self.list_of_v2ray_subscription_configs = list_of_configs
        json_configs = []
        for config in list_of_configs:
            path = f"{config_path()}\\v2ray_profiles\\subscriptions\\{subscription_name}\\{config}"
            if not inside_windows:
                path = path.replace("\\", "/")
            temp = self._read_content_of_config_file(path)
            json_configs.append(temp)
        return json_configs

    def _referesh_gost_subscription_folder(self, subscription_name):
        # list_of_configs = (
        #     os.popen(
        #         f"dir {config_path()}\\gost_profiles\\subscriptions\\{subscription_name} /a-d /B"
        #         if inside_windows()
        #         else f"ls -p  {config_path()}/gost_profiles/subscriptions/{subscription_name} | grep -v /"
        #     )
        #     .read()
        #     .split("\n")
        # )
        # list_of_configs = [x for x in list_of_configs if x]
        if inside_windows():
            path = f"{config_path()}\\gost_profiles\\subscriptions\\{subscription_name}"
        else:
            path = f"{config_path()}/gost_profiles/subscriptions/{subscription_name}"

        list_of_configs = [
            file
            for file in os.listdir(path)
            if os.path.isfile(os.path.join(path, file))
        ]
        self.list_of_gost_subscription_configs = list_of_configs
        json_configs = []
        for config in list_of_configs:
            path = f"{config_path()}\\gost_profiles\\subscriptions\\{subscription_name}\\{config}"
            if not inside_windows:
                path = path.replace("\\", "/")
            temp = self._read_content_of_config_file(path)
            json_configs.append(temp)
        return json_configs

    def _referesh_gost_folder(self):
        # list_of_configs = (
        #     os.popen(f"dir {config_path()}\\gost_profiles /a-d /B").read().split("\n")
        #     if inside_windows()
        #     else os.popen(f"ls -p {config_path()}/gost_profiles | grep -v /")
        #     .read()
        #     .split("\n")
        # )
        # list_of_configs = [x for x in list_of_configs if x]

        if inside_windows():
            path = f"{config_path()}\\gost_profiles"
        else:
            path = f"{config_path()}/gost_profiles"

        self.check_folder_if_not_make(path)
        list_of_configs = [
            file
            for file in os.listdir(path)
            if os.path.isfile(os.path.join(path, file))
        ]

        self.list_of_gost_configs = list_of_configs
        json_configs = []
        for config in list_of_configs:
            # print("gost config:",config)
            path = f"{config_path()}\\gost_profiles\\{config}"
            if not inside_windows:
                path = path.replace("\\", "/")
            json_configs.append(self._read_content_of_config_file(path))
        return json_configs

    def _read_content_of_config_file(self, file_path) -> json:
        # print(f"221 this is text: {file_path}*")
        if not inside_windows():
            file_path = file_path.replace("\\", "/")
        with open(f"{file_path}", "r", encoding="utf-8") as json_file:
            # Load the JSON data
            text = json_file.read()
        data = json.loads(text, strict=False)
        return data


if __name__ == "__main__":
    RefereshTableContent()
    while True:
        time.sleep(10)
