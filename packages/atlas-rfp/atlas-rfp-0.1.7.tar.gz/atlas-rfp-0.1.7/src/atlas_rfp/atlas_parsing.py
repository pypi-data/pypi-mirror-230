"""
This submodule handles parsing the HTML versions
of the Atlas pages to generate Python models of
the data.
"""
import re
from typing import Tuple

from bs4 import BeautifulSoup # type: ignore
from bs4.element import Tag, PageElement   # type: ignore
import requests
import datetime
import warnings
from moneyed import Money, USD

from .models import *

def parse_search_result(row: Tag) -> Optional[RFPSearchResult]:
    parsed = {}
    for i, col in enumerate(row.find_all('td', class_='data')):
        if i == 0:
            # Should be an a href
            a_tag = col.find('a')
            if a_tag is None:
                warnings.warn('Unable to find RFP details hyperlink')
                return None
            parsed['rfp_number'] = int(a_tag.text)
            parsed['rfp_details_url'] = f'https://adminappsts.mit.edu/rfp/{a_tag["href"]}'
        elif i == 1:
            parsed['creation_date'] = datetime.datetime.strptime(
                col.text.strip(),
                "%m/%d/%Y"
            ).date()
        elif i == 2:
            parsed['payee'] = Person(name=col.text.strip())
        elif i == 3:
            parsed['created_by'] = Person(
                name=col['title'],
                kerberos=col.text.strip()
            )
        elif i == 4:
            parsed['rfp_name'] = col.text.strip()
        elif i == 5:
            # Check if it is payed or not
            if col.text.strip() == 'Paid':
                parsed['location_status'] = 'Paid'
            else:
                parsed['location_status'] = Person(
                    name = col['title'],
                    kerberos=col.find('a').text.strip()
                )
        elif i == 6:
            if col.text.strip() == 'Multiple':
                parsed['cost_object'] = 'Multiple'
            else:
                parsed['cost_object'] = CostObject(
                    id = int(col.text.strip()),
                    name = col['title']
                )
        elif i == 7:
            parsed['amount'] = Money(col.text.strip().strip('$'), USD)
    return RFPSearchResult(**parsed)

# Predicates for searching
def _filter_previous_sibling(tag, func) -> bool:
    previous_tag = tag.find_previous_sibling()
    if previous_tag is None:
        return False
    return func(previous_tag)

def _has_class(tag, class_str) -> bool:
    classes = tag.get('class')
    if classes is None:
        return False
    return class_str in classes

def _data_td_preceded_by_th(tag, th_str) -> bool:
    return (
        tag.name == 'td' and
        _has_class(tag, 'data') and
        _filter_previous_sibling(tag,
            lambda sibling: sibling.name == 'th'
            and sibling.text.strip() == th_str
        )
    )

def _class_preceded_by_tag(tag, tag_class, pre_tag, pre_str) -> bool:
    return (
        _has_class(tag, tag_class) and
        _filter_previous_sibling(tag,
            lambda sibling: sibling.name == pre_tag
            and sibling.text.strip() == pre_str
        )
    )

