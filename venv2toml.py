import os
import sys
from importlib.metadata import distributions
import importlib
from datetime import datetime

# Находим pyvenv.cfg
venv_root = sys.prefix
cfg_path = os.path.join(venv_root, "pyvenv.cfg")

python_version = None
if os.path.exists(cfg_path):
    with open(cfg_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version"):
                python_version = line.strip().split("=")[1].strip()
                break

if not python_version:
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

# Настройки проекта
project_name = "NStor_TOML_generator"
project_version = "0.2.0"
current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
project_description = f"Сгенерировано автоматически {current_time}"

# Установленные пакеты
installed_packages = {d.metadata["Name"].lower(): d.version for d in distributions()}

# Определяем CUDA/CPU для PyTorch
torch_index = "pypi"
torch_url = ""
if "torch" in installed_packages:
    torch_module = importlib.import_module("torch")
    if torch_module.version.cuda:
        cuda_ver = torch_module.version.cuda.replace(".", "")
        torch_index = f"pytorch-cu{cuda_ver}"
        torch_url = f"https://download.pytorch.org/whl/cu{cuda_ver}"
    else:
        torch_index = "pytorch-cpu"
        torch_url = "https://download.pytorch.org/whl/cpu"  # исправлено, чтобы не было пустого url

# Формируем список зависимостей (с отступами для TOML)
dep_lines = []
for pkg, ver in installed_packages.items():
    if pkg in ["torch", "torchvision", "torchaudio"]:
        dep_lines.append(f'\t"{pkg}"')
    else:
        dep_lines.append(f'\t"{pkg}=={ver}"')

dependencies_block = ",\n".join(dep_lines)

# TOML
toml_content = f"""[project]
name = "{project_name}"
version = "{project_version}"
description = "{project_description}"
requires-python = "=={python_version}"
dependencies = [
{dependencies_block},
]

[[tool.uv.index]]
name = "{torch_index}"
url = "{torch_url}"
explicit = true

[tool.uv.sources]
torch = [
  {{ index = "{torch_index}", marker = "platform_system == 'Windows'" }},
]
torchvision = [
  {{ index = "{torch_index}", marker = "platform_system == 'Windows'" }},
]
torchaudio = [
  {{ index = "{torch_index}", marker = "platform_system == 'Windows'" }},
]
"""

with open("pyproject.toml", "w", encoding="utf-8") as f:
    f.write(toml_content)

print("pyproject.toml сгенерирован автоматически из pyvenv.cfg и venv.")
