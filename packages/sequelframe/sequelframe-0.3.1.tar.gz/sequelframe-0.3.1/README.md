<sequelframe>
  <installation>
    <pip>pip install sequelframe</pip>
  </installation>
  <features>
    <load>Load CSV and Excel files into SQLite.</load>
    <query>Execute SQL queries on the loaded data.</query>
    <view>Easily view all data with the show() method.</view>
    <delete>Delete the SQLite database file when done with the kill() method.</delete>
  </features>
  <usage>
    <initialization>
      To start, initialize the sequelframe with the path to your data file:
      ```python
      from sequelframe import sequelframe
      sf = sequelframe("your_file_path.csv")
      ```
    </initialization>
    <run-queries>
      Execute SQL queries on the loaded data using:
      ```python
      result = sf.runsql("Your SQL query here")
      ```
    </run-queries>
    <view-data>
      To view all the loaded data:
      ```python
      sf.show()
      ```
    </view-data>
    <cleanup>
      To delete the SQLite database file:
      ```python
      sf.kill()
      ```
    </cleanup>
  </usage>
  <supported-file-types>
    <csv>.csv</csv>
    <excel>.xls, .xlsx</excel>
  </supported-file-types>
  <examples>
    <csv>
      ```python
      from sequelframe import sequelframe
      sf = sequelframe("data.csv")
      result = sf.runsql("SELECT * FROM data WHERE some_column = some_value")
      sf.show()
      sf.kill()
      ```
    </csv>
    <excel>
      ```python
      from sequelframe import sequelframe
      sf = sequelframe("data.xlsx")
      result = sf.runsql("SELECT column1, column2 FROM data")
      sf.kill()
      ```
    </excel>
  </examples>
</sequelframe>
