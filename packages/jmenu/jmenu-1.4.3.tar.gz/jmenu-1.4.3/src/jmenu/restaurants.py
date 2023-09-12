from collections import namedtuple

Restaurant = namedtuple(
    "Restaurant", ["name", "client_id", "kitchen_id", "menu_type", "relevant_menus"]
)
Marking = namedtuple("Marking", ["letters", "explanation"])

API_URL = "https://fi.jamix.cloud/apps/menuservice/rest/haku/menu"

SKIPPED_ITEMS = [
    "proteiinilisäke",
    "Täysjyväriisi",
    "Lämmin kasvislisäke",
    "Höyryperunat",
    "Tumma pasta",
    "Meillä tehty perunamuusi",
]

RESTAURANTS = [
    Restaurant("Foobar", 93077, 49, 84, ["Foobar Salad and soup", "Foobar Rohee"]),
    Restaurant("Foodoo", 93077, 48, 89, ["Foodoo Salad and soup", "Foodoo Reilu"]),
    Restaurant("Kastari", 95663, 5, 2, ["Ruokalista"]),
    Restaurant("Kylymä", 93077, 48, 92, ["Kylymä Rohee"]),
    Restaurant("Mara", 93077, 49, 111, ["Salad and soup", "Ravintola Mara"]),
    Restaurant("Napa", 93077, 48, 79, ["Napa Rohee"]),
]

MARKINGS = [
    Marking("G", "Gluteeniton"),
    Marking("M", "Maidoton"),
    Marking("L", "Laktoositon"),
    Marking("SO", "Sisältää soijaa"),
    Marking("SE", "Sisältää selleriä"),
    Marking("MU", "Munaton"),
    Marking("[S], *", "Kelan korkeakouluruokailunsuosituksen mukainen"),
    Marking("SIN", "Sisältää sinappia"),
    Marking("<3", "Sydänmerkki"),
    Marking("VEG", "Vegaani"),
]
