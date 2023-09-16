import json
import re
from ast import literal_eval
from collections import Counter
from datetime import timedelta
from decimal import Decimal
from functools import lru_cache, total_ordering
from textwrap import dedent
from typing import Dict, List, Set, Union

import sqlglot
from more_itertools import unique_everseen

from kolo.django_schema import verbose_name


DATABASES = {
    "postgresql": "postgres",
}


UUID_REPR_REGEX = re.compile(
    r"UUID\(\'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\'\)"
)
DECIMAL_REPR_REGEX = re.compile(r"Decimal\('(\d+.?\d+?)'\)")
TIMEDELTA_REPR_REGEX = re.compile(
    r"datetime.timedelta\((?:days=(\d+),? ?)?(?:seconds=(\d+),? ?)?(?:microseconds=(\d+))?\)"
)
TIMEDELTA_STR_REGEX = re.compile(r"(\d+) days (\d+)\.(\d+) seconds")
TIMEDELTA_MICROSECONDS_REGEX = re.compile(r"\d+")


def is_auto_now(field):
    django_field = field.schema["django_field"]
    if django_field not in (
        "django.db.models.fields.DateTimeField",
        "django.db.models.fields.DateField",
    ):
        return False
    return field.schema["auto_now"] or field.schema["auto_now_add"]


def parse_value(value, column_schema):
    if value is None:
        return None
    if column_schema["django_field"] == "django.db.models.fields.UUIDField":
        uuid_match = UUID_REPR_REGEX.match(str(value))
        if uuid_match:
            value = uuid_match[1]
    elif column_schema["django_field"] == "django.db.models.fields.json.JSONField":
        try:
            value = json.loads(value)
        except json.decoder.JSONDecodeError:
            pass
    elif column_schema["django_field"] == "django.db.models.fields.DecimalField":
        decimal_match = DECIMAL_REPR_REGEX.match(str(value))
        if decimal_match:
            value = Decimal(decimal_match[1])
    elif column_schema["django_field"] == "django.db.models.fields.DurationField":
        if isinstance(value, str):
            timedelta_match = TIMEDELTA_REPR_REGEX.match(value)
            duration_match = TIMEDELTA_STR_REGEX.match(value)
            microseconds_match = TIMEDELTA_MICROSECONDS_REGEX.match(value)
            if timedelta_match:
                groups = [int(g) if g else 0 for g in timedelta_match.groups()]
                value = timedelta(
                    days=groups[0], seconds=groups[1], microseconds=groups[2]
                )
            elif duration_match:
                groups = duration_match.groups()  # type: ignore
                value = timedelta(
                    days=int(groups[0]),
                    seconds=int(groups[1]),
                    microseconds=int(groups[2]),
                )
            elif microseconds_match:  # pragma: no branch
                value = timedelta(microseconds=int(microseconds_match.group()))
        else:
            value = timedelta(microseconds=value)
    return value


class TooComplicatedError(Exception):
    pass


