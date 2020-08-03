from pathlib import Path
import pytoml as toml
from aiohttp import web

def redirect(request, name, **kw):
    router = request.app.router
    location = router[name].url_for(**kw)
    return web.HTTPFound(location=location)

class BaseConfig:

    debug = True
    app_name = "BlockChain"
    secret_key = b'TyzLMReLCWUiPsTFMActw_0dtEU7kAcFXHNYYm64DNI='

    PROJECT_ROOT = Path(__file__).parent.parent
    static_dir = str(PROJECT_ROOT / "static")
    db_dir = str(PROJECT_ROOT / "database")

    def load_config(path = None):
        if path != None:
            path = Path(__file__).parent.parent / path
        else:
            path = Path(__file__).parent.parent / 'config/user_config.toml'

        with open(path) as f:
            conf = toml.load(f)
        return conf
