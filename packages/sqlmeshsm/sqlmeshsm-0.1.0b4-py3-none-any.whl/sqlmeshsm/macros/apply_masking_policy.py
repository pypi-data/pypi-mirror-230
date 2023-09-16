import json

from sqlmesh.core.macros import MacroEvaluator, macro


@macro()
def apply_masking_policy(
    evaluator: MacroEvaluator,
    model,
    column,
    func,
    conditional_columns=[],
    materialization="TABLE",
    dry_run=False,
):
    cond_columns = ",".join([x.name for x in conditional_columns.expressions])
    sql = """
        ALTER {materialization} {model}
        MODIFY COLUMN {column}
        SET MASKING POLICY {func} {conditional_columns} FORCE;
        """.format(
        materialization=materialization,
        model=model,
        column=column,
        func=func,
        conditional_columns=f"USING ({cond_columns})" if cond_columns else "",
    )

    if dry_run:
        sql = sql.replace("'", "''")
        return f"INSERT INTO common.log (id) VALUES('{json.dumps(sql)}')"
    return sql
