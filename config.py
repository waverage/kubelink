import os
import yaml

class Config:
    def __init__(self) -> None:
        self.CONFIG_DIR_PATH = self._getConfigDir()
        self.CONFIG_FILENAME = 'config.yaml'
        self.CONFIG_FILE_PATH = os.path.join(self.CONFIG_DIR_PATH, self.CONFIG_FILENAME)

        self._configFolderCheck()

    def savePreset(self, preset: dict) -> bool:
        filteredPreset = self._filterPresetProps(preset)
        config = self._readConfig()
        if config == None:
            config = {
                'presets': [filteredPreset]
            }
        else:
            self._mergePresets(config, filteredPreset)

        return self._writeConfig(config)

    def presetExists(self, presetName: str) -> bool:        
        preset = self.findPreset(presetName)
        return preset != None
    
    def findPreset(self, name: str):
        config = self._readConfig()
        if config == None:
            return False

        if 'presets' not in config:
            return None

        for v in config['presets']:
            if v['name'] == name:
                return v
        return None

    def _getConfigDir(self):
        home = os.path.expanduser('~')
        return os.path.join(home, '.klink')

    def _configFolderCheck(self):
        if not os.path.isdir(self.CONFIG_DIR_PATH):
            os.mkdir(self.CONFIG_DIR_PATH)

        if not os.path.exists(self.CONFIG_FILE_PATH):
            f = open(self.CONFIG_FILE_PATH, 'w')
            f.write('')
            f.close()

    def _readConfig(self):
        if not os.path.exists(self.CONFIG_FILE_PATH):
            return None

        f = open(self.CONFIG_FILE_PATH, 'r')
        data = yaml.load(f, Loader=yaml.FullLoader)
        f.close()
        return data

    def _writeConfig(self, config: dict) -> bool:
        f = open(self.CONFIG_FILE_PATH, 'w')
        yaml.dump(config, f)
        f.close()
        return True

    def _filterPresetProps(self, preset: dict):
        allowedProps = ['name', 'source', 'destination', 'namespace', 'selector', 'container']
        for k in preset:
            if k not in allowedProps:
                del preset[k]
        return preset

    def _mergePresets(self, config: dict, preset: dict):
        # Merge values with existing config
        for v in config['presets']:
            if v['name'] == preset['name']:
                for prop in preset:
                    v[prop] = preset[prop]
                return config
        config['presets'].append(preset)
        return config