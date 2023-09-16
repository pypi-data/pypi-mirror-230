# sequelframe
A lightweight library to use SQL with pandas DataFrames. It temporarily saves the DataFrame in an SQLite database, allowing you to run SQL queries against it.

## Installation
```bash
pip install sequelframe
```

## Usage

```python
from sequelframe import sequelframe
```

### Initialization
```python
# Initialize with a CSV or Excel file
db = sequelframe('path_to_file.csv')
```

### Run SQL Queries
```python
# SELECT statement
result = db.runsql('SELECT * FROM data WHERE age > 25')

# INSERT statement
db.runsql('INSERT INTO data (name, age, country) VALUES ("John Doe", 30, "USA")')

# UPDATE statement
db.runsql('UPDATE data SET age = 31 WHERE name = "John Doe"')

# DELETE statement
db.runsql('DELETE FROM data WHERE name = "John Doe"')

# ALTER statement
db.runsql('ALTER TABLE data ADD COLUMN gender TEXT')
```

### Other Functions
```python
# Display all data
db.show()

# Close the connection and remove the temporary SQLite database
db.kill()
```

## Cleaning up
When you're done with the `sequelframe` object, it's recommended to use the `kill` method to clean up the resources.
