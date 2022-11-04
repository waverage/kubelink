from watchdog.events import FileSystemEventHandler
import os
import subprocess

class EventHandler(FileSystemEventHandler):
    def __init__(self, preset, pods) -> None:
        super().__init__()
        self.preset = preset
        self.pods = pods

    def on_any_event(self,event):
        #print('Recived event : ' + event.event_type + ' - ' + event.src_path)
        pass

    def on_modified(self, event):
        self._uploadFile(event.src_path)
    
    def on_created(self, event):
        self._uploadFile(event.src_path, created=True)

    def on_deleted(self, event):
        # TODO: Need to delete file via kubectl exec
        pass

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
            print('Path is wrong. fullPath: ', fullLocalPath)
            return None

    def _getRemotePath(self, relativePath):
        return os.path.join(self.preset['destination'], relativePath)

    def _isNeedUpload(self, filePath):
        # Ignore PhpStorm temp files
        return len(filePath) >= 1 and filePath[-1:] != '~'

    def _uploadFile(self, filePath, created=False):
        if not self._isNeedUpload(filePath):
            return

        relPath = self._getRelativePath(filePath)
        if relPath == None:
            return
        print('_uploadFile rel path: ', relPath)

        remotePath = self._getRemotePath(relPath)

        print('Remote path', remotePath)

        for pod in self.pods:
            remoteUri = self.preset['namespace'] + '/' + pod['name'] + ':' + remotePath
            print('Remote uri: ', remoteUri)
            self._cpCommand(filePath, remoteUri)


    def _cpCommand(self, localPath, remoteUri):
        # kubectl cp /tmp/foo <some-namespace>/<some-pod>:/tmp/bar
        command = ['kubectl', 'cp', localPath, remoteUri]
        print(' '.join(command))
        result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
        print(result.stdout)