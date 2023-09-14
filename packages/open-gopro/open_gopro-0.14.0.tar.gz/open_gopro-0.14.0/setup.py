# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['open_gopro',
 'open_gopro.api',
 'open_gopro.ble',
 'open_gopro.ble.adapters',
 'open_gopro.demos',
 'open_gopro.demos.gui',
 'open_gopro.demos.gui.components',
 'open_gopro.models',
 'open_gopro.proto',
 'open_gopro.wifi',
 'open_gopro.wifi.adapters']

package_data = \
{'': ['*']}

install_requires = \
['bleak==0.20.2',
 'construct>=2,<3',
 'packaging>=21,<22',
 'pexpect>=4,<5',
 'protobuf>=3,<4',
 'pydantic>=1,<2',
 'pytz>=2023.3,<2024.0',
 'requests>=2,<3',
 'rich>=12,<13',
 'tzlocal>=5.0.1,<6.0.0',
 'wrapt>=1,<2',
 'zeroconf>=0,<1']

extras_require = \
{'gui': ['opencv-python>=4,<5', 'tk>=0.1,<0.2', 'Pillow>=9,<10']}

entry_points = \
{'console_scripts': ['gopro-gui = open_gopro.demos.gui.gui_demo:entrypoint',
                     'gopro-livestream = '
                     'open_gopro.demos.gui.livestream:entrypoint',
                     'gopro-log-battery = '
                     'open_gopro.demos.log_battery:entrypoint',
                     'gopro-photo = open_gopro.demos.photo:entrypoint',
                     'gopro-preview-stream = '
                     'open_gopro.demos.gui.preview_stream:entrypoint',
                     'gopro-video = open_gopro.demos.video:entrypoint',
                     'gopro-webcam = open_gopro.demos.gui.webcam:entrypoint',
                     'gopro-wifi = open_gopro.demos.connect_wifi:entrypoint']}

