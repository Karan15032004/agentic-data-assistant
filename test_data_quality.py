import json
from src.agents.data_quality_agent import _run_data_quality_checks
from src.agents.metadata_agent import _list_tables_raw, _1_get_table_schema

#  Create fake metadata structure
metadata = {
    "database_summary": {
        "tables": []
    }
}

# Get real table name
tables_json = json.loads(_list_tables_raw())
table_name = tables_json["tables"][0]

# Get real schema
schema_json = json.loads(_1_get_table_schema(table_name))

metadata["database_summary"]["tables"].append({
    "table_name": table_name,
    "schema": schema_json["schema"]
})

# Run quality check
result = _run_data_quality_checks(metadata)

print("\nData Quality Output:\n")
print(result)
try:
    parsed = json.loads(result)
    print("\nJSON is valid.")
except:
    print("\nInvalid JSON.")
