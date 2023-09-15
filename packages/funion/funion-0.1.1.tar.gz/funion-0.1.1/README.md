##Funion

A tool to combine all the required libraries or contracts for a target contract together to a single file. The combining process is not straightforward. The dependent contracts or libraries must come first. In other words, the base contracts must come first while the derived contracts come later. This also explain why usually the last contract in a Solidity file with multiple contracts is considered as the target contract if no target contact is given when fuzzing or symbolic executing a solidity file.

One use case is to collect a dataset of Solidity smart contracts. For each contract, all its dependent libraries or contracts are put in one single file.

### Install from Pypi: ###
```
pip install funion
```

### How to use it: ###

Here is an example to merge all the libraries or contracts required by the contract VestingWallet into a single file.
```bash
merge --solidity_file_path C:\Users\18178\contracts\finance\
      --solidity_file_name VestingWallet.sol
      --contract_name VestingWallet
      --solc_version 0.8.0
      --import_paths C:\Users\18178\contracts\ .
      --result_path C:\Users\18178\contracts\
```
Assume that the code of all the related libraries or contracts are available and use the same compiler version.

Notes:
- **--import_paths** specifies a list of the root directories where the related libraries or contracts are located.

- The paths in the import statements in the Solidity files should be related to the directories specified in **--import_paths**

- In the exemplar use case above, all the libraries and contracts (including the target contract VestingWallet) are in the same root directory _C:\Users\18178\contracts\_. 

**<hr>**
In case you run this project in Pycharm IDE, here are the arguments provided to the merge.py for the contract VestingWallet. All the related files are in the **contracts** folder.
```
--solidity_file_path
.\contracts\finance\
--solidity_file_name
VestingWallet.sol
--contract_name
VestingWallet
--solc_version
0.8.0
--import_paths
.\contracts\
--result_path
.
```

The contract dependency is shown here:
```json
{'IERC20': [], 
  'IERC20Permit': [], 
  'SafeERC20': ['Address', 'IERC20', 'IERC20Permit'], 
  'Address': [], 
  'Context': [], 
  'VestingWallet': ['Address', 'Context', 'IERC20', 'IERC20Permit', 'SafeERC20']
}
```
For example, SafeERC20 depends on Address, IERC20, IERC20Permit.


This is the ordered contracts or libraries:
```json
['IERC20', 'IERC20Permit', 'Address', 'Context', 'SafeERC20', 'VestingWallet']
```

The merged file organizes the code of these contracts or libraries based on the order given above.