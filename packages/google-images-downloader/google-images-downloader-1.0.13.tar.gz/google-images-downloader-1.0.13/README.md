# google-images-downloader

[![PyPI version](https://badge.fury.io/py/google-images-downloader.svg)](https://badge.fury.io/py/google-images-downloader)
[![Test](https://github.com/Harkame/google-images-downloader/actions/workflows/test.yml/badge.svg)](https://github.com/Harkame/google-images-downloader/actions/workflows/test.yml)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/35653176f62b47aa8666544e6c30dcfd)](https://app.codacy.com/gh/Harkame/google-images-downloader/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/6ab037c4ca021b4be8ab/maintainability)](https://codeclimate.com/github/Harkame/google-images-downloader/maintainability)
[![CodeFactor](https://www.codefactor.io/repository/github/harkame/google-images-downloader/badge)](https://www.codefactor.io/repository/github/harkame/google-images-downloader)

[![Coverage Status](https://coveralls.io/repos/github/Harkame/google-images-downloader/badge.svg)](https://coveralls.io/github/Harkame/google-images-downloader)
[![codecov](https://codecov.io/gh/Harkame/google-images-downloader/graph/badge.svg?token=9qdPDbT1e0)](https://codecov.io/gh/Harkame/google-images-downloader)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Requirements

- [Google Chrome](https://www.google.com/chrome/)(Used by default)

OR

- [Firefox](https://www.mozilla.org/en-US/firefox/new/)

## Installation

```shell
pip install google-images-downloader
```

OR

```shell
git clone https://github.com/Harkame/GoogleImagesDownloader.git

cd GoogleImagesDownloader

pip install .
```

## Usage

### Command line

#### Basic usage

```shell
google-images-downloader -q QUERY1 QUERY2 "LONG QUERY 3"
```

For more informations

```shell
google-images-downloader -h
```

### Programmatically

```python
from google_images_downloader import GoogleImagesDownloader

downloader = GoogleImagesDownloader(browser="chrome", show=False, debug=False,
                                    quiet=False, disable_safeui=False)  # Constructor with default values

downloader.download("bear")  # Download 50 images in ./downloads folder

downloader.download("cat", destination="C:\download\destination")  # Download at specified destination

downloader.download("bird", limit=200)  # Download 100 images

downloader.download("dog", resize=(256, 256))  # Download with images resizing

downloader.download("fish", file_format="JPEG")  # Download with images re-formatting (JPEG or PNG)

downloader.close()  # Do not forget to close the driver
```

#### Specify browser to use for web scraping

```python
from google_images_downloader import GoogleImagesDownloader

downloader = GoogleImagesDownloader(browser="firefox")  # Default : "chrome"

downloader.close()  # Do not forget to close the driver
```

## Tests

```shell
pip install tox

tox
```
