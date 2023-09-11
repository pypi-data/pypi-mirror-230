import atlas_rfp.atlas_parsing
from pathlib import Path

class Pseudoresponse:
    text: str
    def __init__(self, text: str):
        self.text = text

def open_file_as_pseudoresponse(filename: Path):
    basepath = Path(__file__).resolve().parent
    return Pseudoresponse((basepath / filename).read_text())

def test_request_rfp_parse():
    request_rfp_page = open_file_as_pseudoresponse(Path('files/request_rfp_token.html'))
    expected = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'
    assert atlas_rfp.atlas_parsing.parse_csrf_token(request_rfp_page) == expected

def test_request_token_parse():
    upload_page = open_file_as_pseudoresponse(Path('files/post_upload_token.html'))
    expected = '1A2B3C4D5E6F'
    assert atlas_rfp.atlas_parsing.parse_csrf_token(upload_page) == expected

def test_save_rfp_token_parse():
    save_rfp_page = open_file_as_pseudoresponse(Path('files/save_rfp.html'))
    expected = '1A2B3C4D5E6F'
    assert atlas_rfp.atlas_parsing.parse_csrf_token(save_rfp_page) == expected

def test_new_rfp_number_parse():
    save_rfp_page = open_file_as_pseudoresponse(Path('files/save_rfp.html'))
    expected = 109130351
    assert atlas_rfp.atlas_parsing.parse_save_rfp_for_rfp_num(save_rfp_page) == expected

def test_send_to_token_parse():
    send_to_search_page = open_file_as_pseudoresponse(Path('files/send_to_page.html'))
    expected = '1A2B3C4D5E6F'
    assert atlas_rfp.atlas_parsing.parse_csrf_token(send_to_search_page) == expected

def test_send_to_search_token_parse():
    send_to_search_page = open_file_as_pseudoresponse(Path('files/multiple_sendto_recipient.html'))
    expected = '1A2B3C4D5E6F'
    assert atlas_rfp.atlas_parsing.parse_csrf_token(send_to_search_page) == expected

def test_rfp_sending_parse():
    success_page = open_file_as_pseudoresponse(Path('files/successful_sendto.html'))
    fail_page = open_file_as_pseudoresponse(Path('files/failed_sendto.html'))
    assert atlas_rfp.atlas_parsing.parse_final_confirmation_page(success_page) == (True, 'Your RFP has been forwarded to test1@MIT.EDU.')
    assert atlas_rfp.atlas_parsing.parse_final_confirmation_page(fail_page) == (False, 'You cannot forward the RFP to yourself.')