import solcx
from solcx import compile_standard
import solcast
from funion.utils import read_a_file, remove_comments


def get_all_AST_nodes(solidity_file_path:str, solidity_file_name:str, solc_version:str, import_paths:list):
    """
    get the AST nodes of all the involved contracts
    :param solidity_file_path:
    :param solidity_file_name:
    :param solc_version:
    :param import_paths:
    :return:
    """


    # solcx_binary_path = "/home/wei/.solcx/"
    # os.environ["SOLCX_BINARY"] = solcx_binary_path

    if solc_version not in solcx.get_installed_solc_versions():
        solcx.install_solc(solc_version)
    solcx.set_solc_version(solc_version)

    solidity_file_path = solidity_file_path + solidity_file_name

    allowed_paths = import_paths + ["."]
    file_content = read_a_file(solidity_file_path)
    file_content = remove_comments(file_content)

    # Compile the contract using py-solc-x
    compiled_contract = compile_standard(
        {
            "language": "Solidity",
            "sources": {solidity_file_path: {"content": file_content}},
            # "sources": {file: {"urls": [file]}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "": ["ast"],
                        # "*": ["metadata", "evm.bytecode", "evm.deployedBytecode", "abi", 'ir', 'sotrageLayout',
                        #       "irAst"]  # ["abi", "evm.bytecode"]
                    }
                }
            }
        },
        allow_paths=allowed_paths
    )

    SourceUnit_all_nodes = solcast.from_standard_output(compiled_contract)

    return SourceUnit_all_nodes


def get_ast_root_node(solidity_file_path:str, solidity_file_name:str, solc_version:str, import_paths:list):
    """
    get the AST node of the target contract

    :param solidity_data_path:
    :param solidity_file_name:
    :param contract_name:
    :param solc_version:
    :param import_paths:
    :return:
    """


    # solcx_binary_path = "/home/wei/.solcx/"
    # os.environ["SOLCX_BINARY"] = solcx_binary_path

    if solc_version not in solcx.get_installed_solc_versions():
        solcx.install_solc(solc_version)
    solcx.set_solc_version(solc_version)

    allowed_paths = import_paths + ["." ]

    solidity_file_path = solidity_file_path+ solidity_file_name

    file_content = read_a_file(solidity_file_path)
    file_content = remove_comments(file_content)

    # Compile the contract using py-solc-x
    compiled_contract = compile_standard(
        {
            "language": "Solidity",
            "sources": {solidity_file_path: {"content": file_content}},
            # "sources": {file: {"urls": [file]}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "": ["ast"],
                        # "*": ["metadata", "evm.bytecode", "evm.deployedBytecode", "abi", 'ir', 'sotrageLayout',
                        #       "irAst"]  # ["abi", "evm.bytecode"]
                    }
                }
            }
        },
        allow_paths=allowed_paths
    )

    SourceUnit_all_nodes = solcast.from_standard_output(compiled_contract)
    for node in SourceUnit_all_nodes:
        if hasattr(node, 'absolutePath'):
            if node.absolutePath == solidity_file_path:
                return node, file_content

    return SourceUnit_all_nodes[0], file_content
