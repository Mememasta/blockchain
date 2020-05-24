from pathlib import Path
import yaml

class BaseConfig:

    debug = True
    app_name = "BlockChain"
    secret_key = b'TyzLMReLCWUiPsTFMActw_0dtEU7kAcFXHNYYm64DNI='
    
    PROJECT_ROOT = Path(__file__).parent.parent
    static_dir = str(PROJECT_ROOT / "static")

    def load_config(config_file = None):
        default_file = Path(__file__).parent.parent / 'config/config.yaml'
        with open(default_file, 'r') as f:
            config = yaml.safe_load(f)

        cf_dict = {}
        if config_file:
            cf_dict = yaml.safe_load(config_file)

        config.update(**cf_dict)

        return config

