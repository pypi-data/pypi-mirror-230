from pypika import Query
from pypika.dialects import (
    PostgreSQLQueryBuilder,
    RedShiftQueryBuilder,
    SnowflakeQueryBuilder,
)
from pypika.enums import Dialects

from metrics_layer.core.model.definitions import Definitions

SnowflakeQueryBuilder.ALIAS_QUOTE_CHAR = None
RedShiftQueryBuilder.ALIAS_QUOTE_CHAR = None
RedShiftQueryBuilder.QUOTE_CHAR = None
PostgreSQLQueryBuilder.ALIAS_QUOTE_CHAR = None
PostgreSQLQueryBuilder.QUOTE_CHAR = None


class SnowflakeQuery(Query):
    """
    Defines a query class for use with Snowflake.
    """

    @classmethod
    def _builder(cls, **kwargs) -> SnowflakeQueryBuilder:
        return SnowflakeQueryBuilder(**kwargs)


class PostgresQuery(Query):
    """
    Defines a query class for use with Snowflake.
    """

    @classmethod
    def _builder(cls, **kwargs) -> PostgreSQLQueryBuilder:
        return PostgreSQLQueryBuilder(**kwargs)


class RedshiftQuery(Query):
    """
    Defines a query class for use with Amazon Redshift.
    """

    @classmethod
    def _builder(cls, **kwargs) -> "RedShiftQueryBuilder":
        return RedShiftQueryBuilder(dialect=Dialects.REDSHIFT, **kwargs)


class BigQueryQuery(Query):
    """
    Defines a query class for use with BigQuery.
    """

    @classmethod
    def _builder(cls, **kwargs) -> SnowflakeQueryBuilder:
        return SnowflakeQueryBuilder(**kwargs)


query_lookup = {
    Definitions.snowflake: SnowflakeQuery,
    Definitions.bigquery: BigQueryQuery,
    Definitions.redshift: RedshiftQuery,
    Definitions.postgres: PostgresQuery,
    Definitions.druid: PostgresQuery,  # druid core query logic is postgres compatible
}

if_null_lookup = {
    Definitions.snowflake: "ifnull",
    Definitions.bigquery: "ifnull",
    Definitions.redshift: "ifnull",
    Definitions.postgres: "ifnull",
    Definitions.druid: "nvl",
}
