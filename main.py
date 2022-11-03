import sys
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from EventHandler import EventHandler
import argparse
import yaml
import subprocess

def getConfigDir():
    home = os.path.expanduser('~')
    return os.path.join(home, '.klink')

CONFIG_DIR_PATH = getConfigDir()
CONFIG_FILENAME = 'config.yaml'
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, CONFIG_FILENAME)

def configFolderCheck():
    if not os.path.isdir(CONFIG_DIR_PATH):
        os.mkdir(CONFIG_DIR_PATH)

    if not os.path.exists(CONFIG_FILE_PATH):
        f = open(CONFIG_FILE_PATH, 'w')
        f.write('')
        f.close()

def readConfig():
    if not os.path.exists(CONFIG_FILE_PATH):
        return None

    f = open(CONFIG_FILE_PATH, 'r')
    data = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
    return data

def writeConfig(config):
    f = open(CONFIG_FILE_PATH, 'w')
    yaml.dump(config, f)
    f.close()

def mergePresets(config, preset):
    # Merge values with existing config
    found = False
    added = False
    for v in config['presets']:
        if v['name'] == args.name:
            found = True
            for prop in preset:
                v[prop] = preset[prop]
    if not found:
        config['presets'].append(preset)
        added = True

    return added

def presetNotFoundErr():
    print('Preset not found. First you have to run: "klink create" to create a preset')
    exit(1)

def findPreset(config, name):
    for v in config['presets']:
        if v['name'] == name:
            return v
    return None

def findPods(selector, namespace, containerName):
    command = ['kubectl', 'get', 'pod', '-n', namespace, '--selector', selector, '-o', 'yaml']
    result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
    result = yaml.load(result.stdout, yaml.FullLoader)

    if result == None or 'items' not in result:
        print('Failed to get pods from kubernetes with command: ', command.join(' '))
        exit(1)
    result = result['items']
    #print('result', result)

    if len(result) == 0:
        return []

    pods = []
    for item in result:
        countContainers = len(item['spec']['containers'])
        if countContainers == 0:
            continue
            
        for container in item['spec']['containers']:
            if containerName == '' or container['name'] == containerName:
                pods.append({
                    'name': item['metadata']['name'],
                    'container': container['name'],
                })

    return pods

def createCommand(args):
    configFolderCheck()

    config = readConfig()
    preset = {
        'name': args.name,
        'source': args.source,
        'destination': args.destination,
        'namespace': args.namespace,
        'selector': args.selector,
        'container': args.container
    }

    added = False
    if config == None:
        config = {
            'presets': [
                preset,
            ]
        }
        added = True
    else:
        added = mergePresets(config, preset)

    writeConfig(config)

    if added:
        print('Successfully added preset: ' + args.name)
    else:
        print('Successfully updated preset: ' + args.name)

def watchCommand(args):
    config = readConfig()
    if config == None:
        presetNotFoundErr()
    
    preset = findPreset(config, args.name)
    if preset == None:
        presetNotFoundErr()
    
    print('Found preset:', preset)

    pods = findPods(preset['selector'], preset['namespace'], preset['container'])
    print('pods', pods)

    if len(pods) == 0:
        print('Pods to sync not found!')
        exit()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = EventHandler(preset, pods)
    observer = Observer()
    observer.schedule(event_handler, preset['source'], recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

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

    if command == 'create':
        createCommand(args)
    elif command == 'watch':
        watchCommand(args)
    else:
        print('Invalid command: ' + command)
        exit(1)
