from typing import NamedTuple, List
from datetime import date
from io import StringIO 
from itertools import chain
import re
from functools import cached_property

def load_distanc_metrix_from_csv(ft_csv: str) -> dict[tuple[str, str], int]:
    """vytvori matici vzdalenosti pode csv tabulky"""
    def _read_distances_from_csv(stream):
        import csv
        rows = csv.reader(stream)
        _, *column_names = next(rows)
        for source, *distances in rows:
            for destination, distance in zip(column_names, distances):
                yield source, destination, int(distance)
    
    return {(s, d): distance for s, d, distance in _read_distances_from_csv(StringIO(ft_csv.strip()))}

class CitiesDistanceCalculator:
    """Trida s odpovednosti pocitani vzdalenosti mezi mesty
    """

    def __init__(self, matrix: dict[tuple[str, str], int]):
        """Matrix je slovnik, kde klic je dvonice meste a 
           hodnova je vzdalenost mezi nimi."""
        self.__matrix = matrix

    @cached_property
    def cities(self) -> set[str]:
        "Seznam mest, mezi kterymi je mozne spocitat vzdalenost"
        return set(chain.from_iterable(self.__matrix))

    def distance(self, s, d) -> int:
        """funkce pro spocitani vzdalenosti mezi dema mesty

        Args:
            s, d (str): nazvy mest, ze seznamu cities

        Returns:
            int: vzdalenost v kilomentrech
        """
        return self.__matrix[(s, d)]

with open('./assets/cz.csv', mode='r', encoding='utf-8') as csv:
    matrix = load_distanc_metrix_from_csv(csv.read())
    CITIES_DISTANCE_CALCULATOR = CitiesDistanceCalculator(matrix)

from operator import add

class Trip(NamedTuple):
    date: date
    attendants: List[str]
    cities: List[str]
    notes: str | None

    def total_distance(self,* ,distanc_calculator = CITIES_DISTANCE_CALCULATOR):
        "spocita celkovou vzdalenist ujetou na tripu"
        dvojice = zip(self.cities, self.cities[1:])
        distances = [distanc_calculator.distance(s,d) for s,d in dvojice]
        return sum(distances)


class Journal(NamedTuple):
    title: str
    trips: List[Trip]

def create_journal(title: str) -> Journal:
    """
    Generates a new record with a specified heading and an empty trip list.

    Args:
        title (str): The heading of the record.

    Returns:
        Journal: An object representing the record with the given heading and an empty list of trips.

    Example:
        >>> j = create_journal("My European Vacation")
        >>> j.title
        'My European Vacation'
        >>> j.trips
        []

    Note:
        The trips attribute in the Journal object is initialized as an empty list. Trips can be added to this list later.
    """
    try:
        if not re.match(r'[\w\s]{3,}', title):
            raise ValueError()
        
        title = re.sub(r"\s+", " ", title)
        return Journal(title.strip().title(), [])
    except:
        raise ValueError(f"Title must be a non-empty string, but got {title}")
    

def save_journal(journal: Journal, directory='.'):
    import json
    with open(f"{directory}/{journal.title}.json", mode='w', encoding='utf-8') as f:
        json.dump(journal, f, default=str)
    