try:from localstack_ext import config as _config_ext;ACTIVATE_PRO=_config_ext.ACTIVATE_PRO
except ImportError:ACTIVATE_PRO=False