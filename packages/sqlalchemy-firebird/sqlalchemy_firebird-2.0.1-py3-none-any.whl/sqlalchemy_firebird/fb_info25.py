"""Provide Firebird 2.5 specific information.

    Variables:
        MAX_IDENTIFIER_LENGTH -> int
        RESERVED_WORDS -> set
        ISCHEMA_NAMES -> dict

.._Firebird 2.5:
    https://www.firebirdsql.org/file/documentation/html/en/refdocs/fblangref25/firebird-25-language-reference.html#fblangref25-intro

"""

from packaging import version

from sqlalchemy import __version__ as SQLALCHEMY_VERSION
from sqlalchemy.types import BIGINT
from sqlalchemy.types import BLOB
from sqlalchemy.types import DATE
from sqlalchemy.types import FLOAT
from sqlalchemy.types import INTEGER
from sqlalchemy.types import NUMERIC
from sqlalchemy.types import SMALLINT
from sqlalchemy.types import TEXT
from sqlalchemy.types import TIME
from sqlalchemy.types import TIMESTAMP

from .types import CHAR
from .types import VARCHAR
from .types import DOUBLE_PRECISION

# https://www.firebirdsql.org/file/documentation/html/en/refdocs/fblangref25/firebird-25-language-reference.html#fblangref25-datatypes
# "Length cannot exceed 31 characters."
MAX_IDENTIFIER_LENGTH = 31

# https://www.firebirdsql.org/file/documentation/html/en/refdocs/fblangref25/firebird-25-language-reference.html#fblangref25-appx03-reskeywords
# This set is for Firebird versions >= 2.5.1
RESERVED_WORDS = {
    "add",
    "admin",
    "all",
    "alter",
    "and",
    "any",
    "as",
    "at",
    "avg",
    "begin",
    "between",
    "bigint",
    "bit_length",
    "blob",
    "both",
    "by",
    "case",
    "cast",
    "char",
    "char_length",
    "character",
    "character_length",
    "check",
    "close",
    "collate",
    "column",
    "commit",
    "connect",
    "constraint",
    "count",
    "create",
    "cross",
    "current",
    "current_connection",
    "current_date",
    "current_role",
    "current_time",
    "current_timestamp",
    "current_transaction",
    "current_user",
    "cursor",
    "date",
    "day",
    "dec",
    "decimal",
    "declare",
    "default",
    "delete",
    "deleting",
    "disconnect",
    "distinct",
    "double",
    "drop",
    "else",
    "end",
    "escape",
    "execute",
    "exists",
    "external",
    "extract",
    "fetch",
    "filter",
    "float",
    "for",
    "foreign",
    "from",
    "full",
    "function",
    "gdscode",
    "global",
    "grant",
    "group",
    "having",
    "hour",
    "in",
    "index",
    "inner",
    "insensitive",
    "insert",
    "inserting",
    "int",
    "integer",
    "into",
    "is",
    "join",
    "leading",
    "left",
    "like",
    "long",
    "lower",
    "max",
    "maximum_segment",
    "merge",
    "min",
    "minute",
    "month",
    "national",
    "natural",
    "nchar",
    "no",
    "not",
    "null",
    "numeric",
    "octet_length",
    "of",
    "on",
    "only",
    "open",
    "or",
    "order",
    "outer",
    "parameter",
    "plan",
    "position",
    "post_event",
    "precision",
    "primary",
    "procedure",
    "rdb$db_key",
    "real",
    "record_version",
    "recreate",
    "recursive",
    "references",
    "release",
    "returning_values",
    "returns",
    "revoke",
    "right",
    "rollback",
    "row_count",
    "rows",
    "savepoint",
    "second",
    "select",
    "sensitive",
    "set",
    "similar",
    "smallint",
    "some",
    "sqlcode",
    "sqlstate",
    "start",
    "sum",
    "table",
    "then",
    "time",
    "timestamp",
    "to",
    "trailing",
    "trigger",
    "trim",
    "union",
    "unique",
    "update",
    "updating",
    "upper",
    "user",
    "using",
    "value",
    "values",
    "varchar",
    "variable",
    "varying",
    "view",
    "when",
    "where",
    "while",
    "with",
    "year",
}

# https://www.firebirdsql.org/file/documentation/html/en/refdocs/fblangref25/firebird-25-language-reference.html#fblangref25-datatypes
ISCHEMA_NAMES = {
    "SMALLINT": SMALLINT,
    "INT": INTEGER,
    "INTEGER": INTEGER,
    "BIGINT": BIGINT,
    "FLOAT": FLOAT,
    "DOUBLE PRECISION": FLOAT
    if version.parse(SQLALCHEMY_VERSION).major < 2
    else DOUBLE_PRECISION,
    "DATE": DATE,
    "TIME": TIME,
    "TIMESTAMP": TIMESTAMP,
    "DECIMAL": NUMERIC,
    "NUMERIC": NUMERIC,
    "VARCHAR": VARCHAR,
    "CHAR VARYING": VARCHAR,
    "CHARACTER VARYING": VARCHAR,
    "CHAR": CHAR,
    "CHARACTER": CHAR,
    # Compatibility
    "SHORT": SMALLINT,
    "LONG": INTEGER,
    "QUAD": FLOAT,
    "TEXT": TEXT,
    "INT64": BIGINT,
    "DOUBLE": FLOAT,
    "VARYING": VARCHAR,
    "CSTRING": CHAR,
    "BLOB": BLOB,
}
