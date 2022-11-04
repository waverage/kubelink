import sys
import argparse
from commands.create import createCommand
from commands.watch import WatchCommand
from config import Config
import logging

logLevelNameToInt = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'error': logging.ERROR,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='klink',
        description='Klink description',
        epilog='Text at the bottom of help'
    )
    logLevelArgumentHelp = 'Set log level. Default: info. Available levels: info, debug, error'
    parser.add_argument('--log', help=logLevelArgumentHelp, default='info')

    subparsers = parser.add_subparsers(help='sub-command help')

    createp = subparsers.add_parser('create', help='Create a klink preset')
    createp.add_argument('--name', help='Name of klink preset')
    createp.add_argument('-s', '--source', help='Local source directory to sync')
    createp.add_argument('-d', '--destination', help='Destination directory in kubernetes pod')
    createp.add_argument('--namespace', help='Kubernetes namespace', default="default")
    createp.add_argument('-l', '--selector', help='Label selector to find pod. For example: -s "app=php"', default="")
    createp.add_argument('-c', '--container', help='Container name. Required if pod contains more than one container', default="")
    createp.add_argument('--log', help=logLevelArgumentHelp, default='info')

    watchp = subparsers.add_parser('watch', help='Watch source directory to any changes and sync it to kubernetes pod')
    watchp.add_argument('name', help='Klink preset name. If you didn\'t create it yet, you have to run "klink create" command')
    watchp.add_argument('--log', help=logLevelArgumentHelp, default='info')

    args = parser.parse_args()

    logLevel = args.log
    if logLevel not in logLevelNameToInt:
        logLevel = 'info'
    logging.basicConfig(level=logLevelNameToInt[logLevel])

    if len(sys.argv) < 2:
        parser.print_help()
        exit()
    else:
        command = sys.argv[1]
    config = Config()

    if command == 'create':
        createCommand(config, args)
    elif command == 'watch':
        watch = WatchCommand(config, args)
        watch.run()
    else:
        logging.error('Invalid command: ' + command)
        exit(1)
