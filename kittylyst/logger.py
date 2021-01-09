from typing import Dict, List
from abc import ABC, abstractmethod
import os

import matplotlib.pyplot as plt
import numpy as np

from kittylyst.misc import format_metrics, save_config


class ILogger(ABC):
    """An abstraction that syncs experiment run with monitoring tools."""

    @abstractmethod
    def log_metrics(
        self,
        metrics: Dict[str, float],
        scope: str = None,
        # experiment info
        experiment_key: str = None,
        global_sample_step: int = 0,
        global_batch_step: int = 0,
        global_epoch_step: int = 0,
        # stage info
        stage_key: str = "infer",
        stage_epoch_len: int = 0,
        stage_epoch_step: int = 0,
        # loader info
        loader_key: str = None,
        loader_batch_len: int = 0,
        loader_batch_step: int = 0,
        loader_sample_step: int = 0,
    ) -> None:
        pass

    @abstractmethod
    def log_image(
        self,
        image: np.ndarray,
        scope: str = None,
        # experiment info
        experiment_key: str = None,
        global_sample_step: int = 0,
        global_batch_step: int = 0,
        global_epoch_step: int = 0,
        # stage info
        stage_key: str = "infer",
        stage_len: int = 0,
        stage_epoch_step: int = 0,
        # loader info
        loader_key: str = None,
        loader_batch_len: int = 0,
        loader_batch_step: int = 0,
        loader_sample_step: int = 0,
    ) -> None:
        pass

    @abstractmethod
    def log_hparams(
        self,
        hparams: Dict,
        scope: str = None,
        # experiment info
        experiment_key: str = None,
    ) -> None:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


# @TODO: scope should be enum
# @TODO: logger could have extra init params for logging level choice
class ConsoleLogger(ILogger):
    # def __init__(self, include: List[str] = None, exclude: List[str] = None):
    #     self.include = include
    #     self.exclude = exclude

    def log_metrics(
        self,
        metrics: Dict[str, float],
        scope: str = None,
        # experiment info
        experiment_key: str = None,
        global_sample_step: int = 0,
        global_batch_step: int = 0,
        global_epoch_step: int = 0,
        # stage info
        stage_key: str = "infer",
        stage_epoch_len: int = 0,
        stage_epoch_step: int = 0,
        # loader info
        loader_key: str = None,
        loader_batch_len: int = 0,
        loader_batch_step: int = 0,
        loader_sample_step: int = 0,
    ) -> None:
        # if self.exclude is not None and scope in self.exclude:
        #     return
        # elif (
        #     self.include is not None and scope in self.include
        # ) or self.include is None:
        if scope == "loader":
            prefix = f"{loader_key} ({stage_epoch_step}/{stage_epoch_len}) "
            msg = prefix + format_metrics(metrics)
            print(msg)

    def log_image(
        self,
        image: np.ndarray,
        scope: str = None,
        # experiment info
        experiment_key: str = None,
        global_sample_step: int = 0,
        global_batch_step: int = 0,
        global_epoch_step: int = 0,
        # stage info
        stage_key: str = "infer",
        stage_len: int = 0,
        stage_epoch_step: int = 0,
        # loader info
        loader_key: str = None,
        loader_batch_len: int = 0,
        loader_batch_step: int = 0,
        loader_sample_step: int = 0,
    ) -> None:
        pass

    def log_hparams(
        self,
        hparams: Dict,
        scope: str = None,
        # experiment info
        experiment_key: str = None,
    ) -> None:
        print(f"Hparams ({experiment_key}): {hparams}")

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass


# @TODO: scope should be enum
# @TODO: logger could have extra init params for logging level choice
class LogdirLogger(ILogger):
    def __init__(self, logdir: str):
        self.logdir = logdir
        self.loggers = {}
        os.makedirs(self.logdir, exist_ok=True)

    def _make_header(self, metrics: Dict[str, float], loader_key: str):
        log_line_header = "step,"
        for metric in sorted(metrics.keys()):
            log_line_header += metric + ","
        log_line_header = (
            log_line_header[:-1] + "\n"
        )  # replace last "," with new line
        self.loggers[loader_key].write(log_line_header)

    def _log_metrics(
        self, metrics: Dict[str, float], step: int, loader_key: str
    ):
        log_line_csv = f"{step},"
        for metric in sorted(metrics.keys()):
            log_line_csv += str(metrics[metric]) + ","
        log_line_csv = (
            log_line_csv[:-1] + "\n"
        )  # replace last "," with new line
        self.loggers[loader_key].write(log_line_csv)

    def log_metrics(
        self,
        metrics: Dict[str, float],
        scope: str = None,
        # experiment info
        experiment_key: str = None,
        global_sample_step: int = 0,
        global_batch_step: int = 0,
        global_epoch_step: int = 0,
        # stage info
        stage_key: str = "infer",
        stage_epoch_len: int = 0,
        stage_epoch_step: int = 0,
        # loader info
        loader_key: str = None,
        loader_batch_len: int = 0,
        loader_batch_step: int = 0,
        loader_sample_step: int = 0,
    ) -> None:
        if scope == "epoch":
            for loader_key, per_loader_metrics in metrics.items():
                if loader_key not in self.loggers.keys():
                    self.loggers[loader_key] = open(
                        os.path.join(self.logdir, f"{loader_key}.csv"), "a+"
                    )
                    self._make_header(
                        metrics=per_loader_metrics, loader_key=loader_key
                    )
                self._log_metrics(
                    metrics=per_loader_metrics,
                    step=stage_epoch_step,
                    loader_key=loader_key,
                )

    def log_image(
        self,
        image: np.ndarray,
        scope: str = None,
        # experiment info
        experiment_key: str = None,
        global_sample_step: int = 0,
        global_batch_step: int = 0,
        global_epoch_step: int = 0,
        # stage info
        stage_key: str = "infer",
        stage_len: int = 0,
        stage_epoch_step: int = 0,
        # loader info
        loader_key: str = None,
        loader_batch_len: int = 0,
        loader_batch_step: int = 0,
        loader_sample_step: int = 0,
    ) -> None:
        if scope == "epoch":
            plt.imsave(
                os.path.join(
                    self.logdir, f"img_{stage_key}_{stage_epoch_step}.png"
                ),
                image,
            )

    def log_hparams(
        self,
        hparams: Dict,
        scope: str = None,
        # experiment info
        experiment_key: str = None,
    ) -> None:
        save_config(
            config=hparams, path=os.path.join(self.logdir, "hparams.yml")
        )

    def flush(self) -> None:
        for logger in self.loggers.values():
            logger.flush()

    def close(self) -> None:
        for logger in self.loggers.values():
            logger.close()
