from handlers.base import Index, NewTransaction, FullChain, Mine, RegisterNode, Consensus

from config.common import BaseConfig

def setup_routes(app):
    app.router.add_get('/', Index.get, name = 'index')
    app.router.add_get('/chain', FullChain.get, name = 'chain')
    app.router.add_get('/nodes/resolve', Consensus.get, name = 'resolve')
    app.router.add_get('/mine', Mine.get, name = 'mine')


    app.router.add_post('/new_transaction', NewTransaction.post)
    app.router.add_post('/nodes/register', RegisterNode.post, name = 'register_node')

def setup_static_routes(app):
    app.router.add_static('/static/', path = BaseConfig.static_dir, name = 'static')
