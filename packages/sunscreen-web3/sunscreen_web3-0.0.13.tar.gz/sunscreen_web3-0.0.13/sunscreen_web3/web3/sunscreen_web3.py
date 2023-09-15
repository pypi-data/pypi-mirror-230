import json
from web3 import Web3
from solcx import install_solc, set_solc_version, compile_files, link_code # type: ignore
from web3.middleware import geth_poa_middleware # type: ignore
import os
from hexbytes import HexBytes # type: ignore


def initialize_web3(config):
    install_solc(version=config["solidity_version"])
    set_solc_version(config["solidity_version"])
    w3 = Web3(Web3.HTTPProvider(config["rpc_endpoint"])) # type: ignore
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def set_account_config(config, address, pvt_key):
    account_file_name = config["account_file"]
    if os.path.exists(account_file_name):
        os.remove(account_file_name)

    with open(address + ".key", "w") as file:
        file.write(pvt_key)

    json_data = {
        "address": address,
    }
    # Create the JSON file and write JSON data to it
    with open(account_file_name, "w") as json_file:
        json.dump(json_data, json_file, indent=4)


def load_or_create_account(w3, config):
    account_file_name = config["account_file"]
    if not os.path.exists(account_file_name):
        account = w3.eth.account.create()

        with open(account.address + ".key", "w") as file:
            file.write(account._private_key.hex())

        json_data = {
            "address": account.address,
        }
        # Create the JSON file and write JSON data to it
        with open(account_file_name, "w") as json_file:
            json.dump(json_data, json_file, indent=4)

    # Read the existing JSON data from the file
    accounts = None
    with open(account_file_name, "r") as json_file:
        accounts = json.load(json_file)

    with open(accounts["address"] + ".key", "r") as file:
        return {"address": accounts["address"], "private_key": HexBytes(file.read())}


def deploy_solidity_object(
    w3, account_address, private_key, abi, bytecode, chain_id, *argv
):
    nonce = w3.eth.get_transaction_count(account_address)
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = contract.constructor(*argv).build_transaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": account_address,
            "nonce": nonce,
        }
    )
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_receipt["contractAddress"]


def deploy_libraries(w3, account, remappings, config, libraries):
    # Solidity source files
    source_files = list(map(lambda x: x["source"], list(libraries.values())))

    # Compile the contracts
    compiled_files = compile_files(source_files, output_values=["abi", "bin"], import_remappings=remappings)

    def create_object(name, libs, compiles):
        source = libs[name]["source"]
        abi = compiles[f"{source}:{name}"]["abi"]
        bin = compiles[f"{source}:{name}"]["bin"]
        address = deploy_solidity_object(
            w3, account["address"], account["private_key"], abi, bin, config["chain_id"]
        )

        return {"source": source, "abi": abi, "bin": bin, "address": address}

    return dict(
        zip(
            list(libraries.keys()),
            map(
                lambda x: create_object(x, libraries, compiled_files),
                list(libraries.keys()),
            ),
        )
    )


def deploy_contracts(w3, account, remappings, config, libraries, contracts):
    # Solidity source files
    library_source_files = list(map(lambda x: x["source"], list(libraries.values())))
    contract_source_files = list(map(lambda x: x["source"], list(contracts.values())))

    source_files = library_source_files + contract_source_files

    # Compile the contracts
    compiled_files = compile_files(source_files, output_values=["abi", "bin"], import_remappings=remappings)

    def create_object(name, lib_mapping, contracts, compiles):
        source = contracts[name]["source"]
        abi = compiles[f"{source}:{name}"]["abi"]
        bin = compiles[f"{source}:{name}"]["bin"]
        linked_bin = link_code(bin, lib_mapping)

        address = deploy_solidity_object(
            w3,
            account["address"],
            account["private_key"],
            abi,
            linked_bin,
            config["chain_id"],
            *(contracts[name]["constructor_args"]),
        )

        return {
            "source": source,
            "abi": abi,
            "bin": bin,
            "linked_bin": linked_bin,
            "address": address,
        }

    lib_mappings = dict(
        zip(
            map(lambda x: f"{libraries[x]['source']}:{x}", list(libraries.keys())),
            map(lambda x: f"{libraries[x]['address']}", list(libraries.keys())),
        )
    )

    return dict(
        zip(
            list(contracts.keys()),
            map(
                lambda x: create_object(x, lib_mappings, contracts, compiled_files),
                list(contracts.keys()),
            ),
        )
    )


def export_contract_abi_to_file(address, abi, file_name):
    json_data = {"address": address, "abi": abi}
    with open(file_name, "w") as json_file:
        json.dump(json_data, json_file, indent=4)


def load_contract_abi_from_file(w3, file_name):
    with open(file_name, "r") as json_file:
        c = json.load(json_file)
        return w3.eth.contract(address=c["address"], abi=c["abi"])
