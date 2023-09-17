import os
from abc import abstractmethod
import logging
from thompcoUtils.email_utils import EmailSender
from thompcoUtils import config_utils, email_utils, log_utils
from thompcoUtils.genericArgs import GenericArgParser


class GenericAppConfig(config_utils.ConfigManager):
    """
    the AppConfig contains all configurable values from the command line and configuration file
    """
    def __init__(self, arg_parser: GenericArgParser, app_name: str, has_logging=True, has_email=True, has_temp=True):
        """
        Creates a new AppConfig which reads the configuration file.
        It overrides any values based on the arguments passed in to the ArgParser.
        @param arg_parser: the ArgParser responsible for parsing the command-line arguments
        @param app_name: the name of this application
        @param has_logging: indicates the application has logging
        @param has_temp: indicates the application requires a temp folder
        @param has_email: indicates the application uses email
        """
        self.has_logging = has_logging
        self.has_email = has_email
        self.has_temp = has_temp
        new_file = not os.path.exists(arg_parser.config)
        super().__init__(arg_parser.config, create=new_file)
        self._init(arg_parser, app_name)
        self._custom_finalize(arg_parser, app_name)

        if self.has_email:
            self.email_config = email_utils.EmailConnectionConfig(self)

            if arg_parser.test_email:
                sender = EmailSender(self.email_config)
                sender.send(self.recipients, subject=f'Test from {app_name}',
                            message='If you receive this, the email system is working')
                print(f'A test email has been sent to the following recipients: {",".join(self.recipients)}')
                exit(0)

        if new_file:
            self.finalize()
            exit()

    def _init(self, arg_parser: GenericArgParser, app_name: str):
        """
        Initializes the core values from the configuration file used by most applications.
        Note that values set on the command line will overwrite values in the configuration file.
        After this function completes, logging will be available for the app to use.
        NOTE that the following entries are under the "config" section in the configuration file.
        For more information on them, please see the generated configuration file:
        * log folder
        * log config file
        * temp folder

        NOTE that the following entries are under the "email connection" section in the configuration file.
        For more information on them, please see the generated configuration file:
            * email recipients
        * send messages
        @param arg_parser: the ArgParser responsible for parsing the command-line arguments
        @param app_name: the name of this application
        @return: None
        """
        header = 'config'
        if self.has_logging:
            log_folder = self.read_entry(header, 'log folder', '/var/log', notes=f'location of log files')

            if arg_parser.log_folder:  # override if set on command line
                log_folder = arg_parser.log_folder
            log_file = f'{log_folder}/{app_name}.log'

            if not os.path.exists(log_folder):  # create the folder, if necessary
                os.makedirs(log_folder)

            # Set up the log configuration file:
            self.log_config_file = self.read_entry(header, 'log config file', 'logging.ini',
                                                   notes=f'name of the log configuration file.')
            if arg_parser.log_config:  # override if set on command line
                self.log_config_file = arg_parser.log_config
            if os.path.exists(self.log_config_file):
                self._set_log_config_file_folder(log_file=log_file)  # update the log file name
            else:
                self._create_log_configfile(log_file_name=log_file)  # create the log configuration file

            log_utils.load_log_config(self.log_config_file)
            log_level = self.read_entry(header, 'log level', 'None',
                                        notes=f'log level (over-rides settings in {self.log_config_file})')

            if log_level.lower() != 'none':
                logging.getLogger().setLevel(logging.getLevelName(arg_parser.log_level.upper()))

        if self.has_temp:
            self.temp_folder = self.read_entry(header, 'temp folder', '/tmp', notes=f'location of the temporary files')

            if arg_parser.temp_folder:  # override if set on command line
                self.temp_folder = arg_parser.temp_folder
            if not os.path.exists(self.temp_folder):
                os.makedirs(self.temp_folder)

        if self.has_email:
            header = 'email connection'
            self.recipients = self.read_entry(
                header, 'email recipients', 'recipient1@gmail.com, recipient2@yahoo.com',
                notes='recipients to receive the notifications').split(',')
            self.send_emails = self.read_entry(
                header, 'send messages', True,
                notes='Turn this off to prevent emails being sent')

            if arg_parser.send_emails is not None:
                self.send_emails = arg_parser.send_emails

    def temp_file(self, file_name: str):
        """
        returns the full path to the specified file in the temp directory (set up initially).
        This function does not validate or confirm that the file exists, but the temp directory was confirmed earlier
        in the _init() function
        @param file_name: the name of the file in the temp directory
        @return the fully qualified name of the file in the temp directory
        """
        return os.path.join(self.temp_folder, file_name)

    @abstractmethod
    def _custom_finalize(self, arg_parser: GenericArgParser, app_name: str):
        """
        Gets any custom values used by the application from the configuration file.
        It is up to the implementor to decide if values from the command line should override them
        (see AppConfig._finalize() for examples)
        @param app_name: the name of this application
        @return: None
        """
        raise RuntimeError('Should never instantiate this base class')

    def _set_log_config_file_folder(self, log_file):
        """
        updates the log configuration file with the specified log file
        @param log_file: full path to the log file
        @return: None
        """
        lines = []
        entered_section = False

        with open(self.log_config_file, 'r') as fp:
            line = fp.readline()

            while line:
                if 'handler_rotatingFileHandler' in line:
                    entered_section = True
                if line.strip() == '':
                    entered_section = False
                if entered_section and 'args=' in line:
                    sections = line.split(',')
                    sections[0] = f"args=('{log_file}'"
                    new_line = ''

                    for section in sections:
                        new_line += section + ','
                    line = new_line[:-1]
                lines.append(line)
                line = fp.readline()
        with open(self.log_config_file, 'w') as fp:
            for line in lines:
                fp.write(line)

    def _create_log_configfile(self, log_file_name: str):
        """
        Creates a log file configuration file (should only be called if it doesn't exist)
        @param log_file_name: the log file for this application
        @return: None
        """
        log_contents = f'''# Note that the way log_utils works is that you need to specify the filename and function for 
    # the qualname
# Use the example below for assistance:
[loggers]
keys:run, root

[handlers]
keys:consoleHandler,rotatingFileHandler

[formatters]
keys:logFormatter

[logger_run]
level:DEBUG
qualname:main.run
handlers:rotatingFileHandler,consoleHandler
propagate:0

[logger_root]
level:INFO
handlers:rotatingFileHandler,consoleHandler

[handler_consoleHandler]
class:StreamHandler
formatter:logFormatter
args:(sys.stdout,)

[handler_rotatingFileHandler]
class : logging.handlers.RotatingFileHandler
args=('{log_file_name}','a',20000,500)
formatter=logFormatter

[formatter_logFormatter]
format:%(asctime)s:%(levelname)-9s:%(name)s - %(message)s <%(name)s>
datefmt:
'''
        with open(self.log_config_file, 'w') as f:
            f.write(log_contents)


class CustomAppConfig(GenericAppConfig):
    def __init__(self, arg_parser: GenericArgParser, app_name: str):
        """
        Calls the base class initialization
        """
        super().__init__(arg_parser, app_name)

    def _custom_finalize(self, arg_parser: GenericArgParser, app_name: str):
        """
        Gets any custom values used by the application from the configuration file.
        It is up to the implementor to decide if values from the command line should override them
        (see AppConfig._finalize() for examples)
        @param app_name: the name of this application
        @return: None
        """
        header = 'test'
        self.test = self.read_entry(
            header, 'test', 'this is a test',
            notes='notes for test')

        # noinspection PyUnresolvedReferences
        if arg_parser.test is not None:
            # noinspection PyUnresolvedReferences
            self.test = arg_parser.test
