# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['semantix_genai_serve', 'semantix_genai_serve.huggingface']

package_data = \
{'': ['*']}

install_requires = \
['bitsandbytes==0.41.1', 'kserve==0.11.0', 'transformers>=4.28.0']

setup_kwargs = {
    'name': 'semantix-genai-serve',
    'version': '0.0.3a0',
    'description': '',
    'long_description': '# Semantix GenAI Serve\n\nSemantix GenAI Serve is a library designed for users of Semantix GenAI Hub to create their own servers running AI models. This library provides an easy-to-use interface for serving AI models using the scalable infrastructure of Semantix GenAI Hub.\n\n## Features\n\n- Easy integration with Hugging Face Transformers models\n- Support for serving Seq2Seq models\n- Customizable server settings\n- Built-in support for GPU acceleration\n\n## Installation\n\nTo install the Semantix GenAI Serve library, run the following command:\n\n```bash\npip install semantix-genai-serve\n```\n\n## Usage\n\n### Basic Example\n\nHere\'s a simple example of how to use the Semantix GenAI Serve library to serve a Hugging Face Transformers model:\n\n```python\nfrom semantix_genai_serve import SemantixTorchKserve\nfrom semantix_genai_serve.huggingface import ServeAutoSeq2SeqLM\n\nclass MyModel(ServeAutoSeq2SeqLM):\n    def predict(self, payload, headers):\n        # Implement your custom inference logic here\n        pass\n\nmodel = MyModel(checkpoint="facebook/bart-large-cnn")\nmodel.start_server()\n```\n\n### Customizing Server Settings\n\nYou can customize the server settings by passing additional arguments to the `SemantixTorchKserve` constructor:\n\n```python\nmodel = MyModel(\n    checkpoint="facebook/bart-large-cnn",\n    name="my_model",\n    base_cache_dir="/path/to/cache",\n    force_local_load=True\n)\n```\n\n- `name`: The name of the predictor (default: "predictor")\n- `base_cache_dir`: The base directory for caching models (default: "/mnt/models"). Do not change that when deploying to Semantix GenAI Hub.\n- `force_local_load`: If set to `True`, the model will be loaded from the local cache directory instead of downloading from Hugging Face\'s model hub (default: `False`). Do not change that when deploying to Semantix GenAI Hub.\n\n### Implementing Custom Inference Logic\n\nTo implement custom inference logic, you need to override the `predict` method in your model class:\n\n```python\nclass MyModel(ServeAutoSeq2SeqLM):\n    def predict(self, payload, headers):\n        # Implement your custom inference logic here\n        input_example = payload["input_example"]\n        # do something for inference\n        # your output must be a dictionary so it gets automatically converted to JSON\n        return {"response": "output"}\n```\n\n## Contributing\n\nWe welcome contributions to the Semantix GenAI Serve library! If you have any suggestions, bug reports, or feature requests, please open an issue on our GitHub repository.\n\n## License\n\nSemantix GenAI Serve is released under the [MIT License](LICENSE.txt).\n',
    'author': 'Dev Team',
    'author_email': 'dev@semantix.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
