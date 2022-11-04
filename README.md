### Klink ###

klink automatically sync files to kubernetes pods. It speed up your development. You just work with your local files and them automatically syncing to your kubernetes cluster.

Using klink is as simple as:
1. `klink create --name mypreset -s ./ -d /code --namespace default -l "app=backend"` to create a preset with your settings
2. `klink watch mypreset` to start syncing files
