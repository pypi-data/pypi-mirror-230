from typing import Any, Union, Literal

class RelQuery:
    def __init__(self, db: "RelDatabase", query: str = "") -> None:
        self.db = db
        self.query = query
        self.waiting = []

    def select(self, table: str, columns: Union[list[str], Literal["*"]], distinct: bool = False, limit: int = None, into: str = None) -> "RelQuery":
        raise NotImplementedError
    
    def where(self, condition: str) -> "RelQuery":
        raise NotImplementedError
    
    def having(self, condition: str) -> "RelQuery":
        raise NotImplementedError
    
    def order(self, column: str, descending: bool = False) -> "RelQuery":
        raise NotImplementedError
    
    def insert(self, table: str, data: Union[list[dict[str, Any]], dict[str, Any]]) -> "RelQuery":
        raise NotImplementedError
    
    def update(self, table: str, data: dict[str, Any]) -> "RelQuery":
        raise NotImplementedError
    
    def delete(self, table: str) -> "RelQuery":
        raise NotImplementedError
    
    def join(self, table: str, mode: Literal["inner", "left", "right", "full"], on: str) -> "RelQuery":
        raise NotImplementedError
    
    def __str__(self) -> str:
        return self.query + "\n".join(self.waiting) + ";"
    
    def execute(self, commit: bool = False) -> list[dict[str, Any]]:
        return self.db.execute(str(self), commit=commit)

class RelDatabase:
    def __init__(self, connection_args: dict = {}) -> None:
        self.connection_args = connection_args

    def execute(self, query: str, commit: bool = False) -> list[dict[str, Any]]:
        raise NotImplementedError
    
    def commit(self) -> None:
        raise NotImplementedError
    
    def rollback(self) -> None:
        raise NotImplementedError
    
    def create_table(self, name: str, columns: dict[str, str], exist_ok: bool = True, commit: bool = False) -> None:
        raise NotImplementedError
    
    def exists(self, table: str) -> bool:
        raise NotImplementedError
    
    def query(self) -> RelQuery:
        raise NotImplementedError