import yaml
import luigi.contrib.opener
import os
from . import gcs_opener
from . import luigi_client

# Valid values for status is
# None: Not started yet
# "running": The pipeline is currently running
# "done": The pipeline succeeded
# "failed": The pipeline failed

class PoltergustPipelineClient(object):
    def __init__(self,
                 pipeline_url = None,
                 
                 task_name = None,
                 task_params = {},

                 name = None,
                 output_url = None,
                 log_url = None,
    
                 environment = None,
                 variables = {},

                 status = None,
                 set_status = lambda status: status):

        self.pipeline_url = pipeline_url or os.environ.get("PIPELINE_URL", "./pipelines")
        
        self.name = name
        self.output_url = output_url
        self.log_url = log_url

        self.task_name = task_name
        self.task_params = task_params

        self.environment = environment
        self.variables = variables
    
        self._status = status
        self.set_status = set_status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self.set_status(value)
        self._status = value
        
    @property
    def url(self):
        return "%s.config.yaml" % (self.base_url,)

    @property
    def base_url(self):
        return "%s/%s" % (self.pipeline_url, self.name)

    @property
    def _task_name(self):
        return self.task_name.rsplit(".", 1)[1]
    
    @property
    def _task_module(self):
        return self.task_name.rsplit(".", 1)[0]
    
    @property
    def config(self):
        task = {
            "name": self._task_name,
            "module": self._task_module,
        }
        task.update(self.task_params)
        return {
            "environment": self.environment,
            "task": task,
            "variables": self.variables
        }
    
    def launch(self):
        with luigi.contrib.opener.OpenerTarget(self.url).open("w") as f:
            yaml.dump(self.config, f)

        self.status = "running"

    def cancel(self):
        luigi.contrib.opener.OpenerTarget(self.url).remove()
        
        self.status = None

    def get_loggers(self):
        if not hasattr(self, "loggers"):
            self.loggers = {
                "MakeEnvironment": luigi_client.LuigiTaskClient("MakeEnvironment", path=self.environment),
                "RunTask": luigi_client.LuigiTaskClient("RunTask", path=self.base_url),
                "Task":luigi_client.LuigiTaskClient(
                    self._task_name,
                    **{key.replace("-", "_"): value for key, value in self.task_params.items()}),
            }
        return self.loggers

    def update_status(self):
        if luigi.contrib.opener.OpenerTarget(self.output_url).exists():
            self.status = "done"
        elif luigi.contrib.opener.OpenerTarget("%s.error.yaml" % (self.base_url,)).exists():
            self.status = "failed"
    
    def get_log(self):
        logs = self.get_logs()
        return [logitem for log in logs.values() for logitem in log]

    @property
    def log_target(self):
        return luigi.contrib.opener.OpenerTarget(self.log_url)
    
    def get_logs(self):
        def flatten_logs(logs):
            return [logitem for log in logs for logitem in log]
        res = {}
        if self.status == "running":
            loggers = self.get_loggers()
            res["MakeEnvironment"] = flatten_logs(self.get_loggers()["MakeEnvironment"].get_logs())
            res["RunTask"] = flatten_logs(self.get_loggers()["RunTask"].get_logs())
            res["Task"] = flatten_logs(self.get_loggers()["Task"].get_logs_yaml())
        elif self.status is not None:
            try:
                with self.log_target.open() as f:
                    res["Task"] = yaml.load(f, Loader=yaml.SafeLoader)
            except:
                pass
            res["RunTask"] = []
            for url in self.log_target.fs.list_wildcard("%s.*.log.txt" % (self.base_url,)):
                with luigi.contrib.opener.OpenerTarget(url).open() as f:
                    res["RunTask"].append(f.read().split("\n"))
            res["RunTask"] = flatten_logs(res["RunTask"])
        #elif self.status is None:
        #    pass
            
        return res
