import PySimpleGUI as sg


class FileBrowser:
    def get_folder_path(self):
        path = self.execute_folder()
        self.close()
        return path

    def get_file_path(self):
        path = self.execute()
        self.close()
        return path

    def execute(self):
        layout = [
            [sg.T("")],
            [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")],
            [sg.Button("Upload")],
        ]

        ###Building Window
        self.window = sg.Window("File Browser", layout, keep_on_top=True)

        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == "Exit":
                break
            elif event == "Upload":
                value = values["-IN-"]
                break
        try:
            return value
        except:
            return None

    def execute_folder(self):
        layout = [
            [sg.Text("Select a folder:")],
            [sg.Input(size=(40, 1)), sg.FolderBrowse(key="-FOLDER-")],
            [sg.Button("Select"), sg.Button("Exit")],
        ]

        self.window = sg.Window("Folder Browser", layout)

        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == "Exit":
                break
            elif event == "Select":
                # Get the selected folder path from the Input element
                selected_folder_path = values["-FOLDER-"]
                # Do something with the selected folder path (e.g., print it)
                return selected_folder_path

    def close(self):
        try:
            self.window.close()
        except:
            pass


if __name__ == "__main__":
    print(FileBrowser().get_folder_path())
