# gw-dsl-parser-py


## Install

```
pip install gw-dsl-parser
```

## Develop

```
pip install ./

python ./scripts/download_wasm.py
```

## Example

```python
from gw_dsl_parser import get_sql_from_payload

payload = {"workflow": [{"type": "view", "query": [{"op": "aggregate", "groupBy": [], "measures": [{"field": "*", "agg": "count", "asFieldKey": "count"}]}]}]}
table_name = "test_table"
sql = get_sql_from_payload(table_name, payload)
```
