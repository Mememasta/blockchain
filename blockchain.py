import hashlib
import json
import requests
import socket
import os

from time import time
from uuid import uuid4
from urllib.parse import urlparse
from pynat import get_ip_info
from config.common import BaseConfig



class Blockchain(object):

    def __init__(self):
        with open(os.path.join(BaseConfig.db_dir + '/chain.json')) as f:
            self.chain = json.load(f)["chain"]
        
        #self.chain = []
        self.current_document = []        

        #topology, ext_ip, ext_port = get_ip_info()
        self.nodes = set()
        #self.nodes.add(ext_ip + ":" + str(ext_port))
        #print(self.nodes)

        #Создание первого блока
        if self.chain == []:
            self.new_block(previous_hash = 1, proof = 100)

    def new_block(self, proof, previous_hash = None):
        #Создание нового блока и внесение в цепь
        block = {
                'index': len(self.chain) + 1,
                'timestamp': time(),
                'document': self.current_document,
                'proof': proof,
                'previous_hash': previous_hash or self.hash(self.chain[-1]),
                }

        #Обновление текущего списка отправленных документов
        self.current_document = [] 

        self.chain.append(block)

        with open(os.path.join(BaseConfig.db_dir + '/chain.json'), 'w') as f:
            json.dump({"chain": self.chain}, f)

        return block

    def new_document(self, sender, recipient, document_data):
        #Добавление новой транзакции в список транзакций

        self.current_document.append({
            'sender': sender,
            'recipient': recipient,
            'document_data': document_data
            })

        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block):
       block_string = json.dumps(block, sort_keys = True).encode() 
       return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        #Вернет последний блок цепочки
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        #Подтверждение работы(простая проверка алгоритма)
        
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        #Подтверждение доказательства работы

        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        #Добавление нового узла

        parsed_url = urlparse("http://" + address)
        ip_port = parsed_url.netloc
        self.nodes.add(ip_port)

    
    def valid_chain(self, chain):
        #Проверка, является ли хэш в блоке верным

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        #Алгоритм консенсуса, разрешает конфликты, заменяя цепь на самую длинную в цепи

        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for nodes in neighbours:
            try:
                response = requests.get(f'http://{nodes}/api/chain')
                status = response.status_code
            except:
                status = 404

            if status == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            with open(os.path.join(BaseConfig.db_dir + '/chain.json'), 'w'):
                json.dump({"chain": self.chain})
            return True

        return False

