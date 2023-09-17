from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from abc import abstractmethod


class GenericArgParser:
    def __init__(self, app_name: str, help_description, help_epilog='', has_logging=True, has_temp=True, has_email=True):
        """
        Creates a new ArgParser.
        @param app_name: the name of this application
        @param help_description: description to be displayed at the beginning of the help output
        @param help_epilog: epilog is displayed at the end of the help output
        @param has_logging: indicates the application has logging
        @param has_temp: indicates the application requires a temp folder
        @param has_email: indicates the application uses email
        """
        self.has_logging = has_logging
        self.has_email = has_email
        self.has_temp = has_temp
        parser = ArgumentParser(prog=app_name,
                                description=help_description,
                                formatter_class=RawDescriptionHelpFormatter,
                                epilog=help_epilog)
        self._init(parser)
        self._custom_init(parser)
        args, unknown_args = parser.parse_known_args()

        if args.config:
            self.config = args.config
        else:
            self.config = 'app-config.ini'
        self._finalize(args)
        self._custom_finalize(args)

    def _init(self, parser: ArgumentParser):
        """
        Initializes the parser with common values to be parsed from the command line
        @param parser: the ArgumentParser
        @return None
        """
        parser.add_argument('--config', required=False,
                            help='Configuration file')

        if self.has_logging:
            parser.add_argument('--log-config', required=False,
                                help='Log configuration file')
            parser.add_argument('--log-folder', required=False,
                                help='Logs folder')
            parser.add_argument('--log-level', required=False,
                                help='Force logging in all locations to the specified level (i.e. debug, info, etc)')
        if self.has_temp:
            parser.add_argument('--temp-folder', required=False,
                                help='Temporary files folder')
        if self.has_email:
            parser.add_argument('--send-emails', required=False, action='store_true',
                                help='Sends emails as required by the application')
            parser.add_argument('--test-email', required=False, action='store_true',
                                help='Send a test email to validate the email configuration and exits.  '
                                     'This is for testing only')

    @abstractmethod
    def _custom_init(self, parser: ArgumentParser):
        """
        Initializes the derived class's parser with common values to be parsed from the command line.
        See ArgParser._init() for examples
        @param parser: the ArgumentParser
        @return None
        """
        raise RuntimeError('Should never instantiate this base class')

    def _finalize(self, args: Namespace):
        """
        finalizes the command line arguments and adds them as member variables to this class
        @param args: the args parsed by the command line argument parser
        @returns: None
        """
        self.log_config = args.log_config
        self.log_folder = args.log_folder
        self.temp_folder = args.temp_folder

        if self.has_email:
            self.log_level = args.log_level
            self.send_emails = args.send_emails
            self.test_email = args.test_email

    @abstractmethod
    def _custom_finalize(self, args: Namespace):
        """
        Finalizes the derived class's command line arguments and adds them as member variables to this class
        See ArgParser._finalize() for examples
        @param args: the args parsed by the command line argument parser
        @returns: None
        """
        raise RuntimeError('Should never instantiate this base class')


class CustomArgParser(GenericArgParser):
    def __init__(self, app_name: str):
        """
        Calls the base class initialization
        @param app_name: the name of this application
        """
        help_description = '''This application is used to test the args and config files.  
Use this to describe what the application does
        '''
        help_epilog = '''additional information:
                 I have indented it
                 exactly the way
                 I want it
             '''
        super().__init__(app_name=app_name, help_description=help_description, help_epilog=help_epilog)

    def _custom_init(self, parser):
        """
        initializes the derived class's command line arguments
        @param parser: the command line argument parser
        @returns: None
        """
        parser.add_argument('--test', required=False,
                            help='testing value')

    def _custom_finalize(self, args: ArgumentParser):
        """
        Finalizes the derived class's command line arguments and adds them as member variables to this class
        See ArgParser._finalize() for examples
        @param args: the args parsed by the command line argument parser
        @returns: None
        """
        # noinspection PyUnresolvedReferences
        self.test = args.test
