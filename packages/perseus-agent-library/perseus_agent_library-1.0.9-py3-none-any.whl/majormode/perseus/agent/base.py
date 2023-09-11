# Copyright (C) 2021 Majormode.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Majormode or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Majormode.
#
# MAJORMODE MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY
# OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT.  MAJORMODE SHALL NOT BE LIABLE FOR ANY
# LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING
# OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

from abc import ABC
from abc import abstractmethod
import argparse
import getpass
import logging
import sys
import time

from majormode.perseus.constant.logging import LOGGING_LEVELS
from majormode.perseus.constant.logging import LoggingLevelLiteral
from majormode.perseus.utils import cast
from majormode.perseus.utils import env
from majormode.perseus.utils import rdbms


class BaseAgent(ABC):
    DEFAULT_IDLE_TIME = 5000

    DEFAULT_LOGGING_FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    DEFAULT_LOGGING_LEVEL = LoggingLevelLiteral.info

    def __init__(
            self,
            idle_time=None,
            logging_formatter: logging.Formatter = None,
            logging_level: LoggingLevelLiteral = None,
            name=None):
        """
        Build an object `BaseAgent`.

        @param name: Name of the agent.
        """
        self.__name = name or self.__class__.__name__
        self.__do_loop = False
        self.__idle_time = idle_time or self.DEFAULT_IDLE_TIME

        self.__logger = self.__setup_logger(
            logging_formatter=logging_formatter,
            logging_level=logging_level
        )

    @classmethod
    def __get_console_handler(cls, logging_formatter: logging.Formatter = None):
        """
        Return a logging handler that sends logging output to the system's
        standard output.


        @param logging_formatter: An object `Formatter` to set for this
            handler.  Defaults to `BaseAgent.DEFAULT_LOGGING_FORMATTER`.


        @return: An instance of the `StreamHandler` class.
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging_formatter or cls.DEFAULT_LOGGING_FORMATTER)
        return console_handler

    @classmethod
    def __setup_logger(
            cls,
            logging_formatter=None,
            logging_level=None,
            logger_name=None):
        """
        Setup a logging handler that sends logging output to the system's
        standard output.


        @param logging_formatter: An object `Formatter` to set for this
            handler.  Defaults to `BaseAgent.DEFAULT_LOGGING_FORMATTER`.

        @param logging_level: An item of the enumeration `LoggingLevelLiteral`
            that specifies the threshold for the logger to `level`.  Logging
            messages which are less severe than `level` will be ignored;
            logging messages which have severity level or higher will be
            emitted by whichever handler or handlers service this logger,
            unless a handler’s level has been set to a higher severity level
            than `level`.  Defaults to `BaseAgent.DEFAULT_LOGGING_LEVEL`.

        @param logger_name: Name of the logger to add the logging handler to.
            If `logger_name` is `None`, the function attaches the logging
            handler to the root logger of the hierarchy.


        @return: An object `Logger`.
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(LOGGING_LEVELS[logging_level or cls.DEFAULT_LOGGING_LEVEL])
        logger.addHandler(cls.__get_console_handler(logging_formatter=logging_formatter))
        logger.propagate = False
        return logger

    @abstractmethod
    def _run(self, **kwargs):
        raise NotImplementedError("This method MUST be implemented by the inheriting class")

    def _init(self):
        """
        """

    def set_logging_formatter(self, logging_formatter: logging.Formatter) -> None:
        for handler in self.__logger.handlers:
            handler.setFormatter(logging_formatter)

    def set_logging_level(self, logging_level: LoggingLevelLiteral) -> None:
        self.__logger.setLevel(LOGGING_LEVELS[logging_level or self.DEFAULT_LOGGING_LEVEL])

    def start(
            self,
            do_loop: bool = False,
            logging_formatter: logging.Formatter = None,
            logging_level: LoggingLevelLiteral = None,
            **kwargs):
        """

        @param do_loop:
        @param logging_formatter:
        @param logging_level:
        @param kwargs:
        @return:
        """
        self.__do_loop = do_loop

        if logging_level:
            self.set_logging_level(logging_level)

        if logging_formatter:
            self.set_logging_formatter(logging_formatter)

        was_active = self._run(**kwargs)
        while self.__do_loop:
            if not was_active:
                logging.debug(f"Waiting {float(self.__idle_time) / 1000}ms for more action...")
                time.sleep(float(self.__idle_time) / 1000)

            was_active = self._run(**kwargs)

    def stop(self):
        if not self.__do_loop:
            raise ValueError("This agent has not be started for running for ever")
        self.__do_loop = False


class BaseCliAgent(BaseAgent, ABC):
    def __init__(
            self,
            description=None,
            env_file_path_name=None,
            idle_time=None,
            name=None):
        """
        Build an object `BaseCliAgent`


        @param description: Text to display before the argument help.

        @param name: Name of the agent.
        """
        super().__init__(idle_time=idle_time, name=name)

        env.loadenv(env_file_path_name)

        # Setup the command line argument parser.
        self.__argument_parser = self.__build_argument_parser(description=description)
        self.__arguments = None

    @classmethod
    def __build_argument_parser(
            cls,
            description):
        """
        Build the command-line parser of the agent


        @param description: Text to display before the argument help.


        @return: An object `ArgumentParser`.
        """
        parser = argparse.ArgumentParser(description=description)

        # Generate the list of the literals of the supported logging levels.
        logging_level_literals = [
            str(logging_level_literal)
            for logging_level_literal in LOGGING_LEVELS.keys()
        ]

        parser.add_argument(
            '--logging-level',
            dest='logging_level_literal',
            metavar='LEVEL',
            required=False,
            default=str(LoggingLevelLiteral.info),
            help=f"specify the logging level ({', '.join(logging_level_literals)})."
        )

        return parser

    @property
    def _argument_parser(self):
        return self.__argument_parser

    def _init(self):
        super()._init()
        # Convert argument strings to objects and assign them as attributes of
        # the namespace.  This is done here to give the chance to the inheriting
        # class to add its custom arguments in its constructor.
        self.__arguments = self.__argument_parser.parse_args()

    @property
    def arguments(self):
        if self.__arguments is None:
            self.__arguments = self.__argument_parser.parse_args()
        return self.__arguments

    def start(
            self,
            do_loop=False,
            logging_formatter=None,
            logging_level=None):
        super().start(
            do_loop=do_loop,
            logging_level=logging_level or cast.string_to_enum(
                self.__arguments.logging_level_literal,
                LoggingLevelLiteral))


