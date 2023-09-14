import pandas as pd
import datetime
import re


def build_existing_update_message(existing_message, html_message):
    message_id = existing_message['id']
    year_month_day = datetime.datetime.now().strftime('%Y-%m-%d')
    last_run_time = re.search(f'<td>{year_month_day}(.*)</td>', html_message)
    if last_run_time:
        last_run_time = year_month_day + last_run_time.group(1)
    else:
        last_run_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html_message = existing_message['body.content']
    mentions = existing_message['mentions']
    importance = 'normal'
    if 'Error Count' in existing_message['body.content']:
        find_count = re.search('Error Count:</b>(.*)<br>', existing_message['body.content'])
        if find_count:
            count_number = find_count.group(1)
            new_count = int(count_number) + 1
            find_last_run_time = re.search('Latest RunTime:</b>(.*)<br>', existing_message['body.content'])
            if find_last_run_time:
                html_message = html_message.replace(f'Latest RunTime:</b>{find_last_run_time.group(1)}<br>',
                                                    f'Latest RunTime:</b> {last_run_time}<br>')

                html_message = html_message.replace(f'Error Count:</b>{count_number}<br>',
                                                    f'Error Count:</b> {new_count}<br>')
            else:
                html_message = html_message.replace(f'Error Count:</b>{count_number}<br>',
                                                    f'Latest RunTime:</b> {last_run_time}<br>'
                                                    f'<b>Error Count:</b> {new_count}<br>')

            if int(count_number) >= 3:
                importance = 'high'

    return message_id, html_message, mentions, importance


class TeamsLogging:
    """ Manage Error Logs in Microsoft Teams """

    def __init__(self, teams_connection, vivantio_connection=None):
        if teams_connection is None:
            raise Exception('A connection to the Microsoft Teams class is required to connect to Teams Logging')
        else:
            self.ms_teams_con = teams_connection

        self.vivantio = False
        if vivantio_connection:
            self.vivantio = True
            self.vivantio_con = vivantio_connection

    def upload_message(self, team_name, channel_name, subject, mentions=None, message=None, html_message=None,
                       pipeline=None, section=None, error_time=None, project=None):
        """ Post a message to the channel id passed in """
        if message is None and html_message is None:
            raise Exception('Either message or html_message must be provided')

        if subject is None:
            raise Exception('subject is required')

        if html_message is None:
            message_content = {}
            if project is not None:
                message_content['Project'] = project
            if pipeline is not None:
                message_content['Pipeline'] = pipeline
            if message is not None:
                message_content['ErrorMessage'] = message
            if section is not None:
                message_content['Section'] = section
            if error_time is not None:
                message_content['RunTime'] = error_time
            else:
                message_content['RunTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            html_message = pd.DataFrame.from_dict(message_content, orient='index').T.to_html(index=False)

        team_response_df, status_code = self.ms_teams_con.get_teams(team_name=team_name)
        team_id = team_response_df['id'].values[0]

        channel_response_df, status_code = self.ms_teams_con.get_channel_info(team_id=team_id,
                                                                              channel_name=channel_name)
        channel_id = channel_response_df['id'].values[0]

        exists = False
        existing_message = pd.Series()
        if message is not None:
            exists, existing_message = self.ms_teams_con.check_for_existing_message(message=message, team_id=team_id,
                                                                                    channel_id=channel_id)

        if exists:
            message_id, html_message, mentions, importance = build_existing_update_message(existing_message,
                                                                                           html_message)

            update_message, update_message_status = self.ms_teams_con.update_message(team_id=team_id,
                                                                                     channel_id=channel_id,
                                                                                     message_id=message_id,
                                                                                     message=html_message,
                                                                                     importance=importance,
                                                                                     mentions=mentions)

            return update_message, update_message_status
        else:
            vivantio_ticket_info = None
            if self.vivantio:
                vivantio_ticket_df = self.vivantio_con.create_ticket(title=subject, message=html_message)
                vivantio_ticket_id = vivantio_ticket_df['InsertedItemId'].values[0]
                vivantio_ticket_info = self.vivantio_con.get_ticket(vivantio_ticket_id)

            new_message, new_message_status = self.ms_teams_con.post_message(team_id=team_id, channel_id=channel_id,
                                                                             message=html_message, subject=subject,
                                                                             mentions=mentions,
                                                                             vivantio_ticket=vivantio_ticket_info)

            return new_message, new_message_status
