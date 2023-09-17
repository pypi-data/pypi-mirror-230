from .adapters import *
from .database import RelDatabase, RelQuery
from pydantic import BaseModel, PrivateAttr
from typing import Callable, Any, Optional, Union, TypeVar

RECORD_LOAD_FUNC = Callable[[RelQuery, dict[str, Any]], RelQuery]
RECORD_SAVE_FUNC = Callable[[RelQuery, "Record"], RelQuery]

class Record(BaseModel):
    _orm: "Pythrel" = PrivateAttr()
    _db_data: Optional[Any] = PrivateAttr(default=None)

    def __init__(self, orm: "Pythrel", db_data: Optional[Any] = None, **data) -> None:
        super().__init__(**data)
        self._orm = orm
        self._db_data = db_data

R = TypeVar("R", bound=Record)

class Pythrel:
    def __init__(self, adapter: RelDatabase) -> None:
        self.adapter = adapter

    def load(self, cls: type[R], func: RECORD_LOAD_FUNC, options: dict[str, Any] = {}, db_data: Optional[Any] = None) -> list[R]:
        raw_results = func(self.adapter.query(), options).execute()
        return [cls(self, db_data=db_data, **record) for record in raw_results]
    
    def load_columns(self, cls: type[R], table: str, columns: Union[str, list[str]], distinct: bool = False, limit: int = None, where: str = None) -> list[R]:
        def load_cols_internal(query: RelQuery, options: dict[str, Any]) -> RelQuery:
            select = query.select(options["table"], options["columns"], distinct=options["distinct"], limit=options["limit"])
            if options["where"]:
                select = select.where(options["where"])
            return select
        return self.load(cls, load_cols_internal, {"table": table, "columns": columns, "distinct": distinct, "limit": limit, "where": where}, db_data={"type": "columns", "table": table})
    
    def load_query(self, cls: type[R], query: RelQuery) -> list[R]:
        results = query.execute()
        return [cls(self, db_data=None, **record) for record in results]
    
    def create(self, record: type[R], table: str, **data) -> R:
        new_record = record(orm=self, db_data={"type": "columns", "table": table}, **data)
        self.adapter.query().insert(table, new_record.dict()).execute(commit=True)
        return new_record
    
    def save(self, record: R, key: str = None):
        if not record._db_data:
            raise AttributeError("Provided record does not contain save data")
        
        if record._db_data["type"] == "columns":
            if not key:
                raise AttributeError("key is required to save column record")
            kv = getattr(record, key, 0)
            self.adapter.query().update(record._db_data["table"], record.dict()).where("{table}.{key} = {value}".format(
                table=record._db_data["table"],
                key=key,
                value=f"'{kv}'" if type(kv) == str else kv
            )).execute(commit=True)
            return
        
        raise TypeError("Unkown record save type: " + record._db_data.get("type", "UNKNOWN"))
    
    def query(self) -> RelQuery:
        return self.adapter.query()

    