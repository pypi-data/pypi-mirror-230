import json
import os

import verify4py.utils as Utils
from verify4py.Issuer import Issuer, VERSION
from verify4py.json_utils import json_wrap


class JsonIssuer(Issuer):
    def __init__(self,
                 smart_contract_address,
                 node_host,
                 issuer_address='',
                 issuer_name='',
                 chain_id=1104,
                 hash_type='sha256'):
        super(JsonIssuer, self).__init__(smart_contract_address, node_host, issuer_address, issuer_name, chain_id,
                                         hash_type)

    def issue_json(self,
                   id: str,
                   source_file_path: str,
                   destination_file_path: str,
                   expire_date: int,
                   desc: str,
                   additional_info: str,
                   private_key: str = "",
                   key_store="",
                   passphrase: str = ""):
        # validation
        if not os.path.exists(source_file_path) or not os.path.isfile(source_file_path):
            raise ValueError('Source path should be valid')

        if os.path.isdir(destination_file_path):
            raise ValueError('Destination path already exists')

        verifymn = {
            "issuer": {
                "name": self.issuer_name,
                "address": self.issuer_address
            },
            "info": {
                "name": self.issuer_name,
                "desc": desc,
                "cerNum": id,
                "additionalInfo": additional_info
            },
            "version": VERSION,
            "blockchain": {
                "network": "CorexMain" if self.chain_id == 1104 else "CorexTest",
                "smartContractAddress": self.smart_contract_address
            }
        }
        f = open(source_file_path)
        json_data = json.load(f)
        json_data['verifymn'] = verifymn
        wrapped_json_str = json_wrap(json_data)
        hash_val = Utils.calc_hash_str(wrapped_json_str)
        (tx, proof), error = self.issue(id, hash_val, expire_date, desc, private_key, key_store, passphrase)
        if error is None:
            verifymn['chainpointProof'] = proof
            json_data['verifymn'] = verifymn
            with open(destination_file_path, 'w') as f:
                json.dump(json_data, f, indent=4)
        return tx, error

    def verify_json(self, file_path: str):
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise ValueError('Source path should be valid')

        hash = self.__verify_json_file(file_path)
        return self.verify_root(hash)

    def revoke_json(self, file_path: str, revoker_name: str,
                    private_key: str = "",
                    key_store="",
                    passphrase: str = ""):
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise ValueError('Source path should be valid')
        hash = self.__verify_json_file(file_path)
        return self.revoke(hash, revoker_name, private_key, key_store, passphrase)

    def __verify_json_file(self, file_path):
        f = open(file_path)
        json_data = json.load(f)
        verifymn = json_data['verifymn']
        chainpoint_proof = verifymn.pop("chainpointProof", None)
        json_data['verifymn'] = verifymn
        json_data['verifymn'] = verifymn
        wrapped_json_str = json_wrap(json_data)
        hash_val = Utils.calc_hash_str(wrapped_json_str)
        return hash_val
