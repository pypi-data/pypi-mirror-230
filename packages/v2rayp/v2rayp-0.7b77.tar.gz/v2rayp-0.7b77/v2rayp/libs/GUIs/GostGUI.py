import json
import sys

sys.path.append("v2rayp")

import PySimpleGUI as psg
from libs.in_win import config_path, inside_windows

psg.set_options(font=("Arial Bold", 11))
page_data = dict()
page_data["remote_protocol"] = ""
page_data["remote_address"] = ""
page_data["remote_port"] = ""
page_data["remote_user"] = ""
page_data["remote_password"] = ""
page_data["remark"] = ""


class GostGUI:
    def __init__(self, pname, subscription="") -> None:
        if pname:
            self.pname = pname
            self.subscription = subscription
            self.load_json_data()

        else:
            self.page_data = page_data
            self.pname = f'{page_data["remote_protocol"]}_{page_data["remote_port"]}'
        self.layout = [
            [self.generate_top_parts()],
            [psg.HorizontalSeparator()],
            # [self.generate_middle_parts()],
            # [psg.HorizontalSeparator()],
            # [self.generate_bottom_parts()],
            # [psg.HorizontalSeparator()],
            # [self.generate_ending_parts()],
            # [psg.HorizontalSeparator()],
            [self.generate_buttons()],
        ]

    def getLayout(self) -> list:
        return self.layout

    def generate_top_parts(self):
        layout = [
            [psg.Text("Gost", justification="center", font=("Arial Bold", 18))],
            [psg.HorizontalSeparator()],
            [psg.Text(f'{self.page_data["remark"]}')],
            [
                psg.Text("Protocol:\t\t"),
                psg.InputText(
                    default_text=self.page_data["remote_protocol"], key="protocol"
                ),
            ],
            [
                psg.Text("Address:\t\t"),
                psg.InputText(
                    default_text=self.page_data["remote_address"], key="address"
                ),
            ],
            [
                psg.Text("Port:\t\t"),
                psg.InputText(default_text=self.page_data["remote_port"], key="port"),
            ],
            [
                psg.Text("Username:\t"),
                psg.InputText(
                    default_text=self.page_data["remote_user"], key="username"
                ),
            ],
            [
                psg.Text("Password:\t"),
                psg.InputText(
                    default_text=self.page_data["remote_password"], key="password"
                ),
            ],
        ]
        return layout

    def generate_buttons(self):
        layout = [
            psg.Button(key="confirm", button_text="Confirm"),
            psg.Button(key="cancel", button_text="Cancel"),
        ]
        return layout

    def start_window(self):
        layout = self.getLayout()
        self.window = psg.Window(
            "Gost",
            layout,
            # size=(600, 790),
            resizable=True,
            no_titlebar=True,
            grab_anywhere=True,
            keep_on_top=True,
        )
        while True:
            event, values = self.window.read()
            # print("event:", event, "values:", values)
            if event == psg.WIN_CLOSED or "cancel" in event:
                self.page_data = None
                break
            elif "confirm" in event:
                self.gether_data()

                break
        self.window.close()
        return self.page_data

    def gether_data(self):
        self.page_data["remote_protocol"] = self.window["protocol"].get()
        self.page_data["remote_address"] = self.window["address"].get()
        self.page_data["remote_port"] = self.window["port"].get()
        self.page_data["remote_user"] = self.window["username"].get()
        self.page_data["remote_password"] = self.window["password"].get()

    def load_json_data(self):
        subscription_path = ""

        if len(self.subscription) > 1:
            subscription_path = f"\\subscriptions\\{self.subscription}"
        with open(
            f"{config_path()}\\gost_profiles{subscription_path}\\{self.pname}",
            "r",
        ) as json_file:
            # Write the JSON data to the file
            self.page_data = json.load(json_file)
        self.page_data["remark"] = self.pname


if __name__ == "__main__":
    GostGUI(None).start_window()
