"""
Helper Pydantic models that define the state
of the RFP system. We can load these models
using Beautifulsoup for parsing.
"""
import datetime
from typing import Dict, List, Optional, Union
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from pydantic import BaseModel, PositiveInt, HttpUrl, field_validator, ConfigDict
from moneyed import Money, USD

class Person(BaseModel):
    """
    Model representing a person.

    The name field is required, the
    kerberos is optional (not displayed
    in several RFP pages).
    """
    name: str
    kerberos: Optional[str] = None

class MailingInstructions(BaseModel):
    """
    Model representing extra mailing
    instructions.
    Used for non-direct-deposit reimbursements.
    """
    addressee: Person
    phone: str
    address: str
    city: str
    state: str
    postal_code: str
    country: str
    tax_type: str
    ssn_tin: str

class GLAccount(BaseModel):
    """
    A model representing a
    GL account, separating its
    ID and name.
    """
    id: int
    name: str

class CostObject(BaseModel):
    """
    A model representing a
    cost object, separating its
    ID and name.
    """
    id: int
    name: str

class LineItem(BaseModel):
    """
    A model defining a reimbursable
    line-item.
    """
    approved: bool
    date_of_service: datetime.date
    gl_account: GLAccount
    cost_object: CostObject
    amount: Money
    explanation: str

    # Allow the Money entry
    model_config = ConfigDict(arbitrary_types_allowed=True)

class LineItemRequest(BaseModel):
    """
    A model defining a request
    for a reimbursable line-item.
    """
    date_of_service: datetime.date
    gl_account_id: int 
    cost_object_id: int
    amount: Money
    explanation: str

    @field_validator('amount', mode='before')
    @classmethod
    def parse_money(cls, v: str) -> Money:
        return Money(v, USD)

    # Allow the Money entry
    model_config = ConfigDict(arbitrary_types_allowed=True)

class Receipt(BaseModel):
    id: PositiveInt
    url: HttpUrl

class AttachmentUpload(BaseModel):
    filename: str
    data: bytes
    mime: str

class RFPAction(BaseModel):
    """
    A model representing an action taken on an RFP.
    """
    datetime: datetime.datetime
    action: str
    actor: Optional[str]

class RFPCreationData(BaseModel):
    """
    A model representing the data needed
    to create an RFP
    """
    payee: Person
    rfp_name: str
    line_items: List[LineItemRequest]
    attachments: List[AttachmentUpload]
    office_note: str
    recipient_msg: Optional[str] = None

    def to_postable_dict(self) -> Dict[str,str]:
        """
        Returns a serializable form of this RFP
        that can be posted to the SaveRfp endpoint.
        """
        result = {
            'rfpDocument.shortDescription': self.rfp_name,
            'rfpDocument.messageForAP': self.office_note,
        }
        for i, line_item in enumerate(self.line_items):
            result[f'rfpDocument.lineItems[{i}].serviceDate'] = line_item.date_of_service.strftime('%m/%d/%Y')
            result[f'rfpDocument.lineItems[{i}].glAccount.glAccountNumber'] = str(line_item.gl_account_id)
            result[f'rfpDocument.lineItems[{i}].costObject.costObjectNumber'] = str(line_item.cost_object_id)
            result[f'rfpDocument.lineItems[{i}].amount'] = str(line_item.amount.amount)
            result[f'rfpDocument.lineItems[{i}].explanation'] = line_item.explanation
        return result

class RFP(BaseModel):
    """
    A model representing a submitted RFP.
    """
    inbox: Union[None,Person,Literal['Paid']]
    rfp_number: PositiveInt
    payee: Person
    company_code: str
    rfp_name: str
    rfp_type: str
    amount: Money
    payment_method: Union[MailingInstructions,Literal['Direct Deposit'],Literal['Check']]
    line_items: List[LineItem]
    office_note: str
    receipts: List[Receipt]
    history: List[RFPAction]
    # Allow the Money entry
    model_config = ConfigDict(arbitrary_types_allowed=True)

class RFPSearchResult(BaseModel):
    """
    A model representing a RFP search result.

    In addition to some basic information about
    the RFP, this object also includes the URL
    needed to get RFP details.
    """
    rfp_number: PositiveInt
    rfp_details_url: HttpUrl
    creation_date: datetime.date
    payee: Person
    created_by: Person
    rfp_name: str
    location_status: Union[Person,Literal['Paid']]
    cost_object: Union[CostObject,Literal['Multiple']]
    amount: Money
    # Allow the Money entry
    model_config = ConfigDict(arbitrary_types_allowed=True)