class AssertInsert:
    def __init__(self, variable_name, model, fields, import_path=None, query=None):
        self.variable_name = variable_name
        self.model = model
        self.fields = fields
        self.query = query
        self.import_path = import_path

    @classmethod
    def from_raw(cls, fields, query, table_schema, names, primary_key):
        module = table_schema["model_module"]
        model = table_schema["model_name"]
        verbose_name = table_schema["verbose_name"]
        variable_name = names.next_variable_name(
            verbose_name, primary_key.name, primary_key.value_repr
        )
        return cls(
            variable_name, f"{model}", fields, f"from {module} import {model}", query
        )

    def update_fields(self, names, schema):
        fields = []
        for field in self.fields:
            if field.schema["primary_key"]:
                continue  # pragma: no cover
            if field.schema["django_field"] == "django.db.models.fields.DateTimeField":
                continue  # pragma: no cover
            if field.schema["django_field"] == "django.db.models.fields.json.JSONField":
                continue  # pragma: no cover
            if field.skip_default():
                continue

            if field.schema["is_relation"]:
                related_model = field.schema["related_model"]
                if related_model is None:
                    fields.append(field)
                    continue
                verbose_name = schema[related_model]["verbose_name"]
                related_pk = field.schema["related_pk"]
                try:
                    field.value_repr = field.value = names.names[
                        (verbose_name, related_pk, field.value_repr)
                    ]
                except KeyError:  # pragma: no cover
                    pass

            fields.append(field)
        self.fields = fields

    def __eq__(self, other):
        if not isinstance(other, AssertInsert):
            return NotImplemented  # pragma: no cover
        return (self.variable_name, self.model, self.fields) == (
            other.variable_name,
            other.model,
            other.fields,
        )

    def __repr__(self):
        return dedent(  # pragma: no cover
            f"""\
            AssertInsert(
                "{self.variable_name}",
                "{self.model}",
                {self.fields},
            )"""
        )

    def unique_fields(self):
        unique = []
        rest = []
        for field in self.fields:
            if field.schema.get("has_unique", False):
                unique.append(field)
            else:
                rest.append(field)
        return unique, rest

    def foreign_keys(self):
        foreign = []
        rest = []
        for field in self.fields:
            if field.schema["is_relation"]:
                foreign.append(field)
            else:
                rest.append(field)
        return foreign, rest

    def get_template_parts(self, fields):
        yield f"{self.variable_name} = {self.model}.objects.get("
        for field in fields:
            yield f"{field.name}={field.value_repr},"
        yield ")"

    def get_fields(self):
        fields, rest = self.unique_fields()
        if not fields:
            fields, rest = self.foreign_keys()
        return fields, rest

    @property
    def template_parts(self):
        fields, rest = self.get_fields()

        yield from self.get_template_parts(fields)

        for field in rest:
            yield field.assert_equal_template(self.variable_name)

    @property
    def pytest_template_parts(self):
        fields, rest = self.get_fields()

        yield from self.get_template_parts(fields)

        for field in rest:
            yield field.assert_equal_template_pytest(self.variable_name)


class AssertUpdate:
    def __init__(self, variable_name, model, table, fields, query=None):
        self.variable_name = variable_name
        self.model = model
        self.table = table
        self.fields = fields
        self.query = query

    def __repr__(self):
        return dedent(
            f"""\
            AssertUpdate(
                "{self.variable_name}",
                "{self.model}",
                "{self.table}",
                {self.fields},
            )"""
        )

    def __eq__(self, other):
        if not isinstance(other, AssertUpdate):
            return NotImplemented  # pragma: no cover
        return (self.variable_name, self.fields) == (other.variable_name, other.fields)

    def update_fields(self, names, schema):
        fields = []
        for field in self.fields:
            if field.schema["primary_key"]:
                continue  # pragma: no cover
            if field.schema["django_field"] == "django.db.models.fields.DateTimeField":
                continue  # pragma: no cover
            if field.schema["django_field"] == "django.db.models.fields.json.JSONField":
                continue  # pragma: no cover

            if field.schema["is_relation"]:
                related_model = field.schema["related_model"]
                verbose_name = schema[related_model]["verbose_name"]
                related_pk = field.schema["related_pk"]
                try:
                    field.value_repr = field.value = names.names[
                        (verbose_name, related_pk, field.value_repr)
                    ]
                except KeyError:  # pragma: no cover
                    pass
                else:
                    field.name = field.schema["field_name"]

            fields.append(field)

        for name, schema in schema[self.table]["fields"].items():
            if schema["gfk_object_id_field"]:
                fields = collect_gfk(fields, name, schema, names)
        self.fields = fields

    @property
    def template_parts(self):
        if not self.fields:
            return
        yield f"{self.variable_name}.refresh_from_db()"
        for field in self.fields:
            yield field.assert_equal_template(self.variable_name)

    @property
    def pytest_template_parts(self):
        if not self.fields:
            return
        yield f"{self.variable_name}.refresh_from_db()"
        for field in self.fields:
            yield field.assert_equal_template_pytest(self.variable_name)