setup_kwargs = {
    'name': 'open-gopro',
    'version': '0.14.0',
    'description': 'Open GoPro API and Examples',
    'long_description': '# Open GoPro Python SDK\n\n<img alt="GoPro Logo" src="https://raw.githubusercontent.com/gopro/OpenGoPro/main/docs/assets/images/logos/logo.png" width="50%" style="max-width: 500px;"/>\n\n[![Build and Test](https://img.shields.io/github/actions/workflow/status/gopro/OpenGoPro/python_sdk_test.yml)](https://github.com/gopro/OpenGoPro/actions/workflows/python_sdk_test.yml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPI](https://img.shields.io/pypi/v/open-gopro)](https://pypi.org/project/open-gopro/)\n[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/gopro/OpenGoPro/blob/main/LICENSE)\n![Coverage](https://raw.githubusercontent.com/gopro/OpenGoPro/main/demos/python/sdk_wireless_camera_control/docs/_static/coverage.svg)\n\nThis is a Python package that provides an\ninterface for the user to exercise the Open GoPro Bluetooth Low Energy (BLE) and Wi-Fi / USB HTTP API\'s as well as install command line interfaces to take photos, videos, and view video streams.\n\n-   Free software: MIT license\n-   Documentation: [View on Open GoPro](https://gopro.github.io/OpenGoPro/python_sdk/)\n-   View on [Github](https://github.com/gopro/OpenGoPro/tree/main/demos/python/sdk_wireless_camera_control)\n\n## Documentation\n\n> Note! This README is only an overview of the package.\n\nComplete documentation can be found on [Open GoPro](https://gopro.github.io/OpenGoPro/python_sdk/)\n\n## Features\n\n-   Top-level GoPro class interface to use BLE, WiFi, and / or USB\n-   Cross-platform (tested on MacOS Big Sur, Windows 10, and Ubuntu 20.04)\n    -   BLE implemented using [bleak](https://pypi.org/project/bleak/)\n    -   Wi-Fi controller provided in the Open GoPro package (loosely based on the [Wireless Library](https://pypi.org/project/wireless/)\n-   Supports all commands, settings, and statuses from the [Open GoPro API](https://gopro.github.io/OpenGoPro/)\n-   [Asyncio](https://docs.python.org/3/library/asyncio.html) based\n-   Automatically handles connection maintenance:\n    -   manage camera ready / encoding\n    -   periodically sends keep alive signals\n-   Includes detailed logging for each module\n-   Includes demo scripts installed as command-line applications to show BLE, WiFi, and USB functionality such as:\n    -   Take a photo\n    -   Take a video\n    -   Configure and view a GoPro webcam stream\n    -   GUI to send all commands and view the live / preview stream\n    -   Log the battery\n\n## Installation\n\n> Note! This package requires Python >= 3.8 and < 3.12\n\nThe minimal install to use the Open GoPro library and the CLI demos is:\n\n```console\n$ pip install open-gopro\n```\n\nTo also install the extra dependencies to run the GUI demos, do:\n\n```console\n$ pip install open-gopro[gui]\n```\n\n## Usage\n\nTo automatically connect to GoPro device via BLE and WiFI, set the preset, set video parameters, take a\nvideo, and download all files:\n\n```python\nimport asyncio\nfrom open_gopro import WirelessGoPro, Params\n\nasync def main():\n    async with WirelessGoPro() as gopro:\n        await gopro.ble_setting.resolution.set(Params.Resolution.RES_4K)\n        await gopro.ble_setting.fps.set(Params.FPS.FPS_30)\n        await gopro.ble_command.set_shutter(shutter=Params.Toggle.ENABLE)\n        await asyncio.sleep(2) # Record for 2 seconds\n        await gopro.ble_command.set_shutter(shutter=Params.Toggle.DISABLE)\n\n        # Download all of the files from the camera\n        media_list = (await gopro.http_command.get_media_list()).data.files\n        for item in media_list:\n            await gopro.http_command.download_file(camera_file=item.filename)\n\nasyncio.run(main())\n```\n\nAnd much more!\n\n## Demos\n\n> Note! These demos can be found on [Github](https://github.com/gopro/OpenGoPro/tree/main/demos/python/sdk_wireless_camera_control/open_gopro/demos)\n\nDemos can be found in the installed package in the "demos" folder. They are installed as a CLI entrypoint\nand can be run as shown below.\n\n## Command Line Interface (CLI) Demos\n\nAll of these demos are CLI only and can thus be run with the minimal (non-GUI) install.\n\nCapture a photo and download it to your computer:\n\n```bash\n$ gopro-photo\n```\n\nCapture a video and download it to your computer:\n\n```bash\n$ gopro-video\n```\n\nConnect to the GoPro and log battery consumption in to a .csv:\n\n```bash\n$ gopro-log-battery\n```\n\nConnect to the GoPro\'s Wi-Fi AP and maintain the connection:\n\n```bash\n$ gopro-wifi\n```\n\nFor more information on each, try running with help as such:\n\n```bash\n$ gopro-photo --help\n\nusage: gopro-photo [-h] [-i IDENTIFIER] [-l LOG] [-o OUTPUT] [-w WIFI_INTERFACE]\n\nConnect to a GoPro camera, take a photo, then download it.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -i IDENTIFIER, --identifier IDENTIFIER\n                        Last 4 digits of GoPro serial number, which is the last 4 digits of the default camera SSID. If not used, first\n                        discovered GoPro will be connected to\n  -l LOG, --log LOG     Location to store detailed log\n  -o OUTPUT, --output OUTPUT\n                        Where to write the photo to. If not set, write to \'photo.jpg\'\n  -w WIFI_INTERFACE, --wifi_interface WIFI_INTERFACE\n                        System Wifi Interface. If not set, first discovered interface will be used.\n```\n\n\n## GUI Demos\n\nThese demos require the additional GUI installation.\n\nStart the preview stream and view it:\n\n```bash\n$ gopro-preview-stream\n```\n\nStart the live stream and view it:\n\n```bash\n$ gopro-live-stream\n```',
    'author': 'Tim Camise',
    'author_email': 'tcamise@gopro.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/gopro/OpenGoPro/tree/main/demos/python/sdk_wireless_camera_control',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
