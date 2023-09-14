""""""


__author__ = 'p4irin'
__email__ = '139928764+p4irin@users.noreply.github.com'
__version__ = '1.0.0'


import requests
import os
import json
import wget
import zipfile
from typing import Literal, List


_path_to_assets = './assets'


class _Location:
    chrome = f'{_path_to_assets}/chrome'
    chromedriver = f'{_path_to_assets}/chromedriver'


location = _Location


class UnknownChromeVersion(Exception):
    """Raised when the version of Chrome for Testing is unknown."""
    pass


class ChromedriverVersionDoesNotExist(Exception):
    """No chromedriver exists for corresponding Chrome for testing version."""
    pass


class Assets(object):

    _base_url = 'https://googlechromelabs.github.io/chrome-for-testing'
    _last_known_good_versions_json_api_endpoint = (
        f"{_base_url}/last-known-good-versions-with-downloads.json"
    )
    _known_good_versions_json_api_endpoint = (
        f'{_base_url}/known-good-versions-with-downloads.json'
    )
    _successful_installation_message = """
Finished installing version {version} of Chrome for Testing and Chromedriver.
-------------------------------------------
Version {version} is the active version.
-------------------------------------------

Usage:

from selenium.webdriver import ChromeOptions, ChromeService, Chrome
import c4t

options = ChromeOptions()
options.binary_location = c4t.location.chrome
service = ChromeService(executable_path=c4t.location.chromedriver)
browser = Chrome(options=options, service=service)
browser.get('https://pypi.org/user/p4irin/')
browser.close()
browser.quit()
"""

    def __init__(self) -> None:
        self._create_assets_dir()
        self._platform = ''
        self._download_dir = ''

    def _create_assets_dir(self):
        print('Create "assets" directory.')
        try:
            os.mkdir(_path_to_assets)
        except FileExistsError:            
            print('Skipping: The assets directory already exists.')
        except Exception as e:
            raise SystemExit(e)
        
    def _installation_path_of(
            self, binary: Literal['chrome', 'chromedriver']
        ) -> str:

        return f'{self._download_dir}/{binary}-{self._platform}'
        
    def _make_executable(
            self, files: List[str],
            for_binary: Literal['chrome', 'chromedriver']
        ) -> None:

        for file in files:
            os.chmod(f'{self._installation_path_of(for_binary)}/{file}', 0o755)

    def _download(
            self,
            binary: Literal['chrome', 'chromedriver'],
            for_platform: str,
            from_url: str
        ) -> str:

        binary_zip_file = f'{binary}-{for_platform}.zip'
        binary_zip_file_path = f'{self._download_dir}/{binary_zip_file}'
        if os.path.isfile(f'{binary_zip_file_path}'):
            print(f'{binary_zip_file} exists. Skipping download.')
            return binary_zip_file
        print(f'Downloading {binary_zip_file}.')
        try:
            wget.download(from_url, self._download_dir)
            print('\n')
        except Exception as e:
            print(f'wget threw Exception {e}')
            raise e
        return binary_zip_file

    def _unzip(
            self,
            binary: Literal['chrome', 'chromedriver'],
            from_zip_file: str,
            for_platform: str='linux64'
        ) -> None:

        print(f'Unzipping {from_zip_file}')
        binary_path = f'{self._download_dir}/{binary}-{for_platform}/{binary}'
        if os.path.isfile(binary_path):
            print(f'{from_zip_file} already unzipped. Skipping')
        else:
            with zipfile.ZipFile(
                    f'{self._download_dir}/{from_zip_file}'
                 ) as zfh:
                zfh.extractall(f'{self._download_dir}')

    def _create_symlink(
            self,
            to_binary: Literal['chrome', 'chromedriver'],
            version: str,
            for_platform: str='linux64'
        ):

        symlink_to_chrome = f'{_path_to_assets}/{to_binary}'

        if os.path.islink(symlink_to_chrome):
            link_target = os.readlink(symlink_to_chrome)
            if version not in link_target.split('/'):
                os.remove(symlink_to_chrome)

        if not os.path.islink(symlink_to_chrome):
            print(
                f'Creating symlink to {to_binary} version {version}'
            )
            os.symlink(
                f'./{version}/{to_binary}-{for_platform}/{to_binary}',
                f'{_path_to_assets}/{to_binary}'
            )
            return
        
        if version in link_target.split('/'):
            print(
                f'Symlink for {to_binary} version {version} already ' +
                'exists. Skipping'
            )
        


    def install(self, version: str='latest', platform: str='linux64') -> None:
        self._platform = platform

        if version == 'latest':
            json_api_endpoint = (
                self._last_known_good_versions_json_api_endpoint
            )
        else:
            json_api_endpoint = self._known_good_versions_json_api_endpoint

        try:
            r = requests.get(json_api_endpoint)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        
        json_response = json.loads(r.text)
        if version == 'latest':
            stable_channel = json_response['channels']['Stable']
            version = stable_channel['version']
            chrome_downloads = stable_channel['downloads']['chrome']
            chromedriver_downloads = (
                stable_channel['downloads']['chromedriver']
            )
        else:
            versions = json_response['versions']
            found_version = False
            for a_version in versions:
                if a_version['version'] == version:
                    chrome_downloads = a_version['downloads']['chrome']
                    try:
                        chromedriver_downloads = (
                            a_version['downloads']['chromedriver']
                        )
                    except KeyError:
                        raise ChromedriverVersionDoesNotExist
                    found_version = True
                    break
            if not found_version:
                raise UnknownChromeVersion

        self._download_dir = f'{_path_to_assets}/{version}'
        print(f'Create directory {self._download_dir}')
        try:
            os.makedirs(
                self._download_dir,
                mode=0o775
            )
        except FileExistsError:
            print('Skipping: Directory exists.')

        for chrome in chrome_downloads:
            if chrome['platform'] == platform:
                chrome_zip_file = self._download(
                    binary='chrome',
                    for_platform=platform,
                    from_url=chrome['url']
                )
                break

        for chromedriver in chromedriver_downloads:
            if chromedriver['platform'] == platform:
                chromedriver_zip_file = self._download(
                    binary='chromedriver',
                    for_platform=platform,
                    from_url=chromedriver['url']
                )
                break

        self._unzip(
            binary='chrome', 
            from_zip_file=chrome_zip_file,
            for_platform='linux64'
        )

        chrome_files_to_make_executable = [
            "chrome", "chrome_crashpad_handler", "chrome_sandbox",
            "chrome-wrapper", "libEGL.so", "libGLESv2.so",
            "libvk_swiftshader.so", "libvulkan.so.1", "nacl_helper",
            "nacl_helper_bootstrap", "nacl_irt_x86_64.nexe", "xdg-mime",
            "xdg-settings"
        ]

        # zipfile doesn't preserve file permissions
        self._make_executable(
            chrome_files_to_make_executable, for_binary='chrome'
        )

        self._unzip(
            binary='chromedriver',
            from_zip_file=chromedriver_zip_file,
            for_platform='linux64'
        )

        self._make_executable(['chromedriver'], for_binary='chromedriver')

        self._create_symlink(
            to_binary='chrome',
            version=version,
            for_platform='linux64'
        )

        self._create_symlink(
            to_binary='chromedriver',
            version=version,
            for_platform='linux64'
        )

        print(self._successful_installation_message.format(version=version))
