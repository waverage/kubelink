import time
from watchdog.observers import Observer
from event_handler import EventHandler
import logging
from config import Config
from argparse import Namespace
from kubernetes import Kubernetes

class WatchCommand:
    def __init__(self, config: Config, args: Namespace) -> None:
        self.config = config
        self.args = args

    def run(self):
        preset = self.config.findPreset(self.args.name)        
        if preset == None:
            logging.error('Preset not found. First you have to run: "klink create" to create a preset')
            exit(1)
        
        logging.debug('Found preset: ' + str(preset))

        kube = Kubernetes()

        pods = kube.findPods(preset['selector'], preset['namespace'], preset['container'])
        logging.info('Found ' + str(len(pods)) + ' pods')

        if len(pods) == 0:
            print('Pods to sync not found!')
            exit()

        event_handler = EventHandler(preset, pods)
        observer = Observer()
        observer.schedule(event_handler, preset['source'], recursive=True)
        observer.start()

        logging.info('Watch on changes')

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
