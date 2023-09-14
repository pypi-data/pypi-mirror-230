# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exa', 'exa.inference', 'exa.quant']

package_data = \
{'': ['*']}

install_requires = \
['shapeless', 'transformers']

setup_kwargs = {
    'name': 'exxa',
    'version': '0.0.4',
    'description': 'Exa - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Exa\nUltra-optimized fast inference library for running exascale LLMs locally on modern consumer-class GPUs.\n\n## Principles\n- Radical Simplicity (Utilizing super-powerful LLMs with as minimal code as possible)\n- Ultra-Optimizated (High Performance classes that extract all the power from these LLMs)\n- Fludity & Shapelessness (Plug in and play and re-architecture as you please)\n\n---\n\n# 🤝 Schedule a 1-on-1 Session\nBook a [1-on-1 Session with Kye](https://calendly.com/apacai/agora), the Creator, to discuss any issues, provide feedback, or explore how we can improve Zeta for you.\n\n---\n\n## 📦 Installation 📦\nYou can install the package using pip\n\n```bash\npip install exxa\n```\n-----\n\n\n\n# Usage\n\n## Inference\n```python\nfrom exa import Inference\n\nmodel = Inference(\n    model_id="georgesung/llama2_7b_chat_uncensored",\n    quantized=True\n)\n\nmodel.run("What is your name")\n```\n\n\n## GPTQ Inference\n\n```python\n\nfrom exa import GPTQInference\n\nmodel_id = "facebook/opt-125m"\nmodel = GPTQInference(model_id=model_id, max_length=400)\n\nprompt = "in a land far far away"\nresult = model.run(prompt)\nprint(result)\n\n```\n\n## Quantize\n\n```python\nfrom exa import Quantize\n\n#usage\nquantize = Quantize(\n     model_id="bigscience/bloom-1b7",\n     bits=8,\n     enable_fp32_cpu_offload=True,\n)\n\nquantize.load_model()\nquantize.push_to_hub("my model")\nquantize.load_from_hub(\'my model\')\n\n\n```\n\n-----\n\n## 🎉 Features 🎉\n\n- **World-Class Quantization**: Get the most out of your models with top-tier performance and preserved accuracy! 🏋️\u200d♂️\n  \n- **Automated PEFT**: Simplify your workflow! Let our toolkit handle the optimizations. 🛠️\n\n- **LoRA Configuration**: Dive into the potential of flexible LoRA configurations, a game-changer for performance! 🌌\n\n- **Seamless Integration**: Designed to work seamlessly with popular models like LLAMA, Falcon, and more! 🤖\n\n----\n\n## 💌 Feedback & Contributions 💌\n\nWe\'re excited about the journey ahead and would love to have you with us! For feedback, suggestions, or contributions, feel free to open an issue or a pull request. Let\'s shape the future of fine-tuning together! 🌱\n\n------\n\n\n# License\nMIT\n\n\n\n',
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
