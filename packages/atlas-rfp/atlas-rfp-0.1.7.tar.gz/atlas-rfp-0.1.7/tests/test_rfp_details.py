import atlas_rfp.atlas_parsing
from atlas_rfp.models import Person
from pathlib import Path

class Pseudoresponse:
    text: str
    def __init__(self, text: str):
        self.text = text

def open_file_as_pseudoresponse(filename: Path):
    basepath = Path(__file__).resolve().parent
    return Pseudoresponse((basepath / filename).read_text())

def test_single_rfp():
    details = open_file_as_pseudoresponse(Path('files/display_single_receipt.html'))
    rfp = atlas_rfp.atlas_parsing.parse_rfp_details(details)
    assert rfp is not None
    assert len(rfp.receipts) == 1
    assert rfp.receipts[0].id == 1
    assert str(rfp.receipts[0].url) == "https://adminappsts.mit.edu/rfp/DownloadAttachment.action?arDocType=ZFIIINVPRE&sapObjectType=BKPF&archiveDocId=34572134786123ABCCADE"
    assert type(rfp.inbox) == Person and rfp.inbox.kerberos == 'example'

def test_multi_rfp():
    details = open_file_as_pseudoresponse(Path('files/display_dual_receipt.html'))
    rfp = atlas_rfp.atlas_parsing.parse_rfp_details(details)
    assert rfp is not None
    assert len(rfp.receipts) == 2
    assert str(rfp.receipts[0].url) == "https://adminappsts.mit.edu/rfp/DownloadAttachment.action?arDocType=ZFIIINVPRE&sapObjectType=BKPF&archiveDocId=005056826E6C1EDE8FF660B5FAE9673D"
    assert type(rfp.inbox) == Person and rfp.inbox.kerberos == 'example'

def test_finished_rfp():
    details = open_file_as_pseudoresponse(Path('files/display_finished.html'))
    rfp = atlas_rfp.atlas_parsing.parse_rfp_details(details)
    assert rfp is not None
    assert len(rfp.receipts) == 5
    assert rfp.inbox == 'Paid'

def test_rfp():
    details = open_file_as_pseudoresponse(Path('files/display_test4.html'))
    rfp = atlas_rfp.atlas_parsing.parse_rfp_details(details)