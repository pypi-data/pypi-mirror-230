import os
import sys
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

    
def get_driver(profile_name: str, headless:bool = True, options: Options = None):
    profile_path = get_profile_path(profile_name)
    driver_path = get_driver_path()
    if options is None:
        options = Options()
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.accept_insecure_certs = True
    return uc.Chrome(options=options, user_data_dir=profile_path, driver_executable_path=driver_path, headless=headless)

def get_profile_path(profile_name: str):
    profile_path = None
    if sys.platform == 'linux' or sys.platform == 'linux2':
        profile_path = os.path.expanduser('~/.config/google-chrome', profile_name)
    elif sys.platform == 'win32' or sys.platform == 'win64':
        profile_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', profile_name)
    elif sys.platform == 'darwin':
        profile_path = os.path.expanduser('~/Library/Application Support/Google/Chrome', profile_name)
    return profile_path

def get_driver_path():
    driver_path = None
    if sys.platform == 'linux' or sys.platform == 'linux2':
        pass
    elif sys.platform == 'win32' or sys.platform == 'win64':
        driver_path = os.path.join('chromedrivers', 'windows.exe')
    elif sys.platform == 'darwin':
        driver_path = os.path.join('chromedrivers', 'mac')
    return driver_path
