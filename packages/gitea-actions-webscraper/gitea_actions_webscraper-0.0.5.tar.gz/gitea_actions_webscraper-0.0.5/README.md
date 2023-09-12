# Gitea Actions Webscraper

Install with:

```
pip install gitea_actions_webscraper
```

Example usage:

```py
from gitea_actions_webscraper import GiteaActionsWebscraper
import json

print('Verifying Gitea Actions Webscraper configuration...')
gitea_actions_webscraper = GiteaActionsWebscraper('https://codeberg.org', 'User/Repository', 'YOUR_i_like_gitea_COOKIE')
print('Gitea Actions Webscraper configuration verified!')

actions = gitea_actions_webscraper.getFirstActionsPage()
lastAction = actions[0]
print(lastAction.commitTitle)
print(json.dumps(lastAction.getArtifacts(), indent = 4))
print(json.dumps(lastAction.getLogs(), indent = 4))
messages = '\n'.join([stepLog['message'] for stepLog in lastAction.getStepLogs(0)])
print(messages)
```
