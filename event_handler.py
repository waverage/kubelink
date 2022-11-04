from watchdog.events import FileSystemEventHandler
import os
import subprocess
import logging

class EventHandler(FileSystemEventHandler):
    def __init__(self, preset, pods) -> None:
        super().__init__()
        self.preset = preset
        self.pods = pods

    def on_any_event(self,event):
        #print('Recived event : ' + event.event_type + ' - ' + event.src_path)
        pass

    def on_modified(self, event):
        # Skip uploading directory on modified event
        if os.path.isdir(event.src_path):
            return

        self._uploadFile(event.src_path)
    
    def on_created(self, event):
        self._uploadFile(event.src_path)

    def on_deleted(self, event):
        self._deleteFile(event.src_path)

    def _getRelativePath(self, fullLocalPath):
        source = self.preset['source']
        if fullLocalPath == source:
            return None

        if fullLocalPath.find(source) == 0:
            # ok
            path = fullLocalPath[len(source):]
            if path[0] == '/':
                path = path[1:]
            return path
        else:
            logging.error('_getRelativePath - Path is wrong. fullPath: ' + fullLocalPath)
            return None

    def _getRemotePath(self, relativePath):
        return os.path.join(self.preset['destination'], relativePath)

    def _isNeedSkip(self, filePath) -> bool:
        # Ignore PhpStorm temp files
        return len(filePath) < 1 or filePath[-1:] == '~'

    def _uploadFile(self, filePath):
        if self._isNeedSkip(filePath):
            logging.debug('Ignore file: ' + filePath)
            return

        relPath = self._getRelativePath(filePath)
        if relPath == None:
            return
        logging.debug('Relative local path: ' + relPath)

        remotePath = self._getRemotePath(relPath)

        logging.debug('Remote path: ' + remotePath)

        for pod in self.pods:
            remoteUri = self.preset['namespace'] + '/' + pod['name'] + ':' + remotePath
            logging.debug('Remote URI: ' + remoteUri)
            logging.info('Upload file: ' + relPath)
            self._cpCommand(filePath, remoteUri, pod['container'])

    def _deleteFile(self, localFilePath):
        if self._isNeedSkip(localFilePath):
            logging.debug('Ignore file: ' + localFilePath)
            return

        relPath = self._getRelativePath(localFilePath)
        logging.debug('Delete file relative path: ' + str(relPath))
        if relPath == None:
            logging.error('Delete file relative path is None: ' + localFilePath)
            return

        remotePath = self._getRemotePath(relPath)
        logging.info('Delete file: ' + remotePath)

        for pod in self.pods:
            self._deleteCommand(pod['name'], remotePath, pod['container'], self.preset['namespace'])

    def _deleteCommand(self, podName, filepath, container=None, namespace='default'):
        #k exec provider-m-php-b5579ddbb-5v9hn -n production -- sh -c 'rm -rf /code/myfile.txt'
        command = ['kubectl', 'exec', podName, '-n', namespace]
        if container != None and container != '':
            command.append('-c')
            command.append(container)

        command.append('--')
        command.append('sh')
        command.append('-c')
        command.append("rm -rf " + filepath)
        logging.debug('rm command: ' + ' '.join(command))

        result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
        logging.debug('rm result: ' + result.stdout)
        return result.stdout

    def _cpCommand(self, localPath, remoteUri, container=None):
        if not os.path.exists(localPath):
            logging.debug('Copy file failed - file does not exists: ' + str(localPath))
            return

        # kubectl cp /tmp/foo <some-namespace>/<some-pod>:/tmp/bar
        command = ['kubectl', 'cp', localPath, remoteUri]
        if container != None and container != '':
            command.append('-c')
            command.append(container)

        logging.debug('cp command: ' + ' '.join(command))
        result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
        logging.debug('cp result: ' + result.stdout)