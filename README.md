# gspreadsheet_fdw
_Multicorn-based PostgreSQL foreign data wrapper for Google Spreadsheets_

Makes your Google Spreadsheets appear as foreign tables in your PostgreSQL database.

## Installation
You need a recent PostgreSQL install (9.1+) and you need to have installed the excellent
[Multicorn](http://multicorn.org/) FDW-in-python framework into PostgreSQL. 

You need the [Google Data binding for python](http://code.google.com/p/gdata-python-client/):

```
pip install gdata
```

Then just clone and install as usual:

```
git clone git://github.com/lincolnturner/gspreadsheet_fdw.git
cd gspreadsheet_fdw
python setup.py install
```

## Example
See file `test.sql`.

Start `psql` and if you haven't used multicorn yet, enable it with:
```sql
CREATE EXTENSION multicorn;
```

Then create the gspreadsheet 'server' with:
```sql
CREATE SERVER multicorn_gspreadsheet FOREIGN DATA WRAPPER multicorn
options (
  wrapper 'gspreadsheet_fdw.GspreadsheetFdw' );
```

### Make a Google Spreadsheet 
Head over to Google Drive and make a Google Spreadsheet which conforms to the 
rules of a 
[list-based feed](https://developers.google.com/google-apps/spreadsheets/#working_with_list-based_feeds). 
In essence:
* Put column names in the first row: untitled columns will not be read
* A blank row terminates the table (data below won't be read)
* Put it in the first (and only) worksheet

Get the Google API 'key' (for want of a better term), which is a 44-character string 
matching regexp `[A-Za-z0-9_]{44}`. It lives between the `/spreadsheets/d/` and possible 
trailing `/edit/blah` in the URL of your Google Spreadsheet.

### Create the foreign table
You can then use 'normal' DDL to create a foreign table with column names that match those 
in your spreadsheet. The gdata API seems to automatically downcase and remove spaces from
the column headers, which is very handy. But probably best not relied on. Give your columns 
simple lowercase names.

```sql
CREATE FOREIGN TABLE staff_gspreadsheet (
  givenname character varying,
  surname   character varying,
  phone     character varying,
  office    character varying
) server multicorn_gspreadsheet options(
  email 'yourname@gmail.com',
  password 'yourB!g$ecreT',
  key '1hoYrcViweamARnxdU1IW-Ivd8hjKHKPzkGSLbKHLeno'
);
```

### Try querying it
You should be able to try this example, the `key` corresponds to a small public test table. 
You will of course need to change the `email` parameter to your Google account and
the password to your Google password. 

Then you should be able to execute queries against your new foreign table:
```sql
SELECT * FROM staff_gspreadsheet;
```
Should produce:
```
   givenname    | surname  | phone | office 
----------------+----------+-------+--------
 Isidior        | Rabi     | 49823 | 26.102
 Chandrasekhara | Raman    | 43803 | 26.108
 Norman         | Ramsey   | 41082 | 26.103
 Eugene         | Wigner   | 40921 | 26.114
 Ettore         | Majorana | 40010 | 26.117
(5 rows)

```

### Qualifiers 
Qualifiers are in essence SQL `WHERE` clauses which are sent down to the foreign data wrapper
to reduce the traffic on the network. For example, executing

```sql
SELECT * FROM staff_gspreadsheet WHERE surname='Ramsey';
```

is translated into a Google list-feed 'query' which returns only that row. At present, anything
more sophisticated than this gets mistranslated (largely due to type-casting issues, i.e. 
everything is a `VARCHAR` right now).

First thing to do in type-aware-qualifiers branch is to selectively quote only character 
and text values and not quote numerical values.

Removing the quals code altogether makes things work better, as without quals processing the 
whole foreign table is always returned but postgres then does the right thing and applies the
WHERE clause once it gets its hands on the data. To be fixed soon.

## Further info

### Materialized views
Google Drive is always available, except when it isn't. Materialized views are a 
wonderful thing and highly recommended for caching your online data in PostgreSQL. 

## Limitations
Very minimal functionality implemented so far.
* Read-only
* All data read as PostgreSQL type `character varying`
* Simple queries only (=, >, < might work up to type-casting issues)

## To do
* Insert, update and delete 
* Sensible type awareness, at least numeric versus text
* Handle quals properly, i.e find out what pg emits and what gdata understand
  (Example: `name LIKE 'Blog%'` emits `name~~'Blog%'` which gdata API doesn't understand)
* Some sort of sane authentication that doesn't involve Google passwords in the data catalog!


