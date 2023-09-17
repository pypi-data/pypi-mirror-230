import re
import subprocess
from typing import List, Union

from . import utils
from enum import Enum


class DeviceTypes(str, Enum):
    HEADPHONE = "headphone"
    MICROPHONE = "microphone"


class PacmdExecutor:
    def execute(self, exec_args: list):
        return subprocess.run(
            ["pacmd"] + exec_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )


class Device:
    def __init__(self, index: str, name: str, type: DeviceTypes, is_current_device: bool):
        self.index = index
        self.name = name
        self.is_current_device = is_current_device
        self.type = type.value

    def __repr__(self):
        return (f"Device(index={self.index}, device={self.name},"
                f" type_={self.type}, is_current_device={self.is_current_device})")

    def dict(self):
        return {
            "index": self.index,
            "name": self.name,
            "type": self.type,
            "is_current_device": self.is_current_device
        }


class SearchDevices:
    def __init__(self):
        self.pacmd = PacmdExecutor()

    def _search(self, text_stdout: str, device_type: DeviceTypes) -> List[Device]:
        raw_devices = self._text_stdout_parse(text_stdout)
        devices = []
        for device_txt in raw_devices:
            lines = [line for line in device_txt.split("\n")]
            is_current_device = "*" in lines[0]
            index = utils.get_number(lines[0])
            name = (
                " ".join(lines[1].split(" ")[1:])
                .strip()
                .replace("<", "")
                .replace(">", "")
            )
            devices.append(
                Device(index=index, name=name, type=device_type, is_current_device=is_current_device)
            )
        return devices

    def get_headphones(self) -> List[Device]:
        text_stdout = self.pacmd.execute(["list-sinks"]).stdout.decode("utf-8")
        return self._search(text_stdout, DeviceTypes.HEADPHONE)

    def get_microphones(self) -> List[Device]:
        text_stdout = self.pacmd.execute(["list-sources"]).stdout.decode("utf-8")
        return self._search(text_stdout, DeviceTypes.MICROPHONE)

    def get_current_headphone(self) -> Union[Device, None]:
        headphones = self.get_headphones()
        for headphone in headphones:
            if headphone.is_current_device:
                return headphone
        return None

    def get_current_microphone(self) -> Union[Device, None]:
        microphones = self.get_microphones()
        for microphone in microphones:
            if microphone.is_current_device:
                return microphone
        return None

    def get_device_by_name(self, name: str, device_type: DeviceTypes) -> Union[Device, None]:
        devices = []
        if device_type == DeviceTypes.HEADPHONE:
            devices = self.get_headphones()
        elif device_type == DeviceTypes.MICROPHONE:
            devices = self.get_microphones()
        for device in devices:
            if device.name == name:
                return device

    @classmethod
    def _text_stdout_parse(cls, text_stdout: str) -> list:
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


class AudioController(SearchDevices):
    def __init__(self):
        super().__init__()
        self.pacmd = PacmdExecutor()

    def set_default_device(self, device: Device) -> bool:
        if not device:
            return False

        if device.type == DeviceTypes.HEADPHONE:
            execution = self.pacmd.execute(["set-default-sink", device.index])
        elif device.type == DeviceTypes.MICROPHONE:
            execution = self.pacmd.execute(["set-default-source", device.index])
        else:
            return False

        is_success = execution.stdout.decode("utf-8") == ""
        return is_success
