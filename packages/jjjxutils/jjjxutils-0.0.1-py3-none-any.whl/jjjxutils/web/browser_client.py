import requests
import platform

from ..archive.zip import extract_ignoring_folders
from ..imports import import_rel

class BrowserClient:
    driver = None
    selenium = None

    def __init__(self):
        raise NotImplementedError


class ChromeClient(BrowserClient):
    def __init__(self, selenium):
        self.selenium = selenium
        self.download_chromedriver()
        options = self.selenium.webdriver.chrome.options.Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = self.selenium.webdriver.Chrome(options=options)

    def download_chromedriver(self):
        chrome_version_data = requests.get(
            "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json",
            timeout=30
        ).json()
        stable_chromedriver_downloads = chrome_version_data["channels"]["Stable"][
            "downloads"
        ]["chromedriver"]

        system = platform.system()
        if system == "Linux":
            found_platform = "linux64"
        elif system == "Darwin":
            found_platform = "mac-x64"
        elif system == "Windows":
            if "64bit" in platform.architecture():
                found_platform = "win64"
            else:
                found_platform = "win32"
        else:
            raise NotImplementedError(f"Unsupported platform {system}")

        for possible_donwload in stable_chromedriver_downloads:
            if possible_donwload["platform"] == found_platform:
                chromedriver_download = possible_donwload
                break
        else:
            raise FileNotFoundError(
                f"Could not find chromedriver for {found_platform}")

        chromedriver_zip = requests.get(
            chromedriver_download["url"], timeout=30)

        return extract_ignoring_folders(chromedriver_zip.content)


def get_selenium():
    return import_rel("selenium.webdriver")
