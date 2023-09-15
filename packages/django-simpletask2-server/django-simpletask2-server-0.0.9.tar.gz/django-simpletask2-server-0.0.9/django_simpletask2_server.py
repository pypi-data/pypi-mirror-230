import re
import time
import json
import logging
import threading
import urllib
import base64

import requests
import click
import redis
from fastutils import logutils
from daemon_application import DaemonApplication

logger = logging.getLogger(__name__)

class DjangoSimpleTask2Server(DaemonApplication):
    default_config = {
        "server": "http://127.0.0.1:8000/django-simpletask2/",
        "redis": "redis://localhost:6379/0?decode_responses=True",
        "channels": "default",
        "channel-name-template": "django-simpletask2:channels:{channel}",
        "channel-name-strip-regex": "^django-simpletask2:channels:(?P<channel>.*)$",
        "channel-flags-template": "django-simpletask2:flags:{channel}",
        "task-pull-engine": "redis",
        "task-pull-timeout": 5,
        "do-auto-reset-task": True,
        "auto-reset-task-interval": 60,
        "threads": 1,
        "idle-sleep": 5,
        "error-sleep": 5,
        "pidfile": "django-simpletask2-server.pid",
        "logfile": "django-simpletask2-server.log"
    }
    def get_main_options(self):
        options = [
            click.option("-s", "--server"),
            click.option("-a", "--aclkey"),
            click.option("-r", "--redis"),
            click.option("--channels"),
            click.option("--channel-name-template"),
            click.option("--channel-name-strip-regex"),
            click.option("--channel-flags-template"),
            click.option("--task-pull-engine"),
            click.option("--task-pull-timeout", type=int),
            click.option("--do-auto-reset-task/--no-do-auto-reset-task", is_flag=True, default=None),
            click.option("--auto-reset-task-interval", type=int),
            click.option("-t", "--threads", type=int),
            click.option("--idle-sleep", type=int),
            click.option("--error-sleep", type=int),
        ]
        return options + super().get_main_options()

    def get_redis_connection(self):
        return redis.from_url(self.config["redis"])

    def main(self):
        logutils.setup(**self.config)
        logger.info("DjangoSimpleTask2Server starts with config: {config}".format(config=json.dumps(self.config)))
        if self.config["do-auto-reset-task"]:
            do_auto_reset_task_thread = threading.Thread(target=self.do_auto_reset_task)
            do_auto_reset_task_thread.setDaemon(True)
            do_auto_reset_task_thread.start()
        for _ in range(self.config["threads"] - 1):
            worker = threading.Thread(target=self.do_task)
            worker.setDaemon(True)
            worker.start()
        self.do_task()

    def do_auto_reset_task(self):
        while True:
            try:
                self._do_auto_reset_task()
            except Exception as error:
                logger.error("do_auto_reset_task failed: error={error}.".format(error=str(error)))
            time.sleep(self.config["auto-reset-task-interval"])

    def _do_auto_reset_task(self):
        do_auto_reset_task_url = urllib.parse.urljoin(self.config["server"], "./do_auto_reset")
        params = {
            "aclkey": self.config["aclkey"],
        }
        logger.debug("do_auto_reset_task calling api: url={url}, params={params}".format(url=do_auto_reset_task_url, params=json.dumps(params)))
        response = requests.post(do_auto_reset_task_url, json=params)
        logger.debug("do_auto_reset_task call api got response: {content}.".format(content=response.content))
        try:
            response_data = json.loads(response.content)
        except Exception as error:
            logger.warning("do_auto_reset_task call api got NON-json response: error={error}, response.content={content}.".format(error=str(error), content=response.content))
            return False
        if not response_data["success"]:
            logger.warning("do_auto_reset_task call api got NON-success response: {response_data}.".format(response_data=json.dumps(response_data)))
        else:
            logger.info("do_auto_reset_task call api got success response: {response_data}.".format(response_data=json.dumps(response_data)))
        return True

    def do_task(self):
        error_sleep = self.config["error-sleep"]
        idle_sleep = self.config["idle-sleep"]
        while True:
            try:
                result = self.do_a_task()
            except Exception as error:
                result = False
                logger.exception("do_a_task got error: {error}!".format(error=str(error)))
                time.sleep(error_sleep)
            if result is None:
                time.sleep(idle_sleep)

    def get_a_task_from_redis(self):
        try:
            redis_conn = self.get_redis_connection()
            channel_name_template = self.config["channel-name-template"]
            channels = [channel_name_template.format(channel=channel) for channel in self.config["channels"].split(",")]
            task = redis_conn.blpop(channels, timeout=self.config["task-pull-timeout"])
            if not task:
                logger.debug("got NO task whiling pulling task from channels: {channels}".format(channels=channels))
                return None
            else:
                logger.debug("got task {task}.".format(task=task))
            channel_fullname, task_info = task
            channel = re.match(self.config["channel-name-strip-regex"], channel_fullname).groupdict()["channel"]
            channel_flags = self.config["channel-flags-template"].format(channel=channel)
            redis_conn.srem(channel_flags, task_info)
            return task_info
        except Exception as error:
            logger.error("get_a_task_from_redis failed: {error}".format(error=str(error)))
            return None

    def get_a_task_from_service(self):
        try:
            get_a_task_url = urllib.parse.urljoin(self.config["server"], "./get_a_task")
            params = {
                "aclkey": self.config["aclkey"],
                "channels": self.config["channels"],
            }
            response = requests.post(get_a_task_url, json=params)
            response_data = json.loads(response.content)
            return response_data["result"]
        except Exception as error:
            logger.error("get_a_task_from_service failed: {error}".format(error=str(error)))
            return None

    def get_a_task(self):
        if self.config["task-pull-engine"] == "redis":
            return self.get_a_task_from_redis()
        else:
            return self.get_a_task_from_service()
    
    def do_a_task(self):
        task_info = self.get_a_task()
        if not task_info:
            return None

        do_task_url = urllib.parse.urljoin(self.config["server"], "./do_task")
        params = {
            "aclkey": self.config["aclkey"],
            "task_info": task_info,
            "step": 1,
        }
        logger.debug("calling do_task api: url={url}, params={params}".format(url=do_task_url, params=json.dumps(params)))
        response = requests.post(do_task_url, json=params)
        logger.debug("calling do_task api go result: {}".format(response.content))
        response_data = json.loads(response.content)
        if response_data["error"]["code"] == 0:
            if not response_data["result"]["continue_flag"]:
                logger.info("task done, task_info={task_info}!".format(task_info=task_info))
            else:
                logger.info("task needs more works to do, task_info={task_info}...".format(task_info=task_info))
                result = self.task_do_more_work(task_info, response_data)
                if result:
                    logger.info("task done, task_info={task_info}!".format(task_info=task_info))
                    return True
                else:
                    logger.info("task failed while doing extra works, task_info={task_info}!".format(task_info=task_info))
                    return False
        else:
            logger.warning("task failed at server side: task_info={task_info}, response_data={response_data}.".format(task_info=task_info, response_data=response_data))
            return False

    def task_do_more_work(self, task_info, response_data):
        while response_data["error"]["code"] == 0 and response_data["result"]["continue_flag"]:
            step = response_data["result"]["next_step"]
            logger.debug("task {task_info} doing step {step}.".format(task_info=task_info, step=step))
            do_task_url = urllib.parse.urljoin(self.config["server"], "./do_task")
            params = {
                "aclkey": self.config["aclkey"],
                "task_info": response_data["result"]["task_info"],
                "step": response_data["result"]["next_step"],
                "proxied_content": None,
            }
            proxy = response_data.get("result", {}).get("data", {}).get("proxy", None)
            if proxy:
                try:
                    logger.debug("task {task_info} needs a proxy request, proxy settings: {proxy}".format(task_info=task_info, proxy=proxy))
                    response = requests.request(**proxy)
                    logger.debug("task {task_info} proxy request got response: {content}.".format(task_info=task_info, content=response.content))
                    params["proxied_content"] = base64.encodebytes(response.content).decode("utf-8")
                    params["proxied_error"] = None
                except Exception as error:
                    params["proxied_content"] = None
                    params["proxied_error"] = "task {task_info} proxy request failed: proxy={proxy}, error={error}.".format(task_info=task_info, proxy=proxy, error=str(error))
            logger.debug("task {task_info} calling do_task api to do step {step} with url={url}, params={params}".format(task_info=task_info, step=step, url=do_task_url, params=params))
            response = requests.post(do_task_url, json=params)
            logger.debug("task {task_info} calling do_task api got response: {content}".format(task_info=task_info, content=response.content))
            response_data = json.loads(response.content)
        if response_data["error"]["code"] != 0:
            logger.warning("task {task_info} calling to_task api got bad response: {content}".format(task_info=task_info, content=json.dumps(response_data)))
            return False
        else:
            return True

controller = DjangoSimpleTask2Server().get_controller()

if __name__ == "__main__":
    controller()
