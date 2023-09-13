import base64
import hashlib
import json
import os
from urllib.parse import parse_qs, urlencode, urlparse

from libs.in_win import config_path


class ConfigDataScheme:
    protocol = ""
    uuid = ""
    address = ""
    port = ""
    attributes = ""


class URLTools_for_V2Ray:
    def __init__(self, url: str, localport=7595) -> None:
        self.localport = localport
        self.url2Config(url)
        self.mainConfigGenerator()

    def toJsonConfigString(self):
        return self.finalConfig

    def containsBase64(self, text):
        try:
            base64.b64decode(text).decode("utf-8")
        except:
            # print(f"not base64: {e}")
            return False

        return True

    # def v2ray_json_to_url(self, json_data: dict):
    #     #       self.page_data["remark"] = self.window["alias"].get()
    #     # self.page_data["server_address"] = self.window["address"].get()
    #     # self.page_data["port"] = self.window["port"].get()
    #     # self.page_data["uuid"] = self.window["uuid"].get()
    #     # self.page_data["user_security"] = self.window["encryptionmethod"].get()
    #     # # self.page_data["grpc_serviceName"] = "imi"
    #     # self.page_data["network"] = self.window["transport_protocol"].get()
    #     # self.page_data["security"] = self.window["tls"].get()
    #     # self.page_data["sni"] = self.page_data["serverName"] = self.window["sni"].get()
    #     # self.page_data["fingerprint"] = self.window["fingerprint"].get()
    #     # self.page_data["publicKey"] = self.window["publickey"].get()
    #     # self.page_data["shortId"] = self.window["shortid"].get()
    #     # self.page_data["spiderX"] = self.window["spiderx"].get()

    #     attributes = {
    #         "v": "2",
    #         "ps": json_data["remark"],
    #         "add": json_data["server_address"],
    #         "port": json_data["port"],
    #         "id": json_data["uuid"],
    #         "aid": json_data["aid"],
    #         "type": json_data["network"],
    #         "security": json_data["security"],
    #         "spx": json_data["spiderX"],
    #         "sid": json_data["shortId"],
    #         "pbk": json_data["publicKey"],
    #         "fp": json_data["fingerprint"],
    #         "sni": json_data["sni"],
    #     }
    #     # base64_config = base64.urlsafe_b64encode(json.dumps(attributes).encode("utf-8")).decode("utf-8")

    #     # Create the V2Ray VMess URL
    #     v2ray_url = f"{json_data['protocol']}://"

    def generate_random_md5_hash(self):
        return hashlib.md5(os.urandom(128)).hexdigest()

    def url2Config(self, text: str):
        split_parts = text.split("://")
        protocol = split_parts[0]
        text1 = split_parts[1]
        self.configData = ConfigDataScheme()
        if self.containsBase64(text1):
            self.configData.protocol = protocol
            decoded_text = base64.b64decode(text1).decode("utf-8")
            self.configData.attributes = json.loads(decoded_text)
            self.configData.protocol = protocol
            self.configData.uuid = self.configData.attributes["id"]
            self.configData.address = self.configData.attributes["add"]
            self.configData.port = self.configData.attributes["port"]
            try:
                self.profileName = self.configData.attributes["ps"]
            except:
                self.profileName = f"{self.configData.protocol}_{self.configData.attributes['type']}_{self.generate_random_md5_hash()}"

        else:
            parsed_url = urlparse(text)
            # Extracting data from the URL
            self.configData.protocol = parsed_url.scheme
            self.configData.uuid = parsed_url.username
            self.configData.address = parsed_url.hostname
            self.configData.port = parsed_url.port
            query_params = parse_qs(parsed_url.query)
            self.configData.attributes = {
                key: value[0] for key, value in query_params.items()
            }

            try:
                self.profileName = text.split("#")[1].strip()
            except:
                self.profileName = f"{self.configData.protocol}_{self.configData.attributes['type']}_{self.generate_random_md5_hash()}"

    def generate_scheme_settings(self):
        if self.configData.protocol in ["vmess", "vless"]:
            config_template = r"""{
            "protocol": "PROTOCOL",
            "settings": {
            "vnext": [
                {
                    "address": "ADDR",
                    "port": PORT,
                    "users": [
                    {
                        "id": "ID",
                        "alterId": 0,
                        "email": "t@t.tt",
                        "security": "auto",
                        "encryption": "none"
                    }
                    ]
                }
                ]}
            }"""

            scheme = (
                config_template.replace("PROTOCOL", self.configData.protocol)
                .replace("ADDR", self.configData.address)
                .replace("PORT", str(self.configData.port))
                .replace("ID", self.configData.uuid)
            )
            self.scheme = json.loads(scheme)
        elif self.configData.protocol == "trojan":
            config_template = r"""{
                "protocol": "PROTOCOL",
                "settings": {
                    "servers": [
                    {
                        "address": "ADDR",
                        "method": "chacha20",
                        "ota": false,
                        "password": "PAASWORD",
                        "port": PORT,
                        "level": 1
                    }
                    ]
                }
            }
            """
            scheme = (
                config_template.replace("PROTOCOL", self.configData.protocol)
                .replace("ADDR", self.configData.address)
                .replace("PORT", str(self.configData.port))
                .replace("PAASWORD", self.configData.uuid)
            )
            self.scheme = json.loads(scheme)

        # return json.dumps(self.configData.attributes, indent=4)

    def generate_streamSettings(self):
        attributes = self.configData.attributes
        if "reality" in str(attributes):
            if attributes["type"] == "tcp":
                realityconfig = r"""{
                "streamSettings": {
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {
                        "serverName": "sni",
                        "fingerprint": "fp",
                        "show": false,
                        "publicKey": "pbk",
                        "shortId": "sid",
                        "spiderX": "spx"
                    }
                }
                }
                """
                realityconfig = (
                    realityconfig.replace("sni", attributes["sni"])
                    .replace("fp", attributes["fp"])
                    .replace("pbk", attributes["pbk"])
                    .replace("spx", attributes["spx"])
                )

                try:
                    realityconfig = realityconfig.replace("sid", attributes["sid"])
                except:
                    realityconfig = realityconfig.replace("sid", "")

                return json.loads(realityconfig)  # json.dumps(realityconfig, indent=4)

            elif attributes["type"] == "grpc":
                realityconfig = r"""{
                "streamSettings": {
                        "network": "grpc",
                        "security": "reality",
                        "realitySettings": {
                        "serverName": "sni",
                        "fingerprint": "fp",
                        "show": false,
                        "publicKey": "pbk",
                        "shortId": "SID",
                        "spiderX": "spx"
                        },
                        "grpcSettings": {
                        "serviceName": "ServiceName",
                        "multiMode": false,
                        "idle_timeout": 60,
                        "health_check_timeout": 20,
                        "permit_without_stream": false,
                        "initial_windows_size": 0
                        }
                    }
                    }
                    """
                realityconfig = (
                    realityconfig.replace("sni", attributes["sni"])
                    .replace("fp", attributes["fp"])
                    .replace("pbk", attributes["pbk"])
                    .replace("spx", attributes["spx"])
                )

                try:
                    realityconfig = realityconfig.replace("SID", attributes["sid"])
                except:
                    realityconfig = realityconfig.replace("SID", "")

                try:
                    realityconfig = realityconfig.replace(
                        "ServiceName", attributes["serviceName"]
                    )
                except:
                    realityconfig = realityconfig.replace("ServiceName", "")

                return json.loads(realityconfig)  # json.dumps(realityconfig, indent=4)
        elif "tls" in attributes or "security" in attributes:
            try:
                security = attributes["tls"]
            except:
                security = attributes["security"]
            if security == "tls":
                realityconfig = r"""{
            "streamSettings": {
                    "network": "NET",
                    "security": "tls",
                    "tlsSettings": {
                    "allowInsecure": false,
                    "serverName": "SNI",
                    "alpn": [""],
                    "fingerprint": "FP",
                    "show": false
                    }
                }
                }
                """
                realityconfig = (
                    realityconfig.replace("SNI", attributes["sni"])
                    .replace("FP", attributes["fp"] if "fp" in attributes else "chrome")
                    .replace(
                        "NET",
                        attributes["net"]
                        if "net" in attributes
                        else attributes["type"],
                    )
                )
                data = json.loads(realityconfig)
                data["streamSettings"]["tlsSettings"]["alpn"] = (
                    attributes["alpn"].split(",")
                    if "alpn" in attributes
                    else "http/1.1"
                )
            else:
                realityconfig = """{
                    "streamSettings": {
                    "network": "NET",
                    "wsSettings": {
                    "path": "/",
                    "headers": {}
                    }
                }
                }
                """
                realityconfig = realityconfig.replace("NET", attributes["net"])
                data = json.loads(realityconfig)
            return data

    def mainConfigGenerator(self):
        config_template = """    {
            "log": {
                "access": "",
                "error": "",
                "loglevel": "debug"
            },
            "inbounds": [
                {
                "tag": "socks",
                "port": LOCALSOCKSPORT,
                "listen": "127.0.0.1",
                "protocol": "socks",
                "sniffing": {
                    "enabled": true,
                    "destOverride": [
                    "http",
                    "tls"
                    ],
                    "routeOnly": true
                },
                "settings": {
                    "auth": "noauth",
                    "udp": true,
                    "allowTransparent": false
                }
                },
                {
                "tag": "http",
                "port": LOCALHTTPPORT,
                "listen": "127.0.0.1",
                "protocol": "http",
                "sniffing": {
                    "enabled": true,
                    "destOverride": [
                    "http",
                    "tls"
                    ],
                    "routeOnly": true
                },
                "settings": {
                    "auth": "noauth",
                    "udp": true,
                    "allowTransparent": false
                }
                }
            ],
            "outbounds": [
                {
                "tag": "proxy",
                PART1,
                PART2,
                "mux": {
                    "enabled": false,
                    "concurrency": -1
                }
                },
                {
                "tag": "direct",
                "protocol": "freedom",
                "settings": {}
                },
                {
                "tag": "block",
                "protocol": "blackhole",
                "settings": {
                    "response": {
                    "type": "http"
                    }
                }
                }
            ],
            "dns": {
                "servers": [
                "1.1.1.1",
                "8.8.8.8"
                ]
            },
            "routing": {
                "domainStrategy": "AsIs",
                "rules": [
                {
                    "type": "field",
                    "inboundTag": [
                    "api"
                    ],
                    "outboundTag": "api"
                },
                {
                    "type": "field",
                    "port": "0-65535",
                    "outboundTag": "proxy"
                }
                ]
            }
            }"""
        self.generate_scheme_settings()
        self.streamSettings = self.generate_streamSettings()
        scheme = self.delete_braces(json.dumps(self.scheme, indent=4))

        streamSettings = self.delete_braces(json.dumps(self.streamSettings, indent=4))
        self.finalConfig = (
            config_template.replace("PART1", scheme)
            .replace("PART2", streamSettings)
            .replace("LOCALSOCKSPORT", str(self.localport))
            .replace("LOCALHTTPPORT", str(self.localport + 1))
        )

        # config = json.loads(config)

    def delete_braces(self, string):
        """Deletes braces from the beginning and end of a string."""
        start_index = string.find("{")
        end_index = string.rfind("}")
        return string[start_index + 1 : end_index]