def parse_rfp_details(response: requests.Response) -> Optional[RFP]:
    page = BeautifulSoup(response.text, features='html.parser')

    rfp = {}

    current_status_div = page.find(
        lambda tag: tag.name == 'div'
        and _filter_previous_sibling(tag,
            lambda sibling: sibling.name == 'h2'
            and sibling.text.strip() == 'Current Status'
        )
    )
    if current_status_div is None:
        warnings.warn('Unable to locate Current Status table')
        return None
    # The box might be labeled both "Inbox" and "Status"
    inbox_status = current_status_div.find(
        lambda tag: _data_td_preceded_by_th(tag, 'Inbox')
    )

    if inbox_status is None:
        inbox_status = current_status_div.find(
            lambda tag: _data_td_preceded_by_th(tag, 'Status')
        )

    if inbox_status is None:
        warnings.warn('Unable to locate inbox status field!')
        inbox = None
    else:
        inbox = inbox_status.text.strip()
        if inbox == 'Sent to bank for payment':
            rfp['inbox'] = 'Paid'
        
        mailto_link = inbox_status.find('a')
        if mailto_link is not None:
            name = mailto_link.text.strip()
            kerb_re = re.match(r'^mailto:([^@]+)@[mM][iI][tT]\.[eE][dD][uU]$', mailto_link['href'])
            rfp['inbox'] = Person(name=name, kerberos=kerb_re.group(1) if kerb_re is not None else None)

    # Find the section container preceded by the H2 "Payment Details"
    details_div = page.find(
        lambda tag: tag.name == 'div'
        and _filter_previous_sibling(tag,
            lambda sibling: sibling.name == 'h2'
            and sibling.text.strip() == 'Payment Details'
        )
    )
    if details_div is None:
        warnings.warn('Unable to locate Payment Details table in RFP details')
        return None
    
    rfp_number_td = details_div.find(
        lambda tag: _data_td_preceded_by_th(tag, 'RFP Number')
    )
    if rfp_number_td is None:
        warnings.warn('Unable to locate RFP number field in RFP details')
        return None
    rfp['rfp_number'] = int(rfp_number_td.text.strip())

    payee_td = details_div.find(
        lambda tag: _data_td_preceded_by_th(tag, 'Payee')
    )
    if payee_td is None:
        warnings.warn('Unable to locate payee field in RFP details')
        return None
    rfp['payee'] = Person(name=payee_td.text.strip())

    rfp_name_td = details_div.find(
        lambda tag: _data_td_preceded_by_th(tag, 'Name of RFP')
    )
    if rfp_name_td is None:
        warnings.warn('Unable to locate RFP name field in RFP details')
        return None
    rfp['rfp_name'] = rfp_name_td.text.strip()

    # Company code, rfp type, payment method are loaded from the details div
    company_code_td = details_div.find(
        lambda tag: _data_td_preceded_by_th(tag, 'Company Code')
    )
    if company_code_td is None:
        warnings.warn('Unable to locate Company Code entry')
        return None
    rfp['company_code'] = company_code_td.text.strip()

    rfp_type_td = details_div.find(
        lambda tag: _data_td_preceded_by_th(tag, 'Type of RFP')
    )
    if rfp_type_td is None:
        warnings.warn('Unable to locate Type of RFP entry')
        return None
    rfp['rfp_type'] = rfp_type_td.text.strip()

    payment_method_td = details_div.find(
        lambda tag: _data_td_preceded_by_th(tag, 'Payment Method')
    )
    rfp['payment_method'] = payment_method_td.text.strip()

    rfp['line_items'] = []
    for line_item in page.find_all('div', attrs={'class': 'lineItem'}):
        item = {}
        item['approved'] = line_item.find('img', alt='approved') is not None

        details_table = line_item.find('table', attrs={'class': 'topHeadersTable'})
        if details_table is None:
            warnings.warn('Unable to find line-item details table')
            return None
        tbody = details_table.find('tbody')
        if tbody is None:
            warnings.warn('Unable to find line-item table body')
            return None
        
        for i, td in enumerate(tbody.find_all('td', attrs={'class': 'data'})):
            if i == 0:
                item['date_of_service'] = datetime.datetime.strptime(
                    td.text.strip(),
                    "%m/%d/%Y"
                ).date()
            elif i == 1:
                account_match = re.match(r"(?P<id>\d+) - (?P<name>.+)", td.text.strip())
                if account_match is None:
                    warnings.warn('Unable to parse the line item GL account')
                    return None
                item['gl_account'] = GLAccount(
                    id=int(account_match['id']),
                    name=account_match['name']
                )
            elif i == 2:
                co_match = re.match(r"(?P<id>\d+) - (?P<name>.+)", td.text.strip())
                if co_match is None:
                    warnings.warn('Unable to parse the line item cost object')
                    return None
                item['cost_object'] = CostObject(
                    id=int(co_match['id']),
                    name=co_match['name']
                )
            elif i == 3:
                # Strip leading dollar sign and any internal commas
                item['amount'] = Money(td.text.strip().strip('$').replace(',',''), USD)
            else:
                warnings.warn(f'Unexpected entry in line item details table! Entry: {td}')
                return None
        # Locate explanation
        explanation_div = line_item.find(
            lambda tag: _class_preceded_by_tag(
                tag, 'data', 'h4', 'Explanation'
        ))
        if explanation_div is None:
            warnings.warn('Unable to locate explanation div in line item!')
            return None
        item['explanation'] = explanation_div.text.strip()
        rfp['line_items'].append(LineItem(**item))
    
    rfp['amount'] = sum([item.amount for item in rfp['line_items']])
    # Load office note, if it exists
    office_note_div = page.find(
        lambda tag: _class_preceded_by_tag(
            tag, 'sectionContainer', 'h3', 'Note to Central Office'
        )
    )
    if office_note_div is None:
        rfp['office_note'] = ''
    else:
        rfp['office_note'] = office_note_div.find('div', attrs={'class': 'data'}).text.strip()

    receipts_div = page.find('div', attrs={'class': 'receiptsList'})
    rfp['receipts'] = []
    if receipts_div is None:
        # Try to load single receipt
        receipt_button = page.find('button', attrs={'class': 'showReceipts'})
        if receipt_button is None:
            warnings.warn('Unable to locate receipt list')
        else:
            rfp['receipts'].append(Receipt(id=1, url=f"https://adminappsts.mit.edu{receipt_button['value']}"))
    else:
        for tag in receipts_div.find_all('a'):
            url = tag['href']
            if not url.startswith("http"):
                url = f"https://adminappsts.mit.edu{url}"
            rfp['receipts'].append(Receipt(
                id=re.match(r'#(\d+),?', tag.text.strip()).group(1),
                url=url
            ))
    
    history_div = page.find(
        lambda tag: _class_preceded_by_tag(
            tag, 'sectionContainer', 'h2', 'RFP History'
        )
    )
    if history_div is None:
        warnings.warn('Unable to locate history div')
        return None
    rfp['history'] = []
    history_table = history_div.find('tbody')
    if history_table is None:
        warnings.warn('Unable to locate the history table')
        return None
    
    for row in history_table.find_all('tr'):
        cells = list(row.find_all('td', attrs={'class': 'data'}))
        if len(cells) < 3:
            warnings.warn('Unable to parse history row')
            return None
        # Parse the action into actor and action
        action_split = cells[2].text.strip().split(' by ')
        action: str = ''
        actor: Optional[str] = None
        if len(action_split) == 2:
            action = action_split[0]
            actor = action_split[1]
        elif 'payment' in action_split[0].lower() and 'sent' in action_split[0].lower():
            action = action_split[0]
            actor = 'Bank'
        else:
            action = action_split[0]
        rfp['history'].append(RFPAction(
            datetime=datetime.datetime.strptime(
                f'{cells[0].text.strip()} {cells[1].text.strip()}',
                "%m/%d/%Y %I:%M %p"
            ),
            action=action,
            actor=actor,
        ))
    return RFP(**rfp)
    

