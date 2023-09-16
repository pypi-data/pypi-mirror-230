import json
import sys

import PySimpleGUI as psg

sys.path.append("v2rayp")
from libs.in_win import config_path, inside_windows


class SubscriptionGUI:
    def __init__(self) -> None:
        self.get_subs()
        self.layout = [[self.generate_top_parts()], [self.generate_buttons()]]

    def get_subs(self):
        subscription_guide_path = f"{config_path()}\\gui\\subscription.json"
        if not inside_windows():
            subscription_guide_path = subscription_guide_path.replace("\\", "/")
        try:
            with open(subscription_guide_path, "r") as file:
                self.json_object = json.load(file)
        except:
            pass

    def getLayout(self) -> list:
        return self.layout

    def generate_top_parts(self):
        rows = []

        try:
            len(self.json_object["subscriptions"])
        except:
            layout = [
                [
                    psg.Text(
                        "Configurations",
                        justification="center",
                        font=("Arial Bold", 18),
                    )
                ],
                [],
            ]
            return layout

        for sub in self.json_object["subscriptions"]:
            subscription_name = sub["subscription_name"]
            url = sub["url"]

            row = [
                [psg.HorizontalSeparator()],
                [
                    psg.Text("Sub Name:\t"),
                    psg.InputText(
                        default_text=subscription_name, key=f"sname_{subscription_name}"
                    ),
                ],
                [
                    psg.Text("URL:\t\t"),
                    psg.InputText(default_text=url, key=f"url_{subscription_name}"),
                ],
                [
                    psg.Column(
                        [[psg.Button("Delete", key=f"delete_{subscription_name}")]],
                        justification="center",
                    )
                ],
            ]
            rows.append(row)

        layout = [
            [
                psg.Text(
                    "Configurations", justification="center", font=("Arial Bold", 18)
                )
            ],
            rows,
        ]
        return layout

    def generate_buttons(self):
        layout = [
            psg.Button(key="confirm", button_text="Confirm"),
            psg.Button(key="new", button_text="New"),
            psg.Button(key="cancel", button_text="Cancel"),
        ]
        return layout

    def start_window(self):
        layout = self.getLayout()
        self.window = psg.Window(
            "Subscription Configs",
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

            if "confirm" in event:
                page_data = self.save_return()
                break

            elif "new" in event:
                page_data = self.save_return()
                break

            elif "cancel" in event or event == psg.WIN_CLOSED:
                page_data = None
                break
        self.window.close()
        return page_data


if __name__ == "__main__":
    SubscriptionGUI().start_window()
