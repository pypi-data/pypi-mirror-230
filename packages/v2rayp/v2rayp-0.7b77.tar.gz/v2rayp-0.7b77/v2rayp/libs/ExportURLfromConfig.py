import base64
import json
import os


class ExportURLfromConfig:
    def __init__(self, file_path="", pname="temp", new_profile: bool = False) -> None:
        if not new_profile:
            self.file_path = file_path
            self.pname = pname
            self.__load_json__()

    def share_link(
        self,
    ):
        security = self.json_data["outbounds"][0]["streamSettings"]["security"]
        print(security)

        if ("reality" == security) or ("trojan" == self.protocol):
            out = self.__construct_simple_link__()
        else:
            out = self.__toBase64Link__()

        return out

    def __toBase64Link__(self):
        my_string = str(self.__extract_attributes_as_json__())  # .replace(",", ",\n")
        b64 = base64.b64encode(my_string.encode("utf-8")).decode("utf-8")
        return f"{self.protocol}://{b64}"

    @staticmethod
    def construc_simple_link_from_edit_page(page_data):
        pname = page_data["remark"]
        security = page_data["security"]
        protocol = page_data["protocol"]
        address = page_data["server_address"]
        password = page_data["uuid"]
        port = page_data["port"]

        if security == "reality":
            server_name = page_data["sni"]
            fingerprint = page_data["fingerprint"]
            public_key = page_data["publicKey"]
            short_id = page_data["shortId"]
            spider_x = page_data["spiderX"]

            link = f"{protocol}://{password}@{address}:{port}?security={security}&sni={server_name}&fp={fingerprint}&pbk={public_key}&sid={short_id}&spx={spider_x}&type=grpc#{pname}"
            return link
        elif security == "tls":
            server_name = page_data["sni"]
            type = page_data["network"]
            link = f"{protocol}://{password}@{address}:{port}?security={security}&sni={server_name}&type={type}&headerType=none#{pname}"
            return link

    def __construct_simple_link__(self):
        json_data = self.json_data
        # self.protocol = json_data["outbounds"][0]["protocol"]
        security = json_data["outbounds"][0]["streamSettings"]["security"]
        try:
            address = json_data["outbounds"][0]["settings"]["servers"][0]["address"]
            password = json_data["outbounds"][0]["settings"]["servers"][0]["password"]
            port = json_data["outbounds"][0]["settings"]["servers"][0]["port"]

        except:
            address = json_data["outbounds"][0]["settings"]["vnext"][0]["address"]
            password = json_data["outbounds"][0]["settings"]["vnext"][0]["users"][0][
                "id"
            ]
            port = json_data["outbounds"][0]["settings"]["vnext"][0]["port"]

        if security == "reality":
            server_name = json_data["outbounds"][0]["streamSettings"][
                "realitySettings"
            ]["serverName"]
            fingerprint = json_data["outbounds"][0]["streamSettings"][
                "realitySettings"
            ]["fingerprint"]
            public_key = json_data["outbounds"][0]["streamSettings"]["realitySettings"][
                "publicKey"
            ]
            short_id = json_data["outbounds"][0]["streamSettings"]["realitySettings"][
                "shortId"
            ]
            spider_x = json_data["outbounds"][0]["streamSettings"]["realitySettings"][
                "spiderX"
            ]

            link = f"{self.protocol}://{password}@{address}:{port}?security={security}&sni={server_name}&fp={fingerprint}&pbk={public_key}&sid={short_id}&spx={spider_x}&type=grpc#{self.pname}"
            return link
        elif security == "tls":
            server_name = json_data["outbounds"][0]["streamSettings"]["tlsSettings"][
                "serverName"
            ]
            type = json_data["outbounds"][0]["streamSettings"]["network"]
            link = f"{self.protocol}://{password}@{address}:{port}?security={security}&sni={server_name}&type={type}&headerType=none#{self.pname}"
            return link

    def __extract_attributes_as_json__(self):
        json_data = self.json_data
        output = dict()
        output["v"] = "2"
        # self.protocol = json_data["outbounds"][0]["protocol"]
        output["ps"] = self.pname
        if ("vmess" in json_data) or ("vless" in json_data):
            output["add"] = json_data["outbounds"][0]["settings"]["vnext"][0]["address"]
            output["port"] = str(
                json_data["outbounds"][0]["settings"]["vnext"][0]["port"]
            )
            output["id"] = json_data["outbounds"][0]["settings"]["vnext"][0]["users"][
                0
            ]["id"]
            output["aid"] = json_data["outbounds"][0]["settings"]["vnext"][0]["users"][
                0
            ]["alterId"]
            # str(json_data["outbounds"][0]["streamSettings"]["mux"]["enabled"])
            output["scy"] = json_data["outbounds"][0]["settings"]["vnext"][0]["users"][
                0
            ]["security"]

        output["net"] = json_data["outbounds"][0]["streamSettings"]["network"]
        output["tls"] = json_data["outbounds"][0]["streamSettings"]["security"]

        try:
            output["sni"] = json_data["outbounds"][0]["streamSettings"]["tlsSettings"][
                "serverName"
            ]
        except:
            output["sni"] = ""

        # output["allowInsecure"] = json_data["outbounds"][0]["streamSettings"][
        #     "tlsSettings"
        # ]["allowInsecure"]
        try:
            output["alpn"] = ""

            alpn = output["alpn"] = json_data["outbounds"][0]["streamSettings"][
                "tlsSettings"
            ]["alpn"][0]

            alpn = output[
                "alpn"
            ] = f'{alpn},{json_data["outbounds"][0]["streamSettings"]["tlsSettings"]["alpn"][1]}'

            alpn = output[
                "alpn"
            ] = f'{alpn},{json_data["outbounds"][0]["streamSettings"]["tlsSettings"]["alpn"][2]}'

            # output[
            #     "alpn"
            # ] = f',{json_data["outbounds"][0]["streamSettings"]["tlsSettings"]["alpn"][2]}'
            # output["alpn"] = (
            #     ","
            #     + json_data["outbounds"][0]["streamSettings"]["tlsSettings"]["alpn"][2]
            # )

            # output["alpn"] = []
            # output["alpn"].append(
            #     json_data["outbounds"][0]["streamSettings"]["tlsSettings"]["alpn"][0]
            # )

            # output["alpn"].append(
            #     json_data["outbounds"][0]["streamSettings"]["tlsSettings"]["alpn"][1]
            # )
            # output["alpn"].append(
            #     json_data["outbounds"][0]["streamSettings"]["tlsSettings"]["alpn"][2]
            # )
        except Exception as e:
            pass  # print("Err occured", str(e))
        try:
            output["fp"] = json_data["outbounds"][0]["streamSettings"]["tlsSettings"][
                "fingerprint"
            ]
        except:
            pass

        return json.dumps(output)

    def __load_json__(self):
        with open(self.file_path, "r") as file:
            self.json_data = json.load(file)
        self.protocol = self.json_data["outbounds"][0]["protocol"]


if __name__ == "__main__":
    # path = "C:\\Users\\imi-pc\\Nextcloud\\Documents\\Codes\\gost-runner\\V2rayP\\%appdata\\roaming%\v2rayp\configs\\reality-trojan-2096.json"
    path = "C:\\Users\\imi-pc\\Desktop\\temp.json"
    eufc = ExportURLfromConfig(path)
    print(eufc.share_link())
