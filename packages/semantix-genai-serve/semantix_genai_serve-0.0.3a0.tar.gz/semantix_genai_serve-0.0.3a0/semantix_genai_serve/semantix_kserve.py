import os
import kserve
import torch
import logging
from abc import abstractmethod
from typing import Optional, Dict

class SemantixTorchKserve(kserve.Model):

    def __init__(self, checkpoint: str, name: Optional[str] = None, base_cache_dir: Optional[str] = None,
                 force_local_load: Optional[bool] = False):
        if name is None:
            name = os.getenv("PREDICTOR_NAME", "predictor")
        super().__init__(name)
        default_cache_dir_on_remote = os.getenv("BASE_CACHE_DIR", "/mnt/models")
        if base_cache_dir is None:
            base_cache_dir = default_cache_dir_on_remote
        self.name = name

        if torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

        if "STORAGE_URI" in os.environ:
            if force_local_load:
                logging.warning("STORAGE_URI is set, but force_local_load is True, will change force_local_load to False")
                force_local_load = False
            if base_cache_dir is not None:
                logging.warning("STORAGE_URI is set, but base_cache_dir is not None, will ignore base_cache_dir")
                base_cache_dir = default_cache_dir_on_remote
        self.checkpoint = checkpoint
        self.load(checkpoint, base_cache_dir, force_local_load)
    
    @abstractmethod
    def load(self, checkpoint: str, base_cache_dir: str, force_local_load: bool):
        pass
    
    @abstractmethod
    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        pass

    def start_server(self):
        num_workers = os.getenv("NUM_WORKERS", 1)
        kserve.ModelServer(workers=num_workers).start([self])