class AssertDelete:
    def __init__(self, model, fields, query=None):
        self.model = model
        self.fields = fields
        self.query = query

    def __repr__(self):
        return dedent(
            f"""\
            AssertDelete(
                "{self.model}",
                {self.fields},
            )"""
        )

    def __eq__(self, other):
        if not isinstance(other, AssertDelete):
            return NotImplemented  # pragma: no cover
        return (self.model, self.fields) == (other.model, other.fields)

    def update_fields(self, names, schema):
        pass

    @property
    def template_parts(self):
        yield f"self.assertFalse({self.model}.objects.filter("
        for field in self.fields:
            yield f"{field.name}={field.value_repr},"
        yield ").exists())"

    @property
    def pytest_template_parts(self):
        yield f"assert not {self.model}.objects.filter("
        for field in self.fields:
            yield f"{field.name}={field.value_repr},"
        yield ").exists()"


class DjangoCreate:
    def __init__(
        self,
        table,
        model,
        primary_key,
        values,
        variable_name,
        import_path=None,
        query=None,
    ):
        self.table = table
        self.model = model
        self.primary_key = primary_key
        self.values = values
        self.import_path = import_path
        self.query = query
        self.variable_name = variable_name

    @classmethod
    def from_raw(cls, table, values, query, schema_data, names):
        module = schema_data[table]["model_module"]
        model = schema_data[table]["model_name"]
        values = tuple(values)
        primary_key = find_pk(values)
        verbose_name = schema_data[table]["verbose_name"]
        variable_name = names.next_variable_name(
            verbose_name, primary_key.name, primary_key.value_repr
        )
        return cls(
            table,
            f"{model}",
            primary_key,
            values,
            variable_name,
            f"from {module} import {model}",
            query,
        )

    def update_fields(self, names, schema):
        fields = self.values
        for name, field_schema in schema[self.table]["fields"].items():
            if field_schema["gfk_object_id_field"]:
                fields = collect_gfk(fields, name, field_schema, names)

        updated_fields = []
        for field in fields:
            if field.schema["primary_key"]:
                continue
            if field.schema["null"] and field.value is None:
                continue
            if is_auto_now(field):
                continue
            if field.skip_default():
                continue
            if field.schema["is_relation"]:
                related_model = field.schema["related_model"]
                if related_model is None:
                    updated_fields.append(field)
                    continue  # Generic Foreign Key
                verbose_name = schema[related_model]["verbose_name"]
                related_pk = field.schema["related_pk"]
                try:
                    field.value_repr = field.value = names.names[
                        (verbose_name, related_pk, field.value_repr)
                    ]
                except KeyError:
                    field.name = field.schema["field_attname"]
            updated_fields.append(field)

        self.values = tuple(updated_fields)

    def __eq__(self, other):
        if not isinstance(other, DjangoCreate):
            return NotImplemented
        return (self.table, self.model, self.values, self.variable_name) == (
            other.table,
            other.model,
            other.values,
            other.variable_name,
        )

    def __hash__(self):
        return hash((self.table, self.model, self.values, self.variable_name))

    def __repr__(self):
        return dedent(
            f"""\
            DjangoCreate(
                "{self.table}",
                "{self.model}",
                {self.primary_key},
                {self.values},
                "{self.variable_name}",
            )"""
        )

    @property
    def template_parts(self):
        yield f"{self.variable_name}, _created = {self.model}.objects.get_or_create("
        for field in self.values:
            yield f"{field.name}={field.value_repr},"
        defaults = {self.primary_key.name: self.primary_key.raw_value}
        yield f"defaults={defaults},"
        yield ")"


