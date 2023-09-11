import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ezconfig_client import loader


# from ezconfig_client import loader

res = loader.get_latest_config()

print(res['version'])
print(res['config_data'])
print(res['config_hash'])
