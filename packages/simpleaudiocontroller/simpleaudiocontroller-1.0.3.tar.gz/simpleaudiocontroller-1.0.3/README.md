
# Simple Audio Controller

The Simple Audio Controller is a Python module that provides a simple interface for interacting with audio devices and controlling audio settings using the PulseAudio command-line tool 'pacmd'.

## Features

- List available headphones and microphones.
- Set default audio devices (headphones and microphones).
- Retrieve information about the current default devices.
- Search for audio devices by name.

## Requirements

- Python 3.x
- PulseAudio (pacmd command-line tool)

## Installation

You can install the Simple Audio Controller using pip:

```bash
pip install simpleaudiocontroller
```

## Usage

Here's how you can use the Simple Audio Controller in your Python code:

```python
from simpleaudiocontroller import AudioController

# Create an instance of the AudioController
audio_controller = AudioController()

# List available headphones and microphones
headphones = audio_controller.get_headphones()
microphones = audio_controller.get_microphones()

# Set the default headphone device
if audio_controller.set_default_device(headphones[0]):
    print("Default headphone set successfully.")

# Set the default microphone device
if audio_controller.set_default_device(microphones[0]):
    print("Default microphone set successfully.")
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.