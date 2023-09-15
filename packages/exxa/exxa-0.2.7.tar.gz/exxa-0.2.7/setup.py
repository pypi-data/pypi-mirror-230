# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exa', 'exa.benchmarking', 'exa.inference', 'exa.quant', 'exa.utils']

package_data = \
{'': ['*']}

install_requires = \
['accelerate',
 'auto-gptq',
 'bitsandbytes',
 'diffusers',
 'optimum',
 'termcolor',
 'transformers']

setup_kwargs = {
    'name': 'exxa',
    'version': '0.2.7',
    'description': 'Exa - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Exa\nBoost your GPU\'s LLM performance by 300% on everyday GPU hardware, as validated by renowned developers, in just 5 minutes of setup and with no additional hardware costs.\n\n-----\n\n## Principles\n- Radical Simplicity (Utilizing super-powerful LLMs with as minimal lines of code as possible)\n- Ultra-Optimizated Peformance (High Performance code that extract all the power from these LLMs)\n- Fludity & Shapelessness (Plug in and play and re-architecture as you please)\n\n---\n\n# 🤝 Schedule a 1-on-1 Session\nBook a [1-on-1 Session with Kye](https://calendly.com/apacai/agora), the Creator, to discuss any issues, provide feedback, or explore how we can improve Exa for you.\n\n---\n\n## 📦 Installation 📦\nYou can install the package using pip\n\n```bash\npip install exxa\n```\n-----\n\n\n\n# Usage\n\n## Inference\nGenerate text using pretrained models with optional quantization with minimal configuration and straightforward usage.\n\n- Load specified pre-trained models with device flexibility (CPU/CUDA).\n- Set a default maximum length for the generated sequences.\n- Choose to quantize model weights for faster inference.\n- Use a custom configuration for quantization as needed.\n- Generate text through either a direct call or the run method.\n- Simple usage for quick text generation based on provided prompts.\n\n```python\nfrom exa import Inference\n\nmodel = Inference(\n    model_id="georgesung/llama2_7b_chat_uncensored",\n    quantized=True\n)\n\nmodel.run("What is your name")\n```\n\n\n## GPTQ Inference\nEfficiently generate text using quantized GPT-like models built for HuggingFace\'s pre-trained models with optional quantization and only a few lines of code for instantiation and generation.\n\n- Load specified pre-trained models with an option for quantization.\n- Define custom bit depth for the quantization (default is 4 bits).\n- Fine-tune quantization parameters using specific datasets.\n- Set maximum length for generated sequences to maintain consistency.\n- Tokenize prompts and generate text based on them seamlessly.\n\n```python\n\n# !pip install exxa\nfrom exa import GPTQInference\n\nmodel_id = "gpt2-medium"\ninference = GPTQInference(\n    model_id, \n    quantization_config_bits=2, \n    max_length=400, \n    quantization_config_dataset=\'c4\'\n)\noutput_text = inference.run("The future of AI is")\nprint(output_text)\n```\n\n## Quantize\nAchieve smaller model sizes and faster inference by utilizing a unified interface tailored to HuggingFace\'s framework and only a simple class instantiation with multiple parameters is needed.\n- Efficiently quantize HuggingFace\'s pretrained models with specified bits (default is 4 bits).\n- Set custom thresholds for quantization for precision management.\n- Ability to skip specific modules during quantization for sensitive model parts.\n- Offload parts of the model to CPU in FP32 format for GPU memory management.\n- Specify if model weights are already in FP16 format.\n- Choose from multiple quantization types like "fp4", "int8", and more.\n- Option to enable double quantization for more compression.\n- Verbose logging for a detailed understanding of the quantization process.\n- Seamlessly push to and load models from the HuggingFace model hub.\n- In-built logger initialization tailored for quantization logs.\n- Log metadata for state and settings introspection.\n\n\n```python\nfrom exa import Quantize\n\n#usage\nquantize = Quantize(\n     model_id="bigscience/bloom-1b7",\n     bits=8,\n     enable_fp32_cpu_offload=True,\n)\n\nquantize.load_model()\nquantize.push_to_hub("my model")\nquantize.load_from_hub(\'my model\')\n\n\n```\n\n-----\n\n## 🎉 Features 🎉\n\n- **World-Class Quantization**: Get the most out of your models with top-tier performance and preserved accuracy! 🏋️\u200d♂️\n  \n- **Automated PEFT**: Simplify your workflow! Let our toolkit handle the optimizations. 🛠️\n\n- **LoRA Configuration**: Dive into the potential of flexible LoRA configurations, a game-changer for performance! 🌌\n\n- **Seamless Integration**: Designed to work seamlessly with popular models like LLAMA, Falcon, and more! 🤖\n\n----\n\n## 💌 Feedback & Contributions 💌\n\nWe\'re excited about the journey ahead and would love to have you with us! For feedback, suggestions, or contributions, feel free to open an issue or a pull request. Let\'s shape the future of fine-tuning together! 🌱\n\n------\n\n# Benchmarks\nThe following is what we benchmark for according to the [🤗 LLM-Perf Leaderboard 🏋️ benchmarks](https://huggingface.co/spaces/optimum/llm-perf-leaderboard)\n\n\n- https://huggingface.co/spaces/optimum/llm-perf-leaderboard\n- https://github.com/huggingface/optimum-benchmark\n\n## Metrics \n- Backend 🏭\n- Dtype 📥\n- Optimizations 🛠️\n- Quantization 🗜️\n- Class 🏋️\n- Type 🤗\n- Memory (MB) ⬇️\n- Throughput (tokens/s) ⬆️\n- Energy (tokens/kWh) ⬇️\n- Best Score (%) ⬆️\n- Best Scored LLM 🏆\n\n# License\nMIT\n\n# Todo\n\n- Setup utils logger classes for metric logging with useful metadata such as token inference per second, latency, memory consumption\n- Add cuda c++ extensions for radically optimized classes for high performance quantization + inference on the edge\n\n\n\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/Exa',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
