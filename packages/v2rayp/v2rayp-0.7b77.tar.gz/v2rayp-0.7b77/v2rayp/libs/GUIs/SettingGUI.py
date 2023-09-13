import sys

import PySimpleGUI as psg

sys.path.append("v2rayp")
from libs.in_win import FactorySetting

psg.set_options(font=("Arial Bold", 11))


page_data = dict()
page_data["keep_top"] = True
page_data["close_to_tray"] = False
page_data["auto_connect"] = False
page_data["start_minimized"] = False
page_data["cloudflare_address"] = "bruce.ns.cloudflare.com"
page_data["cloudflare_port"] = "2087"
page_data["segmentation_timeout"] = 5
page_data["num_of_fragments"] = 100
page_data["beep"] = True


class SettingGUI:
    def __init__(self, page_data=page_data) -> None:
        self.settings = page_data
        self.layout = [
            [self.generate_top_parts()],
            [psg.HorizontalSeparator()],
            [self.factory_reset_layout()],
            [psg.HorizontalSeparator()],
            [self.generate_middle_parts()],
            [psg.HorizontalSeparator()],
            [self.generate_buttons()],
        ]

    def getLayout(self) -> list:
        return self.layout

    def factory_reset_layout(self):
        row = [
            [psg.Text("Factory Reset:", font=("Arial Bold", 14))],
            [
                psg.Checkbox(
                    "Factory:\t\t",
                    default=bool(self.settings["keep_top"]),
                    key="keep_top",
                ),
            ],
        ]
        return row

    def generate_top_parts(self):
        layout = [
            [psg.Text("Settings", justification="center", font=("Arial Bold", 18))],
            [psg.HorizontalSeparator()],
            [
                psg.Text("Beep:\t"),
                psg.Checkbox(
                    text="",
                    default=self.settings["beep"] if "beep" in self.settings else False,
                    key="beep",
                ),
            ],
            [psg.HorizontalSeparator()],
            [psg.Text("Configs:", font=("Arial Bold", 14))],
            [psg.Button("Factory Reset", key="factory")],
            [
                psg.Checkbox(
                    "Minimize to tray on close:\t\t",
                    default=bool(self.settings["close_to_tray"]),
                    key="close_to_tray",
                ),
            ],
            [
                psg.Checkbox(
                    "Auto connect on start:\t\t",
                    default=bool(self.settings["auto_connect"]),
                    key="auto_connect",
                ),
            ],
            [
                psg.Checkbox(
                    "Start minimized:\t\t",
                    default=bool(self.settings["start_minimized"]),
                    key="start_minimized",
                ),
            ],
        ]
        return layout

    def generate_middle_parts(self):
        layout = [
            [psg.Text("Segmentation Settings:", font=("Arial Bold", 14))],
            [
                psg.Text("Cloudflare Address:\t"),
                psg.InputText(
                    default_text=self.settings["cloudflare_address"],
                    key="cloudflare_address",
                    size=(20, 10),
                ),
            ],
            # [
            #     psg.Text("Cloudflare Port:\t\t"),
            #     psg.InputText(
            #         size=(20, 10),
            #         default_text=self.settings["cloudflare_port"],
            #         key="cloudflare_port",
            #     ),
            # ],
            [
                psg.Text("Segmentation Timeout:\t"),
                psg.InputText(
                    size=(20, 10),
                    default_text=self.settings["segmentation_timeout"],
                    key="segmentation_timeout",
                ),
            ],
            [
                psg.Text("Number of Segmentation:\t"),
                psg.InputText(
                    size=(20, 10),
                    default_text=self.settings["num_of_fragments"],
                    key="num_of_fragments",
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

    def save_gui(self):
        self.settings["keep_top"] = self.window["keep_top"].get()
        self.settings["close_to_tray"] = self.window["close_to_tray"].get()
        self.settings["auto_connect"] = self.window["auto_connect"].get()
        self.settings["start_minimized"] = self.window["start_minimized"].get()
        self.settings["cloudflare_address"] = self.window["cloudflare_address"].get()
        # self.settings["cloudflare_port"] = self.window["cloudflare_port"].get()
        self.settings["num_of_fragments"] = self.window["num_of_fragments"].get()
        self.settings["segmentation_timeout"] = self.window[
            "segmentation_timeout"
        ].get()
        self.settings["beep"] = self.window["beep"].get()

    def close(self):
        self.window.close()

    def start_window(self) -> dict:
        layout = self.getLayout()
        self.window = psg.Window(
            "Vmess",
            layout,
            # size=(600, 790),
            resizable=False,
            # no_titlebar=True,
            keep_on_top=True,
            grab_anywhere=True,
        )
        while True:
            event, _ = self.window.read()
            # print("event:", event, "values:", values)
            if event == psg.WIN_CLOSED:
                break
            if "confirm" in event:
                self.save_gui()
                break
            elif "cancel" in event:
                self.settings = None
                break
            elif "factory" in event:
                response = psg.popup_yes_no(
                    "***Warning***", "Are you sure?", keep_on_top=True
                )
                print(response)
                if response == "Yes":
                    self.factory_reset()
                    # os.execv(
                    #     sys.executable, [os.path.basename(sys.executable)] + sys.argv
                    # )
                    self.window.close()
                    return "factory_reset"
                break

        self.window.close()
        return self.settings

    def factory_reset(self):
        FactorySetting.delete_config_folder()


if __name__ == "__main__":
    print(SettingGUI(page_data).start_window())
