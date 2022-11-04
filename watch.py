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
            print('Preset not found. First you have to run: "klink create" to create a preset')
            exit(1)
        
        print('Found preset:', preset)

        kube = Kubernetes()

        pods = kube.findPods(preset['selector'], preset['namespace'], preset['container'])
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
