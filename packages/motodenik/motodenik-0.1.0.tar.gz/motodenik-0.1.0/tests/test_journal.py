from unittest.mock import MagicMock
import pytest

from motodenik.journal import *
from textwrap import dedent 

@pytest.mark.parametrize("title", [
    "My Journal",
    "my journal",
    "MY JOURNAL",
    "My\tJournal", 
    "My Journal ",
    "\tMy Journal",
    "My Journal\n",
])
def test_create_journal(title):
    # Act
    journal = create_journal(title)
    # Asserts
    assert isinstance(journal, Journal)
    assert journal.title == "My Journal"
    assert journal.trips == []

@pytest.mark.parametrize("title", [
    None,
    "",
    "!",
    ["My", "Journal"], 
    123
])
def test_create_journal_illegal_title(title):
    # Act + Asserts
    with pytest.raises(ValueError):
        create_journal(title)

@pytest.fixture
def brno_plzen_olomouc_csv():
    return dedent('''\
        "Vzdálenost (kilometry)","Brno","Plzeň","Olomouc"
        "Brno","0","10","20"
        "Plzeň","10","0","30"
        "Olomouc","20","40","0"
        ''')

def test_load_distanc_metrix_from_csv(brno_plzen_olomouc_csv):
    # Act
    result = load_distanc_metrix_from_csv(brno_plzen_olomouc_csv)
    # Asserts
    assert len(result) == 9
    assert result[("Brno", "Olomouc")] == 20

def test_load_distanc_metrix_from_csv_with_last_empty_line(brno_plzen_olomouc_csv):
    # Arrange
    csv = brno_plzen_olomouc_csv + "\n\n"
    # Act
    result = load_distanc_metrix_from_csv(csv)
    # Asserts
    assert len(result) == 9
    assert result[("Brno", "Olomouc")] == 20

@pytest.fixture
def brno_plzen_olomouc_cdc(brno_plzen_olomouc_csv):
    matrix = load_distanc_metrix_from_csv(brno_plzen_olomouc_csv)
    return CitiesDistanceCalculator(matrix)
    
class TestCitiesDistanceCalculator:

    def test_cities(self, brno_plzen_olomouc_cdc: CitiesDistanceCalculator):
        assert brno_plzen_olomouc_cdc.cities == {'Brno', 'Plzeň', 'Olomouc'}

    def test_distance(self, brno_plzen_olomouc_cdc: CitiesDistanceCalculator):
        assert brno_plzen_olomouc_cdc.distance('Plzeň', 'Olomouc') == 30
        assert brno_plzen_olomouc_cdc.distance('Olomouc', 'Plzeň') == 40

class TestTrip:

    @pytest.mark.xfail
    def test_total_distance_monkeypatch(self, monkeypatch, brno_plzen_olomouc_cdc):
        monkeypatch.setattr(CITIES_DISTANCE_CALCULATOR, 'distance', brno_plzen_olomouc_cdc.distance)
        trip = Trip(None, None, ['Brno', 'Plzeň', 'Olomouc'], None)
        # Act + Assert
        assert trip.total_distance == 40

    def test_total_distance_mocker(self, mocker, brno_plzen_olomouc_cdc):
        from unittest.mock import MagicMock

        spy: MagicMock = mocker.spy(brno_plzen_olomouc_cdc, 'distance')
        trip = Trip(None, None, ['Brno', 'Plzeň'], None)
        # Act
        result = trip.total_distance(distanc_calculator = brno_plzen_olomouc_cdc)
        # Assert
        assert result == 10
        spy.assert_called_once_with('Brno', 'Plzeň')


from shutil import rmtree

@pytest.fixture(scope='module')
def journal_dir(tmp_path_factory: pytest.TempPathFactory):
    tmp_dir = tmp_path_factory.mktemp('test_journal')
    yield tmp_dir
    rmtree(str(tmp_dir))
    

# Unite test mock umi mokovat metodu open :-)

@pytest.mark.integration
def test_save_journal(journal_dir):
    journal = Journal('test_save_journal', [
        Trip(date(2023,3,2), ['Pepa'], ['Brno', 'Plzeň', 'Olomouc','Brno'], 'Okruzni jizda'),
        Trip(date(2023,3,10), ['Pepa', 'Jirka'], ['Brno', 'Olomouc'], 'Jdeme na tvaruzky'),
    ])
    # Act
    save_journal(journal, journal_dir)
    # Assert
    assert (journal_dir / "test_save_journal.json").exists()