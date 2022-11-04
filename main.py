import sys
import argparse
from create import createCommand
from watch import WatchCommand
from config import Config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='klink',
        description='Klink description',
        epilog='Text at the bottom of help'
    )

    subparsers = parser.add_subparsers(help='sub-command help')

    createp = subparsers.add_parser('create', help='Create a klink preset')
    createp.add_argument('--name', help='Name of klink preset')
    createp.add_argument('-s', '--source', help='Local source directory to sync')
    createp.add_argument('-d', '--destination', help='Destination directory in kubernetes pod')
    createp.add_argument('--namespace', help='Kubernetes namespace', default="default")
    createp.add_argument('-l', '--selector', help='Label selector to find pod. For example: -s "app=php"', default="")
    createp.add_argument('-c', '--container', help='Container name. Required if pod contains more than one container', default="")

    watchp = subparsers.add_parser('watch', help='Watch source directory to any changes and sync it to kubernetes pod')
    watchp.add_argument('name', help='Klink preset name. If you didn\'t create it yet, you have to run "klink create" command')

    args = parser.parse_args()

    command = sys.argv[1]
    config = Config()

    if command == 'create':
        createCommand(config, args)
    elif command == 'watch':
        watch = WatchCommand(config, args)
        watch.run()
    else:
        print('Invalid command: ' + command)
        exit(1)