if __name__ == "__main__":
    # url = r"trojan://EM2y7NdIQJ@shahryar.ddns.net:13616?security=reality&sni=microsoft.com&fp=firefox&pbk=-6LB0M5afd9i1UpzezmGtDYQg-3GCCXEFgio5j_KXCc&sid=8ccc&spx=%2F&type=tcp&headerType=none#shahryar-trojan1-reality"
    # url = r"trojan://o9qIL2MGtR@shahryar.ddns.net:49030?security=reality&sni=microsoft.com&fp=firefox&pbk=tEwI2UUIGMRW8wrWj8pZEREDRDta9EegrwuhLsDXHgk&spx=%2F&type=grpc&serviceName=shahryar.ddns.net&mode=gun#trojan-grpc-r85l64s3v3"
    # url = r"trojan://LjWyuE2d8M@hels.ddns.net:44838?security=reality&sni=yahoo.com&fp=firefox&pbk=8LIuGGsdhR59qjyRALAmGKNuKVlyH3t8OqJmRRdyKl4&sid=92cd56b1&spx=%2F&type=grpc#reality-test-vfbd9h81"
    # url = r"trojan://o9qIL2MGtR@shahryar.ddns.net:49030?security=reality&sni=microsoft.com&fp=firefox&pbk=tEwI2UUIGMRW8wrWj8pZEREDRDta9EegrwuhLsDXHgk&spx=%2F&type=grpc&serviceName=shahryar.ddns.net&mode=gun#trojan-grpc-r85l64s3v3"
    # url = r"vmess://ew0KICAidiI6ICIyIiwNCiAgInBzIjogInZtZXNzX25vdGxzLXAwdW56aDMiLA0KICAiYWRkIjogImhlbHMuZGRucy5uZXQiLA0KICAicG9ydCI6ICIxMzE0NSIsDQogICJpZCI6ICIzMGRiNDRmNS0yNTVmLTRhYmUtOGEzNC00MDg0OTRhNzZhNDkiLA0KICAiYWlkIjogIjAiLA0KICAic2N5IjogImF1dG8iLA0KICAibmV0IjogIndzIiwNCiAgInR5cGUiOiAibm9uZSIsDQogICJob3N0IjogIiIsDQogICJwYXRoIjogIi8iLA0KICAidGxzIjogIm5vbmUiLA0KICAic25pIjogIiIsDQogICJhbHBuIjogIiINCn0="

    # url = r"trojan://EM2y7NdIQJ@shahryar.ddns.net:13616?security=reality&sni=microsoft.com&fp=firefox&pbk=-6LB0M5afd9i1UpzezmGtDYQg-3GCCXEFgio5j_KXCc&sid=8ccc&spx=%2F&type=tcp&headerType=none#shahryar-trojan1-reality"
    url = r"trojan://LjWyuE2d8M@hels.ddns.net:44838?security=reality&sni=yahoo.com&fp=firefox&pbk=8LIuGGsdhR59qjyRALAmGKNuKVlyH3t8OqJmRRdyKl4&sid=92cd56b1&spx=%2F&type=grpc#reality-test-vfbd9h81"
    print(URLTools_for_V2Ray(url).toJsonConfigString())

####################
###################
#####################
