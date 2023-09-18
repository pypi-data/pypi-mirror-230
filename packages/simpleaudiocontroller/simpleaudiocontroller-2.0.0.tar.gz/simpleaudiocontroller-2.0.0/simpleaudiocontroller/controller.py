import re
import subprocess
from typing import List, Union

from . import utils
from enum import Enum


class DeviceTypes(str, Enum):
    HEADPHONE = "headphone"
    MICROPHONE = "microphone"


def pacmd(exec_args: list):
    return subprocess.run(
        ["pacmd"] + exec_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


class Device:
    def __init__(self, index: str, name: str, type_: DeviceTypes, is_current_device: bool):
        self.index = index
        self.name = name
        self.is_current_device = is_current_device
        self.type = type_.value

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

    def get_headphones(self) -> List[Device]:
        text_stdout = pacmd(["list-sinks"]).stdout.decode("utf-8")
        return self._search(text_stdout, DeviceTypes.HEADPHONE)

    def get_microphones(self) -> List[Device]:
        text_stdout = pacmd(["list-sources"]).stdout.decode("utf-8")
        return self._search(text_stdout, DeviceTypes.MICROPHONE)

    def get_current_headphone(self) -> Union[Device, None]:
        headphones = self.get_headphones()
        return self._get_device_by("is_current_device", True, headphones)

    def get_current_microphone(self) -> Union[Device, None]:
        microphones = self.get_microphones()
        return self._get_device_by("is_current_device", True, microphones)

    def get_device_by_name(self, name: str) -> Union[Device, None]:
        devices = self.get_headphones() + self.get_microphones()
        return self._get_device_by("name", name, devices)

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
                Device(index=index, name=name, type_=device_type, is_current_device=is_current_device)
            )
        return devices

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

    @staticmethod
    def _get_device_by(key: str, value, devices: List[Device]) -> Union[Device, None]:
        for device in devices:
            if getattr(device, key) == value:
                return device
        return None


class AudioController(SearchDevices):

    def set_default_device(self, device: Device) -> bool:
        if not device:
            return False

        if device.type == DeviceTypes.HEADPHONE:
            execution = pacmd(["set-default-sink", device.index])
        elif device.type == DeviceTypes.MICROPHONE:
            execution = pacmd(["set-default-source", device.index])
        else:
            return False

        is_success = execution.stdout.decode("utf-8") == ""
        return is_success
