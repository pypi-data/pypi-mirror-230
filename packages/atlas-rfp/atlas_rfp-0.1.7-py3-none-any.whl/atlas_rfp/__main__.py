import json
import datetime
from touchstone_auth import TouchstoneSession
from moneyed import Money, USD
from . import submit_rfp
from . import models
with open('credentials.json', encoding='utf-8') as configfile:
    config = json.load(configfile)

with TouchstoneSession('https://adminappsts.mit.edu/rfp/SearchEntry.action?sapSystemId=PS1',
        config['certfile'], config['password'], 'cookiejar.pickle',
        verbose=True) as s:
    test_rfp = models.RFPCreationData(
        payee=models.Person(name='Test Person', kerberos='test1'),
        rfp_name='Test from atlas-rfp package',
        line_items=[
            models.LineItemRequest(
                date_of_service=datetime.date(2023,1,27),
                gl_account_id=421000,
                cost_object_id=123456,
                amount=Money(10,USD),
                explanation='First line item'
                )
        ],
        attachments=[
            models.AttachmentUpload(filename='test.txt', data='test file 1'.encode('utf8'), mime='text/plain'),
            models.AttachmentUpload(filename='test2.txt', data='test file 2'.encode('utf8'), mime='text/plain'),
        ],
        office_note='',
        recipient_msg='Please delete this'
    )
    print(submit_rfp(s, rfp=test_rfp, recipient=models.Person(name='Test Person2', kerberos='test2')))