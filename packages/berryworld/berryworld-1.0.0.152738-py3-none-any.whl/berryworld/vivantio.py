import requests as req
import json
import pandas as pd
import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class Vivantio:
    def __init__(self, token=None):
        if token is None:
            raise Exception('Token is required to connect to DevOps')

        self.headers = {
            'Authorization': 'Basic ' + token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        self.session = req.Session()
        retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=30)
        retry.BACKOFF_MAX = 190

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.base_url = 'https://webservices-na01.vivantio.com/api'

    def session_request(self, method, url, headers=None, data=None):
        if headers is None:
            headers = self.headers

        if data is None:
            response = self.session.request(method, url, headers=headers)
        else:
            response = self.session.request(method, url, headers=headers, data=data)

        if str(response.status_code).startswith('2'):
            return response
        else:
            raise Exception(f'Status: {response.status_code} - {response.text}')

    def get_clients(self, record_type_id=None):
        items = []
        if record_type_id is not None:
            items.append({"FieldName": "RecordTypeId", "Op": "Equals", "Value": record_type_id})

        client_query = json.dumps(
            {
                "Query": {
                    "Items": items,
                    "Mode": "MatchAll"
                }
            }
        )

        url = f'{self.base_url}/Client/Select'
        response = self.session_request('POST', url, data=client_query)
        response = response.json()
        response_df = pd.json_normalize(response['Item'])

        return response_df

    def get_tickets(self, record_type_id=None, client_id=None, open_date=None, close_date=None,
                    last_modified_date=None):
        items = []
        if record_type_id is not None:
            items.append({"FieldName": "RecordTypeId", "Op": "Equals", "Value": record_type_id})
        if client_id is not None:
            items.append({"FieldName": "ClientId", "Op": "Equals", "Value": client_id})
        if open_date is not None:
            items.append({"FieldName": "OpenDate", "Op": "GreaterThanOrEqualTo", "Value": open_date})
        if close_date is not None:
            items.append({"FieldName": "CloseDate", "Op": "LessThanOrEqualTo", "Value": close_date})
        if last_modified_date is not None:
            items.append({"FieldName": "LastModifiedDate", "Op": "LessThanOrEqualTo", "Value": last_modified_date})

        ticket_query = json.dumps(
            {
                "Query": {
                    "Items": items,
                    "Mode": "MatchAll"
                }
            }
        )

        url = f'{self.base_url}/Ticket/Select'
        response = self.session_request('POST', url, data=ticket_query)
        response = response.json()

        return response

    def get_ticket(self, ticket_id):
        url = f'{self.base_url}/Ticket/SelectById/{ticket_id}'
        response = self.session_request('POST', url)

        response = response.json()
        response_df = pd.json_normalize(response['Item'])

        return response_df

    def get_config_info(self, record_type_id, extension='category'):
        url = f'{self.base_url}/Configuration/'
        if extension.lower() == 'priority':
            url += f'CategorySelectByRecordTypeId/{record_type_id}'
        else:
            url += f'PrioritySelectByRecordTypeId/{record_type_id}'

        response = self.session_request('POST', url)

        response = response.json()
        response_df = pd.json_normalize(response['Results'])

        return response_df

    def get_sla_info(self, extension='sla', ticket_id=None):
        if extension.lower() == 'priority':
            url = f'{self.base_url}/Configuration/SLAStageTargetSelectByPriority/{ticket_id}'
        else:
            url = f'{self.base_url}/Ticket/SLAStageInstanceSelectByTicket/{ticket_id}'

        response = self.session_request('POST', url)

        response = response.json()
        response_df = pd.json_normalize(response['Results'])

        return response_df

    def create_ticket(self, title, message):
        if title is None:
            raise Exception('Ticket title is required')

        if message is None:
            raise Exception('Ticket message is required')

        ticket_payload = {
            "RecordTypeId": 11,
            "ClientId": 60,
            "OpenDate": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "Title": title,
            "CallerName": "Data Alert",
            "CallerEmail": "Data.Alert@poupart.onmicrosoft.com",
            "StatusId": 35,
            "PriorityId": 81
        }

        if message is not None:
            if isinstance(message, pd.DataFrame):
                message = message.to_html()
            ticket_payload['DescriptionHtml'] = message

        ticket_payload = json.dumps(ticket_payload)

        url = f'{self.base_url}/Ticket/Insert'
        response = self.session_request('POST', url, data=ticket_payload)

        response = response.json()
        response_df = pd.DataFrame.from_dict(response, orient='index').T

        return response_df

    def add_note_ticket(self, ticket_id, message=None):
        if message is None:
            raise Exception('An update message is required')

        url = f'{self.base_url}/Ticket/AddNote'
        ticket_payload = json.dumps(
            {
                "AffectedTickets": [ticket_id],
                "Date": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "Notes": message
            }
        )

        response = self.session_request('POST', url, data=ticket_payload)
        response = response.json()

        return response

    def close_ticket(self, ticket_id, message=None):
        if message is None:
            raise Exception('A close message is required')

        open_status_url = f'{self.base_url}/Ticket/ChangeStatus'
        status_payload = json.dumps(
            {
                "AffectedTickets": [ticket_id],
                "Date": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "StatusId": 122
            }
        )
        response = self.session_request('POST', open_status_url, data=status_payload)
        if str(response.status_code).startswith('2'):
            url = f'{self.base_url}/Ticket/Close'
            ticket_payload = json.dumps(
                {"AffectedTickets": [ticket_id],
                 "CloseStatusId": 124,
                 "CloseDate": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 "Notes": message
                 }
            )

            response = self.session_request('POST', url, data=ticket_payload)

        response = response.json()

        return response

    def delete_ticket(self, ticket_id):
        url = f'{self.base_url}/Ticket/Delete'

        delete_payload = json.dumps(
            {
                "AffectedTickets": [
                    ticket_id
                ],
                "Date": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            }, default=str
        )

        response = self.session_request('DELETE', url, data=delete_payload)
        response = response.json()

        return response