def parse_search(search_response:requests.Response) -> List[RFPSearchResult]:
    """
    Parses a Response object into a list of RFP search results.

    Arguments
    ---------
    search_response: A HTML response containing the Atlas RFP search page.

    Returns
    -------
    A list of RFPSearchResults representing the search results.
    """
    html = BeautifulSoup(search_response.text, features='html.parser')
    # Get the search results table
    results_table = html.find(id='searchResultsTable')
    if results_table is None:
        raise RuntimeError('Unable to find search results table!')
    results_body = results_table.find('tbody')
    if not isinstance(results_body, Tag):
        raise RuntimeError('Unable to locate `tbody` tag in search results table!')
    return [x for x in 
           [parse_search_result(row) for row in results_body.find_all('tr')]
           if x is not None]

def parse_payee_search_for_vendor_id(search_response: requests.Response, kerberos: str) -> int:
    """
    Parses a payee search and returns the "vendor number" needed
    to submit an RFP against.

    Arguments
    ---------
    search_response: An HTML response from the rfp/SearchForPayee.action endpoint.

    Returns
    -------
    The vendor ID needed to submit things to rfp/RequestRfp.action

    Raises
    ------
    RuntimeError if the payee is not unique or otherwise not found.
    """
    html = BeautifulSoup(search_response.text, features='html.parser')
    # Locate the response table
    payee_div = html.find(
        lambda tag: _class_preceded_by_tag(
            tag, 'sectionContainer', 'h2', 'Select Payee'
        )
    )
    if payee_div is None:
        raise RuntimeError("Could not locate payee table div in payee search response!")
    table_body = payee_div.find('tbody')
    if table_body is None:
        raise RuntimeError("Could not locate payee table")
    rows = list(table_body.find_all('td', class_='data'))
    for row in rows:
        payee_link = row.find('a')
        if payee_link is None:
            raise RuntimeError("Could not locate link with payee vendor ID!")
        vendor_id_extract = re.search(r"vendorNumber=(\d+)", payee_link['href'])
        if vendor_id_extract is None:
            raise RuntimeError("Could not parse payee link to get vendor number!")
        
        # Verify that the kerberos matches, if we have multiple payees
        payee_kerberos = re.match(r".*\(([^,]+),.*\)", payee_link.text.strip())
        if payee_kerberos is None:
            raise RuntimeError("Could not parse payee Kerberos")
        if payee_kerberos.group(1) != kerberos:
            continue
        return int(vendor_id_extract.group(1))
    raise RuntimeError("Unable to locate payee! Could not find a matching kerberos")