@total_ordering
class DjangoField:
    def __init__(self, name, column_name, value, schema=None):
        self.name = name
        self.column_name = column_name
        self.value_repr = repr(value)
        self.raw_value = value
        self.value = repr(value) if isinstance(value, str) else value
        self.schema = schema

    @classmethod
    def from_column(cls, column, value, table_schema):
        field_schema = table_schema["fields"][column.name]
        name = field_schema["field_name"]
        value = parse_value(value, field_schema)
        return cls(name, column.name, value, field_schema)

    @classmethod
    def from_identifier(cls, identifier, value, table_schema):
        field_schema = table_schema["fields"][identifier.name]
        if isinstance(value, sqlglot.expressions.Null):
            value = None
        elif isinstance(value, sqlglot.expressions.Boolean):
            value = value.this
        elif isinstance(value, sqlglot.expressions.Cast):
            value = value.name
        elif isinstance(value, sqlglot.expressions.Anonymous):
            value = str(value)
        elif value.is_string:
            value = value.name
        else:
            value = literal_eval(value.name)
        value = parse_value(value, field_schema)
        return cls(field_schema["field_name"], identifier.name, value, field_schema)

    @classmethod
    def from_eq(cls, eq, schema_fields):
        name = eq.left.name
        right = eq.right
        if isinstance(right, sqlglot.expressions.Literal):
            value = right.name
        elif isinstance(right, sqlglot.expressions.Boolean):
            value = right.this
        elif isinstance(right, sqlglot.expressions.Cast) and right.name:
            value = right.name
            # TODO: Do something reasonable with `right.to`
        elif isinstance(right, sqlglot.expressions.Paren):
            raise TooComplicatedError()
        else:
            raise TooComplicatedError()  # pragma: no cover
        field_schema = schema_fields[name]
        value = parse_value(value, field_schema)
        return cls(field_schema["field_attname"], name, value, field_schema)

    def __eq__(self, other):
        return (self.name, self.column_name, self.value) == (
            other.name,
            other.column_name,
            other.value,
        )

    def __lt__(self, other) -> bool:
        if self.name == other.name:
            if self.value is None:
                return False
            if other.value is None:
                return True
            return repr(self.value) < repr(other.value)
        return self.name < other.name

    def __hash__(self):
        return hash((self.name, self.column_name, self.value))

    def __repr__(self):
        return f'DjangoField("{self.name}", "{self.column_name}", {self.value})'

    def assert_equal_template(self, variable_name):
        return f"self.assertEqual({variable_name}.{self.name}, {self.value_repr})"

    def assert_equal_template_pytest(self, variable_name):
        return f"assert {variable_name}.{self.name} == {self.value_repr}"

    def skip_default(self):
        if "default" not in self.schema:
            return False

        default_schema = self.schema["default"]
        if repr(default_schema["value"]) == self.value_repr:
            return True

        if "type" not in default_schema:
            return False

        field_type = default_schema["type"]
        value = default_schema["value"]
        if field_type == "Decimal" and self.value == Decimal(value):
            return True
        if field_type == "timedelta" and self.value == timedelta(  # pragma: no branch
            **value
        ):
            return True
        return False


class DjangoQuery:
    def __init__(self, table, query):
        self.table = table
        self.query = query

    def __repr__(self):
        return f'DjangoQuery("{self.table}", {self.query})'

    def __eq__(self, other):
        return (self.table, self.query) == (
            other.table,
            other.query,
        )  # pragma: no cover

    def update_fields(self, names, schema):
        pass


class VariableNames:
    def __init__(self):
        self.counts: Counter = Counter()
        self.names = {}

    def next_variable_name(self, verbose_name, field_name, field_repr):
        full_key = verbose_name, field_name, field_repr
        try:
            return self.names[full_key]
        except KeyError:
            pass

        key = verbose_name, field_name
        self.counts[key] += 1
        suffix = self.counts[key]
        if suffix == 1:
            name = verbose_name
        else:
            name = f"{verbose_name}_{suffix}"
        self.names[full_key] = name
        return name


