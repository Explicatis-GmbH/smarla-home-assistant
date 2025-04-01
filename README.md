# Swing2Sleep Smarla - Home Assistant Integration

This custom component for [home assistant](https://home-assistant.io/) will let you connect your Swing2Sleep Smarla device
to Home Assistant.

The Swing2Sleep App is required for pairing.

Smarla devices need to have Version 1.6.X or greater to support Home Assistant pairing!

**This component will set up the following platforms.**

| Platform         | Description                           |
| ---------------- | ------------------------------------- |
| `number`         | Sends a number value to the device.   |
| `sensor`         | Show some measurements of device.     |
| `switch`         | Switch something `On` or `Off`.       |

## HACS Installation

1. Copy github repository link
2. Install in HACS with Repo link

## Manual Installation

1. Using the tool of choice to open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `smarla`.
4. Download _all_ the files from the `custom_components/smarla/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Swing2Sleep Smarla"


## Configuration

- The integration configuration is done in the UI

---
