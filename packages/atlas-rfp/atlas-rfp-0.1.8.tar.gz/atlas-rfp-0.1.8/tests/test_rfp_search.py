import atlas_rfp.atlas_parsing
from pathlib import Path

class Pseudoresponse:
    text: str
    def __init__(self, text: str):
        self.text = text

def open_file_as_pseudoresponse(filename: Path):
    basepath = Path(__file__).resolve().parent
    return Pseudoresponse((basepath / filename).read_text())

def test_basic_search():
    search = open_file_as_pseudoresponse(Path('files/payee_search.html'))
    assert atlas_rfp.atlas_parsing.parse_payee_search_for_vendor_id(search, 'test') == 12345678

def test_multiple_person_search():
    search = open_file_as_pseudoresponse(Path('files/multiple_payee_search.html'))
    assert atlas_rfp.atlas_parsing.parse_payee_search_for_vendor_id(search, 'test1') == 12345678
    assert atlas_rfp.atlas_parsing.parse_payee_search_for_vendor_id(search, 'test2') == 87654321