def parse_csrf_token(search_response: requests.Response) -> str:
    """
    Parses a RFP request and returns the "CSFR token" needed
    to save an RFP against.

    Arguments
    ---------
    search_response: An HTML response from the rfp/RequestRfp.action endpoint.

    Returns
    -------
    The token needed to submit things to rfp/SaveRFP.action
    """
    html = BeautifulSoup(search_response.text, features='html.parser')
    # Locate the main page form
    main_form = html.find('form', attrs={'id': 'PageForm', 'name': 'PageForm'})
    if main_form is None:
        raise RuntimeError("Unable to locate RFP request form on page!")
    token_input = main_form.find('input', attrs={'name': 'token', 'type': 'hidden'})
    if token_input is None:
        raise RuntimeError("Unable to locate CSFR token on RFP request page!")
    return token_input['value']
    
def parse_save_rfp_for_rfp_num(save_rfp_response: requests.Response) -> int:
    """
    Parses the Save RFP page and returns the new RFP number.
    
    Arguments
    ---------
    save_rfp_response: An HTML response from the rfp/SaveRfp.action endpoint.
    
    Returns
    -------
    The newly created RFP number
    """
    html = BeautifulSoup(save_rfp_response.text, features='html.parser')
    # Locate the reimbursement details field
    main_div = html.find('div', attrs={'id': 'rfpDetails', 'class': 'sectionContainer'})
    if main_div is None:
        raise RuntimeError("Unable to locate RFP details div!")
    first_data_td = main_div.find('td', attrs={'class': 'data'})
    if first_data_td is None:
        raise RuntimeError("Unable to locate first table entry for RFP number")
    return int(first_data_td.text.strip())

def parse_final_confirmation_page(send_response: requests.Response) -> Tuple[bool,str]:
    """
    Parses the final RFP send-to page, returning the final state of the RFP.
    
    Arguments
    ---------
    send_response: An HTML response from the rf/SendRfp.action endpoint.
    
    Returns
    -------
    A tuple containing (successful, message). The first entry is
    False for an error, True for success.
    """
    html = BeautifulSoup(send_response.text, features='html.parser')
    # Locate the message div
    error_div = html.find('div', attrs={'class': 'portlet-msg-error'})
    success_div = html.find('div', attrs={'class': 'portlet-msg-success'})
    if success_div:
        return (True, success_div.text.strip())
    if error_div:
        return (False, error_div.text.strip())
    raise RuntimeError("Unable to determine sending state")
