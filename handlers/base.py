import aiohttp_jinja2
import hashlib
import json
import time

from aiohttp import web
from aiohttp_session import get_session
from config.common import BaseConfig
from textwrap import dedent
from uuid import uuid4, uuid5, NAMESPACE_DNS
from blockchain import Blockchain
from config.common import redirect

node_identifier = str(uuid4()).replace('-', '')


blockchain = Blockchain()

class Index(web.View):

    @aiohttp_jinja2.template('index.html')
    async def get(self):
        session = await get_session(self)
        print(session)
        user = {}
        status = {}
        if 'user' in session:
            send = 0
            post = 0
            user = session['user']
            chain = str(blockchain.chain[1:]).replace("\'", "\"")
            chains = json.loads(chain)
            for chain in chains:
                doc = chain["document"][0]
                sender = doc['sender']
                recipient = doc['recipient']
                if sender == user:
                    send = send + 1
                elif recipient == user:
                    post = post + 1
            status = [send, post]
        return dict(user = user, status = status)
    
    async def post(self):
        session = await get_session(self)
        location = self.app.router['index'].url_for()
        if 'user' not in session:
            session['user'] = node_identifier
            print(session)
        return web.HTTPFound(location=location)

class Mine:
    
    @aiohttp_jinja2.template("mine.html")
    async def get(self):
        last_block = blockchain.last_block
        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof)
        
        blockchain.new_document(
                sender = "0",
                recipient = node_identifier,
                document_data = "mine"
                
                )

        previous_hash = blockchain.hash(last_block)
        block = blockchain.new_block(proof, previous_hash)

        response = {
                'message': 'Новый блок создан',
                'index': block['index'],
                'documents': block['document'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']
                }

        return dict(response=response)

class NewDocument(web.View):
    
    @aiohttp_jinja2.template("create_document.html")
    async def get(self):
        session = await get_session(self)
        if 'user' in session:
            user_id = session['user']
            return dict(user_id=user_id)

        return redirect(self, 'index')

        
    async def post(self):
        replaced = blockchain.resolve_conflicts()
        values = await self.post()
        session = await get_session(self)
        location = self.app.router['new_block'].url_for()
        user = session['user']

        required = ['sender', 'recipient', 'document_data']
        if not all(key in values for key in required):
            return web.Response(text="Missing values")

        if values['sender'] == user:
            index = blockchain.new_document(values['sender'], values['recipient'], values['document_data'].filename)

            last_block = blockchain.last_block
            last_proof = last_block['proof']
            proof = blockchain.proof_of_work(last_proof)
        
        #blockchain.new_document(
        #        sender = "0",
        #        recipient = node_identifier,
        #        document_data = "mine"
        #        
        #        )

            previous_hash = blockchain.hash(last_block)
            block = blockchain.new_block(proof, previous_hash)

        #response = {
        #        'message': 'Новый блок создан',
        #        'index': block['index'],
        #        'documents': block['document'],
        #        'proof': block['proof'],
        #        'previous_hash': block['previous_hash']
        #        }

            return redirect(self, 'chain')
        
        return redirect(self, 'new_block')

#class ViewDocument:
#
#    @aiohttp_jinja2.template('view_document.html')
#    async def get(self):
        
        

class FullChain(web.View):
    
    @aiohttp_jinja2.template('chain.html')
    async def get(self):
        replaced = blockchain.resolve_conflicts()
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain)
        }
        return dict(response=response)

class RegisterNode:

    @aiohttp_jinja2.template('nodes.html')
    async def get(self):
        response = {}
        if blockchain.nodes:
            response = {
                'total_nodes': list(blockchain.nodes)
            }

        return dict(response=response)

    async def post(self):
        #values = await self.json()
        values = await self.post()
        nodes = []
        nodes.append("http://" + values['nodes'])
        if nodes is None:
            return web.json_response({"Error": "Please supply a valid list of nodes"})

        for node in nodes:
            blockchain.register_node(node)

        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(blockchain.nodes)
        }

        #return web.json_response(response)
        location = self.app.router['nodes'].url_for()
        return web.HTTPFound(location=location)

class Consensus:

    async def get(self):

        replaced = blockchain.resolve_conflicts()

        if replaced:
            response = {
                    'message': 'Our chain was replaces',
                    'new_chain': blockchain.chain
                    }
        else:
            response = {
                    'message': 'Out chain is authoritative',
                    'chain': blockchain.chain
                    }

        return web.json_response(response)