class BaseCliRdbmsAgent(BaseCliAgent, ABC):
    # Environment variables of the connection property to the Relational
    # DataBase Management System (RDBMS) server.
    ENV_RDBMS_HOSTNAME = 'RDBMS_HOSTNAME'
    ENV_RDBMS_PORT = 'RDBMS_PORT'
    ENV_RDBMS_DATABASE_NAME = 'RDBMS_DATABASE_NAME'
    ENV_RDBMS_USERNAME = 'RDBMS_USERNAME'
    ENV_RDBMS_PASSWORD = 'RDBMS_PASSWORD'

    def __init__(
            self,
            description=None,
            idle_time=None,
            name=None):
        super().__init__(
            description=description,
            idle_time=idle_time,
            name=name)

        self.__include_rdbms_arguments(self._argument_parser)

        self.__rdbms_hostname = None
        self.__rdbms_port = None
        self.__rdbms_database_name = None
        self.__rdbms_username = None
        self.__rdbms_password = None

        self.__rdbms_properties = None

    @classmethod
    def __include_rdbms_arguments(cls, parser):
        """
        Add the command line arguments to define the properties to connect to
        a Relational DataBase Management System (RDBMS) server


        @note: The password to connect to the RDBMS server CANNOT be passed as
            an argument on the command line as the password would be leaked
            into the process table, and thus visible to anybody running `ps(1)`
            on the system, and the password would leaked into the shell's
            history file.
            [https://www.netmeister.org/blog/passing-passwords.html]


        @param parser: An object `ArgumentParser`.


        @return: The object `ArgumentParser` that has been passed to this
            function.
        """
        parser.add_argument(
            '--rdbms-hostname',
            required=False,
            default=env.getenv(cls.ENV_RDBMS_HOSTNAME, is_required=False),
            help="specify the host name of the machine on which the server is running.")

        parser.add_argument(
            '--rdbms-port',
            required=False,
            type=int,
            default=env.getenv(cls.ENV_RDBMS_PORT, data_type=env.DataType.integer, is_required=False),
            help="specify the database TCP port or the local Unix-domain socket file "
                 "extension on which the server is listening for connections. Defaults "
                 "to the port specified at compile time, usually 5432.")

        default_database_name = env.getenv(cls.ENV_RDBMS_DATABASE_NAME, is_required=False)
        parser.add_argument(
            '--rdbms-database-name',
            required=default_database_name is None,
            default=default_database_name,
            help='Specify the name of the database to connect to.')

        parser.add_argument(
            '--rdbms-username',
            required=False,
            default=env.getenv(cls.ENV_RDBMS_USERNAME, is_required=False) or getpass.getuser(),
            help="connect to the database as the user username instead of the default.")

        return parser

    def _acquire_connection(self, auto_commit=False, connection=None):
        """
        Return a connection to a Relational DataBase Management System (RDBMS)
        the most appropriate for the service requesting this connection.


        @param auto_commit: Indicate whether the transaction needs to be
            committed at the end of the session.

        @param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.


        @return: An object `RdbmsConnection` to be used supporting the
            Python clause `with ...:`.
        """
        return rdbms.RdbmsConnection.acquire_connection(
            self.__rdbms_properties,
            auto_commit=auto_commit,
            connection=connection)

    def _init(self):
        super()._init()

        if self.__rdbms_hostname is None:
            self.__rdbms_hostname = self.arguments.rdbms_hostname

        if self.__rdbms_port is None:
            self.__rdbms_port = self.arguments.rdbms_port

        if self.__rdbms_database_name is None:
            self.__rdbms_database_name = self.arguments.rdbms_database_name

        if self.__rdbms_username is None:
            self.__rdbms_username = self.arguments.rdbms_username

        self.__rdbms_password = env.getenv(self.ENV_RDBMS_PASSWORD, is_required=False) \
            or getpass.getpass(f"Password for user {self.__rdbms_username}: ")

        self.__rdbms_properties = {
            None: {
                'rdbms_hostname': self.__rdbms_hostname,
                'rdbms_port': self.__rdbms_port,
                'rdbms_database_name': self.__rdbms_database_name,
                'rdbms_account_username': self.__rdbms_username,
                'rdbms_account_password': self.__rdbms_password,
            },
        }

    def start(
            self,
            do_loop=False,
            logging_formatter=None,
            logging_level=None):
        self._init()
        super().start(
            do_loop=do_loop,
            logging_formatter=logging_formatter,
            logging_level=logging_level)


class FakeCliRdbmsAgent(BaseCliRdbmsAgent):
    def _run(self):
        logging.info('Completed work!')


if __name__ == "__main__":
    agent = FakeCliRdbmsAgent()
    agent.start()
