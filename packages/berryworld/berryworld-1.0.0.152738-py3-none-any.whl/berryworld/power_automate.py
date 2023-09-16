import math
import requests as req
import json
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class PowerAutomate:
    def __init__(self, organisation_id, environment_id, business_unit, delegated=True, credentials=None):
        if credentials is None:
            raise Exception('Credentials are required to connect to Power Automate')

        if all(k in credentials for k in ("client_id", "client_secret")):
            self.client_id = credentials['client_id']
            self.client_secret = credentials['client_secret']
        else:
            raise Exception('Credentials require a client_id and client_secret to connect to Power Automate')

        if delegated and all(k in credentials for k in ("username", "password")):
            self.username = credentials['username']
            self.password = credentials['password']
        else:
            raise Exception('Delegated credentials require a username and password to connect to Power Automate')

        self.session = req.Session()
        retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=30)
        retry.BACKOFF_MAX = 190

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.token_url = f'https://login.microsoftonline.com/{organisation_id}/oauth2/v2.0/token'

        self.environment_id = environment_id
        self.filter_limit = 15
        self.base_flow_url = f'https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple'

        if delegated:
            self.grant_type = 'password'
        else:
            self.grant_type = 'client_credentials'
            self.business_unit = business_unit

        self.headers = self.generate_bearer_token()

    def generate_bearer_token(self, grant_type=None, scope=None):
        bearer_payload = f'grant_type={self.grant_type}&client_id={self.client_id}&client_secret={self.client_secret}'
        if grant_type is not None:
            bearer_payload = f'grant_type={grant_type}&client_id={self.client_id}&client_secret={self.client_secret}'

        if grant_type == 'client_credentials' or self.grant_type == 'client_credentials':
            if scope is None:
                scope = 'https://management.azure.com/.default'
            bearer_payload = bearer_payload + f'&scope={scope}'
        else:
            if scope is None:
                scope = 'https://service.flow.microsoft.com/.default'
            bearer_payload = bearer_payload + f'&username={self.username}' \
                                              f'&password={self.password}&scope={scope}'

        bearer_headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        token_response = self.session.request("POST", self.token_url, headers=bearer_headers, data=bearer_payload)
        auth_status_code = token_response.status_code

        if str(auth_status_code).startswith('2'):
            auth_access_token = 'Bearer ' + json.loads(token_response.text)['access_token']
            headers = {"Authorization": f"{auth_access_token}", "Content-Type": "application/json"}
        else:
            raise Exception(f'Error: {auth_status_code} - {token_response.text}')

        return headers

    def paginate(self, response):
        paginated_df = pd.DataFrame()

        pagination_keys = ['@odata.nextLink', '@odata.deltaLink', 'nextLink']
        pagination_response = response.copy()
        while any([key in pagination_response for key in pagination_keys]):
            link_key = pagination_keys[([key in pagination_response for key in pagination_keys]).index(True)]
            pagination_response = self.session.request("GET", pagination_response[link_key], headers=self.headers)
            pagination_response = json.loads(pagination_response.text)['value']
            paginated_df = pd.concat([paginated_df, pd.DataFrame(pagination_response)])

        return paginated_df

    def session_request(self, method, url, headers=None, data=None):
        if headers is None:
            headers = self.headers

        if data is None:
            response = self.session.request(method, url, headers=headers)
        else:
            response = self.session.request(method, url, headers=headers, data=data)

        if response.status_code == 204:
            return pd.DataFrame()
        elif str(response.status_code).startswith('2'):
            response = (json.loads(response.text))
            if 'value' in response:
                response_df = pd.DataFrame(response['value'])
            else:
                response_df = pd.DataFrame([response])

            paginated_response_df = self.paginate(response)
            if len(paginated_response_df) > 0:
                response_df = pd.concat([response_df, paginated_response_df]).reset_index(drop=True)
        else:
            raise Exception(f'Status: {response.status_code} - {response.text}')

        return response_df

    def list_flow_owners(self, flow_id):
        flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/flows/{flow_id}/' \
                   f'owners?api-version=2016-11-01'

        flow_owners_response = self.session_request("GET", flow_url).to_dict(orient='records')
        flow_user_ids = [owner['name'] for owner in flow_owners_response if
                         owner['properties']['principal']['type'] == 'User']

        flow_group_ids = [owner['name'] for owner in flow_owners_response if
                          owner['properties']['principal']['type'] == 'Group']

        return flow_user_ids, flow_group_ids

    def list_graph_accounts(self, account_type, account_ids=None):
        graph_url = None
        if account_type == 'users':
            graph_url = f'https://graph.microsoft.com/v1.0/users?$top=999'
        elif account_type == 'groups':
            graph_url = f'https://graph.microsoft.com/v1.0/groups?$top=999'

        accounts_df = pd.DataFrame()
        if graph_url is not None:
            if account_ids is not None:
                graph_url = graph_url + '&$filter=' + ' or '.join([f'id eq \'{user_id}\'' for user_id in account_ids])

            headers = self.generate_bearer_token(grant_type='client_credentials',
                                                 scope='https://graph.microsoft.com/.default')

            accounts_df = self.session_request("GET", graph_url, headers=headers)

        return accounts_df

    def enrich_owners(self, flows_df):
        accounts_df = pd.DataFrame()
        user_ids = []
        group_ids = []

        flows_df['Owners'] = None
        for i, flow in flows_df.iterrows():
            flow_user_ids, flow_group_ids = self.list_flow_owners(flow['name'])
            flows_df.at[i, 'Owners'] = (flow_user_ids + flow_group_ids)

            user_ids = user_ids + flow_user_ids
            group_ids = group_ids + flow_group_ids

        if len(user_ids) > 0:
            user_ids = list(dict.fromkeys(user_ids))
            batch_steps = math.ceil(len(user_ids) / self.filter_limit)
            for batch in range(batch_steps):
                batch_user_ids = user_ids[batch * self.filter_limit:(batch + 1) * self.filter_limit]
                accounts_df = pd.concat([accounts_df, self.list_graph_accounts('users', batch_user_ids)])

        if len(group_ids) > 0:
            group_ids = list(dict.fromkeys(group_ids))
            batch_steps = math.ceil(len(group_ids) / 15)
            for batch in range(batch_steps):
                batch_group_ids = group_ids[batch * 15:(batch + 1) * 15]
                accounts_df = pd.concat([accounts_df, self.list_graph_accounts('groups', batch_group_ids)])

        if accounts_df.shape[0] > 0:
            flows_df = flows_df.explode('Owners')
            flows_df = flows_df.merge(accounts_df[['displayName', 'id']], how='left',
                                      left_on='Owners',
                                      right_on='id', suffixes=('', '_account'))

            null_account_mask = flows_df['displayName'].isnull()
            flow_name_mask = flows_df.groupby('name')['name'].transform('count') > 1
            flows_df = flows_df[~(null_account_mask & flow_name_mask)]

            flows_df = flows_df[flows_df['displayName'].notna()]
            flows_df = flows_df.groupby(['name', 'id', 'type']).agg({
                'displayName': list,
                'properties': list
            }).reset_index()
            flows_df.rename(columns={'displayName': 'Owners'}, inplace=True)

        return flows_df

    def enrich_run_history(self, flows_df):
        flows_runs_df = pd.DataFrame()
        for i, flow in flows_df.iterrows():
            flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/flows/{flow["name"]}/' \
                       f'runs?api-version=2016-11-01'

            run_info_df = self.session_request("GET", flow_url)
            if run_info_df.shape[0] > 0:
                run_info_df.rename(columns={'properties': 'RunProperties'}, inplace=True)
                run_info_df['ErrorCount'] = run_info_df['RunProperties'].apply(
                    lambda x: x['status'] != 'Succeeded').sum()
                run_info_df['RunCount'] = run_info_df['RunProperties'].count()
                run_info_df['LastRun'] = run_info_df['RunProperties'].apply(lambda x: x['startTime']).max()
                run_info_df['LastRunStatus'] = run_info_df['RunProperties'].apply(lambda x: x['status']).max()
                run_info_df['ErrorMessage'] = run_info_df['RunProperties'].apply(
                    lambda x: x['error']['message'] if 'error' in x else None)

                run_info_df['name'] = flow['name']
                run_info_df = run_info_df.groupby(['name', 'ErrorCount', 'RunCount', 'LastRun', 'LastRunStatus']).agg({
                    'RunProperties': list,
                    'ErrorMessage': list
                }).reset_index()

                run_info_df['ErrorMessage'] = run_info_df['ErrorMessage'].apply(
                    lambda x: [e for e in x if not pd.isna(e)])

                flows_runs_df = pd.concat([flows_runs_df, run_info_df])

        if flows_runs_df.shape[0] > 0:
            flows_df = pd.merge(flows_df, flows_runs_df, how='left', on='name')
            flows_df[['ErrorCount', 'RunCount']] = flows_df[['ErrorCount', 'RunCount']].fillna(0).astype(int)

        return flows_df

    def enrich_connections(self, flows_df):
        flows_connections_df = pd.DataFrame()
        for i, flow in flows_df.iterrows():
            flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/flows/{flow["name"]}/' \
                       f'connections?api-version=2016-11-01'

            connections_df = self.session_request("GET", flow_url)
            if connections_df.shape[0] > 0:
                connections_df.rename(columns={'name': 'ConnectionName'}, inplace=True)
                connections_df['name'] = flow['name']
                connections_df_properties = pd.concat(
                    connections_df.apply(lambda row: pd.json_normalize(row['properties']).assign(name=row['name']),
                                         axis=1).tolist(),
                    ignore_index=True)

                expanded_statuses_df = pd.concat(connections_df_properties.apply(
                    lambda row: pd.json_normalize(row['statuses']).assign(original_index=row.name), axis=1).tolist(),
                                                 ignore_index=True)
                connections_df_properties = connections_df_properties.drop(columns=['statuses'])

                connections_df_properties = connections_df_properties.merge(expanded_statuses_df, left_index=True,
                                                                            right_on='original_index')

                connections_df_properties['ConnectionType'] = connections_df_properties['apiId'].apply(
                    lambda x: x.split('apis/')[1])

                connections_df_properties.rename(columns={'displayName': 'ConnectionAccountName',
                                                          'status': 'ConnectionStatus',
                                                          'lastModifiedTime': 'ConnectionLastModifiedTime'},
                                                 inplace=True)

                property_columns = ['name', 'ConnectionType', 'ConnectionAccountName', 'ConnectionStatus',
                                    'ConnectionLastModifiedTime', 'isDelegatedAuthConnection']
                if 'error.code' in connections_df_properties.columns:
                    connections_df_properties.rename(columns={'error.code': 'ConnectionErrorCode',
                                                              'error.message': 'ConnectionErrorMessage'}, inplace=True)
                    property_columns.extend(['ConnectionErrorCode', 'ConnectionErrorMessage'])

                if 'authenticatedUser.name' in connections_df_properties.columns:
                    connections_df_properties.rename(columns={'authenticatedUser.name': 'AuthenticatedUserName'},
                                                     inplace=True)
                    property_columns.extend(['AuthenticatedUserName'])

                connections_df_properties = connections_df_properties[property_columns]

                null_account_mask = connections_df_properties['AuthenticatedUserName'].isnull()
                flow_name_mask = connections_df_properties.groupby('name')['name'].transform('count') > 1
                connections_df_properties = connections_df_properties[~(null_account_mask & flow_name_mask)]

                grouped_property_columns = {column: list for column in property_columns[1:]}
                connections_df_properties_group = connections_df_properties.groupby(['name']).agg(
                    grouped_property_columns).reset_index()

                connections_df_properties_group['ConnectionsCount'] = connections_df_properties_group[
                    'ConnectionType'].apply(lambda x: len(x))

                flows_connections_df = pd.concat([flows_connections_df, connections_df_properties_group])

        if flows_connections_df.shape[0] > 0:
            flows_df = pd.merge(flows_df, flows_connections_df, how='left', on='name')
            flows_df['ConnectionsCount'] = flows_df['ConnectionsCount'].fillna(0).astype(int)

        return flows_df

    def list_flows(self, enrich=False, enrich_info=False, enrich_owners=False, enrich_run_history=False,
                   enrich_connections=False):
        flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/flows?api-version=2016-11-01'

        flows_df = self.session_request("GET", flow_url)

        if enrich:
            enrich_owners = True
            enrich_info = True
            enrich_run_history = True
            enrich_connections = True

        if enrich_owners:
            flows_df = self.enrich_owners(flows_df)
            flows_df.drop_duplicates(subset=['name'], inplace=True)

        if enrich_info:
            if 'properties' in flows_df.columns:
                flows_info_df = pd.DataFrame()
                flows_list = []
                for i, prop in flows_df[['name', 'properties']].iterrows():
                    flow_info_response = prop['properties']
                    if isinstance(flow_info_response, list) & (len(flow_info_response) > 0):
                        flow_info_response = flow_info_response[0]
                    flow_info = {'name': prop['name']}
                    for key in flow_info_response.keys():
                        if isinstance(flow_info_response[key], (dict, list, bool)):
                            flow_info[key] = [flow_info_response[key]]
                        else:
                            if len(flow_info_response[key]) > 0:
                                flow_info[key] = flow_info_response[key]

                    flows_list.append(flow_info)
                    flows_info_df = pd.DataFrame(flows_list)

                flows_df = pd.merge(flows_df, flows_info_df, on='name', how='left')

        if enrich_run_history:
            flows_df = self.enrich_run_history(flows_df)

        if enrich_connections:
            flows_df = self.enrich_connections(flows_df)

        return flows_df

    def update_flow(self, flow_id, payload):
        flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/' \
                   f'flows/{flow_id}?api-version=2016-11-01'

        # currently no support to patch flow owners, can only be done via flow UI or admin center (09/2023)
        if isinstance(payload, dict):
            if 'properties' not in payload.keys():
                payload = {'properties': payload}
        elif isinstance(payload, pd.DataFrame):
            payload = {'properties': payload.to_dict(orient='records')[-1]}

        flow_patch_response = self.session_request("PATCH", flow_url, data=payload)

        return flow_patch_response

    def delete_flow(self, flow_id):
        flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/' \
                   f'flows/{flow_id}?api-version=2016-11-01'

        flow_delete_response = self.session.request("DELETE", flow_url, headers=self.headers)

        flow_delete_response = json.loads(flow_delete_response.text)

        return flow_delete_response

    def create_flow(self, payload):
        flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/flows?api-version=2016-11-01'

        flow_post_response = self.session_request("POST", flow_url, data=payload)

        return flow_post_response
