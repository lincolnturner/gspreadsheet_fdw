from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG
import gdata.spreadsheet.service as gss

# Thanks to https://github.com/yoavaviram/python-google-spreadsheet    
# for working out the row.custom nonsense!

class GspreadsheetFdw(ForeignDataWrapper):
    """A Google Spreadsheets Foreign Wrapper.
    The following options are required:
    key       -- the google spreadsheet key, looks like 45 alphanumerics
    email     -- your google login. Works with domain emails too it seems.
    password  -- your google password. In the clear and all. Sorry!
    """

    def __init__(self, fdw_options, fdw_columns):
        super(GspreadsheetFdw, self).__init__(fdw_options, fdw_columns)
        self.gd_client = gss.SpreadsheetsService()
        self.key                = fdw_options["key"]
        self.gd_client.email    = fdw_options["email"]
        self.gd_client.password = fdw_options["password"]
        self.column_list  = fdw_columns
        self.column_names = fdw_columns.keys()

    def execute(self, quals, columns):
        self.gd_client.ProgrammaticLogin()
        qualstrings = []
        for qual in quals:
            qualstring = qual.field_name+qual.operator+'"'+qual.value+'"'
            qualstrings.append(qualstring)
        query = ' and '.join(qualstrings)
        log_to_postgres("Query string is %s" % query, DEBUG)
        gd_query = gss.ListQuery()
        gd_query.sq = query or None
        feed = self.gd_client.GetListFeed(self.key, query=gd_query)
        for row in feed.entry:
            rowdict = dict([(col, row.custom[col].text) for col in self.column_names])
            yield rowdict
