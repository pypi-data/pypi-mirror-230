import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class AddRowActionBuilder:
    def __init__(self):
        self._instance = None

    def set_spreadsheet_id(self, spreadsheet_id):
        self._get_instance().spreadsheet_id = spreadsheet_id
        return self

    def set_sheet_id(self, sheet_id):
        self._get_instance().sheet_id = sheet_id
        return self

    def set_credentials(self, credentials):
        self._get_instance().credentials = credentials
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = AddRowAction()
        return self._instance


class AddRowAction:
    def __init__(self):
        self.spreadsheet_id = None
        self.sheet_id = None
        self.credentials = None

    def execute(self, *args):
        if not (self.spreadsheet_id and self.sheet_id and self.credentials):
            raise Exception(
                "Incomplete setup: Make sure to set spreadsheet_id, sheet_id, and credentials."
            )

        # Initialize the Sheets API client
        service = build("sheets", "v4", credentials=self.credentials)

        # Prepare the new row data
        values = [list(args)]  # Convert to a 2D array as the API expects this format

        # Create the request body
        body = {"values": values}

        # Update the sheet
        sheet_range = (
            f"{self.sheet_id}!A1"  # Change this based on where you want to insert
        )
        request = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_range,
                body=body,
                valueInputOption="USER_ENTERED",  # Use 'USER_ENTERED' if you want the values to be parsed by Sheets
            )
        )

        # Execute the request
        response = request.execute()
        return response

    @staticmethod
    def prepare(data):
        builder = AddRowActionBuilder()
        return (
            builder.set_spreadsheet_id(data["spreadsheet_id"])
            .set_sheet_id(data["sheet_id"])
            .set_credentials(data["credentials"])
            .build()
        )


class AddRowsBulkActionBuilder:
    def __init__(self):
        self._instance = None

    def set_spreadsheet_id(self, spreadsheet_id):
        self._get_instance().spreadsheet_id = spreadsheet_id
        return self

    def set_sheet_id(self, sheet_id):
        self._get_instance().sheet_id = sheet_id
        return self

    def set_credentials(self, credentials):
        self._get_instance().credentials = credentials
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = AddRowsBulkAction()
        return self._instance


class AddRowsBulkAction:
    def __init__(self):
        self.spreadsheet_id = None
        self.sheet_id = None
        self.credentials = None

    def execute(self, rows):
        if not (self.spreadsheet_id and self.sheet_id and self.credentials):
            raise Exception(
                "Incomplete setup: Make sure to set spreadsheet_id, sheet_id, and credentials."
            )

        service = build("sheets", "v4", credentials=self.credentials)

        # Prepare the new row data
        values = rows  # Assumes rows is a 2D array

        # Create the request body
        body = {"values": values}

        sheet_range = f"{self.sheet_id}!A1"

        request = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_range,
                body=body,
                valueInputOption="USER_ENTERED",
            )
        )

        response = request.execute()
        return response

    @staticmethod
    def prepare(data):
        builder = AddRowsBulkActionBuilder()
        return (
            builder.set_spreadsheet_id(data["spreadsheet_id"])
            .set_sheet_id(data["sheet_id"])
            .set_credentials(data["credentials"])
            .build()
        )


class UpdateRowActionBuilder:
    def __init__(self):
        self._instance = None

    def set_spreadsheet_id(self, spreadsheet_id):
        self._get_instance().spreadsheet_id = spreadsheet_id
        return self

    def set_sheet_id(self, sheet_id):
        self._get_instance().sheet_id = sheet_id
        return self

    def set_credentials(self, credentials):
        self._get_instance().credentials = credentials
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = UpdateRowAction()
        return self._instance


class UpdateRowAction:
    def __init__(self):
        self.spreadsheet_id = None
        self.sheet_id = None
        self.credentials = None

    def execute(self, row_number, *args):
        if not (self.spreadsheet_id and self.sheet_id and self.credentials):
            raise Exception(
                "Incomplete setup: Make sure to set spreadsheet_id, sheet_id, and credentials."
            )

        # Initialize the Sheets API client
        service = build("sheets", "v4", credentials=self.credentials)

        # Prepare the new row data
        values = [list(args)]

        # Create the request body
        body = {"values": values}

        # Update the sheet
        sheet_range = f"{self.sheet_id}!A{row_number}"
        request = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_range,
                body=body,
                valueInputOption="USER_ENTERED",
            )
        )

        # Execute the request
        response = request.execute()
        return response

    @staticmethod
    def prepare(data):
        builder = UpdateRowActionBuilder()
        return (
            builder.set_spreadsheet_id(data["spreadsheet_id"])
            .set_sheet_id(data["sheet_id"])
            .set_credentials(data["credentials"])
            .build()
        )


class GetRowsActionBuilder:
    def __init__(self):
        self._instance = None

    def set_spreadsheet_id(self, spreadsheet_id):
        self._get_instance().spreadsheet_id = spreadsheet_id
        return self

    def set_sheet_id(self, sheet_id):
        self._get_instance().sheet_id = sheet_id
        return self

    def set_credentials(self, credentials):
        self._get_instance().credentials = credentials
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = GetRowsAction()
        return self._instance


class GetRowsAction:
    def __init__(self):
        self.spreadsheet_id = None
        self.sheet_id = None
        self.credentials = None

    def execute(self, starting_row_number: int, ending_row_number: int):
        if not (self.spreadsheet_id and self.sheet_id and self.credentials):
            raise Exception(
                "Incomplete setup: Make sure to set spreadsheet_id, sheet_id, and credentials."
            )

        # Initialize the Sheets API client
        service = build("sheets", "v4", credentials=self.credentials)

        # Define the range to fetch rows
        sheet_range = f"{self.sheet_id}!A{starting_row_number}:Z{ending_row_number}"

        # Fetch rows from Google Sheet
        request = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_range,
            )
        )

        # Execute the request
        response = request.execute()
        return response.get("values", [])

    @staticmethod
    def prepare(data):
        builder = GetRowsActionBuilder()
        return (
            builder.set_spreadsheet_id(data["spreadsheet_id"])
            .set_sheet_id(data["sheet_id"])
            .set_credentials(data["credentials"])
            .build()
        )


creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# If there are no (valid) credentials available, prompt the user to log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

prepare_data = {
    "spreadsheet_id": "1AfQb-zXEQyYf6mKveV2-NCBGPSKqV_RVFRpBIAq7h2o",
    "sheet_id": "Sheet1",
    "credentials": creds,
}

AnotherSlugName = UpdateRowAction.prepare(prepare_data)
GetRowSlug = GetRowsAction.prepare(prepare_data)


print("Output:")
print(GetRowSlug.execute(1, 1))
