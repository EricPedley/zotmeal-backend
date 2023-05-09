ORDERINGS = [
    'Home',# anteatery main dish
    'Oven',# anteatery pizza
    'Fire And Ice Round Grill',# anteatery main dish 2
    'Grubb / Mainline',# brandywine main dish
    'Compass',# brandywine main dish 2
    'Hearth/Pizza',# brandywine pizza
    'Deli',# anteatery sandwiches
    'The Farm Stand / Deli',
    'Crossroads',# brandywine 3rd entree
    'Sizzle Grill',# anteatery burgers
    'Ember/Grill',# brandywine burgers
    'Vegan',# both vegan
    'Bakery',# anteatery dessert
    'Honeycakes/Bakery',# brandywine dessert
    'Soups',# both soup
    "Farmer's Market",# anteatery salad
    'The Farm Stand / Salad Bar'# brandywine salad
]

def station_ordering_key(station_name: str) -> int:
    '''
    Returns an integer used to sort station names by relevance (basically Eric's personal preferences 😋)
    '''
    try:
        return ORDERINGS.index(station_name)
    except ValueError:# if 
        print(f"ValueError (NON-BREAKING) on station orderings. Key {station_name} is not in list")
        return -1
    
ORDERINGS_CAT = [
    "Entries",
    "EntrÃ©es",
    "Pizza",
    "Cold Sandwiches",
    "Hot Sandwiches",
    "Dessert",
    "Soups",
    "Breads",
    "Sides",
    "Protein",
    "Appetizers",
    "Salads",
    "Condiments",
    "Cold Beverages",
    "Protein",
    "Grains",
    "Sauces"
]

def category_ordering_key(category_name) -> int:
    '''
    Returns an integer used to sort category names by relevance
    '''
    print(category_name[0], "\n")
    try:
        return ORDERINGS_CAT.index(category_name[0])
    except ValueError:
        print(category_name)
        print(f"ValueError (NON-BREAKING) on category orderings. Key {category_name} is not in list")
        return -1
    
combining_keys = [
    "Grubb / Mainline", 
    "Crossroads",
    "Home"
]