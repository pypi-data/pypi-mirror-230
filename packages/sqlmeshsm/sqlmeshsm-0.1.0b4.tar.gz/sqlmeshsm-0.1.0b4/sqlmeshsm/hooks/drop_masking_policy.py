import snowflake.connector
import yaml
from pandas import DataFrame

from sqlmeshsm.hooks.helper import SQLQuery

sqlq = SQLQuery()


def drop_masking_policy(mp_func_name: str, config_path: str):
    """Drop masking policy by a given name

    Args:
        mp_func_name (str): Masking policy function
        config_path (str): Connection config file path
    """
    with open(config_path, "r") as yaml_file:
        config_content = yaml.safe_load(yaml_file)

    config = __parse_sqlmesh_config(config=config_content)
    if not config:
        config = config_content

    # Engine initilization
    connection = snowflake.connector.connect(**config)
    cursor = connection.cursor()

    # Fetch & Unset masking policy references
    cursor.execute(
        sqlq.take("fetch_masking_policy_references", **dict(mp_func_name=mp_func_name))
    )
    columns = DataFrame.from_records(
        iter(cursor), columns=[x[0] for x in cursor.description]
    )

    unset_sql = ""
    for column in columns:
        unset_sql += sqlq.take(
            "unset_masking_policy",
            **dict(
                materialization=column.materialization,
                model=column.model,
                column=column.column,
            )
        )
        cursor.execute(unset_sql)

    # Drop the masking policy
    cursor.execute(
        expressions=sqlq.take("drop_masking_policy", **dict(mp_func_name=mp_func_name))
    )

    # Clean up
    cursor.close()
    connection.close()


def __parse_sqlmesh_config(config: dict):
    """Follow the SQLMesh config.yml file and parse the connection info

    Args:
        config (dict): Config.yml file content

    Returns:
        dict: Config dict or None if failed to parse
    """
    return (
        config.get("gateways", {})
        .get(config.get("default_gateway", ""), {})
        .get("connection")
    )
