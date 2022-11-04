kubelink automatically sync files to kubernetes pods. It speed up your development. You just work with your local files and kubelink automatically syncing them to your kubernetes cluster.

Using kubelink is as simple as:
1. `kubelink create --name mypreset --source ./ --destination /code --namespace default --selector "app=backend"` to create a preset with your settings
2. `kubelink watch mypreset` to start syncing files

kubelink based on `kubectl cp` and `kubectl exec` commands. So, kubelink is lightweight utility.

Requirements
============
* Python >= 3.7
* kubelink requires that the `tar` binary is present in your kubernetes container. If `tar` is not present, kubelink will fail.

Installation
============

Via pip
-------
```
pip install kubelink
```

From source code
----------------
```
git clone https://github.com/waverage/kubelink.git
cd kubelink
python setup.py buiild
python setup.py install
```

Usage
=====


kubelink create
---------------

Create a kubelink config preset with your sync settings.

```
kubelink create --name mypreset --source /Users/bob/myproject --destination /code --namespace default --selector "app=backend"
```

* **--name** - kubelink preset name
* **-s, --source** - Local source directory to sync
* **-d, --destination** - Destination directory in kubernetes pod
* **--namespace** - Kubernetes namespace
* **-l, --selector** - Label selector to find pod. For example: `-s "app=php"`
* **-c, --container** - Container name. Required if pod contains more than one container
* **-h, --help** - Show help
* **--log** - Set log level. Default: info. Available levels: info, debug, error

The presets file location is `~/.kubelink/config.yaml`.
You can create multiple config presets.

Help available by command:
```
kubelink create -h
```

kubelink watch
--------------
Start watching for real-time synchronizations.
```
kubelink watch mypreset
```
* **name** - kubelink preset name
* **-h, --help** - Show help
* **--log** - Set log level. Default: info. Available levels: info, debug, error

Help available by command:
```
kubelink watch -h
```

#### How to build and publish package ####
1.  Build setup.py
```
python setup.py sdist bdist_wheel
```
2. Upload package to Pypi
```
twine upload dist/*
```
