# jmenu

## About

Python app to fetch University of Oulu restaurant menus from Jamix API.

Versions 1.3 and above use the [Jamix API.](https://fi.jamix.cloud/apps/menuservice/rest)

Versions below 1.3 work by rendering the pages with selenium, then scraping the HTML with BeautifulSoup4.

## Installing

Jmenu is available for install on the [Python package index.](https://pypi.org/project/jmenu/)

Install it with pip:

```shell
pip install jmenu
```

## Usage

| Argument        | Example | Description                             |
| :-------------- | :------ | :-------------------------------------- |
| -a, --allergens | g veg   | Highlights appropriately marked results |

| Flag           | Description                         |
| :------------- | :---------------------------------- |
| -h, --help     | Display usage information           |
| -v, --version  | Display version information         |
| -e, --explain  | Display allergen marker information |
| -t, --tomorrow | Fetch menu results for tomorrow     |

## Contributing

**Requirements**

- Python 3.7+
- Virtualenv

Setup the development environment with

```shell
python3 -m virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

Test and run the tool with

```shell
python3 -m src.jmenu.main
```

Build and install the package with

```
python3 -m build
pip install dist/<package_name>.whl
```
