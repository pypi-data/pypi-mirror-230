import json
import os

from pdfrw import PdfReader

from verify4py.Issuer import Issuer, VERSION
import verify4py.utils as Utils
import verify4py.pdf as pdf_utils


class PdfIssuer(Issuer):
    def __init__(self, smart_contract_address,
                 node_host,
                 issuer_address='',
                 issuer_name='',
                 chain_id=1104,
                 hash_type='sha256'):
        super(PdfIssuer, self).__init__(smart_contract_address,
                                        node_host, issuer_address, issuer_name, chain_id, hash_type)

    def issue_pdf(self,
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

        pdf_utils.add_metadata(source_file_path, destination_file_path, verifymn=json.dumps(verifymn))
        # calc hash
        hash_val = Utils.calc_hash(destination_file_path)
        (tx, proof), error = self.issue(id, hash_val, expire_date, desc, private_key, key_store, passphrase)
        return tx, error

    def revoke_pdf(self,
                   file_path: str,
                   revoker_name: str,
                   private_key: str = "",
                   key_store="",
                   passphrase: str = ""
                   ):
        # validation
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise ValueError('Source path should be valid')
        hash_val = Utils.calc_hash(file_path)
        return self.revoke(hash_val.lower(), revoker_name, private_key, key_store, passphrase)

    def verify_pdf(self, file_path):
        hash_val = Utils.calc_hash(file_path)
        pdf = PdfReader(file_path)
        metadata = pdf.Info.get('/verifymn')
        result = self.verify_root(hash_val.lower())
        result['metadata'] = metadata
        return result
