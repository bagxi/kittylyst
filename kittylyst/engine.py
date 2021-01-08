from typing import Any, Dict
from abc import ABC, abstractmethod


# @TODO: should IEngine be ICallback-based?
class IEngine(ABC):
    """
    An abstraction that syncs experiment run with
    different hardware-specific configurations.

    - cpu
    - single-gpu
    - multi-gpu
    - amp (nvidia, torch)
    - ddp (torch, etc)
    """

    @property
    @abstractmethod
    def rank(self) -> int:
        pass

    @property
    @abstractmethod
    def world_size(self) -> int:
        # only for ddp
        pass

    @abstractmethod
    def sync_device(self, tensor_or_module: Any) -> Any:
        pass
        # return any2device(batch, self.device)

    @abstractmethod
    def sync_tensor(self, tensor: Any) -> Any:
        pass

    @abstractmethod
    def init_components(
        self,
        model_fn=None,
        criterion_fn=None,
        optimizer_fn=None,
        scheduler_fn=None,
    ):
        pass

    @abstractmethod
    def deinit_components(self):
        # only for ddp
        pass

    @abstractmethod
    def pack_checkpoint(
        self,
        model=None,
        criterion=None,
        optimizer=None,
        scheduler=None,
        **kwargs,
    ) -> Dict:
        pass

    @abstractmethod
    def unpack_checkpoint(
        self,
        checkpoint: Dict,
        model=None,
        criterion=None,
        optimizer=None,
        scheduler=None,
        **kwargs,
    ) -> None:
        pass

    @abstractmethod
    def save_checkpoint(self, checkpoint: Dict, path: str) -> None:
        pass

    @abstractmethod
    def load_checkpoint(self, path: str) -> Dict:
        pass

    @abstractmethod
    def zero_grad(self, model, optimizer) -> None:
        pass
        model.zero_grad()

    @abstractmethod
    def optimizer_step(self, model, optimizer) -> None:
        pass


class Engine(IEngine):
    @property
    def rank(self) -> int:
        return -1

    @property
    def world_size(self) -> int:
        return 1

    def sync_device(self, tensor_or_module: Any) -> Any:
        return tensor_or_module

    def sync_tensor(self, tensor: Any) -> Any:
        return tensor

    def init_components(
        self,
        model_fn=None,
        criterion_fn=None,
        optimizer_fn=None,
        scheduler_fn=None,
    ):
        model = model_fn()
        criterion = criterion_fn()
        optimizer = optimizer_fn(model=model)
        scheduler = scheduler_fn(optimizer=optimizer)
        return model, criterion, optimizer, scheduler

    def deinit_components(self):
        pass

    def pack_checkpoint(
        self,
        model=None,
        criterion=None,
        optimizer=None,
        scheduler=None,
        **kwargs,
    ) -> Dict:
        return {
            "model": model,
            "criterion": criterion,
            "optimizer": optimizer,
            "scheduler": scheduler,
            **kwargs,
        }

    def unpack_checkpoint(
        self,
        checkpoint: Dict,
        model=None,
        criterion=None,
        optimizer=None,
        scheduler=None,
        **kwargs,
    ) -> None:
        model = checkpoint["model"]
        criterion = checkpoint["criterion"]
        optimizer = checkpoint["optimizer"]
        scheduler = checkpoint["scheduler"]

    def save_checkpoint(self, checkpoint: Dict, path: str) -> None:
        print("checkpoint saved at ", path)
        self._checkpoint_dump = checkpoint  # @TODO: only for test purposes

    def load_checkpoint(self, path: str) -> Dict:
        print("checkpoint loaded from ", path)
        return self._checkpoint_dump

    def zero_grad(self, model, optimizer) -> None:
        model.zero_grad()

    def optimizer_step(self, model, optimizer) -> None:
        optimizer.step()