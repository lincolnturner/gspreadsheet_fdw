
from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG
from oauth2client.service_account import ServiceAccountCredentials
import gspread

class GspreadsheetFdw(ForeignDataWrapper):
    def __init__(self, fdw_options, fdw_columns):
        """A Google Spreadsheets Foreign Wrapper.
    The following options are required:
    gskey     -- the key from the gsheet URL
    headrow   -- which row of the spreadsheet to take column names from. Defaults to 1.
    keyfile   -- the path (on the postgresql-server!) to the .json file containing the appropriate credentials
                 see https://github.com/burnash/gspread and http://gspread.readthedocs.org/en/latest/oauth2.html ,
                 basically, go to https://console.developers.google.com/
                   make (or choose) a project, choose "Enable or manage APIs", enable "Drive API",
                   choose Credentials, then "New credentials", then "server account key".
                   This will make a new email address ending in gserviceaccount.com
                   Yes, it's roundabout, I can't help it...
                 Then just share your gsheetd with the @...gserviceaccount.com email address.
        """
        super(GspreadsheetFdw, self).__init__(fdw_options, fdw_columns)
        self.columns  = fdw_columns
        self.headrow  = int(fdw_options.get('headrow','1'))
        scopes = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(fdw_options["keyfile"], scopes)
        gc = gspread.authorize(credentials)
        self.wks = gc.open_by_key(fdw_options["gskey"]).sheet1

    def execute(self, quals, columns):
        return self.wks.get_all_records(head=int(self.headrow));

