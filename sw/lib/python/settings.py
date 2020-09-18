#!/usr/bin/env python3

from lxml import etree
from typing import List
import sys
from os import path, getenv
import time

PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../')))
sys.path.append(PPRZ_HOME + "/var/lib/python")
from pprzlink.ivy import IvyMessagesInterface
from pprzlink.message import PprzMessage


class PprzSettingsManager:
    def __init__(self, settings_xml_path, ac_id, ivy: IvyMessagesInterface):
        self.ac_id = ac_id
        self.ivy = ivy
        self.settings_grp = PprzSettingsParser.parse(settings_xml_path)
        self.ivy.subscribe(self.update_values, PprzMessage('ground', 'DL_VALUES'))

    def update_values(self, sender, msg):
        if self.ac_id == msg.ac_id:
            for i, value in enumerate(msg.values):
                if value != '?':
                    value = float(value)
                    s = self.settings_grp[i]    # type: PprzSetting
                    s.set(value)

    def __getitem__(self, item):
        return self.settings_grp.__getitem__(item)

    def __setitem__(self, key, value):
        setting = self.settings_grp[key]
        msg = PprzMessage("ground", "DL_SETTING")
        msg['ac_id'] = self.ac_id
        msg['index'] = setting.index
        msg['value'] = value
        self.ivy.send(msg)

    def __len__(self):
        return self.settings_grp.__len__()


class PprzSettingsParser:
    def __init__(self):
        self.setting_nb = 0

    @staticmethod
    def parse(settings_xml_path):
        parser = PprzSettingsParser()
        settings_tree = etree.parse(settings_xml_path)
        sets_element = settings_tree.find("dl_settings")
        return parser.parse_dl_settings(sets_element)

    def parse_dl_setting(self, element):
        var = element.attrib["var"]
        min_v = float(element.attrib["min"])
        max_v = float(element.attrib["max"])
        shortname = element.attrib.get("shortname", var)
        step = float(element.attrib.get("step", 1))
        values = element.attrib.get("values")

        if values is None:
            values = []
        else:
            values = values.split("|")
            count = int((max_v - min_v + step) / step)
            if len(values) != count:
                print("Warning: possibly wrong number of values ({}) for {} (expected {})"
                      .format(len(values), shortname, count))
        setting = PprzSetting(var, self.setting_nb, shortname, min_v, max_v, step, values, element)

        for e_button in element.findall("strip_button"):
            name = e_button.attrib["name"]
            value = e_button.attrib["value"]
            icon = e_button.attrib.get("icon")
            group = e_button.attrib.get("group")
            button = StripButton(value, name, icon, group)
            setting.buttons.append(button)

        for e_key in element.findall("key_press"):
            key = e_key.attrib["key"]
            value = e_key.attrib["value"]
            key_press = KeyPress(key, value)
            setting.key_press.append(key_press)

        self.setting_nb += 1
        return setting

    def parse_dl_settings(self, element):
        name = element.attrib.get("name")
        group = PprzSettingsGrp(name)
        for child in element.getchildren():
            if child.tag == "dl_settings":
                setting_group = self.parse_dl_settings(child)
                group.groups_list.append(setting_group)
            elif child.tag == "dl_setting":
                setting = self.parse_dl_setting(child)
                group.settings_list.append(setting)
            else:
                raise Exception("tag {} not supported!".format(child.tag))
        return group


class PprzSetting:
    """Paparazzi Setting Class"""

    def __init__(self, var, index, shortname, min_value, max_value, step, values, xml):
        self.var = var              # type: str
        self.index = index          # type: int
        self.shortname = shortname  # type: str
        self.min_value = min_value  # type: float
        self.max_value = max_value  # type: float
        self.step = step            # type: float
        self.values = values        # type: List[str]
        self.value = None           # type: float
        self.buttons = []           # type: List[StripButton]
        self.key_press = []         # type: List[KeyPress]
        self.xml = xml

    def __str__(self):
        return "{{var: {}, shortname: {}, index: {}}}".format(self.var, self.shortname, self.index)

    def value_from_name(self, name):
        """Return the index in 'values' table matching a given name. Raise ValueError if the name is unknown."""
        if self.values is None:
            raise ValueError("No named values in this setting")
        return self.values.index(name) + self.min_value

    def set(self, val):
        if isinstance(val, str):
            self.value = self.value_from_name(val)
        elif isinstance(val, float) or isinstance(val, int):
            self.value = val
        else:
            raise Exception("Bad type!")


class StripButton:
    def __init__(self, value, name, icon, group):
        self.value = value
        self.name = name
        self.icon = icon
        self.group = group


class KeyPress:
    def __init__(self, key, value):
        self.value = value
        self.key = key


class PprzSettingsGrp:
    """"Paparazzi Setting Group Class"""

    def __init__(self, name):
        self.name = name
        self.settings_list = []     # type: List[PprzSetting]
        self.groups_list = []       # type: List[PprzSettingsGrp]

    def __str__(self):
        grp_names = [grp.name for grp in self.groups_list]
        settings = [str(setting) for setting in self.settings_list]
        return ", ".join(grp_names + settings)

    def get_all_settings(self):
        all_settings = []
        all_settings += self.settings_list
        for group in self.groups_list:
            all_settings += group.get_all_settings()
        return sorted(all_settings, key=lambda s: s.index)

    def __getitem__(self, item):
        if type(item) == int:
            for setting in self.get_all_settings():
                if item == setting.index:
                    return setting
            raise IndexError("No setting #{}".format(item))
        elif type(item) == str:
            for setting in self.get_all_settings():
                if item == setting.shortname:
                    return setting
            raise AttributeError('No such setting named "{}"'.format(item))

    def __len__(self):
        return len(self.get_all_settings())


def example1():
    # Usage: ./setting.py <path_var_AC>/settings.xml
    settings = PprzSettingsParser.parse(sys.argv[1])
    set_nav_radius = settings["nav_radius"]
    print(set_nav_radius)
    set_no_2 = settings[2]
    print(set_no_2)


def example2():
    # Usage: ./setting.py <path_var_AC>/settings.xml <ac_id>
    ivy = IvyMessagesInterface("DemoSettings")
    try:
        setting_manager = PprzSettingsManager(sys.argv[1], sys.argv[2], ivy)
        while True:
            time.sleep(1)
            setting_manager["altitude"] = setting_manager["altitude"].value + 2
    except KeyboardInterrupt:
        ivy.shutdown()
        print("Stopping on request")


if __name__ == "__main__":
    # example1 usage: ./setting.py <path_var_AC>/settings.xml
    example1()

    # example2 usage: ./setting.py <path_var_AC>/settings.xml <ac_id>
    # example2()

