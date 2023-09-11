import base64
import os
import shutil
import requests
import zipfile
import io
import platform
import json
from urllib.parse import parse_qs

from ..web.browser_client import BrowserClient


class HtmlRenderer:
    def __init__(self, browser_client: BrowserClient):
        self.browser_client = browser_client
        self.driver = browser_client.driver

    def save_current_pdf(self, dest, landscape=False):
        resource = "/session/%s/chromium/send_command_and_get_result" % self.driver.session_id
        url = self.driver.command_executor._url + resource
        body = json.dumps(
            {
                "cmd": "Page.printToPDF",
                "params": {
                    "landscape": landscape,
                    "displayHeaderFooter": False,
                    "printBackground": True,
                    "preferCSSPageSize": False,
                },
            }
        )
        response = self.driver.command_executor._request("POST", url, body)
        with open(dest, "wb") as file:
            file.write(base64.b64decode(response.get("value")["data"]))

    def save_current_png(self, dest, landscape=False):
        if landscape:
            self.driver.set_window_size(1414, 1000)
        else:
            self.driver.set_window_size(1000, 1414)
        self.driver.save_screenshot(dest)

    def save_as_pdf(self, uri, dest, landscape=False):
        self.driver.get(uri)
        self.save_current_pdf(dest, landscape)

    def save_as_png(self, uri, dest, landscape=False):
        self.driver.get(uri)
        self.save_current_png(dest, landscape)
