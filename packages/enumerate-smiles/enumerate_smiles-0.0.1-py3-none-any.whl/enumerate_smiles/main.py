
from rdkit import Chem
from enumerate_smiles import SmilesEnumerator


se = SmilesEnumerator()
print(len(se.enumerate([Chem.MolFromSmiles('c1ccccc1O')])))
