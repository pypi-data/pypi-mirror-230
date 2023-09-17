# pythrel
Abstract relational ORM system

**WARNING:** This is a small project I built mainly to learn how to interface with a few different kinds of SQL database. If you would like to use this in production, no you don't!

## Documentation:

**Installation:**
> `python3 -m pip install pythrel`

**Basic Usage:**
```python
from pythrel import SqliteDatabase, Pythrel, Record
import secrets
import random

# Create database adapter
db = SqliteDatabase(path="test.db")
db.create_table("customers", {"id": "INTEGER", "customerName": "TEXT", "favorite_number": "REAL"})
db.commit()

# Generate some data
CUSTOMERS = {}
for c in range(500):
    CUSTOMERS[c] = {
        "id": c,
        "customerName": secrets.token_urlsafe(8),
        "favorite_number": random.randint(0, 10000)
    }

# Insert data
db.query().insert("customers", list(CUSTOMERS.values())).execute()
db.commit()

# Connect DB instance to ORM
orm = Pythrel(db)

# Use database table rows as objects
print(orm.load_columns(Customer, "customers", "*")[0].dict())
orm.create(Customer, "customers", id=-10, customerName="John", favorite_number=-69)
john = orm.load_columns(Customer, "customers", "*", where="id < 0")[0]
print(john)
john.favorite_number = 1000
orm.save(john, key="id")
print(orm.load_query(Customer, orm.query().select("customers", "*").where("id < 0"))[0])
```