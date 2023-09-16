import os

from sqlmesh.core.macros import MacroEvaluator, macro


@macro()
def create_masking_policy(
    evaluator: MacroEvaluator,
    func,
    ddl_dir=None,
    dry_run=True,
):
    dir = ddl_dir.expression
    if dir is None:
        dir = f"{os.getcwd()}/macros/snow-mask-ddl"
    ddl_file = f"{dir}/{func}.sql"
    func_parts = str(func).split(".")
    if len(func_parts) != 2:
        raise Exception(
            "Function name must be 2 parts e.g. `schema.masking_policy.sql`"
        )

    schema = func_parts[0]
    with open(ddl_file, "r") as file:
        content = file.read()

    sql = ";".join(
        [f"CREATE SCHEMA IF NOT EXISTS {schema}", content.replace("@schema", schema)]
    )
    if dry_run:
        sql = sql.replace("'", "''")
        return f"INSERT INTO common.log (id) VALUES('{sql}')"
    return sql
