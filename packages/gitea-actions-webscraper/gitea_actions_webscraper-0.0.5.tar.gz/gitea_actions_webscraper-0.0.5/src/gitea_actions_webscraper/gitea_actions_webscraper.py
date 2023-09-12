import requests
import re
import json
from lxml import html

class GiteaActionsWebscraper:
    def __init__(self, instance, repository, i_like_gitea):
        self.instance = instance
        self.repository = repository
        self.i_like_gitea = i_like_gitea
        self.actionsUrl = f'{self.instance}/{self.repository}/actions'
        self._verifyConfiguration()

    def getCookies(self):
        cookies = {
            'i_like_gitea': self.i_like_gitea
        }
        return cookies

    def _getFirstActionsPageStr(self):
        cookies = self.getCookies()
        text = requests.get(self.actionsUrl, cookies = cookies).text
        return text

    def _verifyConfiguration(self):
        text = self._getFirstActionsPageStr()
        if text == 'Not found.\n':
            raise ValueError(f"`i_like_gitea` cookie value doesn't give access to {self.actionsUrl}")

    def getFirstActionsPage(self):
        text = self._getFirstActionsPageStr()
        tree = html.fromstring(text)
        items = tree.xpath("//li[@class='item action-item']")
        actions = []
        for item in items:
            divs = item.xpath('div')

            state = divs[0].xpath('span')[0].attrib['data-tooltip-content']

            subDivs = divs[1].xpath('div')
            aAttribs = subDivs[0].xpath('a')[0].attrib
            commitTitle = aAttribs['title']
            runId = aAttribs['href'].split('/')[-1]
            subDiv1 = subDivs[1]
            workflow = subDiv1.xpath('b')[0].text.split(' ')[0]
            as_ = subDiv1.xpath('a')
            commitHash = as_[0].attrib['href'].split('/')[-1]
            commitAuthor = as_[1].text_content()

            branch = divs[2].xpath('a')[0].attrib['href'].split('/')[-1]

            commitDate = divs[3].xpath('div/relative-time')[0].attrib['datetime']
            runTime = divs[3].xpath('div')[1].text_content()

            action = Action(self, state, runId, workflow, branch, commitHash, commitAuthor, commitDate, commitTitle, runTime)
            actions += [action]
        return actions

class Action:
    def __init__(self, giteaActionsWebscraper, state, runId, workflow, branch, commitHash, commitAuthor, commitDate, commitTitle, runTime):
        self.giteaActionsWebscraper = giteaActionsWebscraper
        self.state = state
        self.runId = runId
        self.workflow = workflow
        self.branch = branch
        self.commitHash = commitHash
        self.commitAuthor = commitAuthor
        self.commitDate = commitDate
        self.commitTitle = commitTitle
        self.runTime = runTime
        self.X_Csrf_Token = None
        self.runUrl = f'{self.giteaActionsWebscraper.actionsUrl}/runs/{self.runId}'

    def _loadX_Csrf_Token(self):
        if not self.X_Csrf_Token:
            cookies = self.giteaActionsWebscraper.getCookies()
            text = requests.get(self.runUrl, cookies = cookies).text
            tree = html.fromstring(text)
            content = tree.xpath('//script')[0].text_content()
            self.X_Csrf_Token = re.search(r"csrfToken: '(.*)',", content).group(1)

    def _getHeaders(self):
        self._loadX_Csrf_Token()
        headers = {
            'X-Csrf-Token': self.X_Csrf_Token
        }
        return headers

    def getArtifacts(self):
        cookies = self.giteaActionsWebscraper.getCookies()
        headers = self._getHeaders()
        data = requests.post(f'{self.runUrl}/artifacts', cookies = cookies, headers = headers).json()
        return data

    def getLogs(self):
        cookies = self.giteaActionsWebscraper.getCookies()
        headers = self._getHeaders()
        json_ = {
            'logCursors': []
        }
        data = requests.post(f'{self.runUrl}/jobs/0', cookies = cookies, headers = headers, json = json_).json()
        return data

    def getStepLogs(self, step):
        cookies = self.giteaActionsWebscraper.getCookies()
        headers = self._getHeaders()
        json_ = {
            'logCursors':
            [
                {
                    'step': step,
                    'expanded': True
                }
            ]
        }
        data = requests.post(f'{self.runUrl}/jobs/0', cookies = cookies, headers = headers, json = json_).json()['logs']['stepsLog'][0]['lines']
        return data

    # Only need `i_like_gitea` cookie to download artifacts.
    def getArtifactUrl(self, artifactFileName):
        return f'{self.runUrl}/artifacts/{artifactFileName}'

    # Only need `i_like_gitea` cookie to download logs.
    def getLogsUrl(self):
        return f'{self.runUrl}/jobs/0/logs'
