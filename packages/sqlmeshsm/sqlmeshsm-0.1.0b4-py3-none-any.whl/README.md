# sqlmeshsm

[SQLMesh macros](https://sqlmesh.readthedocs.io/en/stable/concepts/macros/sqlmesh_macros/) used for ❄️ [Dynamic Masking Policies](https://docs.snowflake.com/en/user-guide/security-column-ddm-use) implementation ✏️, and the Snowflake Hooker CLI (`hook`) ⭐

**_List of macros_**:

- `create_masking_policy` ([source](./sqlmeshsm/macros/create_masking_policy.py))
- `apply_masking_policy` ([source](./sqlmeshsm/macros/apply_masking_policy.py))
  
**_Hooks_**:

- `hook drop_masking_policy -c {config.yml} -mp {func}`

## Data Masking Development

### 1. Installation

```bash
pip install sqlmeshsm --upgrade
```

In your `(sqlmesh-project-dir)/macros/__init__.py`, let's import our lib:

```python
from sqlmeshsm import macros
```

### 2. Create masking policy functions

_For example_, the `customer` table needs the following masking policies:

- First Name: mask with `*` except the first 3 characters, fixed length of 10, no masking of `null`
- Last Name: mask with the first character of First Name, no masking of `null`

There are 2 **masking functions**, they **must be created with following requirements**:

- 📂 Files located under `(your-sqlmesh-project)/macros/snow-mask-ddl`
- 🆎 File name format: `{mp_schema}.{mp_function_name}`

```sql
-- /snow-mask-ddl/mp_schema.mp_first_name.sql
CREATE MASKING POLICY IF NOT EXISTS @schema.mp_first_name AS (
    masked_column string
) RETURNS string ->
    LEFT(CASE 
        WHEN masked_column IS NOT NULL THEN LEFT(masked_column, 3)
        ELSE NULL
    END || '**********', 10);
```

```sql
-- /snow-mask-ddl/mp_schema.mp_last_name.sql
CREATE MASKING POLICY IF NOT EXISTS @schema.mp_last_name AS (
    masked_column string,
    first_name_column string
) RETURNS string ->
    CASE 
        WHEN masked_column IS NOT NULL THEN LEFT(first_name_column, 1)
        ELSE NULL
    END;
```

> `@schema` is the keyword to indicate the schema name which matches to the first part of the file name

## 3. Decide to mask model's columns

```sql
/* /models/my_customer_model.sql */
MODEL(
    name my_schema.my_customer_model
    kind FULL
    ...
)

/* REGISTER the masking funcs */
@create_masking_policy(mp_schema.mp_first_name)
@create_masking_policy(mp_schema.mp_last_name)

/* MODEL SQL CODE HERE */

/* USE the masking funcs */
@apply_masking_policy(first_name, mp_schema.mp_first_name)
@apply_masking_policy(my_schema.my_customer_model, last_name, mp_schema.mp_last_name, ['first_name'])
```

Let's plan and apply it now: `sqlmesh plan --select-model my_schema.my_customer_model`

## 4. (Optional) Decide to clean up the masking policies

Let's run the built-in hooks:

```bash
hook drop_masking_policy -c /path/to/sqlmesh/config.yml -mp you_mp_function_name
# for example: hook drop_masking_policy -c tests\macros\config.yaml -mp common.mp_first_name
```

> Try `hook -h` for more options.

**_Voila! Happy Masking 🎉_**

## Contribution

[![buy me a coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?logo=buy-me-a-coffee&logoColor=white&labelColor=ff813f&style=for-the-badge)](https://www.buymeacoffee.com/datnguye)

If you've ever wanted to contribute to this tool, and a great cause, now is your chance!

See the contributing docs [CONTRIBUTING](./CONTRIBUTING.md) for more information.

Our **_Contributors_**:

<a href="https://github.com/datnguye/sqlmesh-snow-mask/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=datnguye/sqlmesh-snow-mask" />
</a>
