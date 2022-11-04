import yaml
import subprocess

class Kubernetes:
    def __init__(self) -> None:
        pass

    def findPods(self, selector: str, namespace: str, containerName: str = ''):
        command = ['kubectl', 'get', 'pod', '-n', namespace, '--selector', selector, '-o', 'yaml']
        result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
        result = yaml.load(result.stdout, yaml.FullLoader)

        if result == None or 'items' not in result:
            #print('Failed to get pods from kubernetes with command: ', command.join(' '))
            return []
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
