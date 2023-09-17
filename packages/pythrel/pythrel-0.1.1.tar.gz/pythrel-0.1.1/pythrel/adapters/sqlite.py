from sqlite3 import Connection, Cursor
from typing import Any, Literal, Union

from pythrel.database import RelQuery
from ..database import RelDatabase, RelQuery
from typing_extensions import TypedDict

class SqliteOptions(TypedDict):
    path: str

class SqliteQuery(RelQuery):
    def select(self, table: str, columns: list[str] | Literal['*'], distinct: bool = False, limit: int = None, into: str = None) -> "SqliteQuery":
        self.query += "SELECT {distinct}{cols}{into} FROM {table}\n".format(
            cols="*" if columns == "*" else ", ".join(columns),
            table=table,
            distinct=" DISTINCT" if distinct else "",
            into=f"INTO {into}" if into else ""
        )
        if limit != None:
            self.waiting.append(f"LIMIT {limit}")
        return self
    
    def where(self, condition: str) -> "SqliteQuery":
        self.query += f"WHERE {condition}\n"
        return self
    
    def having(self, condition: str) -> "SqliteQuery":
        self.query += f"HAVING {condition}\n"
        return self
    
    def order(self, column: Union[str, list[str]], descending: bool = False) -> "SqliteQuery":
        if type(column) == list:
            cols = ", ".join(column)
        else:
            cols = column + ""
        
        self.waiting.insert(0, "ORDER BY {cols} {mode}\n".format(
            cols=cols,
            mode="DESC" if descending else "ASC"
        ))
        return self
    
    def insert(self, table: str, data: Union[list[dict[str, Any]], dict[str, Any]]) -> "SqliteQuery":
        if type(data) == list:
            col_names = list(data[0].keys())
            values = ", ".join(["(" + ", ".join([f"'{record[col]}'" if type(str(record.get(col, "NULL"))) == str and col in record.keys() else str(record.get(col, "NULL")) for col in col_names]) + ")" for record in data])
        else:
            col_names = list(data.keys())
            values = "(" + ", ".join([f"'{data[c]}'" if type(data[c]) == str else str(data[c]) for c in col_names]) + ")"

        self.query += f"INSERT INTO {table} ({', '.join([str(c) for c in col_names])}) VALUES {values}\n"
        return self
    
    def update(self, table: str, data: dict[str, Any]) -> "SqliteQuery":
        self.query += "UPDATE {table} SET {values}\n".format(
            table=table,
            values=", ".join(["{k} = {v}".format(
                k=k,
                v="'" + v + "'" if type(v) == str else v
            ) for k, v in data.items()])
        )
        return self
    
    def delete(self, table: str) -> "SqliteQuery":
        self.query += f"DELETE FROM {table}\n"
        return self
    
    def join(self, table: str, mode: Literal['inner', 'left', 'right', 'full'], on: str) -> "SqliteQuery":
        self.query += "{mode} JOIN {table} ON {on}\n".format(
            mode=mode.upper(),
            table=table,
            on=on
        )
        return self

class SqliteDatabase(RelDatabase):
    def __init__(self, **connection_args: SqliteOptions) -> None:
        super().__init__(connection_args)
        self.connection: Connection = None
        self.cursor: Cursor = None

    def execute(self, query: str, commit: bool = False) -> list[dict[str, Any]]:
        if not self.connection:
            self.connection = Connection(self.connection_args["path"])
        if not self.cursor:
            self.cursor = self.connection.cursor()
        
        result = self.cursor.execute(query)
        description = result.description
        results = result.fetchall()
        if commit:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()
            self.connection = None
            self.cursor = None
        
        return [{description[v][0]: i[v] for v in range(len(i))} for i in results]
    
    def commit(self) -> None:
        if self.connection and self.cursor:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()
            self.connection = None
            self.cursor = None

    def rollback(self) -> None:
        if self.connection and self.cursor:
            self.connection.rollback()
            self.cursor.close()
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    def exists(self, table: str) -> bool:
        return len(self.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")) > 0
    
    def query(self) -> SqliteQuery:
        return SqliteQuery(self)
    
    def create_table(self, name: str, columns: dict[str, str], exist_ok: bool = True, commit: bool = False) -> None:
        if self.exists(name):
            if not exist_ok:
                raise RuntimeError("Table exists")
        else:
            self.execute("CREATE TABLE {name} ({columns});".format(
                name=name,
                columns=", ".join(f"{k} {v}" for k, v in columns.items())
            ), commit=commit)
    

