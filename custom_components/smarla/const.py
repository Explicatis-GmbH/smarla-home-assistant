"""Constants for the Swing2Sleep Smarla integration."""

DOMAIN = "smarla"

NAME = "smarla"
DOMAIN_DATA = f"{DOMAIN}_data"

HOST = "https://devices.swing2sleep.de"

PLATFORMS = ["number", "sensor", "switch"]

STARTUP_MESSAGE = """
-------------------------------------------------------------------
Swing2Sleep Smarla

Version: %s
This is a custom integration for connecting Swing2Sleep Smarla devices!
Smarla devices need to have Version 1.6.X or greater to support Home Assistant pairing!
-------------------------------------------------------------------
"""
