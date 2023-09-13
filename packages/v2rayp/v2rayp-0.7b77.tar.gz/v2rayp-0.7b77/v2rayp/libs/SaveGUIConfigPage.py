import json
import os

from libs.in_win import config_path, inside_windows


class SaveGUIConfigPage:
    def __init__(self, filename, page_data, new_file: bool = False, group="") -> None:
        self.remark = filename
        self.page_data = page_data

        if len(group) > 1:
            self.group_path = f"\\subscriptions\\{group}"
        else:
            self.group_path = ""

        data: dict = self.read_content_of_config_file_as_json()

        if "protocol" in self.page_data:
            if self.page_data["protocol"] in ("vless", "vmess", "trojan"):
                new_data = self.edit_v2ray_configs(data)
                data.update(new_data)
                self.save_data(data)
        else:
            self.save_data(page_data)

    def edit_v2ray_configs(self, data: json) -> dict:
        data["outbounds"][0]["protocol"] = self.page_data["protocol"]
        data["outbounds"][0]["streamSettings"]["network"] = self.page_data["network"]
        if "trojan" in self.page_data["protocol"]:
            data["outbounds"][0]["settings"]["servers"][0]["address"] = self.page_data[
                "server_address"
            ]
            data["outbounds"][0]["settings"]["servers"][0]["method"] = self.page_data[
                "method"
            ]
            data["outbounds"][0]["settings"]["servers"][0]["ota"] = self.page_data[
                "ota"
            ]
            data["outbounds"][0]["settings"]["servers"][0]["password"] = self.page_data[
                "password"
            ]
            data["outbounds"][0]["settings"]["servers"][0]["port"] = self.page_data[
                "port"
            ]
        elif ("vless" in self.page_data["protocol"]) or (
            "vmess" in self.page_data["protocol"]
        ):
            data["outbounds"][0]["settings"]["vnext"][0]["address"] = self.page_data[
                "server_address"
            ]
            data["outbounds"][0]["settings"]["vnext"][0]["port"] = self.page_data[
                "port"
            ]
            data["outbounds"][0]["settings"]["vnext"][0]["users"][0][
                "security"
            ] = self.page_data["security"]

            data["outbounds"][0]["settings"]["vnext"][0]["users"][0][
                "id"
            ] = self.page_data["uuid"]

        if self.page_data["network"] == "grpc":
            try:
                data["outbounds"][0]["streamSettings"]["grpcSettings"][
                    "serviceName"
                ] = self.page_data["grpc_serviceName"]
            except:
                pass

        try:
            data["outbounds"][0]["streamSettings"]["security"] = self.page_data[
                "security"
            ]
            if self.page_data["security"] == "reality":
                data["outbounds"][0]["streamSettings"]["realitySettings"][
                    "serverName"
                ] = self.page_data["serverName"]
                data["outbounds"][0]["streamSettings"]["realitySettings"][
                    "fingerprint"
                ] = self.page_data["fingerprint"]
                data["outbounds"][0]["streamSettings"]["realitySettings"][
                    "publicKey"
                ] = self.page_data["publicKey"]
                data["outbounds"][0]["streamSettings"]["realitySettings"][
                    "shortId"
                ] = self.page_data["shortId"]
                data["outbounds"][0]["streamSettings"]["realitySettings"][
                    "spiderX"
                ] = self.page_data["spiderX"]
            # elif self.security == "reality":
            elif self.page_data["security"] == "tls":
                data["outbounds"][0]["streamSettings"]["tlsSettings"][
                    "serverName"
                ] = self.page_data["serverName"]
                data["outbounds"][0]["streamSettings"]["tlsSettings"][
                    "fingerprint"
                ] = self.page_data["fingerprint"]
                data["outbounds"][0]["streamSettings"]["tlsSettings"]["alpn"] = (
                    str(self.page_data["alpn"]).replace("[", "").replace("]", "")
                )

        except:
            pass

        return data

    def read_content_of_config_file_as_json(self) -> json:
        if "protocol" in self.page_data:
            if self.page_data["protocol"] in ("vless", "vmess", "trojan"):
                json_config_path = (
                    f"{config_path()}\\v2ray_profiles{self.group_path}\\{self.remark}"
                )
        else:
            json_config_path = (
                f"{config_path()}\\gost_profiles{self.group_path}\\{self.remark}"
            )

        if not inside_windows():
            json_config_path = json_config_path.replace("\\", "/")

        with open(json_config_path, "r") as json_file:
            # Load the JSON data
            data = json.load(json_file)
        return data

    def create_path_if_not_exists(self, path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)  # This will create directories recursively
                print(f"Path '{path}' did not exist. Created successfully.")
            except OSError as e:
                print(f"Error creating path '{path}': {e}")
        else:
            print(f"Path '{path}' already exists.")

    def save_data(self, data) -> json:
        if "protocol" in self.page_data:
            if self.page_data["protocol"] in ("vless", "vmess", "trojan"):
                path = f"{config_path()}\\v2ray_profiles{self.group_path}\\"
                if not inside_windows():
                    path = path.replace("\\", "/")
                json_config_path = f"{path}{self.remark}"
        else:
            path = f"{config_path()}\\gost_profiles{self.group_path}\\"
            if not inside_windows():
                path = path.replace("\\", "/")

            json_config_path = f"{path}{self.remark}"

        self.create_path_if_not_exists(path)

        with open(json_config_path, "w") as json_file:
            # Load the JSON data
            json.dump(data, json_file)
