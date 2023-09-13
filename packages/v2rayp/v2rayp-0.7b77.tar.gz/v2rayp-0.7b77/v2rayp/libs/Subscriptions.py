# import parsel

import base64
import json
import os
from urllib.parse import urlparse

import requests
from libs.in_win import config_path, inside_windows
from libs.V2RayURL2Config import generate_v2rayconfig_with_name


class Subscriptions:
    def __init__(self, URL="") -> None:
        self.URL = URL

    def create_name_from_url(self, url):
        # Parse the URL to extract its components
        parsed_url = urlparse(url)

        # Extract the website name (domain) from the URL
        website_name = parsed_url.netloc.split(".")[0]

        # Extract other parts of the URL (path and query) if available
        path_segments = parsed_url.path.split("/")
        other_parts = [segment for segment in path_segments if segment]

        # Combine the website name and other parts to form the name
        name_parts = [website_name] + other_parts
        name = "_".join(name_parts)

        return name

    def put_v2ray_subscription_in_folder(
        self, subscription_name: str, config_name: str, json_config: json
    ):
        path = f"{config_path()}\\v2ray_profiles\\subscriptions\\{subscription_name}"

        file_path = f"{path}\\{config_name}.json"
        if not inside_windows():
            file_path = file_path.replace("\\", "/")
        with open(file_path, "w") as file:
            json.dump(json_config, file, indent=2)

    def put_gost_subscription_in_folder(
        self, subscription_name: str, config_name: str, json_config: json
    ):
        path = f"{config_path()}\\gost_profiles\\subscriptions\\{subscription_name}"

        try:
            os.makedirs(path)
        except Exception as e:
            print("Err occured 744: ", str(e))

        file_path = f"{path}\\{config_name}.json"
        if not inside_windows():
            file_path = file_path.replace("\\", "/")
        with open(file_path, "w") as file:
            json.dump(json_config, file, indent=2)

    def make_subscription(self):
        try:
            text_output = requests.get(self.URL).text.strip()
        except:
            return False
        responses = text_output.split("\n")

        # responses = [
        #     r"trojan://LjWyuE2d8M@hels.ddns.net:44838?security=reality&sni=yahoo.com&fp=firefox&pbk=8LIuGGsdhR59qjyRALAmGKNuKVlyH3t8OqJmRRdyKl4&sid=92cd56b1&spx=%2F&type=grpc"
        # ]
        subscription_name = (
            self.create_name_from_url(self.URL).replace(" ", "_").replace("|", "_")
        )  # "isharifi"
        self.make_folder_ready(subscription_name)

        for response in responses:
            try:
                if "gost://" not in response:
                    json_out, name = generate_v2rayconfig_with_name(response)
                    name = name.replace(" ", "_").replace("|", "_")
                    self.put_v2ray_subscription_in_folder(
                        subscription_name, name, json_out
                    )
                else:
                    content64 = response.replace("gost://", "")
                    content = str(base64.b64decode(content64).decode("utf-8"))
                    json_out = json.loads(content)
                    name = f'{json_out["remote_protocol"]}_{json_out["remote_port"]}'
                    self.put_gost_subscription_in_folder(
                        subscription_name, name, json_out
                    )
            except Exception as e:
                print(e)
        return True

    def make_folder_ready(self, subscription_name):
        ################################temporary remove all subscriptions
        self.delete_subscription_folder()
        ################################
        path = f"{config_path()}\\v2ray_profiles\\subscriptions\\{subscription_name}"
        cmd = f"rmdir /s /q {path}"
        if not inside_windows():
            path = path.replace("\\", "/")
            cmd = f"rm -rf {path}"
        os.popen(cmd).read()
        if not inside_windows():
            path = path.replace("\\", "/")
        cmd = f"mkdir {path}"
        if not inside_windows():
            cmd = f"mkdir -p {path}"
        os.popen(cmd).read()

    def delete_subscription_folder(self):
        path = f"{config_path()}\\v2ray_profiles\\subscriptions\\"
        cmd = f"rmdir /s /q {path}"
        if not inside_windows():
            path = path.replace("\\", "/")
            cmd = f"rm -rf {path}"
        os.popen(cmd).read()

        path = f"{config_path()}\\gost_profiles\\subscriptions\\"
        cmd = f"rmdir /s /q {path}"
        if not inside_windows():
            path = path.replace("\\", "/")
            cmd = f"rm -rf {path}"
        os.popen(cmd).read()


if __name__ == "__main__":
    URL = "https://isharifi.ir/codes/v2ray"
    Subscriptions(URL).make_subscription()
