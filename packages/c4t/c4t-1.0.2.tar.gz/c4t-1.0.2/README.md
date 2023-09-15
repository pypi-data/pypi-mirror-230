# c4t: Chrome for Testing - v1.0.2

Install _Chrome for Testing_ assets. A flavor of Chrome, specifically for testing and a matching chromedriver. The version of assets installed are from the stable channel and currently only for _linux64_ platforms.

## Why Chrome for Testing?

Taken from [the Chrome Developers Blog](https://developer.chrome.com/blog/chrome-for-testing/)

> ...setting up an adequate browser testing environment is notoriously difficult...
>
> You want consistent, reproducible results across repeated test runs—but this may not happen if the browser executable or binary decides to update itself in between two runs.
>
>You want to pin a specific browser version and check that version number into your source code repository, so that you can check out old commits and branches and re-run the tests against the browser binary from that point in time.
>
> Not only do you have to download a Chrome binary somehow, you also need a correspondingly-versioned ChromeDriver binary to ensure the two binaries are compatible.
>
> Chrome for Testing is a dedicated flavor of Chrome targeting the testing use case, without auto-update, integrated into the Chrome release process, made available for every Chrome release
>
> ...finding a matching Chrome and ChromeDriver binary can be completely eliminated by integrating the ChromeDriver release process into the Chrome for Testing infrastructure.

## Installation

### From PyPI

```bash
(venv) $ pip install c4t
(venv) $
```

### From GitHub

```bash
(venv) $ pip install git+https://github.com/p4irin/c4t.git
(venv) $
```

## Verify

```bash
(venv) $ python
Python 3.8.10 (default, Jun  2 2021, 10:49:15) 
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import c4t
>>> c4t.__version__
'<major>.<minor>.<patch>'
>>>
```

or

```bash
(venv) $ python -m pydoc c4t
```

## Usage

### Install the default latest stable version

```bash
Python 3.8.10 (default, May 26 2023, 14:05:08) 
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import c4t
>>> assets = c4t.Assets()
Create "assets" directory.
>>> assets.install()
Create directory ./assets/117.0.5938.62
Downloading chrome-linux64.zip.
100% [......................................................................] 146689409 / 146689409

Downloading chromedriver-linux64.zip.
100% [..........................................................................] 7508443 / 7508443

Unzipping chrome-linux64.zip
Unzipping chromedriver-linux64.zip
Creating symlink to chrome version 117.0.5938.62
Creating symlink to chromedriver version 117.0.5938.62
Finished installing version 117.0.5938.62 of Chrome for Testing and Chromedriver.
-------------------------------------------
Version 117.0.5938.62 is the active version
-------------------------------------------
>>> from selenium.webdriver import ChromeOptions, ChromeService, Chrome
>>> options = ChromeOptions()
>>> options.binary_location = c4t.location.chrome
>>> service = ChromeService(executable_path=c4t.location.chromedriver)
>>> browser = Chrome(options=options, service=service)
>>> browser.get('https://pypi.org/user/p4irin/')
>>> browser.close()
>>> browser.quit()
>>>
```

## Reference

- [Blog](https://developer.chrome.com/blog/chrome-for-testing/)
- [GitHub](https://github.com/GoogleChromeLabs/chrome-for-testing)
