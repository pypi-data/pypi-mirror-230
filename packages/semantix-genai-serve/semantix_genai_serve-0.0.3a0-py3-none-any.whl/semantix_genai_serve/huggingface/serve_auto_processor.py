import os
import torch
from abc import ABC, abstractmethod
from typing import Dict, Optional, Type
from transformers import AutoProcessor, BitsAndBytesConfig
from transformers.modeling_utils import PreTrainedModel
from semantix_genai_serve import SemantixTorchKserve

class ServeAutoProcessor(SemantixTorchKserve):

    def __init__(self, checkpoint: str, model_class: Type[PreTrainedModel], 
                 quantized_load: bool = False, name: Optional[str] = None, 
                 base_cache_dir: Optional[str] = None, force_local_load: Optional[bool] = False):
        self._model_class = model_class
        self._quantized_load = quantized_load
        super().__init__(checkpoint, name, base_cache_dir, force_local_load)

    def load(self, checkpoint: str, base_cache_dir: str, force_local_load: bool):
        if not force_local_load:
            model_path = checkpoint
        else :
            base_cache_dir = os.getenv("BASE_CACHE_DIR", "/mnt/models")
            base_cache_dir = os.path.join(base_cache_dir, self._transform_checkpoint_name(checkpoint))
            model_path = os.path.join(base_cache_dir, "model")
        
        self._processor = AutoProcessor.from_pretrained(model_path, local_files_only=force_local_load, device_map={"": self.device})
        # Create an instasnce of self._model_class
        if self._quantized_load:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                llm_int8_skip_modules=["lm_head", "embed_tokens"],
            )
            self._model = self._model_class.from_pretrained(model_path, quantization_config=bnb_config, local_files_only=force_local_load, device_map={"": self.device})
        else:
            self._model = self._model_class.from_pretrained(model_path, local_files_only=force_local_load, device_map={"": self.device})
        self.ready = True

    def _transform_checkpoint_name(self, checkpoint: str):
        """
        Modifies a checkpoint name in the huggingface format (e.g. 'facebook/bart-large-cnn') to a format that can be used as a model name in the Semantix GenAI model registry (e.g. 'models--facebook--bart-large-cnn'

        Args:
            checkpoint (str): The checkpoint name following the huggingface format
        """
        # Replace all '/' characters with '--'
        transformed = checkpoint.replace('/', '--')
        
        # Prepend 'models--' to the transformed string
        return "models--" + transformed
    
    @abstractmethod
    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        pass