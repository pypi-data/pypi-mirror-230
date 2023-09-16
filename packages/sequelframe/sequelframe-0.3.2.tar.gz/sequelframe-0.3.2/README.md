# sequelframe

sequelframe is a Python library that provides an interface for working with data files (CSV or Excel) using SQL queries through SQLite.

## Installation:
To install the library, use:
```python
pip install sequelframe 
```

## Features:
- Load CSV and Excel files into SQLite.
- Execute SQL queries on the loaded data.
- Easily view all data with the show() method.
- Delete the SQLite database file when done with the kill() method.

## Usage:

### Initialization:
To start, initialize the sequelframe with the path to your data file:
```python
from sequelframe import sequelframe
sf = sequelframe("your_file_path.csv")
```

### Run SQL Queries:
Execute SQL queries on the loaded data using:
```python
result = sf.runsql("Your SQL query here")
```

### View Data:
To view all the loaded data:
```python
sf.show()
```

### Cleanup:
To delete the SQLite database file:
```python
sf.kill()
```

## Supported File Types:
- CSV (.csv)
- Excel (.xls, .xlsx)
Note: Unsupported file types will raise a ValueError.

## Examples:

### For a CSV file:
```python
from sequelframe import sequelframe
sf = sequelframe("data.csv")
result = sf.runsql("SELECT * FROM data WHERE some_column = some_value")
sf.show()
sf.kill()
```

### For an Excel file:
```python
from sequelframe import sequelframe
sf = sequelframe("data.xlsx")
result = sf.runsql("SELECT column1, column2 FROM data")
sf.kill()
```