def build_insert_assert_fields(columns, table_schema, names):
    fields = []
    for identifier, value in columns:
        field = DjangoField.from_identifier(identifier, value, table_schema)
        django_field = table_schema["fields"][field.column_name]["django_field"]
        if django_field == "django.db.models.fields.DateTimeField":
            continue
        fields.append(field)

    for name, schema in table_schema["fields"].items():
        if schema["gfk_object_id_field"]:
            fields = collect_gfk(fields, name, schema, names)
    return fields


def collect_gfk(fields, name, schema, names):
    try:
        from django.contrib.contenttypes.models import ContentType
    except ImportError:  # pragma: no cover
        return fields

    content_type_field = None
    object_id_field = None

    for field in fields:
        if field.schema["field_name"] == schema["gfk_content_type_field"]:
            content_type_field = field
        elif field.schema["field_name"] == schema["gfk_object_id_field"]:
            object_id_field = field

    if content_type_field is None or object_id_field is None:
        return fields  # pragma: no cover

    try:
        content_type = ContentType.objects.get(pk=content_type_field.raw_value)
    except ContentType.DoesNotExist:  # pragma: no cover
        return fields

    model = content_type.model_class()
    value = names.next_variable_name(
        verbose_name(model),
        model._meta.pk.attname,  # type: ignore
        object_id_field.raw_value,
    )
    gfk_field = DjangoField(
        name=name,
        column_name=name,
        value=value,
        schema=schema,
    )
    gfk_field.value_repr = gfk_field.value = value
    collected = []
    for field in fields:
        if field == content_type_field or field == object_id_field:
            continue
        collected.append(field)
    collected.append(gfk_field)
    return collected


def build_update_assert_fields(columns, schema_fields, names):
    fields = []
    for eq in columns:
        if not isinstance(eq, sqlglot.expressions.EQ):
            continue
        try:
            field = DjangoField.from_eq(eq, schema_fields)
        except TooComplicatedError:
            continue
        django_field = schema_fields[field.column_name]["django_field"]
        if django_field == "django.db.models.fields.DateTimeField":
            continue
        if field.skip_default():
            continue
        fields.append(field)
    return fields


def build_delete_lookup_fields(where, table_schema):
    fields = []
    if isinstance(where.this, sqlglot.expressions.In):  # pragma: no branch
        for literal in where.this.expressions:
            field = DjangoField.from_identifier(where.this.this, literal, table_schema)
            fields.append(field)
    return fields


def find_pk(fields):
    for field in fields:
        if field.schema["primary_key"]:
            return field
    return None  # pragma: no cover


def make_table_sort_key(schema_data):
    tables = {}
    for table, data in schema_data.items():
        foreign_keys = []
        for field in data["fields"].values():
            if field["is_relation"] and not field["null"] and field["related_model"]:
                foreign_keys.append(field["related_model"])
        tables[table] = foreign_keys

    @lru_cache(maxsize=None)
    def table_depth(table):
        related_tables = tables[table]

        if len(related_tables) == 0:
            return 0
        return max(table_depth(related) for related in related_tables) + 1

    def sort_key(create):
        if isinstance(create, DjangoCreate):
            return (table_depth(create.table), create.table, create.values)
        return (table_depth(create.table), create.table)

    return sort_key


def parse_columns(columns, row, schema_data):
    columns_by_table: Dict[str, List[DjangoField]] = {}
    for column, value in zip(columns, row):
        if not isinstance(column, sqlglot.exp.Column):
            continue

        table_schema = schema_data[column.table]
        field = DjangoField.from_column(column, value, table_schema)
        columns_by_table.setdefault(column.table, []).append(field)
    return columns_by_table


