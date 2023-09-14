import os
import sys

sys.path.append("v2rayp")
import PySimpleGUI as psg

psg.set_options(font=("Arial Bold", 11))
page_data = dict()
page_data["remark"] = ""
page_data["password"] = ""
page_data["serverName"] = ""
page_data["server_address"] = ""
page_data["port"] = ""
page_data["uuid"] = ""
page_data["user_security"] = ""
page_data["grpc_serviceName"] = ""
page_data["network"] = ""
page_data["security"] = ""
page_data["sni"] = ""
page_data["fingerprint"] = ""
page_data["publicKey"] = ""
page_data["shortId"] = ""
page_data["spiderX"] = ""


class TrojanGUI:
    def __init__(self, page_data: dict = page_data) -> None:
        self.page_data = page_data
        # print(page_data)
        self.layout = [
            [self.generate_top_parts()],
            [psg.HorizontalSeparator()],
            [self.generate_middle_parts()],
            [psg.HorizontalSeparator()],
            [self.generate_bottom_parts()],
            [psg.HorizontalSeparator()],
            [self.generate_ending_parts()],
            [psg.HorizontalSeparator()],
            [self.generate_buttons()],
        ]

    def getLayout(self) -> list:
        return self.layout

    def generate_top_parts(self):
        layout = [
            [psg.Text("Trojan", justification="center", font=("Arial Bold", 18))],
            [psg.HorizontalSeparator()],
            [psg.Text("Servers")],
            [
                psg.Text("Alias:\t\t"),
                psg.InputText(default_text=self.page_data["remark"], key="alias"),
            ],
            [
                psg.Text("Address:\t\t"),
                psg.InputText(
                    default_text=self.page_data["server_address"], key="address"
                ),
            ],
            [
                psg.Text("Port:\t\t"),
                psg.InputText(default_text=self.page_data["port"], key="port"),
            ],
        ]
        return layout

    def generate_middle_parts(self):
        encryption_methods = ["auto", "aes-128-gcm", "chacha20-poly1305"]
        layout = [
            [
                psg.Text("Password:\t"),
                psg.InputText(
                    default_text=self.page_data["password"],
                    key="password",
                ),
            ],
            [
                psg.Text("Flow:\t\t"),
                psg.Combo(
                    values=["none", "xtls-rprx-vision", "xtls-rprx-vision-udp443"],
                    key="flow",
                ),
            ],
            [
                psg.Text("Encryption\nMethod:\t\t"),
                psg.Combo(
                    default_value=self.page_data["user_security"],
                    values=encryption_methods,
                    key="encryptionmethod",
                ),
            ],
        ]
        return layout

    def generate_bottom_parts(self):
        protocols = ["ws", "tcp", "kcp", "grpc", "h2", "quic"]
        layout = [
            [psg.Text("Transport")],
            [
                psg.Text("Transport\nProtocol:\t"),
                psg.Combo(
                    default_value=self.page_data["network"],
                    values=protocols,
                    key="transport_protocol",
                ),
            ],
            [psg.Text("Camouflage Type:\t"), psg.InputText(key="camouflage_type")],
            [psg.Text("Camouflage\ndomain (host):\t"), psg.InputText(key="host")],
            [psg.Text("Path:\t\t"), psg.InputText(key="path")],
            # [
            #     psg.Text("Tls:\t\t"),
            #     psg.Combo(
            #         default_value=self.page_data["security"],
            #         values=["none", "tls", "reality"],
            #         key="tls",
            #     ),
            # ],
        ]
        return layout

    def generate_ending_parts(self):
        tls = ["reality", "tls"]
        layout = [
            [
                psg.Text("TLS:\t\t"),
                psg.Combo(
                    default_value=self.page_data["security"]
                    if "security" in self.page_data
                    else self.page_data["tls"],
                    values=tls,
                    key="tls",
                ),
            ],
            [
                psg.Text("SNI:\t\t"),
                psg.InputText(
                    default_text=self.page_data["serverName"], key="serverName"
                ),
            ],
            [
                psg.Text("Fingerprint:\t"),
                psg.Combo(
                    default_value=self.page_data["fingerprint"],
                    values=["firefox", "chrome", "android"],
                    key="fingerprint",
                ),
            ],
        ]

        if self.page_data["security"] == "reality":
            lay_bott = [
                [
                    psg.Text("Public Key:\t"),
                    psg.InputText(
                        default_text=self.page_data["publicKey"], key="publickey"
                    ),
                ],
                [
                    psg.Text("ShortID:\t\t"),
                    psg.InputText(
                        default_text=self.page_data["shortId"], key="shortid"
                    ),
                ],
                [
                    psg.Text("SpiderX:\t\t"),
                    psg.InputText(
                        default_text=self.page_data["spiderX"], key="spiderx"
                    ),
                ],
            ]
            layout.append(lay_bott)

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
            "Trojan",
            layout,
            # size=(600, 750),
            resizable=True,
            no_titlebar=True,
            grab_anywhere=True,
            keep_on_top=True,
        )
        while True:
            event, values = self.window.read()
            # print("event:", event, "values:", values)
            if event == psg.WIN_CLOSED or "cancel" in event:
                break
            elif "confirm" in event:
                self.page_data["remark"] = self.page_data["ps"] = self.window[
                    "alias"
                ].get()
                self.page_data["server_address"] = self.window["address"].get()
                self.page_data["port"] = self.window["port"].get()
                self.page_data["password"] = self.window["password"].get()
                self.page_data["flow"] = self.window["flow"].get()
                self.page_data["user_security"] = self.window["encryptionmethod"].get()
                self.page_data["network"] = self.window["transport_protocol"].get()
                self.page_data["camouflage_type"] = self.window["camouflage_type"].get()
                self.page_data["host"] = self.window["host"].get()
                self.page_data["path"] = self.window["path"].get()
                self.page_data["security"] = self.page_data["tls"] = self.window[
                    "tls"
                ].get()
                self.page_data["serverName"] = self.window["serverName"].get()
                self.page_data["serverName"] = self.window["serverName"].get()
                self.page_data["fingerprint"] = self.window["fingerprint"].get()
                self.page_data["publicKey"] = self.window["publickey"].get()
                self.page_data["shortId"] = self.window["shortid"].get()
                self.page_data["spiderX"] = self.window["spiderx"].get()

                break

        self.window.close()
        print(self.page_data)
        return self.page_data


if __name__ == "__main__":
    TrojanGUI().start_window()
