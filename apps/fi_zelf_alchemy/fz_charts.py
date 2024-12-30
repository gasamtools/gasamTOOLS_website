from sqlalchemy.sql import text
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import logging

hodl = False


def gather_data_chart_1(**input_data):
    global hodl
    from .algo_engine.signal_engine import signal_data_for_crystal
    from .algo_engine.vault_engine import fund_futures_ini_usdt_value

    if not hodl:
        hodl = fund_futures_ini_usdt_value / float(input_data['candle'])

    charts_1_data = {}
    if is_midnight_utc(input_data['timestamp']):

        charts_1_data['timestamp'] = input_data['timestamp']
        charts_1_data['candle'] = input_data['candle']
        charts_1_data['sma'] = signal_data_for_crystal['SMA50'][-1]['value']
        charts_1_data['bot'] = input_data['bank']['total']
        charts_1_data['hodl'] = hodl * float(input_data['candle'])

    return charts_1_data


def record_data_chart_1(db, db_names, data):
    if data:
        query = text(f"""
            INSERT INTO {db_names['charts_1_db']} (timestamp, hodl, bot, sma, candle)
            VALUES (:timestamp, :hodl, :bot, :sma, :candle)
        """)
        db.session.execute(query,
           {"timestamp": data['timestamp'],
            "hodl": data['hodl'],
            "bot": data['bot'],
            "sma": data['sma'],
            'candle': data['candle']
        })
        db.session.commit()


def export_data_chart_1(db, charts_db, trade_db, sheetName):
    from datetime import datetime
    import pytz

    # GET DATA FROM CHART DB
    query = text(f"""
                SELECT timestamp, hodl, bot, sma, candle
                FROM {charts_db}
            """)
    db_data = db.session.execute(query).mappings().fetchall()


    # CONVERT DATA TO SEND TO GOOGLE SHEETS
    db_data_header = [key for key in db_data[0]]
    db_data_values = []
    for item in db_data:
        item = dict(item)
        item['timestamp'] = datetime.fromtimestamp(item['timestamp'], tz=pytz.utc).strftime("%d/%m/%y")
        db_data_values.append([value for key, value in item.items()])
    db_data_ready = [db_data_header] + db_data_values

    # GET DATA FROM TRADE DB
    query = text(f"""
                    SELECT tdp_1, price 
                    FROM {trade_db}
                    WHERE trade_entry = :trade_entry
                    AND trade_action = :trade_action
                    AND trade_status = :trade_status
                """)
    buy_limit_trades = db.session.execute(query, {"trade_entry": "limit", "trade_action": "buy",
                                                  "trade_status": "filled"}).mappings().fetchall()
    if buy_limit_trades:
        db_data_values = []
        for item in buy_limit_trades:
            item = dict(item)
            item['tdp_1'] = int(item['tdp_1']) + 86400
            item['tdp_1'] = datetime.fromtimestamp(item['tdp_1'], tz=pytz.utc).strftime("%d/%m/%y")
            db_data_values.append([value for key, value in item.items()])


    # COMBINE BOTH DATA LISTS
    for index, item in enumerate(db_data_ready):
        if index == 0:
            item.append('buy_trade')
        else:
            item.append('')
        for subitem in db_data_values:
            if item[0] == subitem[0]:
                item[5] = subitem[1]

    #print(db_data_ready)


    # SEND DATA TO GOGGLE SHEETS
    spreadsheet_id = "1O-YFDcM4lxmT5r9LzsBWBuLZ1FB-at6iHIQz9B-TR_A"
    sheets_api = GoogleSheetsAPI(spreadsheet_id)
    sheets_api.authenticate()
    sheets_api.write_range_safe(f"{sheetName}!A1:F{len(db_data_ready)}", db_data_ready)


def is_midnight_utc(unix_timestamp):
    from datetime import datetime, time
    import pytz
    # Convert Unix timestamp to UTC datetime
    dt = datetime.fromtimestamp(unix_timestamp, tz=pytz.UTC)
    return dt.hour == 0 and dt.minute == 0


class GoogleSheetsAPI:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = None
        self.service = None
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        # Set up logging
        # logging.basicConfig(level=logging.DEBUG)
        # self.logger = logging.getLogger('GoogleSheetsAPI')

    def authenticate(self):
        """Handle the authentication process with Google Sheets API."""
        token_path = os.path.join(self.current_dir, 'token.pickle')
        credentials_path = os.path.join(self.current_dir, 'credentials.json')

        # self.logger.debug(f"Looking for credentials at: {credentials_path}")
        # self.logger.debug(f"Token path: {token_path}")

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"credentials.json not found at {credentials_path}")

        if os.path.exists(token_path):
            # self.logger.debug("Found existing token, attempting to load...")
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # self.logger.debug("Refreshing expired credentials...")
                self.creds.refresh(Request())
            else:
                # self.logger.debug("Starting new OAuth2 flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES)

                try:
                    self.creds = flow.run_local_server(port=0)
                    # self.logger.debug(f"Successfully authenticated using port {port}")
                except Exception as e:
                    raise Exception("Failed to authenticate with all ports")

            # self.logger.debug("Saving new token...")
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        # self.logger.debug("Building service...")
        self.service = build('sheets', 'v4', credentials=self.creds)
        # self.logger.debug("Authentication complete!")

    def read_range(self, range_name):
        """Read data from specified range."""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            return result.get('values', [])
        except Exception as e:
            print(f"Error reading range: {e}")
            return None

    def write_range(self, range_name, values):
        """Write data to specified range."""
        try:
            body = {'values': values}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body).execute()
            return result
        except Exception as e:
            print(f"Error writing to range: {e}")
            return None

    def append_values(self, range_name, values):
        """Append data to specified range."""
        try:
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body).execute()
            return result
        except Exception as e:
            print(f"Error appending values: {e}")
            return None

    def get_sheets(self):
        """Get all sheets in the spreadsheet."""
        try:
            sheets = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute().get('sheets', [])
            return [sheet['properties']['title'] for sheet in sheets]
        except Exception as e:
            #self.logger.error(f"Error getting sheets: {e}")
            return None

    def create_sheet(self, sheet_name):
        """Create a new sheet with the specified name."""
        try:
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            #self.logger.debug(f"Created sheet: {sheet_name}")
            return True
        except Exception as e:
            #self.logger.error(f"Error creating sheet: {e}")
            return False

    def write_range_safe(self, range_name, values):
        """Write data to specified range, creating the sheet if it doesn't exist."""
        # Extract sheet name from range (e.g., "Sheet4!A1:C3" -> "Sheet4")
        sheet_name = range_name.split('!')[0]

        # Check if sheet exists
        existing_sheets = self.get_sheets()
        if sheet_name not in existing_sheets:
            #self.logger.debug(f"Sheet {sheet_name} not found. Creating it...")
            if not self.create_sheet(sheet_name):
                return None

        # Write the data
        return self.write_range(range_name, values)