AnyAssert = Union[DjangoQuery, AssertDelete, AssertInsert, AssertUpdate]


def parse_sql_queries(sql_queries, schema_data):
    names = VariableNames()
    # each select needs to become an insert
    inserts = []
    imports = set()
    asserts: List[AnyAssert] = []
    seen_mutations: Dict[str, Set[str]] = {}
    for query in sql_queries:
        if query["query_data"] is None or query["query"] is None:
            continue

        database = query["database"]
        database = DATABASES.get(database, database)
        try:
            parsed_query = sqlglot.parse_one(query["query"], read=database)
        except sqlglot.errors.ParseError as e:  # pragma: no cover
            print("# Error parsing query:")
            print(f'# {query["query"]}')
            print(f"# {e.errors}")
            continue

        if isinstance(parsed_query, sqlglot.exp.Select):
            columns = [column for (_key, column) in parsed_query.iter_expressions()]
            for batch in query["query_data"]:
                # Skip queries with no columns, eg .count(), .exists()
                if not any(
                    isinstance(column, sqlglot.exp.Column) for column in columns
                ):
                    continue
                for row in batch:
                    columns_by_table = parse_columns(columns, row, schema_data)

                    for table, row in columns_by_table.items():
                        pk = find_pk(row)
                        if pk is None:
                            inserts.append(DjangoQuery(table, query))
                        elif pk.value_repr in seen_mutations.setdefault(table, set()):
                            continue
                        else:
                            create = DjangoCreate.from_raw(
                                table, row, query, schema_data, names
                            )
                            if create.primary_key.raw_value is None:
                                continue
                            inserts.append(create)
                            imports.add(create.import_path)
        else:
            _table = parsed_query.find(sqlglot.exp.Table)
            if _table is None:
                continue  # pragma: no cover
            table_name = _table.name
            table_schema = schema_data[table_name]
            columns = [column for (_key, column) in parsed_query.iter_expressions()]
            if isinstance(parsed_query, sqlglot.expressions.Update):
                where = parsed_query.find(sqlglot.expressions.Where)
                if where is None:
                    continue  # pragma: no cover

                fields = build_update_assert_fields(
                    columns, table_schema["fields"], names
                )

                if isinstance(where.this, sqlglot.expressions.In):
                    lookups = []
                    lookup_name = where.this.this.name
                    for literal in where.this.expressions:
                        lookups.append((lookup_name, literal.name))
                elif isinstance(where.this, sqlglot.expressions.Paren):
                    asserts.append(DjangoQuery(table_name, query))
                    lookups = []
                else:
                    lookup_name = where.this.left.name
                    lookup_value = where.this.right.name
                    lookups = [(lookup_name, lookup_value)]

                verbose_name = table_schema["verbose_name"]
                for lookup_name, lookup_value in lookups:
                    variable_name = names.next_variable_name(
                        verbose_name, lookup_name, lookup_value
                    )
                    assert_update = AssertUpdate(
                        variable_name,
                        table_schema["model_name"],
                        table_name,
                        fields,
                        query,
                    )
                    asserts.append(assert_update)
                    if table_schema["fields"][lookup_name][  # pragma: no branch
                        "primary_key"
                    ]:
                        seen_mutations.setdefault(table_name, set()).add(lookup_value)
            elif isinstance(parsed_query, sqlglot.expressions.Delete):
                where = parsed_query.find(sqlglot.expressions.Where)
                if where is None:
                    continue  # pragma: no cover

                model = table_schema["model_name"]
                module = table_schema["model_module"]
                fields = build_delete_lookup_fields(where, table_schema)
                assert_delete = AssertDelete(model, fields, query)
                asserts.append(assert_delete)
                import_path = f"from {module} import {model}"
                imports.add(import_path)
            elif isinstance(  # pragma: no branch
                parsed_query, sqlglot.expressions.Insert
            ):
                for assert_insert in build_assert_inserts(
                    parsed_query, query, table_schema, table_name, seen_mutations, names
                ):
                    asserts.append(assert_insert)
                    imports.add(assert_insert.import_path)

    deduplicated = unique_everseen(inserts)
    sql_fixtures = sorted(deduplicated, key=make_table_sort_key(schema_data))
    for create in sql_fixtures:
        if isinstance(create, DjangoCreate):
            create.update_fields(names, schema_data)
    for assert_ in asserts:
        assert_.update_fields(names, schema_data)
    return sql_fixtures, imports, merge_asserts(asserts)


