from typing import Optional
from requests import Session
from . import atlas_parsing
from .models import RFP, RFPCreationData, Person

def search(session:Session, *, rfp_number:int) -> Optional[RFP]:
    """
    Search for an RFP and return its information.
    
    Arguments
    ---------
    session: An already-authenticated Requests session.
    rfp_number: The RFP to search for.
    
    Returns
    -------
    Returns a RFP object representing the current state of the RFP.
    """
    response = session.post(
        'https://adminappsts.mit.edu/rfp/SearchForRfps.action',
        data={
            'taxable': '',
            'criteria.parked': 'true',
            '__checkbox_criteria.parked': 'true',
            'criteria.posted': 'true',
            '__checkbox_criteria.posted': 'true',
            '__checkbox_criteria.deleted': 'true',
            'criteria.companyCode': 'CUR',
            'criteria.rfpNumber': str(rfp_number),
            'criteria.createdDateFrom':'', #MM/DD/YY
            'criteria.createdDateTo': '',
            'criteria.payeeName': '',
            'criteria.shortDescription': '',
            'criteria.costObjectNumber': '',
            'criteria.glAccountNumber': ''
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    )
    return atlas_parsing.parse_rfp_details(response)

def submit_rfp(session: Session, *, rfp: RFPCreationData, recipient: Optional[Person]=None) -> RFP:
    """
    Submits an RFP and optionally sends it to a recipient.
    
    Arguments
    ---------
    session: An already-authenticated Requests session.
    rfp: The RFP details to create.
    recipient: If specified, this will attempt to send the RFP to the given recipient.
    
    Returns
    -------
    The newly created RFP object
    """
    if rfp.payee.kerberos is None:
        raise RuntimeError("Specify a kerberos in the payee name so that the proper payee can be identified!")
    _ = session.get('https://adminappsts.mit.edu/rfp/SearchForPayeeStart.action')
    payee_search_response = session.post(
        'https://adminappsts.mit.edu/rfp/SearchForPayee.action',
        data={
            'taxable': 'false',
            'payeeType': 'MIT',
            'payeeName': rfp.payee.name
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    )
    payee_vendor_id = atlas_parsing.parse_payee_search_for_vendor_id(payee_search_response, rfp.payee.kerberos)
    request_rfp_response = session.get(
        'https://adminappsts.mit.edu/rfp/RequestRfp.action',
        params={
            'vendorNumber': payee_vendor_id,
            'taxable': 'false',
            'mitNeedsTaxable': 'false',
        },
    )
    rfp_token = atlas_parsing.parse_csrf_token(request_rfp_response)

    save_rfp_response = session.post(
        'https://adminappsts.mit.edu/rfp/SaveRfp.action',
        data={
            'rfpDocument.taxable': 'false',
            'fromPage': '',
            'redoSearch': '',
            'struts.token.name': 'token',
            'token': rfp_token,
            'rfpDocument.companyCode': 'CUR',
            **rfp.to_postable_dict(),
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    )
    rfp_number = atlas_parsing.parse_save_rfp_for_rfp_num(save_rfp_response)
    csrf_token = atlas_parsing.parse_csrf_token(save_rfp_response)

    # Upload files
    for i, attachment in enumerate(rfp.attachments):
        if i == 0:
            headers = {'Referer': 'https://adminappsts.mit.edu/rfp/SaveRfp.action'}
        else:
            headers = {'Referer': 'https://adminappsts.mit.edu/rfp/UploadAttachmentReimbursement.action'}
        attach_response = session.post(
            'https://adminappsts.mit.edu/rfp/UploadAttachmentReimbursement.action',
            data={
                'mode': 'EDIT',
                'profiling': 'true'
            },
            files={
                'upload': (attachment.filename, attachment.data, attachment.mime)
            },
            headers=headers
        )
        if attach_response.status_code != 200:
            raise RuntimeError("Unable to upload attachment file!")
        csrf_token = atlas_parsing.parse_csrf_token(attach_response)
    
    # Send to recipient if needed
    if recipient:
        send_to_search_response = session.post(
            'https://adminappsts.mit.edu/rfp/SendTo.action',
            data={
                # Everything except companyCode from above
                'rfpDocument.taxable': 'false',
                'fromPage': '',
                'redoSearch': '',
                'struts.token.name': 'token',
                'token': csrf_token,
                **rfp.to_postable_dict(),
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        )
        send_to_token = atlas_parsing.parse_csrf_token(send_to_search_response)

        # We need to generate the search page just to get the final forward token
        send_to_search_results = session.post(
            'https://adminappsts.mit.edu/rfp/SearchForRecipient.action',
            data={
                'struts.token.name': 'token',
                'token': send_to_token,
                'partialApprovalForward': 'false',
                'recipientName': recipient.name
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        )
        forward_token = atlas_parsing.parse_csrf_token(send_to_search_results)

        # Send the final RFP along
        final_response = session.post(
            'https://adminappsts.mit.edu/rfp/SendRfp.action',
            data={
                'struts.token.name': 'token',
                'token': forward_token,
                'partialApprovalForward': 'false',
                'recipientName': recipient.name,
                'recipientKerb': recipient.kerberos,
                'rfpDocument.forwardToMessage': rfp.recipient_msg if rfp.recipient_msg else ''
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        )
        result = atlas_parsing.parse_final_confirmation_page(final_response)
        if not result[0]:
            err = f'Unable to forward RFP: {result[1]}'
            raise RuntimeError(err)
    # Search for and return the newly created RFP
    search_result = search(session, rfp_number=rfp_number)
    if search_result is None:
        raise RuntimeError("Unable to locate RFP after submission!")
    return search_result