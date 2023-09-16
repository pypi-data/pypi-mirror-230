import re
import subprocess
from typing import List, Union

from simpleaudiocontroller import utils


class PacmdExecutor:
    def execute(self, exec_args: list):
        return subprocess.run(
            ["pacmd"] + exec_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )


class Device:
    def __init__(self, index: str, name: str, is_current_device: bool = False):
        self.index = index
        self.name = name
        self.is_current_device = is_current_device

    def __repr__(self):
        return f"Device(index={self.index}, device={self.name}, is_current_device={self.is_current_device})"


class SearchDevices:
    def __init__(self, text_stdout: str):
        self.raw_devices: list = self.parse_text_stdout(text_stdout)

    def search(self) -> List[Device]:
        devices = []
        for device_txt in self.raw_devices:
            lines = [line for line in device_txt.split("\n")]
            is_current_device = "*" in lines[0]
            index = utils.get_number(lines[0])
            name = " ".join(lines[1].split(" ")[1:]).strip()
            devices.append(
                Device(index=index, name=name, is_current_device=is_current_device)
            )
        return devices

    @classmethod
    def parse_text_stdout(cls, text_stdout: str) -> list:
        asterisk_location_re = re.search(r"\* index: \d", text_stdout)
        asterisk_location_index = (
            utils.get_number(asterisk_location_re.group())
            if asterisk_location_re
            else None
        )
        devices_list = re.split(r"index: ", text_stdout)[1:]
        devices = []
        for device_txt in devices_list:
            lines = [line.strip() for line in device_txt.split("\n")]
            lines[0] = "index: " + lines[0]
            if asterisk_location_index:
                index = utils.get_number(lines[0])
                if asterisk_location_index == index:
                    lines[0] = "* " + lines[0]

            devices.append("\n".join(lines))
        return devices


class AudioController:
    def __init__(self):
        self.pacmd = PacmdExecutor()

    def set_default_headphone(self, device: Device) -> bool:
        if not device:
            return False
        execution = self.pacmd.execute(["set-default-sink", device.index])
        return device and execution.stdout.decode("utf-8") == ""

    def set_default_microphone(self, device: Device) -> bool:
        if not device:
            return False
        execution = self.pacmd.execute(["set-default-source", device.index])
        return device and execution.stdout.decode("utf-8") == ""

    def get_current_headphone(self) -> Union[Device, None]:
        headphones = self.get_phones()
        for headphone in headphones:
            if headphone.is_current_device:
                return headphone

    def get_current_microphone(self) -> Union[Device, None]:
        microphones = self.get_microphones()
        for microphone in microphones:
            if microphone.is_current_device:
                return microphone

    def get_microphone_by_name(self, name: str) -> Union[Device, None]:
        microphones = self.get_microphones()
        for microphone in microphones:
            if microphone.name == name:
                return microphone

    def get_phone_by_name(self, name: str) -> Union[Device, None]:
        headphones = self.get_phones()
        for headphone in headphones:
            if headphone.name == name:
                return headphone

    def get_phones(self) -> List[Device]:
        text_stdout = self.pacmd.execute(["list-sinks"]).stdout.decode("utf-8")
        devices = SearchDevices(text_stdout).search()
        return devices

    def get_microphones(self) -> List[Device]:
        text_stdout = self.pacmd.execute(["list-sources"]).stdout.decode("utf-8")
        devices = SearchDevices(text_stdout).search()
        return devices
