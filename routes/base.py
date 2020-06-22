from handlers.api import ApiNewDocument, ApiFullChain, ApiMine, ApiRegisterNode, ApiConsensus
from handlers.base import Index, NewDocument, ViewDocument, FullChain, Mine, RegisterNode, Consensus

from config.common import BaseConfig

def setup_routes(app):
    app.router.add_get('/', Index.get, name = 'index')
    app.router.add_get('/chain', FullChain.get, name = 'chain')
    app.router.add_get('/nodes/resolve', Consensus.get, name = 'resolve')
    #app.router.add_get('/mine', Mine.get, name = 'mine')
    app.router.add_get('/document/create', NewDocument.get, name = 'new_block')
    app.router.add_get('/document/{id}', ViewDocument.get, name='view_document')
    app.router.add_get('/nodes/list', RegisterNode.get, name = 'nodes')

    app.router.add_post('/user/create', Index.post, name="create_user")
    app.router.add_post('/document/new', NewDocument.post, name='new_document')
    app.router.add_post('/nodes/register', RegisterNode.post, name = 'register_node')

def setup_api_routes(app):
    app.router.add_get('/api/chain', ApiFullChain.get)
    app.router.add_get('/api/nodes/resolve', ApiFullChain.get)
    app.router.add_get('/api/nodes/list', ApiRegisterNode.get)

    app.router.add_post('/api/document/new', ApiNewDocument.post)
    app.router.add_post('/api/nodes/register', ApiRegisterNode.post)

def setup_static_routes(app):
    app.router.add_static('/static/', path = BaseConfig.static_dir, name = 'static')
