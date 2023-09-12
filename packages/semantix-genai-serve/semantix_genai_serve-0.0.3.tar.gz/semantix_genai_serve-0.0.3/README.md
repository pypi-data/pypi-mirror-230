# Semantix GenAI Serve

Semantix GenAI Serve is a library designed for users of Semantix GenAI Hub to create their own servers running AI models. This library provides an easy-to-use interface for serving AI models using the scalable infrastructure of Semantix GenAI Hub.

## Features

- Easy integration with Hugging Face Transformers models
- Support for serving Seq2Seq models
- Customizable server settings
- Built-in support for GPU acceleration

## Installation

To install the Semantix GenAI Serve library, run the following command:

```bash
pip install semantix-genai-serve
```

## Usage

### Basic Example

Here's a simple example of how to use the Semantix GenAI Serve library to serve a Hugging Face Transformers model:

```python
from semantix_genai_serve import SemantixTorchKserve
from semantix_genai_serve.huggingface import ServeAutoSeq2SeqLM

class MyModel(ServeAutoSeq2SeqLM):
    def predict(self, payload, headers):
        # Implement your custom inference logic here
        pass

model = MyModel(checkpoint="facebook/bart-large-cnn")
model.start_server()
```

### Customizing Server Settings

You can customize the server settings by passing additional arguments to the `SemantixTorchKserve` constructor:

```python
model = MyModel(
    checkpoint="facebook/bart-large-cnn",
    name="my_model",
    base_cache_dir="/path/to/cache",
    force_local_load=True
)
```

- `name`: The name of the predictor (default: "predictor")
- `base_cache_dir`: The base directory for caching models (default: "/mnt/models"). Do not change that when deploying to Semantix GenAI Hub.
- `force_local_load`: If set to `True`, the model will be loaded from the local cache directory instead of downloading from Hugging Face's model hub (default: `False`). Do not change that when deploying to Semantix GenAI Hub.

### Implementing Custom Inference Logic

To implement custom inference logic, you need to override the `predict` method in your model class:

```python
class MyModel(ServeAutoSeq2SeqLM):
    def predict(self, payload, headers):
        # Implement your custom inference logic here
        input_example = payload["input_example"]
        # do something for inference
        # your output must be a dictionary so it gets automatically converted to JSON
        return {"response": "output"}
```

## Contributing

We welcome contributions to the Semantix GenAI Serve library! If you have any suggestions, bug reports, or feature requests, please open an issue on our GitHub repository.

## License

Semantix GenAI Serve is released under the [MIT License](LICENSE.txt).
