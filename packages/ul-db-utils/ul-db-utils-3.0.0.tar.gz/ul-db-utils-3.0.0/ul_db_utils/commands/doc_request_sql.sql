SELECT
    current_database() as "db_name",
    pgns.nspname as "schema_name",
    tbl.relname as "table_name",
    obj_description(tbl.oid, 'pg_class') as "table_description",
    ARRAY_AGG(pgattr.attname) as "table_field_name",
    ARRAY_AGG(pgtype.typname) as "table_field_type",
    ARRAY_AGG(col_description(tbl.oid, pgattr.attnum)) as "table_field_description"
FROM pg_class tbl
    LEFT OUTER JOIN pg_catalog.pg_namespace pgns ON pgns.nspname = '{schema_db}'
    LEFT OUTER JOIN pg_attribute pgattr ON pgattr.attrelid = tbl.oid AND pgattr.attnum > 0 AND pgattr.atttypid != 0
    LEFT OUTER JOIN pg_type pgtype ON pgtype.oid = pgattr.atttypid
    WHERE tbl.relnamespace = pgns.oid AND tbl.reltype != 0
GROUP BY
    db_name, schema_name, table_name, table_description
ORDER BY table_name;
