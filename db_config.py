"""
Database connection settings, shared by the GUI, the connection check
and the analysis notebook.

Settings are read from config.ini in the project folder. If that file
does not exist, the defaults below are used. Each person keeps their own
config.ini (it is ignored by Git), so nobody's password ends up on GitHub.
"""
import configparser
from pathlib import Path

import mysql.connector

PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_DIR / "config.ini"

DEFAULTS = {
    "host": "localhost",
    "port": "3306",
    "user": "root",
    "password": "1234",
    "database": "mydb",
}


def load_settings():
    """Return the connection settings as a dict."""
    settings = dict(DEFAULTS)
    if CONFIG_FILE.exists():
        parser = configparser.ConfigParser()
        parser.read(CONFIG_FILE, encoding="utf-8")
        if parser.has_section("mysql"):
            settings.update(parser["mysql"])
    settings["port"] = int(settings["port"])
    return settings


def connect(**overrides):
    """Open a new MySQL connection using the settings above."""
    params = load_settings()
    params.update(overrides)
    return mysql.connector.connect(**params)
