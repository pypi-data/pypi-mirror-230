import requests
import urllib.parse
import json
import yaml
import os

class LuigiTaskClient(object):
    def __init__(self, task_name, scheduler_url=None, **task_params):
        self.task_name = task_name
        self.task_params = task_params
        self._scheduler_url = scheduler_url
        self.tasks = {}

    def _match_task_params(self, **params):
        for key, value in self.task_params.items():
            if params.get(key, None) != value:
                return False
        return True

    @property
    def scheduler_url(self):
        if self._scheduler_url is not None:
            return self._scheduler_url
        return os.environ.get("SCHEDULER_URL", "http://127.0.0.1:8082")

    def get_tasks(self, all=False):
        if not self.tasks or all:
            tasks = requests.get(
                self.scheduler_url
                + "/api/task_list?data=" +
                urllib.parse.quote(json.dumps({
                    "upstream_status":"","search": self.task_name}))
            ).json()

            for taskid, task in tasks["response"].items():
                if task['name'] != self.task_name: continue
                if not self._match_task_params(**task['params']):
                    continue
                task["id"] = taskid
                self.tasks[taskid] = task
        return self.tasks
    
    def _get_logs(self, all=False):
        tasks = self.get_tasks(all)
        logs = []
        for task_id in tasks.keys():
            status = requests.get(
                os.environ.get("SCHEDULER_URL", "http://127.0.0.1:8082")
                + "/api/get_task_status_message?data=" + urllib.parse.quote(json.dumps({"task_id": task_id}))
            ).json()
            logs.append(status["response"]["statusMessage"])
        return logs

    def get_logs(self, all=False):
        return [log.split("\n") if log else [] for log in self._get_logs()]
    
    def get_logs_yaml(self):
        return [yaml.load(log, Loader=yaml.SafeLoader) if log else [] for log in self._get_logs()]

