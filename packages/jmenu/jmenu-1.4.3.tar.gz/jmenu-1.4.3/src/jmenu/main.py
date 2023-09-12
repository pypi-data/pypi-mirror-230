from .version import VERSION
from .restaurants import (
    RESTAURANTS,
    MARKINGS,
    API_URL,
    SKIPPED_ITEMS,
    Restaurant,
)
from datetime import datetime, timedelta
import requests
import argparse
from time import time


class ArgsNamespace:
    explain: bool
    allergens: list[str]
    tomorrow: bool


def main():
    args = get_args()
    if args.explain:
        print_explanations()
        exit(0)
    start = time()
    print_menu(args)
    print("Process took {:.2f} seconds.".format(time() - start))


def get_args():
    parser = argparse.ArgumentParser(
        description="Display University of Oulu restaurant menus for the day"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="display version information",
        version=VERSION,
    )
    parser.add_argument(
        "-e",
        "--explain",
        dest="explain",
        action="store_true",
        help="display allergen marking information",
    )
    parser.add_argument(
        "-t",
        "--tomorrow",
        dest="tomorrow",
        action="store_true",
        help="display menus for tomorrow",
    )
    allergens = parser.add_argument_group("allergens")
    allergens.add_argument(
        "-a",
        "--allergens",
        dest="allergens",
        action="extend",
        type=str,
        metavar=("markers", "G, VEG"),
        nargs="+",
        help='list of allergens, for ex. "g veg"',
    )
    return parser.parse_args(namespace=ArgsNamespace())


def get_restaurant_menu_items(rest: Restaurant, fetch_date: datetime) -> list[dict]:
    response = requests.get(
        f"{API_URL}/{rest.client_id}/{rest.kitchen_id}?lang=fi&date={fetch_date.strftime('%Y%m%d')}"
    )
    data = response.json()
    menus = get_menus(data, rest)
    if len(menus) == 0:
        return []
    items = get_menu_items(menus, rest)
    return items


def get_menu_items(menus: dict, rest: Restaurant) -> list[dict]:
    items = []
    for menu in menus:
        day = menu["days"][0]
        mealopts = day["mealoptions"]
        sorted(mealopts, key=lambda x: x["orderNumber"])
        for opt in mealopts:
            for item in opt["menuItems"]:
                if item["name"] not in SKIPPED_ITEMS:
                    items.append(item)
    return items


def get_menus(data: dict, rest: Restaurant) -> list[dict]:
    menus = []
    for kitchen in data:
        for m_type in kitchen["menuTypes"]:
            if m_type["menuTypeName"] in rest.relevant_menus:
                menus.extend(m_type["menus"])
    return menus


def print_menu(args: ArgsNamespace):
    fetch_date = datetime.now()
    if args.tomorrow:
        fetch_date += timedelta(days=1)
    allergens = []
    if args.allergens:
        allergens = [x.lower() for x in args.allergens]

    print_header(fetch_date)
    for res in RESTAURANTS:
        try:
            items = get_restaurant_menu_items(res, fetch_date)
            sorted(items, key=lambda x: x["orderNumber"])
            if len(items) == 0:
                print(res.name.ljust(8), "--")
            else:
                print(res.name)
                if not allergens:
                    for item in items:
                        print("\t", item["name"], item["diets"])
                else:
                    print_highlight(items, allergens)

        except Exception:
            print("Couldn't fetch menu for", res.name)


def print_explanations():
    for mark in MARKINGS:
        print(mark.letters, "\t", mark.explanation)


def print_highlight(items: list[str], allergens: list[str]):
    for item in items:
        diets = [x.strip().lower() for x in item["diets"].split(",")]
        if all(marker in diets for marker in allergens):
            print("\033[92m", "\t", item["name"], item["diets"], "\033[0m")
        else:
            print("\t", item["name"], item["diets"])


def print_header(fetch_date: datetime):
    print("-" * 79)
    print("Menu for", fetch_date.strftime("%d.%m"))
    print("-" * 79)


if __name__ == "__main__":
    main()