def build_assert_inserts(
    parsed_query, query, table_schema, table_name, seen_mutations, names
):
    sql_schema = parsed_query.find(sqlglot.expressions.Schema)
    if sql_schema is None:
        return  # pragma: no cover
    schema_columns = [
        column
        for (_key, column) in sql_schema.iter_expressions()
        if isinstance(column, sqlglot.expressions.Identifier)
    ]
    returning = parsed_query.find(sqlglot.expressions.Returning)
    for sql_values_tuple in parsed_query.find_all(sqlglot.expressions.Tuple):
        value_columns = [
            column for (_key, column) in sql_values_tuple.iter_expressions()
        ]
        zipped_columns = list(zip(schema_columns, value_columns))
        fields = build_insert_assert_fields(zipped_columns, table_schema, names)
        primary_key = None
        if returning:  # pragma: no branch
            for field, value in zip(returning.expressions, query["query_data"][0]):
                field_schema = table_schema["fields"][field.name]
                if field_schema["primary_key"]:  # pragma: no branch
                    primary_key = DjangoField(
                        field.this.name,
                        field.this.name,
                        value,
                        field_schema,
                    )
                    seen_mutations.setdefault(table_name, set()).add(repr(value))
        if primary_key is None:  # pragma: no cover
            continue
        yield AssertInsert.from_raw(fields, query, table_schema, names, primary_key)


def merge_asserts(asserts):
    lookup = {}
    merged: List[AnyAssert] = []
    for _assert in asserts:
        if isinstance(_assert, AssertInsert):
            lookup[_assert.variable_name] = _assert
            merged.append(_assert)
        elif isinstance(_assert, AssertUpdate):
            if _assert.variable_name not in lookup:
                merged.append(_assert)
                continue
            insert = lookup[_assert.variable_name]
            insert.fields = merge_fields(insert, _assert)
        else:
            merged.append(_assert)

    return tidy_deletes(merged)


def tidy_deletes(asserts):
    lookup: Dict[str, List[Set[DjangoField]]] = {}
    tidied: List[AnyAssert] = []
    for _assert in reversed(asserts):
        if isinstance(_assert, AssertDelete):
            lookup.setdefault(_assert.model, []).append(set(_assert.fields))
            tidied.append(_assert)
        elif isinstance(_assert, (AssertInsert, AssertUpdate)):
            if _assert.model not in lookup:
                tidied.append(_assert)
                continue

            if any(
                would_be_deleted(_assert, delete_fields)
                for delete_fields in lookup[_assert.model]
            ):
                continue
            tidied.append(_assert)
        else:
            tidied.append(_assert)

    return list(reversed(tidied))


def would_be_deleted(_assert, delete_fields):
    for delete in delete_fields:
        for field in _assert.fields:
            # If the field is an exact match, check the next delete field
            if field == delete:
                break
            # If the field name is a match, but the value is wrong, we don't delete
            # and can exit early
            if field.name == delete.name:
                return False
        # If none of the fields match the delete field we also don't delete
        else:
            return False
    # If all delete fields have a match, we delete
    return True


def merge_fields(insert, update):
    names = {f.name for f in update.fields}
    fields = []
    for field in insert.fields:
        if field.name in names:
            continue
        fields.append(field)
    fields.extend(update.fields)
    return fields
