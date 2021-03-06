"""v0.1 Licenced under MIT License"""

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from pywinauto import application
from pywinauto.findwindows import ElementNotFoundError
import os
import time
import keyboard
from ast import literal_eval
import traceback

class SettingsPopup(Popup):
    reflex_path_text = ObjectProperty()
    demo_path_text = ObjectProperty()
    #rep_files = ObjectProperty(False)

    def update_settings(self):
        r = open("./reflex.cfg", "w+")
        r.write(self.reflex_path_text.text)
        r.close()
        d = open("./demos.cfg", "w+")
        d.write(self.demo_path_text.text)
        d.close()
        #self.rep_files = True

    def check_demos(self):
        return open("./demos.cfg").read()

    def check_reflex(self):
        return open("./reflex.cfg").read()

    # def rep_files_only(self, instance, value):
    #     if value:
    #         print("checked")
    #     else:
    #         print("unchecked")
    #     print(self.parent)

class Demopedia(BoxLayout):
    reflex_path_text = ObjectProperty()
    demo_list = ObjectProperty()
    fave_button = ObjectProperty()
    last_path_bot = TextInput()
    textinput = TextInput()
    timecode = TextInput()
    last_path = ""
    last_subfolder = ""
    list_adapter = ListAdapter(data=sorted([]), selection_mode='single',
                               allow_empty_selection=True, cls=ListItemButton)
    azerty_num_dict = {".": "shift+;", "0": "shift+à", "1": "shift+&", "2": "shift+é",
                       "3": "shift+\"", "4": "shift+'", "5": "shift+(", "6": "shift+-",
                       "7": "shift+è", "8": "shift+_", "9": "shift+ç"}

    def populate_demo_list(self):
        self.demo_list.adapter = self.list_adapter
        self.demo_list.adapter.bind(on_selection_change=self.display_description)
        demo_cfg_path = open("demos.cfg").read()
        self.last_path_bot.text = demo_cfg_path

        if not demo_cfg_path:
            pass
        elif demo_cfg_path:
            if self.demo_list.adapter.selection and ("." not in self.demo_list.adapter.selection[0].text[-4:]):
                try:
                    if self.last_subfolder != "":
                        self.last_subfolder += "\\" + self.demo_list.adapter.selection[0].text
                    else:
                        self.last_subfolder = self.demo_list.adapter.selection[0].text

                    concat = os.path.join(demo_cfg_path, self.demo_list.adapter.selection[0].text)
                    subdemo_dict = literal_eval(open("./subdemos.cfg").read())

                    if self.last_path:
                        deeper = os.path.join(self.last_path, self.demo_list.adapter.selection[0].text)
                        print(deeper)
                        for deep_demo in os.listdir(deeper):
                            if deep_demo not in self.demo_list.adapter.data:
                                self.demo_list.adapter.data.extend([deep_demo])
                                subdemo_dict[deep_demo] = self.last_subfolder
                                print(self.last_subfolder)
                        r = open("./subdemos.cfg", "w+")
                        r.write(str(subdemo_dict))
                        r.close()
                    else:
                        for deep_demo in os.listdir(concat):
                            if deep_demo not in self.demo_list.adapter.data:
                                subdemo_dict[deep_demo] = self.last_subfolder
                                self.demo_list.adapter.data.extend([deep_demo])
                        r = open("./subdemos.cfg", "w+")
                        r.write(str(subdemo_dict))
                        r.close()
                    self.last_path = concat

                    self.last_path_bot.text = concat
                    self.demo_list.adapter.data = sorted(self.demo_list.adapter.data)
                    return
                except (NotADirectoryError, FileNotFoundError) as e:
                    print("not a directory!")
                    return
            if self.fave_button.state == "down":
                return
            else:
                try:
                    for demo in os.listdir(demo_cfg_path):
                        if demo not in self.demo_list.adapter.data:
                            self.demo_list.adapter.data.extend([demo])
                    self.demo_list.adapter.data = sorted(self.demo_list.adapter.data)
                except FileNotFoundError:
                    self.last_path_bot.text = "not a real folder!"
        else:
            pass

    def add_demo_to_favorites(self):
        try:
            favorites_list = literal_eval(open("./favorites.cfg").read())
            if self.demo_list.adapter.selection:
                for any in self.demo_list.adapter.selection:
                    if any.text in favorites_list:
                        pass
                    else:
                        favorites_list.append(any.text)
                    r = open("./favorites.cfg", "w+")
                    r.write(str(favorites_list))
                    r.close()
        except AttributeError:
            pass

    def populate_favorites(self):
        self.last_path = ""
        self.last_path_bot.text = ""
        self.textinput.text = ""
        self.timecode.text = ""
        self.demo_list.adapter.data = []
        self.fave_button.state = "down"
        self.demo_list.adapter = self.list_adapter
        self.demo_list.adapter.bind(on_selection_change=self.display_description)
        demo_cfg_path = open("demos.cfg").read()
        self.last_path_bot.text = demo_cfg_path
        favorites_list = literal_eval(open("./favorites.cfg").read())

        if favorites_list:
            try:
                for demo in favorites_list:
                    self.demo_list.adapter.data.extend([demo])

                self.demo_list.adapter.data = sorted(self.demo_list.adapter.data)
            except FileNotFoundError:
                print("not a real folder")
        else:
            pass

    def display_description(self, adapter):
        desc_dict = literal_eval(open("./descriptions.cfg").read())
        timecode_dict = literal_eval(open("./timecodes.cfg").read())

        if adapter.selection:
            if adapter.selection[0].text in desc_dict.keys():
                self.textinput.text = desc_dict[adapter.selection[0].text]
            else:
                self.textinput.text = ""
            if adapter.selection[0].text in timecode_dict.keys():
                self.timecode.text = timecode_dict[adapter.selection[0].text]
            else:
                self.timecode.text = ""
            if adapter.selection[0].text[-4:] == ".rep":
                self.last_path_bot.text = "play " + adapter.selection[0].text[:-4]
            else:
                self.last_path_bot.text = adapter.selection[0].text
        else:
            pass

    def save_description(self):
        description_dict = literal_eval(open("./descriptions.cfg").read())
        timecode_dict = literal_eval(open("./timecodes.cfg").read())
        try:
            selected_demo = self.demo_list.adapter.selection[0].text
            demo_description = self.textinput.text
            timecode_text = self.timecode.text

            if selected_demo: # and selected_demo[-4:] == ".rep":
                description_dict[selected_demo] = demo_description
                timecode_dict[selected_demo] = timecode_text

                r = open("./descriptions.cfg", "w+")
                r.write(str(description_dict))
                r.close()

                r = open("./timecodes.cfg", "w+")
                r.write(str(timecode_dict))
                r.close()
            else:
                pass
        except (IndexError, AttributeError):
            print("No selection")

    def delete_demos(self):
        try:
            favorites_list = literal_eval(open("./favorites.cfg").read())
            if self.demo_list.adapter.selection:
                for any in self.demo_list.adapter.selection:
                    self.demo_list.adapter.data.remove(any.text)
                    if any.text in favorites_list:
                        favorites_list.remove(any.text)
                        r = open("./favorites.cfg", "w+")
                        r.write(str(favorites_list))
                        r.close()
                self.textinput.text = ""
                self.timecode.text = ""
        except AttributeError:
            pass

    def clear_demo_list(self):
        self.last_path = ""
        self.last_subfolder = ""
        self.last_path_bot.text = ""
        self.textinput.text = ""
        self.timecode.text = ""
        self.demo_list.adapter.data = []
        self.fave_button.state = "normal"

    def play_demo(self):
        subdemo_dict = literal_eval(open("./subdemos.cfg").read())
        try:
            selection = self.demo_list.adapter.selection[0].text

            if self.demo_list.adapter.selection[0].text in subdemo_dict.keys():
                selection = subdemo_dict[self.demo_list.adapter.selection[0].text] + "\\" + self.demo_list.adapter.selection[0].text
            print("ok")
            if selection[-4:] == ".rep":
                print("okkk")
                try:
                    app = application.Application()
                    app.connect(title="Reflex Arena")
                    app_dialog = app.top_window()
                    app_dialog.Minimize()
                    app_dialog.Restore()
                    time.sleep(0.35)
                    keyboard.press_and_release("`")
                    time.sleep(0.4)
                    keyboard.write(self.last_path_bot.text)
                    time.sleep(0.65)
                    keyboard.press_and_release("enter")
                    time.sleep(0.75)
                    keyboard.press_and_release("`")

                except ElementNotFoundError:
                    cwd = os.getcwd()
                    path = open("reflex.cfg", "r").read()
                    os.chdir(path)
                    app = application.Application()
                    app.start("reflex.exe")
                    os.chdir(cwd)
                    time.sleep(9)
                    keyboard.press_and_release("`")
                    time.sleep(0.4)
                    keyboard.write(self.last_path_bot.text)
                    time.sleep(0.65)
                    keyboard.press_and_release("enter")
                    time.sleep(0.75)
                    keyboard.press_and_release("`")

                except ValueError:
                    #TRY AZERTY KEYBOARDS
                    try:
                        app = application.Application()
                        app.connect(title="Reflex Arena")
                        app_dialog = app.top_window()
                        app_dialog.Minimize()
                        app_dialog.Restore()
                        time.sleep(0.35)
                        keyboard.press_and_release("²")
                        time.sleep(0.4)
                        keyboard.write("play ")
                        for any in str(selection[:-4]):
                            if any.isdigit() or any is ".":
                                keyboard.press_and_release(self.azerty_num_dict[any])
                            else:
                                keyboard.press_and_release(any)
                        time.sleep(0.65)
                        keyboard.press_and_release("enter")
                        time.sleep(0.75)
                        keyboard.press_and_release("²")

                    except ElementNotFoundError:
                        cwd = os.getcwd()
                        path = open("reflex.cfg", "r").read()
                        os.chdir(path)
                        app = application.Application()
                        app.start("reflex.exe")
                        os.chdir(cwd)
                        time.sleep(9)
                        keyboard.press_and_release("²")
                        time.sleep(0.4)
                        keyboard.write("play ")
                        for any in str(selection[:-4]):
                            if any.isdigit() or any is ".":
                                keyboard.press_and_release(self.azerty_num_dict[any])
                            else:
                                keyboard.press_and_release(any)
                        time.sleep(0.65)
                        keyboard.press_and_release("enter")
                        time.sleep(0.75)
                        keyboard.press_and_release("²")

                    except ValueError:
                        #non qwerty/azerty keyboards hit this
                        self.last_path_bot.text = "Unsupported keyboard format- lol sucks"
                    except:
                        traceback.print_exc()

                except OSError:
                    traceback.print_exc()
            else:
                pass
        except:
            traceback.print_exc()

    def open_popup(self):
        SettingsPopup().open()

class DemopediaApp(App):
    def build(self):
        return Demopedia()

if __name__ == '__main__':
    demoApp = DemopediaApp()
    demoApp.run()
