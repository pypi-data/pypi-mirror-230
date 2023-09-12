import sys
import os
import importlib.machinery
import importlib.util

if sys.version_info < (3, 9):
    raise ImportError("The lyd library supports only Python 3.9 and above. Please upgrade your Python version.")

# 获取当前模块（即__init__.py）的目录
base_dir = os.path.dirname(os.path.abspath(__file__))

suffix = None
if sys.platform == "win32":
    suffix = f"cp{sys.version_info.major}{sys.version_info.minor}-win_amd64.pyd"
else:
    suffix = f"cpython-{sys.version_info.major}{sys.version_info.minor}-x86_64-linux-gnu.so"

def load_module(mod_name, mod_file):
    # 使用base_dir构建模块的绝对路径
    absolute_path = os.path.join(base_dir, mod_file)
    loader = importlib.machinery.ExtensionFileLoader(mod_name, absolute_path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod

# For lyd_user_client module (loaded as user_client)
user_client = load_module("lyd_user_client", f"lyd_user_client.{suffix}")

# For lyd_system_client module (loaded as system_client)
system_client = load_module("lyd_system_client", f"lyd_system_client.{suffix}")

