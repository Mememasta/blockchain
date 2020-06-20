import aiohttp_jinja2
import hashlib
import json

from aiohttp import web
from aiohttp_session import get_session
from config.common import BaseConfig
from time import time
from textwrap import dedent
from uuid import uuid4
from .base import blockchain

node_identifier = str(uuid4()).replace('-', '')



class ApiMine:

    async def get(self):
        last_block = blockchain.last_block
        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof)

        blockchain.new_document(
                sender = "0",
                recipient = node_identifier,
                document_data = 1
                
                )

        previous_hash = blockchain.hash(last_block)
        block = blockchain.new_block(proof, previous_hash)

        response = {
                'message': 'New block forged',
                'index': block['index'],
                'documents': block['document'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']
                }
        return web.json_response(response)

class ApiNewDocument:

    async def post(self):
        values = await self.json()
        print(values)

        required = ['sender', 'recipient', 'document_data']
        if not all(key in values for key in required):
            return web.Response(text="Missing values")

        index = blockchain.new_document(values['sender'], values['recipient'], values['document_data'])

        last_block = blockchain.last_block
        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof)


        previous_hash = blockchain.hash(last_block)
        block = blockchain.new_block(proof, previous_hash)

        response = {"message": "Document will be added to Block"}
        return web.json_response(response)

class ApiFullChain:
    
    async def get(self):
        response = {
                'chain': blockchain.chain,
                'length': len(blockchain.chain)
                }
        return web.json_response(response)

class ApiRegisterNode:

    async def get(self):
        response = {
            'node': list(blockchain.nodes)    
        }

        return web.json_response(response)

    async def post(self):
        values = await self.json()

        nodes = values.get('nodes')
        if nodes is None:
            return web.json_response({"Error": "Please supply a valid list of nodes"})

        for node in nodes:
            blockchain.register_node(node)

        response = {
                'message': 'New nodes have been added',
                'total_nodes': list(blockchain.nodes)
                }
        return web.json_response(response)

class ApiConsensus:

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
