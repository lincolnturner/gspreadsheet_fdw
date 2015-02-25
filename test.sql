
CREATE EXTENSION multicorn;

DROP SERVER multicorn_gspreadsheet CASCADE;

CREATE SERVER multicorn_gspreadsheet FOREIGN DATA WRAPPER multicorn
options (
  wrapper 'gspreadsheet_fdw.GspreadsheetFdw' );

CREATE FOREIGN TABLE test_gspreadsheet (
    timestamp  character varying,
    username   character varying,
    anothercol character varying
) server multicorn_gspreadsheet options(
  email 'myemail@gmail.com'
  password 'B!g$ecreT',
  key '4r0WPTB3AYrJgXzVZUU7aoE8oPsJgRnMzlAri0972hdg'
);
