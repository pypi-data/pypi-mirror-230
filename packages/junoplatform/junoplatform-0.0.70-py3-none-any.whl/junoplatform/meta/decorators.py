"""decorators.py: decorator class and functions for junoplatform"""
__author__ = "Bruce.Lu"
__email__ = "lzbgt@icloud.com"
__time__ = "2023/07/20"


import logging
from collections import deque
from urllib.parse import parse_qs
import traceback
import json
import os
import time
import datetime
from functools import wraps
from junoplatform.log import logger
from junoplatform.io.utils import JunoConfig, junoconfig
from junoplatform.io import InputConfig, Storage, DataSet
from threading import Thread, Lock
import numpy as np


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(filename)s %(lineno)d - %(message)s')


class EntryPoint:
    def __init__(self, cfg_in: str | InputConfig, detached: bool = False):
        super(EntryPoint, self).__init__()
        self.cfg_in: InputConfig
        self.detached = detached
        self.storage = Storage()
        # self.dataset = DataSet()
        self.ready = False
        self.que = deque(maxlen=2000)
        self.stop_flag = False
        self.config_lock = Lock()
        self.enable_key = f"system.{junoconfig['plant']}.{junoconfig['module']}.enable"
        if isinstance(cfg_in, str):
            logging.debug(f"loading input spec from file: {cfg_in}")
            try:
                with open(cfg_in, "r", encoding="utf-8") as f:
                    self.cfg_in = InputConfig(**json.load(f))
            except Exception as e:
                msg = f"error in input.json: {e}"
                logger.error(msg)
                exit(1)
        elif isinstance(self.cfg_in, InputConfig):
            logging.info(f"loading input spec from class: {cfg_in}")
            self.cfg_in = cfg_in
        else:
            raise Exception(
                f"cfg_in must be type of InputConfig or string, but provides: {type(self.cfg_in)}")

    def _thread(self, func):
        while True:
            try:
                self.dataset = DataSet()
            except Exception as e:
                logging.error(
                    "fault: failed to create DataSet to clickhouse, will retry in 7 seconds")
                time.sleep(7)
                continue

            self.ready = True
            delay = self.cfg_in.sched_interval
            enable = self.storage.local.read(self.enable_key, cast=int)
            if enable is None:
                enable = 1
            self.stop_flag = not bool(enable)

            if not self.stop_flag:
                self.config_lock.acquire()
                newcfg = JunoConfig()
                self.config_lock.release()
                algo_cfg = newcfg["algo_cfg"]
                logging.info(f"running algo with {algo_cfg}")

                ts = datetime.datetime.now().timestamp()
                if self.cfg_in.items:
                    data, timestamps, names = self.dataset.fetch(
                        tags=self.cfg_in.tags, num=self.cfg_in.items)
                elif self.cfg_in.minutes:
                    time_from = datetime.datetime.now() - datetime.timedelta(minutes=self.cfg_in.minutes)
                    data, timestamps, names = self.dataset.fetch(
                        tags=self.cfg_in.tags, time_from=time_from)
                else:
                    raise Exception("invalid InputConfig")

                td = datetime.datetime.now().timestamp()
                logging.info(f"time used fetching dataset: {td-ts}s")

                try:
                    func(self.storage, algo_cfg, data, timestamps, names)
                except Exception as e:
                    msg = traceback.format_exc()
                    logger.error(f"{e}: {msg}")

                # TODO: output
                te = datetime.datetime.now().timestamp()
                logging.info(f"time used running algo: {te-td}s")

                delay = self.cfg_in.sched_interval - (te - ts) - 0.003
                logging.debug(
                    f"delay in seconds to make up a full sched_interval: {delay}")
                if delay < 0:
                    delay = 0
            else:
                logging.info("module disabled, skip run algo func")

            del self.dataset

            time.sleep(delay)

    def s_get_bool(self, v: str):
        try:
            x = int(v)
            return x != 0
        except:
            if v.lower() in ["t", "true", "y", "yes", "ok", "on", "enable", "active"]:
                return True
            else:
                return False

    def _pulsar(self):
        itopic = f"jprt-down-{junoconfig['plant']}-{junoconfig['module']}"
        while True:
            msg = self.storage.cloud.read(itopic, shared=False)
            data = {}
            logger.info(f"command received: {msg.data()}")
            try:
                data = json.loads(msg.data())
                if "package_id" not in data or junoconfig['package_id'] != data["package_id"]:
                    logger.error(
                        f"invalid msg received {data}, self package_id: {junoconfig['package_id']}")
                    self.storage.cloud.consumers[itopic].acknowledge(msg)
                    continue
            except:
                logger.error(f"invalid msg received: {msg.data()}")
                self.storage.cloud.consumers[itopic].acknowledge(msg)
                continue

            if "cmd" in data:
                if data["cmd"] == "enable":
                    cmd = parse_qs(data['qs'])
                    v = cmd.get('enable', [''])[0]
                    if v:
                        enable = self.s_get_bool(v)
                        if not enable:
                            self.stop_flag = True
                            logging.info("enable=false cmd received")
                        else:
                            self.stop_flag = False
                            logging.info("enable=true cmd received")

                        data = {"enable": enable,
                                "et": datetime.datetime.now().timestamp()*1000, "kind": "1", "package_id": data["package_id"]}
                        self.storage.cloud.write("module_state_new", data)
                        self.storage.local.write(self.enable_key, int(enable))
                elif data["cmd"] == "reconfig":
                    config = data["data"]["config"]
                    self.config_lock.acquire()
                    with open('config.json', 'w', encoding='utf-8') as f:
                        json.dump(config, f)
                    self.config_lock.release()

            else:
                logging.error(f"unkown msg: {data}")

            self.storage.cloud.consumers[itopic].acknowledge(msg)

    def _heart_beat(self):
        while True:
            data = {"enable": not self.stop_flag,
                    "et": datetime.datetime.now().timestamp()*1000, "kind": "0", "package_id": junoconfig["package_id"]}
            self.storage.cloud.write("module_state_new", data)

            # heartbeat interval is 1 minutes
            time.sleep(60)

    def __call__(self, func):
        th = Thread(target=self._thread, args=(func,))
        th.start()

        while not self.ready:
            time.sleep(0)

        pt = Thread(target=self._pulsar)
        pt.start()

        hb = Thread(target=self._heart_beat)
        hb.start()


def auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not os.path.exists(args[0].juno_dir) or not os.path.exists(args[0].juno_file):
            logger.error(f"user not authenticationd.\n\
                          please run `junocli login [api_url]` to use your shuhan account")
            os.makedirs(args[0].juno_dir, exist_ok=True)
            return -1
        return func(*args, **kwargs)

    return wrapper
