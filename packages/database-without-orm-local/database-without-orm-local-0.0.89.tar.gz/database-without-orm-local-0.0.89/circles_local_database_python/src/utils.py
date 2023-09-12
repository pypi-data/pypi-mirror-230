import os


def validate_select_table_name(database_object_name: str) -> None:
    if os.getenv("environment_name") not in ("prod1", "dvlp1") and not database_object_name.endswith("_view"):
        raise Exception("View name must end with '_view' in this environment.")
    
def validate_none_select_table_name(database_object_name: str) -> None:
    if os.getenv("environment_name") not in ("prod1", "dvlp1") and not database_object_name.endswith("_table"):
        raise Exception("Table name must end with '_table' in this environment.")
