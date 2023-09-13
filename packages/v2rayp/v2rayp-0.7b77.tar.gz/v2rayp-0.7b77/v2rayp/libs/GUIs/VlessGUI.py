import sys

sys.path.append("v2rayp")
import PySimpleGUI as psg

psg.set_options(font=("Arial Bold", 11))
page_data = dict()
page_data["remark"] = ""
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


class VlessGUI:
    def __init__(self, page_data=page_data) -> None:
        self.page_data = page_data
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
            [psg.Text("Vless", justification="center", font=("Arial Bold", 18))],
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
        combo_values = ["auto", "aes-128-gcm", "chacha20-poly1305"]
        layout = [
            [
                psg.Text("UUID:\t\t"),
                psg.InputText(default_text=self.page_data["uuid"], key="uuid"),
            ],
            [psg.Text("AlterID:\t\t"), psg.InputText(key="alterid")],
            [
                psg.Text("Encryption\nMethod:\t\t"),
                psg.Combo(
                    default_value=self.page_data["user_security"],
                    values=combo_values,
                    key="encryptionmethod",
                ),
            ],
        ]
        return layout

    def generate_bottom_parts(self):
        protocols = ["ws", "tcp", "kcp", "grpc", "h2", "quic"]
        layout = [
            [psg.Text("Transport", font=("Arial Bold", 14))],
            [
                psg.Text("Transport\nProtocol:\t"),
                psg.Combo(
                    default_value=self.page_data["network"],
                    values=protocols,
                    key="transport_protocol",
                ),
            ],
            [
                psg.Text(
                    font=("", 11), text="Camouflage\nType or GRPC\nServiceName:\t"
                ),
                psg.InputText(
                    default_text=self.page_data["grpc_serviceName"]
                    if self.page_data["network"] == "grpc"
                    else "",
                    key="camouflage_type",
                ),
            ],
            [psg.Text("Camouflage\ndomain (host):\t"), psg.InputText(key="host")],
            [
                psg.Text("Path:\t\t"),
                psg.InputText(
                    default_text=self.page_data["path"]
                    if "path" in self.page_data
                    else "",
                    key="path",
                ),
            ],
        ]
        return layout

    def generate_ending_parts(self):
        # tls = ["reality", "tls"]

        try:
            servername = (
                self.page_data["sni"]
                if "sni" in self.page_data
                else self.page_data["serverName"]
            )
        except:
            servername = self.page_data["server_address"]

        layout = [
            [
                psg.Text("Tls:\t\t"),
                psg.Combo(
                    default_value=self.page_data["security"],
                    values=["none", "tls", "reality"],
                    key="tls",
                ),
            ],
            [
                psg.Text("SNI:\t\t"),
                psg.InputText(
                    default_text=servername,
                    key="sni",
                ),
            ],
            [
                psg.Text("Fingerprint:\t"),
                psg.Combo(
                    default_value=self.page_data["fingerprint"]
                    if "fingerprint" in self.page_data
                    else "",
                    values=["firefox", "chrome", "android"],
                    key="fingerprint",
                ),
            ],
            [
                psg.Text("Public\nKey:\t\t"),
                psg.InputText(
                    default_text=self.page_data["publicKey"]
                    if "publicKey" in self.page_data
                    else "",
                    key="publickey",
                ),
            ],
            [
                psg.Text("ShortID:\t\t"),
                psg.InputText(
                    default_text=self.page_data["shortId"]
                    if "shortId" in self.page_data
                    else "",
                    key="shortid",
                ),
            ],
            [
                psg.Text("SpiderX:\t\t"),
                psg.InputText(
                    default_text=self.page_data["spiderX"]
                    if "spiderX" in self.page_data
                    else "",
                    key="spiderx",
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

    def save_return(self):
        self.page_data["remark"] = self.page_data["ps"] = self.window["alias"].get()
        self.page_data["server_address"] = self.window["address"].get()
        self.page_data["port"] = self.window["port"].get()
        self.page_data["uuid"] = self.window["uuid"].get()
        self.page_data["user_security"] = self.window["encryptionmethod"].get()
        # self.page_data["grpc_serviceName"] = "imi"
        self.page_data["network"] = self.window["transport_protocol"].get()
        self.page_data["security"] = self.window["tls"].get()
        self.page_data["sni"] = self.page_data["serverName"] = self.window["sni"].get()
        self.page_data["fingerprint"] = self.window["fingerprint"].get()
        self.page_data["publicKey"] = self.window["publickey"].get()
        self.page_data["shortId"] = self.window["shortid"].get()
        self.page_data["spiderX"] = self.window["spiderx"].get()
        return self.page_data

    def start_window(self):
        layout = self.getLayout()
        self.window = psg.Window(
            "Vless",
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

            if "cancel" in event or event == psg.WIN_CLOSED:
                page_data = None
                break
            elif "confirm" in event:
                page_data = self.save_return()
                break
        self.window.close()
        return page_data


if __name__ == "__main__":
    VlessGUI(page_data).start_window()
