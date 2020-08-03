import aiohttp_jinja2
import base64
import hashlib
import json
import time

from aiohttp import web, ClientSession
from aiohttp_session import get_session
from aiohttp_security import remember, forget, authorized_userid
from config.common import BaseConfig, redirect
from database.users import User
from security import generate_password_hash, check_password_hash, generate_key
from textwrap import dedent
# from uuid import uuid4, uuid5, NAMESPACE_DNS
from blockchain import Blockchain

# node_identifier = str(uuid4()).replace('-', '')
node_identifier = generate_key('-', '')

blockchain = Blockchain()

class Index(web.View):

    @aiohttp_jinja2.template('index.html')
    async def get(self):
        session = await get_session(self)
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
        else:
            return web.HTTPFound(self.app.router['signup'].url_for())
        return dict(user = user, status = status)

    async def post(self):
        session = await get_session(self)
        location = self.app.router['index'].url_for()
        if 'user' not in session:
            return web.HTTPFound(location=location)

class Register(web.View):

    @aiohttp_jinja2.template('register.html')
    async def get(self):
        session = await get_session(self)
        user_key = node_identifier
        if 'user' in session:
            location = self.app.router['index'].url_for()
            return web.HTTPFound(location = location)
        return dict(user_key = user_key)

    async def post(self):
        data = await self.post()
        print(data)
        user_key = await User.get_user_by_key(self.app['db'], node_identifier)

        if not user_key and data['login'] and data['password']:
            password_hash = generate_password_hash(data['password'])
            create_user = await User.create_user(self.app['db'], node_identifier, data['login'], password_hash)

            return web.HTTPFound(self.app.router['login'].url_for())
        else:
            return {'error': 'Missing values or user already exist'}

        return web.HTTPFound(self.app.router['login'].url_for())

class Login(web.View):

    @aiohttp_jinja2.template('login.html')
    async def get(self):
        session = await get_session(self)
        if 'user' in session:
            return web.HTTPFound(self.app.router['index'].url_for())
        return dict()

    async def post(self):
        data = await self.post()
        session = await get_session(self)

        user = await User.get_user_by_key(self.app['db'], data['user_key'])

        if user and user['login'] == data['login'] and check_password_hash(data['password'], user['password']):
            session['user'] = dict(user)

            return web.HTTPFound(self.app.router['index'].url_for())
        return web.HTTPFound(self.app.router['login'].url_for())

class Logout(web.View):

    async def get(self):
        session = await get_session(self)
        if 'user' in session:
            del session['user']
            return web.HTTPFound(self.app.router['login'].url_for())
        return web.HTTPFound(self.app.router['index'].url_for())

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
            user = session['user']
            return dict(user_id=user['key'])

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

        if values['sender'] == user['key']:
            file = [str(values['document_data'].filename), str(values['document_data'].content_type)]
            print(file)
            b64 = base64.b64encode(values['document_data'].file.read()).strip().decode('utf-8')
            file.append(str(b64))
            index = blockchain.new_document(values['sender'], values['recipient'], file)

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

class ViewDocument:

    @aiohttp_jinja2.template('view_document.html')
    async def get(self):
        hash = self.match_info['id']
        block = {}
        for block in blockchain.chain[1:]:
            hash_chain = block['previous_hash']
            if hash == hash_chain:
                return dict(block=block)



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
        status = []
        if blockchain.nodes:
            for node in blockchain.nodes:
                try:
                    async with ClientSession() as session:
                        async with session.get(f'http://{node}/api/chain') as resp:
                            if resp.status == 200:
                                status.append("online")
                except:
                    status.append("offline")
            response = {
                "total_nodes": list(blockchain.nodes),
                "status_nodes": status
            }

        return dict(response=response)

    async def post(self):
        #values = await self.json()
        values = await self.post()
        nodes = []
        nodes.append(values['nodes'])
        if nodes is None:
            return web.json_response({"Error": "Please supply a valid list of nodes"})

        for node in nodes:
            if node != self.host:
                blockchain.register_node(node)
                try:
                    async with ClientSession() as session:
                        async with session.get(f'http://{node}/api/nodes/list') as resp:
                            if resp.status == 200:
                                ip = await resp.json()
                                print(ip['node'])
                                nodes.extend(ip['node'])
                except:
                    print('error')


        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(blockchain.nodes)
        }

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
