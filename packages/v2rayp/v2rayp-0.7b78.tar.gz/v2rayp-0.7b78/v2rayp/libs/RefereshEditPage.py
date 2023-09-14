import json
import os

from libs.in_win import config_path, inside_windows


class RefereshEditPage:
    def __init__(self, filename, group="") -> None:
        self.page_data = dict()
        self.remark = filename
        self.group = group
        data = self.read_content_of_config_file_as_json()
        self.extract_configs(data)

    def get_editpage_content(self) -> dict:
        self.page_data["remark"] = self.remark
        return self.page_data

    def extract_configs(self, data: json):
        self.page_data["protocol"] = data["outbounds"][0]["protocol"]
        self.page_data["network"] = data["outbounds"][0]["streamSettings"]["network"]
        self.page_data["user_security"] = ""
        if "trojan" in self.page_data["protocol"]:
            self.page_data["server_address"] = data["outbounds"][0]["settings"][
                "servers"
            ][0]["address"]
            self.page_data["method"] = data["outbounds"][0]["settings"]["servers"][0][
                "method"
            ]
            self.page_data["ota"] = data["outbounds"][0]["settings"]["servers"][0][
                "ota"
            ]
            self.page_data["password"] = data["outbounds"][0]["settings"]["servers"][0][
                "password"
            ]
            self.page_data["port"] = data["outbounds"][0]["settings"]["servers"][0][
                "port"
            ]
        elif ("vless" in self.page_data["protocol"]) or (
            "vmess" in self.page_data["protocol"]
        ):
            self.page_data["server_address"] = data["outbounds"][0]["settings"][
                "vnext"
            ][0]["address"]
            self.page_data["port"] = data["outbounds"][0]["settings"]["vnext"][0][
                "port"
            ]
            self.page_data["security"] = data["outbounds"][0]["settings"]["vnext"][0][
                "users"
            ][0]["security"]

            self.page_data["uuid"] = data["outbounds"][0]["settings"]["vnext"][0][
                "users"
            ][0]["id"]

        if self.page_data["network"] == "grpc":
            try:
                self.page_data["grpc_serviceName"] = data["outbounds"][0][
                    "streamSettings"
                ]["grpcSettings"]["serviceName"]
            except:
                pass

        try:
            self.page_data["security"] = data["outbounds"][0]["streamSettings"][
                "security"
            ]
            if self.page_data["security"] == "reality":
                self.page_data["serverName"] = data["outbounds"][0]["streamSettings"][
                    "realitySettings"
                ]["serverName"]
                self.page_data["fingerprint"] = data["outbounds"][0]["streamSettings"][
                    "realitySettings"
                ]["fingerprint"]
                self.page_data["publicKey"] = data["outbounds"][0]["streamSettings"][
                    "realitySettings"
                ]["publicKey"]
                self.page_data["shortId"] = data["outbounds"][0]["streamSettings"][
                    "realitySettings"
                ]["shortId"]
                self.page_data["spiderX"] = data["outbounds"][0]["streamSettings"][
                    "realitySettings"
                ]["spiderX"]
            # elif self.security == "reality":
            elif self.page_data["security"] == "tls":
                self.page_data["serverName"] = data["outbounds"][0]["streamSettings"][
                    "tlsSettings"
                ]["serverName"]
                self.page_data["fingerprint"] = data["outbounds"][0]["streamSettings"][
                    "tlsSettings"
                ]["fingerprint"]
                arr_alpn = data["outbounds"][0]["streamSettings"]["tlsSettings"]["alpn"]
                text = ""
                for alpn in arr_alpn:
                    text = text + "," + alpn
                self.page_data["alpn"] = text

        except:
            self.page_data["security"] = "none"

    def read_content_of_config_file_as_json(self) -> json:
        group = self.group
        if len(group) > 1:
            group_path = f"\\subscriptions\\{group}"
        else:
            group_path = ""
        ################

        json_config_path = f"{config_path()}\\v2ray_profiles{group_path}\\{self.remark}"
        if not inside_windows():
            json_config_path = json_config_path.replace("\\", "/")

        with open(json_config_path, "r") as json_file:
            # Load the JSON data
            data = json.load(json_file)
        return data
