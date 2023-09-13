"""
A simple json-line-logger
"""
from .version import __version__
import time
import json
import os
import pandas as pd
import shutil
import logging
import sys
import inspect


DATEFMT_ISO8601 = "%Y-%m-%dT%H:%M:%S"
FMT = "{"
FMT += '"t":"%(asctime)s.%(msecs)03d"'
FMT += ", "
FMT += '"c":"%(pathname)s:%(funcName)s:%(lineno)s"'
FMT += ", "
FMT += '"l":"%(levelname)s"'
FMT += ", "
FMT += '"m":"%(message)s"'
FMT += "}"


def LoggerStdout(name="stdout"):
    return LoggerStream(stream=sys.stdout, name=name)


def LoggerStream(stream=sys.stdout, name="stream"):
    lggr = logging.Logger(name=name)
    fmtr = logging.Formatter(fmt=FMT, datefmt=DATEFMT_ISO8601)
    stha = logging.StreamHandler(stream)
    stha.setFormatter(fmtr)
    lggr.addHandler(stha)
    lggr.setLevel(logging.DEBUG)
    return lggr


def LoggerFile(path, name="file"):
    lggr = logging.Logger(name=name)
    file_handler = logging.FileHandler(filename=path, mode="w")
    fmtr = logging.Formatter(fmt=FMT, datefmt=DATEFMT_ISO8601)
    file_handler.setFormatter(fmtr)
    lggr.addHandler(file_handler)
    lggr.setLevel(logging.DEBUG)
    return lggr


class TimeDelta:
    def __init__(self, logger, name, level=logging.INFO):
        self.logger = logger
        self.name = name
        self.level = level

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop = time.time()
        self.logger.log(
            level=self.level,
            msg=self.name + ":delta:{:f}".format(self.delta()),
        )

    def delta(self):
        return self.stop - self.start


def reduce(list_of_log_paths, out_path):
    log_records = reduce_into_records(list_of_log_paths=list_of_log_paths)
    log_df = pd.DataFrame(log_records)
    log_df = log_df.sort_values(by=["run_id"])
    log_df.to_csv(out_path + ".tmp", index=False, na_rep="nan")
    shutil.move(out_path + ".tmp", out_path)


def reduce_into_records(list_of_log_paths):
    list_of_log_records = []
    for log_path in list_of_log_paths:
        run_id = int(os.path.basename(log_path)[0:6])
        run = {"run_id": run_id}

        key = ":delta:"
        with open(log_path, "rt") as fin:
            for line in fin:
                logline = json.loads(line)
                if "m" in logline:
                    msg = logline["m"]
                    if key in msg:
                        iname = str.find(msg, key)
                        name = msg[:(iname)]
                        deltastr = msg[(iname + len(key)) :]
                        run[name] = float(deltastr)
            list_of_log_records.append(run)

    return list_of_log_records


class MapAndReducePoolWithLogger:
    def __init__(self, pool, logger):
        self.pool = pool
        self.logger = logger

    def accepts_logger(self):
        signature = inspect.signature(self.pool.map)
        return "logger" in signature.parameters

    def map(self, function, jobs):
        if self.accepts_logger():
            return self.pool.map(function, jobs, logger=self.logger)
        else:
            return self.pool.map(function, jobs)
