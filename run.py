from script.core import startUserSync
import argparse
import logging

class DispatchingFormatter:
    def __init__(self, formatters, default_formatter):
        self._formatters = formatters
        self._default_formatter = default_formatter

    def format(self, record):
        formatter = self._formatters.get(record.name, self._default_formatter)
        return formatter.format(record)

def setup_logger():
    """
    Setting up the used logger. The 'mutate' logger will print whether dry-run is used and changes are being applied.
    """
    log_format = '%(asctime)s - %(levelname)5s - %(module)7s - %(message)s'
    log_format_mut = log_format

    if args.dry_run:
        log_format_mut = '%(asctime)s - %(levelname)5s - %(module)7s - [SKIPPED] %(message)s'
    else:
        log_format_mut = log_format

    
    logger = logging.getLogger()
    while logger.handlers:
            logger.handlers.pop()

    formatter = DispatchingFormatter({
            'mutate': logging.Formatter(log_format_mut),
        },
        logging.Formatter(log_format)
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process config path')
    parser.add_argument('--config', dest='config_path', help='Path to the config_mock.yml file', required=True)
    parser.add_argument('--bind', dest='bind', help='Path to the binding file', required=True)
    parser.add_argument('--dry-run', dest='dry_run', default=False, help='If this flag is set, the script does not '
                                                                         'apply changes to grafana. The would-be '
                                                                         'changes are printed to the console.',
                        action='store_true')
    args = parser.parse_args()

    # setup the logger
    setup_logger()

    # starts the sync process
    startUserSync(args.config_path, args.bind, args.dry_run)
