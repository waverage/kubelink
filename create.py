from config import Config
from argparse import Namespace

def createCommand(config: Config, args: Namespace):
    preset = {
        'name': args.name,
        'source': args.source,
        'destination': args.destination,
        'namespace': args.namespace,
        'selector': args.selector,
        'container': args.container
    }

    isNew = True
    if config.presetExists(preset['name']):
        isNew = False

    if not config.savePreset(preset):
        print('Failed to save a new preset')
        exit(1)

    if isNew:
        print('Successfully added preset: ' + args.name)
    else:
        print('Successfully updated preset: ' + args.name)
