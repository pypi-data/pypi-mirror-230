from dap.integration.plugin import register_database_plugin_type

from .postgres.plugin import PostgresPlugin
from .mysql.mysql_plugin import MysqlPlugin


def load() -> None:
    register_database_plugin_type("postgresql", PostgresPlugin)
    register_database_plugin_type("mysql", MysqlPlugin)
