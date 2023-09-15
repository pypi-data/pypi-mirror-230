import logging

from funion.compile_contract import get_all_AST_nodes
from funion.utils import read_a_file, remove_import_statements, remove_comments

flag_remove_comments=False
logger = logging.getLogger(__name__)
def get_contract_dependencies(all_AST_nodes: list):
    contract_dependency = {}
    contract_paths = {}
    for node in all_AST_nodes:
        paths_dict = {}
        if hasattr(node, 'absolutePath'):
            contract_path = node.absolutePath
            paths_dict['contract_path'] = contract_path
        contract_name = ''

        if hasattr(node, 'nodes'):
            for node_child in node.nodes:
                if hasattr(node_child, 'nodeType'):

                    if node_child.nodeType == 'ContractDefinition':
                        contract_name = node_child.name
                        # get its dependent contracts
                        if hasattr(node_child, 'dependencies'):
                            contract_dependency[node_child.name] = []
                            for dp_con in node_child.dependencies:
                                if hasattr(dp_con, 'name'):
                                    contract_dependency[contract_name].append(dp_con.name)
                    elif node_child.nodeType == 'ImportDirective':
                        if hasattr(node_child, 'absolutePath'):
                            path = node_child.absolutePath
                            if 'import_path' not in paths_dict.keys():
                                paths_dict['import_path'] = [path]
                            else:
                                paths_dict['import_path'].append(path)
        if len(contract_name) > 0:
            contract_paths[contract_name] = paths_dict
    return contract_dependency, contract_paths


def order_contracts(inter_contract_dependency: dict) -> list:
    """
    example:
        {'Ownable': ['Context'],
         'IERC20': [],
         'IERC20Permit': [],
         'SafeERC20': ['Address', 'IERC20'],
         'Address': [],
         'Context': [],
         'VestingWallet': ['Address', 'Context', 'IERC20', 'Ownable', 'SafeERC20']
         }
    :param inter_contract_dependency:
    :return:
    """

    left_contracts = list(inter_contract_dependency.keys())
    ordered_contracts = [con for con in left_contracts if len(inter_contract_dependency[con]) == 0]
    left_contracts = [con for con in left_contracts if con not in ordered_contracts]
    while len(left_contracts) > 0:
        target = left_contracts[0]
        dependents = inter_contract_dependency[target]
        if len([item for item in dependents if item not in ordered_contracts]) == 0:
            ordered_contracts.append(target)
            left_contracts.pop(0)
    return ordered_contracts


def merge_contract_files(ordered_contracts: list, contract_paths: dict, merged_file_path: str):

    file_contents = []
    for con_name in ordered_contracts:
        if con_name not in contract_paths.keys():
            print("no path is found for contract {}".format(con_name))
            continue
        con_path = contract_paths[con_name]['contract_path']

        file_content = read_a_file(con_path)

        if flag_remove_comments:
            file_content=remove_comments(file_content)

        # Remove import statements from the Solidity code
        cleaned_code = remove_import_statements(file_content)

        file_contents.append(cleaned_code)

    with open(merged_file_path, "w") as file_write:
        for content in file_contents:
            file_write.write(content + "\n")
    file_write.close()


def combine_involved_contracts(solidity_file_path:str, solidity_file_name:str, solc_version:str, import_paths:list,result_path:str):


    # get all related AST nodes
    nodes = get_all_AST_nodes(solidity_file_path, solidity_file_name, solc_version, import_paths)

    # get the contract dependency
    contract_dependency, contract_paths = get_contract_dependencies(nodes)
    logger.info(f'The dependency:{contract_dependency}')

    # order contracts based on the dependency
    ordered_contracts = order_contracts(contract_dependency)
    logger.info(f'The order of libraries or contracts:{ordered_contracts}')

    # merge contract file content based on the order of the contracts
    final_file_path_and_name = result_path + "{}".format(solidity_file_name)
    merge_contract_files(ordered_contracts, contract_paths, final_file_path_and_name)

