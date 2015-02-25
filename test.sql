
-- CREATE EXTENSION multicorn;

-- DROP SERVER multicorn_gspreadsheet CASCADE;

CREATE SERVER multicorn_gspreadsheet FOREIGN DATA WRAPPER multicorn
options (
  wrapper 'gspreadsheet_fdw.GspreadsheetFdw' );

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
