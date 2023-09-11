# Copyright 2020 Jacob D. Durrant
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This script identifies and enumerates the possible protonation sites of SMILES
strings.
"""

import os
import copy
from io import StringIO
from typing import List, Optional, Tuple, Union


try:
    import rdkit
    from rdkit import Chem
    from rdkit.Chem import AllChem

    # Disable the unnecessary RDKit warnings
    from rdkit import RDLogger

    RDLogger.DisableLog("rdApp.*")
except:
    msg = "Dimorphite-DL requires RDKit. See https://www.rdkit.org/"
    print(msg)
    raise Exception(msg)


HEADER = ("\nIf you use Dimorphite-DL in your research, please cite:\n"
          "Ropp PJ, Kaminsky JC, Yablonski S, Durrant JD (2019) Dimorphite-DL: An\n"
          "open-source program for enumerating the ionization states of drug-like small\n"
          "molecules. J Cheminform 11:14. doi:10.1186/s13321-019-0336-9.\n")


def print_header():
    """Prints out header information."""
    print(HEADER)

class UtilFuncs:
    """A namespace to store functions for manipulating mol objects. To keep
    things organized."""

    @staticmethod
    def neutralize_mol(mol):
        """All molecules should be neuralized to the extent possible. The user
        should not be allowed to specify the valence of the atoms in most cases.

        :param rdkit.Chem.rdchem.Mol mol: The rdkit Mol objet to be neutralized.
        :return: The neutralized Mol object.
        """

        # Get the reaction data
        rxn_data = [
            [
                "[Ov1-1:1]",
                "[Ov2+0:1]-[H]",
            ],  # To handle O- bonded to only one atom (add hydrogen).
            [
                "[#7v4+1:1]-[H]",
                "[#7v3+0:1]",
            ],  # To handle N+ bonded to a hydrogen (remove hydrogen).
            [
                "[Ov2-:1]",
                "[Ov2+0:1]",
            ],  # To handle O- bonded to two atoms. Should not be Negative.
            [
                "[#7v3+1:1]",
                "[#7v3+0:1]",
            ],  # To handle N+ bonded to three atoms. Should not be positive.
            [
                "[#7v2-1:1]",
                "[#7+0:1]-[H]",
            ],  # To handle N- Bonded to two atoms. Add hydrogen.
            # ['[N:1]=[N+0:2]=[N:3]-[H]', '[N:1]=[N+1:2]=[N+0:3]-[H]'],  # To handle bad azide. Must be
            # protonated. (Now handled
            # elsewhere, before SMILES
            # converted to Mol object.)
            [
                "[H]-[N:1]-[N:2]#[N:3]",
                "[N:1]=[N+1:2]=[N:3]-[H]",
            ]  # To handle bad azide. R-N-N#N should
            # be R-N=[N+]=N
        ]

        # Add substructures and reactions (initially none)
        for i, rxn_datum in enumerate(rxn_data):
            rxn_data[i].append(Chem.MolFromSmarts(rxn_datum[0]))
            rxn_data[i].append(None)

        # Add hydrogens (respects valence, so incomplete).
        mol.UpdatePropertyCache(strict=False)
        mol = Chem.AddHs(mol)

        while True:  # Keep going until all these issues have been resolved.
            current_rxn = None  # The reaction to perform.
            current_rxn_str = None

            for i, rxn_datum in enumerate(rxn_data):
                (
                    reactant_smarts,
                    product_smarts,
                    substruct_match_mol,
                    rxn_placeholder,
                ) = rxn_datum
                if mol.HasSubstructMatch(substruct_match_mol):
                    if rxn_placeholder is None:
                        current_rxn_str = reactant_smarts + ">>" + product_smarts
                        current_rxn = AllChem.ReactionFromSmarts(current_rxn_str)
                        rxn_data[i][3] = current_rxn  # Update the placeholder.
                    else:
                        current_rxn = rxn_data[i][3]
                    break

            # Perform the reaction if necessary
            if current_rxn is None:  # No reaction left, so break out of while loop.
                break
            else:
                mol = current_rxn.RunReactants((mol,))[0][0]
                mol.UpdatePropertyCache(strict=False)  # Update valences

        # The mols have been altered from the reactions described above, we
        # need to resanitize them. Make sure aromatic rings are shown as such
        # This catches all RDKit Errors. without the catchError and
        # sanitizeOps the Chem.SanitizeMol can crash the program.
        sanitize_string = Chem.SanitizeMol(
            mol,
            sanitizeOps=rdkit.Chem.rdmolops.SanitizeFlags.SANITIZE_ALL,
            catchErrors=True,
        )

        return mol if sanitize_string.name == "SANITIZE_NONE" else None

    @staticmethod
    def convert_smiles_str_to_mol(smiles_str):
        """Given a SMILES string, check that it is actually a string and not a
        None. Then try to convert it to an RDKit Mol Object.

        :param string smiles_str: The SMILES string.
        :return: A rdkit.Chem.rdchem.Mol object, or None if it is the wrong type or
            if it fails to convert to a Mol Obj
        """

        # Check that there are no type errors, ie Nones or non-string A
        # non-string type will cause RDKit to hard crash
        if smiles_str is None or type(smiles_str) is not str:
            return None

        # Try to fix azides here. They are just tricky to deal with.
        smiles_str = smiles_str.replace("N=N=N", "N=[N+]=N")
        smiles_str = smiles_str.replace("NN#N", "N=[N+]=N")

        mol = Chem.MolFromSmiles(smiles_str)

        # Check that there are None type errors Chem.MolFromSmiles has
        # sanitize on which means if there is even a small error in the SMILES
        # (kekulize, nitrogen charge...) then mol=None. ie.
        # Chem.MolFromSmiles("C[N]=[N]=[N]") = None this is an example of an
        # nitrogen charge error. It is cased in a try statement to be overly
        # cautious.
        return None if mol is None else mol

    @staticmethod
    def prepare_molecule(smiles_str: str) -> Optional[str]:
        """Prepare the molecule for subsequent protonation.

        :param string: smiles_str: The SMILES string.
        """
        # Convert from SMILES string to RDKIT Mol. This series of tests is
        # to make sure the SMILES string is properly formed and to get it
        # into a canonical form. Filter if failed.
        mol = UtilFuncs.convert_smiles_str_to_mol(smiles_str)
        if mol is None:
            raise ValueError("Poorly formed SMILES string: " + smiles_str)
        # Handle nuetralizing the molecules. Filter if failed.
        mol = UtilFuncs.neutralize_mol(mol)
        if mol is None:
            raise ValueError("Poorly formed SMILES string: " + smiles_str)
        # Remove the hydrogens.
        try:
            mol = Chem.RemoveHs(mol)
        except:
            raise ValueError("Poorly formed SMILES string: " + smiles_str)
        if mol is None:
            raise ValueError("Poorly formed SMILES string: " + smiles_str)
        # Regenerate the smiles string (to standardize).
        new_mol_string = Chem.MolToSmiles(mol, isomericSmiles=True)
        return new_mol_string


class LoadSMIFile(object):
    """A generator class for loading in the SMILES strings from a file, one at
    a time."""

    def __init__(self, filename, silent: bool = False):
        """Initializes this class.

        :param filename: The filename or file object (i.e., StringIO).
        :type filename: str or StringIO
        """

        self.silent = silent

        if type(filename) is str:
            # It's a filename
            self.f = open(filename, "r")
        else:
            # It's a file object (i.e., StringIO)
            self.f = filename

    def __iter__(self):
        """Returns this generator object.

        :return: This generator object.
        :rtype: LoadSMIFile
        """

        return self

    def __next__(self):
        """Ensure Python3 compatibility.

        :return: A dict, where the "smiles" key contains the canonical SMILES
                 string and the "data" key contains the remaining information
                 (e.g., the molecule name).
        :rtype: dict
        """

        return self.next()

    def next(self):
        """Get the data associated with the next line.

        :raises StopIteration: If there are no more lines left iin the file.
        :return: A dict, where the "smiles" key contains the canonical SMILES
                 string and the "data" key contains the remaining information
                 (e.g., the molecule name).
        :rtype: dict
        """

        line = self.f.readline()

        if line == "":
            # EOF
            self.f.close()
            raise StopIteration()

        # Divide line into smi and data
        splits = line.split()
        if len(splits) != 0:
            # Generate mol object
            smiles_str = splits[0]

            try:
                new_mol_string = UtilFuncs.prepare_molecule(smiles_str)
            except ValueError as e:
                if not self.silent:
                    print(f"WARNING: {e.args[0]}")
                return self.next()

            return {"smiles": new_mol_string, "data": splits[1:]}
        else:
            # Blank line? Go to next one.
            return self.next()


class Protonator(object):
    """A generator class for protonating SMILES strings, one at a time."""

    def __init__(self,
                 min_ph: float = 6.4,
                 max_ph: float = 8.4,
                 pka_precision: float = 1.0,
                 max_variants: int = 128,
                 label_states: bool = False,
                 silent: bool = False):
        """Initialize the protonation state generator."""

        self.min_ph = min_ph
        self.max_ph = max_ph
        self.pka_precision = pka_precision
        self.max_variants = max_variants
        self.label_states = label_states
        self.silent = silent
        self.subs = ProtSubstructFuncs.load_protonation_substructs_calc_state_for_ph(self.min_ph,
                                                                                     self.max_ph,
                                                                                     self.pka_precision)
        if not silent:
            print_header()

    def protonate(self, smiles: str) -> Union[List[str], List[Tuple[str, str]]]:
        """Run the protonation process on the given SMILES.

        :param smiles: SMILES of molecule
        :return: protonated SMILES
        """
        if not isinstance(smiles, str):
            raise TypeError('only SMILES can be prepared')
        # Prepare molecules
        smiles = UtilFuncs.prepare_molecule(smiles)
        # Dimorphite-DL may protonate some sites in ways that produce invalid
        # SMILES. We need to keep track of all smiles so we can "rewind" to
        # the last valid one, should things go south.
        properly_formed_smi_found = [smiles]
        # sites is a list of (atom index, "PROTONATED|DEPROTONATED|BOTH",
        # reaction name, mol). Note that the second entry indicates what state
        # the site SHOULD be in (not the one it IS in per the SMILES string).
        # It's calculated based on the probablistic distributions obtained
        # during training.
        protonation_sites = ProtSubstructFuncs.get_prot_sites_and_target_states(smiles, self.subs)
        if len(protonation_sites) == 0:
            return []
        sites, mol_used_to_idx_sites = protonation_sites

        new_mols = [mol_used_to_idx_sites]
        if len(sites) > 0:
            for site in sites:
                # Make a new smiles with the correct protonation state. Note that
                # new_smis is a growing list. This is how multiple protonation
                # sites are handled.
                new_mols = ProtSubstructFuncs.protonate_site(new_mols, site, silent=self.silent)
                if len(new_mols) > self.max_variants:
                    new_mols = new_mols[: self.max_variants]
                    if not self.silent:
                        print(f"WARNING: Limited number of variants to {self.max_variants}: {smiles}")
                # Go through each of these new molecules and add them to the
                # properly_formed_smi_found, in case you generate a poorly
                # formed SMILES in the future and have to "rewind."
                properly_formed_smi_found += [Chem.MolToSmiles(m) for m in new_mols]
        else:
            # Deprotonate the mols (because protonate_site never called to do it).
            mol_used_to_idx_sites = Chem.RemoveHs(mol_used_to_idx_sites)
            new_mols = [mol_used_to_idx_sites]

            # Go through each of these new molecules and add them to the
            # properly_formed_smi_found, in case you generate a poorly formed
            # SMILES in the future and have to "rewind."
            properly_formed_smi_found.append(Chem.MolToSmiles(mol_used_to_idx_sites))

        # In some cases, the script might generate redundant molecules.
        # Phosphonates, when the pH is between the two pKa values and the
        # stdev value is big enough, for example, will generate two identical
        # BOTH states. Let's remove this redundancy.
        new_smis = list(set(Chem.MolToSmiles(m, isomericSmiles=True, canonical=True) for m in new_mols))

        # Sometimes Dimorphite-DL generates molecules that aren't actually
        # possible. Simply convert these to mol objects to eliminate the bad
        # ones (that are None).
        new_smis = [s for s in new_smis if UtilFuncs.convert_smiles_str_to_mol(s) is not None]

        # If there are no smi left, return the input one at the very least.
        # All generated forms have apparently been judged
        # inappropriate/malformed.
        if len(new_smis) == 0:
            properly_formed_smi_found.reverse()
            for smi in properly_formed_smi_found:
                if UtilFuncs.convert_smiles_str_to_mol(smi) is not None:
                    new_smis = [smi]
                    break

        # If the user wants to see the target states, add those to the ends of
        # each line.
        if self.label_states:
            states = [x[1] for x in sites]
            if len(states) == 0:
                states = None
            elif len(states) == 1:
                states = states[0]
            return (new_smis, states)
        return new_smis


class ProtSubstructFuncs:
    """A namespace to store functions for loading the substructures that can
    be protonated. To keep things organized."""

    @staticmethod
    def load_substructre_smarts_file():
        """Loads the substructure smarts file. Similar to just using readlines,
        except it filters out comments (lines that start with "#").

        :return: A list of the lines in the site_substructures.smarts file,
                 except blank lines and lines that start with "#"
        """

        pwd = os.path.dirname(os.path.realpath(__file__))
        site_structures_file = "{}/{}".format(pwd, "site_substructures.smarts")
        lines = [
            l
            for l in open(site_structures_file, "r")
            if l.strip() != "" and not l.startswith("#")
        ]

        return lines

    @staticmethod
    def load_protonation_substructs_calc_state_for_ph(min_ph: float = 6.4,
                                                      max_ph: float = 8.4,
                                                      pka_std_range: float = 1):
        """A pre-calculated list of R-groups with protonation sites, with their
        likely pKa bins.

        :param float min_ph:  The lower bound on the pH range, defaults to 6.4.
        :param float max_ph:  The upper bound on the pH range, defaults to 8.4.
        :param pka_std_range: Basically the precision (stdev from predicted pKa to
                              consider), defaults to 1.
        :return: A dict of the protonation substructions for the specified pH
                 range.
        """

        subs = []

        for line in ProtSubstructFuncs.load_substructre_smarts_file():
            line = line.strip()
            sub = {}
            if line != "":
                splits = line.split()
                sub["name"] = splits[0]
                sub["smart"] = splits[1]
                sub["mol"] = Chem.MolFromSmarts(sub["smart"])

                pka_ranges = [splits[i : i + 3] for i in range(2, len(splits) - 1, 3)]

                prot = []
                for pka_range in pka_ranges:
                    site = pka_range[0]
                    std = float(pka_range[2]) * pka_std_range
                    mean = float(pka_range[1])
                    protonation_state = ProtSubstructFuncs.define_protonation_state(
                        mean, std, min_ph, max_ph
                    )

                    prot.append([site, protonation_state])

                sub["prot_states_for_pH"] = prot
                subs.append(sub)
        return subs

    @staticmethod
    def define_protonation_state(mean, std, min_ph, max_ph):
        """Updates the substructure definitions to include the protonation state
        based on the user-given pH range. The size of the pKa range is also based
        on the number of standard deviations to be considered by the user param.

        :param float mean:   The mean pKa.
        :param float std:    The precision (stdev).
        :param float min_ph: The min pH of the range.
        :param float max_ph: The max pH of the range.
        :return: A string describing the protonation state.
        """

        min_pka = mean - std
        max_pka = mean + std

        # This needs to be reassigned, and 'ERROR' should never make it past
        # the next set of checks.
        if min_pka <= max_ph and min_ph <= max_pka:
            protonation_state = "BOTH"
        elif mean > max_ph:
            protonation_state = "PROTONATED"
        else:
            protonation_state = "DEPROTONATED"

        return protonation_state

    @staticmethod
    def get_prot_sites_and_target_states(smi, subs):
        """For a single molecule, find all possible matches in the protonation
        R-group list, subs. Items that are higher on the list will be matched
        first, to the exclusion of later items.

        :param string smi: A SMILES string.
        :param list subs: Substructure information.
        :return: A list of protonation sites (atom index), pKa bin.
            ('PROTONATED', 'BOTH', or  'DEPROTONATED'), and reaction name.
            Also, the mol object that was used to generate the atom index.
        """

        # Convert the Smiles string (smi) to an RDKit Mol Obj
        mol_used_to_idx_sites = UtilFuncs.convert_smiles_str_to_mol(smi)
        # Check Conversion worked
        if mol_used_to_idx_sites is None:
            raise ValueError("ERROR: Could not parse SMILES  ", smi)
        # Try to Add hydrogens. if failed return []
        try:
            mol_used_to_idx_sites = Chem.AddHs(mol_used_to_idx_sites)
        except:
            raise ValueError("ERROR: Could not add hydrogen atoms  ", smi)

        # Check adding Hs worked
        if mol_used_to_idx_sites is None:
            raise ValueError("ERROR: Could not add hydrogen atoms  ", smi)
        ProtectUnprotectFuncs.unprotect_molecule(mol_used_to_idx_sites)
        protonation_sites = []

        for item in subs:
            smart = item["mol"]
            if mol_used_to_idx_sites.HasSubstructMatch(smart):
                matches = ProtectUnprotectFuncs.get_unprotected_matches(
                    mol_used_to_idx_sites, smart
                )
                prot = item["prot_states_for_pH"]
                for match in matches:
                    # We want to move the site from being relative to the
                    # substructure, to the index on the main molecule.
                    for site in prot:
                        proton = int(site[0])
                        category = site[1]
                        new_site = (match[proton], category, item["name"])

                        if not new_site in protonation_sites:
                            # Because sites must be unique.
                            protonation_sites.append(new_site)

                    ProtectUnprotectFuncs.protect_molecule(mol_used_to_idx_sites, match)
        return protonation_sites, mol_used_to_idx_sites

    @staticmethod
    def protonate_site(mols, site, silent: bool = False):
        """Given a list of molecule objects, we protonate the site.

        :param list mols:  The list of molecule objects.
        :param tuple site: Information about the protonation site.
                           (idx, target_prot_state, prot_site_name)
        :return: A list of the appropriately protonated molecule objects.
        """

        # Decouple the atom index and its target protonation state from the
        # site tuple
        idx, target_prot_state, prot_site_name = site

        state_to_charge = {"DEPROTONATED": [-1], "PROTONATED": [0], "BOTH": [-1, 0]}

        charges = state_to_charge[target_prot_state]

        # Now make the actual smiles match the target protonation state.
        output_mols = ProtSubstructFuncs.set_protonation_charge(
            mols, idx, charges, prot_site_name, silent
        )

        return output_mols

    @staticmethod
    def set_protonation_charge(mols, idx, charges, prot_site_name, silent: bool = False):
        """Sets the atomic charge on a particular site for a set of SMILES.

        :param list mols:                  A list of the input molecule
                                           objects.
        :param int idx:                    The index of the atom to consider.
        :param list charges:               A list of the charges (ints) to
                                           assign at this site.
        :param string prot_site_name:      The name of the protonation site.
        :return: A list of the processed (protonated/deprotonated) molecule
                 objects.
        """

        # Sets up the output list and the Nitrogen charge
        output = []

        for charge in charges:
            # The charge for Nitrogens is 1 higher than others (i.e.,
            # protonated state is positively charged).
            nitrogen_charge = charge + 1

            # But there are a few nitrogen moieties where the acidic group is
            # the neutral one. Amides are a good example. I gave some thought
            # re. how to best flag these. I decided that those
            # nitrogen-containing moieties where the acidic group is neutral
            # (rather than positively charged) will have "*" in the name.
            if "*" in prot_site_name:
                nitrogen_charge = nitrogen_charge - 1  # Undo what was done previously.

            for mol in mols:
                # Make a copy of the molecule.
                mol_copy = copy.deepcopy(mol)

                # Remove hydrogen atoms.
                try:
                    mol_copy = Chem.RemoveHs(mol_copy)
                except:
                    if not silent:
                        print(f"WARNING: Skipping poorly formed SMILES string: {Chem.MolToSmiles(mol_copy)}")
                    continue

                atom = mol_copy.GetAtomWithIdx(idx)

                explicit_bond_order_total = sum(
                    [b.GetBondTypeAsDouble() for b in atom.GetBonds()]
                )

                # Assign the protonation charge, with special care for
                # nitrogens
                element = atom.GetAtomicNum()
                if element == 7:
                    atom.SetFormalCharge(nitrogen_charge)

                    # Need to figure out how many hydrogens to add.
                    if nitrogen_charge == 1 and explicit_bond_order_total == 1:
                        atom.SetNumExplicitHs(3)
                    elif nitrogen_charge == 1 and explicit_bond_order_total == 2:
                        atom.SetNumExplicitHs(2)
                    elif nitrogen_charge == 1 and explicit_bond_order_total == 3:
                        atom.SetNumExplicitHs(1)
                    elif nitrogen_charge == 0 and explicit_bond_order_total == 1:
                        atom.SetNumExplicitHs(2)
                    elif nitrogen_charge == 0 and explicit_bond_order_total == 2:
                        atom.SetNumExplicitHs(1)
                    elif nitrogen_charge == -1 and explicit_bond_order_total == 2:
                        atom.SetNumExplicitHs(0)
                    elif nitrogen_charge == -1 and explicit_bond_order_total == 1:
                        atom.SetNumExplicitHs(1)
                    #### JDD
                else:
                    atom.SetFormalCharge(charge)
                    if element == 8 or element == 16:  # O and S
                        if charge == 0 and explicit_bond_order_total == 1:
                            atom.SetNumExplicitHs(1)
                        elif charge == -1 and explicit_bond_order_total == 1:
                            atom.SetNumExplicitHs(0)

                # Deprotonating protonated aromatic nitrogen gives [nH-]. Change this
                # to [n-].
                if "[nH-]" in Chem.MolToSmiles(mol_copy):
                    atom.SetNumExplicitHs(0)

                mol_copy.UpdatePropertyCache(strict=False)

                output.append(mol_copy)

        return output


class ProtectUnprotectFuncs:
    """A namespace for storing functions that are useful for protecting and
    unprotecting molecules. To keep things organized. We need to identify and
    mark groups that have been matched with a substructure."""

    @staticmethod
    def unprotect_molecule(mol):
        """Sets the protected property on all atoms to 0. This also creates the
        property for new molecules.

        :param rdkit.Chem.rdchem.Mol mol: The rdkit Mol object.
        :type mol: The rdkit Mol object with atoms unprotected.
        """

        for atom in mol.GetAtoms():
            atom.SetProp("_protected", "0")

    @staticmethod
    def protect_molecule(mol, match):
        """Given a 'match', a list of molecules idx's, we set the protected status
        of each atom to 1. This will prevent any matches using that atom in the
        future.

        :param rdkit.Chem.rdchem.Mol mol: The rdkit Mol object to protect.
        :param list match: A list of molecule idx's.
        """

        for idx in match:
            atom = mol.GetAtomWithIdx(idx)
            atom.SetProp("_protected", "1")

    @staticmethod
    def get_unprotected_matches(mol, substruct):
        """Finds substructure matches with atoms that have not been protected.
        Returns list of matches, each match a list of atom idxs.

        :param rdkit.Chem.rdchem.Mol mol: The Mol object to consider.
        :param string substruct: The SMARTS string of the substructure ot match.
        :return: A list of the matches. Each match is itself a list of atom idxs.
        """

        matches = mol.GetSubstructMatches(substruct)
        unprotected_matches = []
        for match in matches:
            if ProtectUnprotectFuncs.is_match_unprotected(mol, match):
                unprotected_matches.append(match)
        return unprotected_matches

    @staticmethod
    def is_match_unprotected(mol, match):
        """Checks a molecule to see if the substructure match contains any
        protected atoms.

        :param rdkit.Chem.rdchem.Mol mol: The Mol object to check.
        :param list match: The match to check.
        :return: A boolean, whether the match is present or not.
        """

        for idx in match:
            atom = mol.GetAtomWithIdx(idx)
            protected = atom.GetProp("_protected")
            if protected == "1":
                return False
        return True


class TestFuncs:
    """A namespace for storing functions that perform tests on the code. To
    keep things organized."""

    @staticmethod
    def test():
        """Tests all the 38 groups."""

        # fmt: off
        smis = [
            # input smiles,            protonated,                  deprotonated,               category
            ["C#CCO",                  "C#CCO",                     "C#CC[O-]",                 "Alcohol"],
            ["C(=O)N",                 "NC=O",                      "[NH-]C=O",                 "Amide"],
            ["CC(=O)NOC(C)=O",         "CC(=O)NOC(C)=O",            "CC(=O)[N-]OC(C)=O",        "Amide_electronegative"],
            ["COC(=N)N",               "COC(N)=[NH2+]",             "COC(=N)N",                 "AmidineGuanidine2"],
            ["Brc1ccc(C2NCCS2)cc1",    "Brc1ccc(C2[NH2+]CCS2)cc1",  "Brc1ccc(C2NCCS2)cc1",      "Amines_primary_secondary_tertiary"],
            ["CC(=O)[n+]1ccc(N)cc1",   "CC(=O)[n+]1ccc([NH3+])cc1", "CC(=O)[n+]1ccc(N)cc1",     "Anilines_primary"],
            ["CCNc1ccccc1",            "CC[NH2+]c1ccccc1",          "CCNc1ccccc1",              "Anilines_secondary"],
            ["Cc1ccccc1N(C)C",         "Cc1ccccc1[NH+](C)C",        "Cc1ccccc1N(C)C",           "Anilines_tertiary"],
            ["BrC1=CC2=C(C=C1)NC=C2",  "Brc1ccc2[nH]ccc2c1",        "Brc1ccc2[n-]ccc2c1",       "Indole_pyrrole"],
            ["O=c1cc[nH]cc1",          "O=c1cc[nH]cc1",             "O=c1cc[n-]cc1",            "Aromatic_nitrogen_protonated"],
            ["C-N=[N+]=[N@H]",         "CN=[N+]=N",                 "CN=[N+]=[N-]",             "Azide"],
            ["BrC(C(O)=O)CBr",         "O=C(O)C(Br)CBr",            "O=C([O-])C(Br)CBr",        "Carboxyl"],
            ["NC(NN=O)=N",             "NC(=[NH2+])NN=O",           "N=C(N)NN=O",               "AmidineGuanidine1"],
            ["C(F)(F)(F)C(=O)NC(=O)C", "CC(=O)NC(=O)C(F)(F)F",      "CC(=O)[N-]C(=O)C(F)(F)F",  "Imide"],
            ["O=C(C)NC(C)=O",          "CC(=O)NC(C)=O",             "CC(=O)[N-]C(C)=O",         "Imide2"],
            ["CC(C)(C)C(N(C)O)=O",     "CN(O)C(=O)C(C)(C)C",        "CN([O-])C(=O)C(C)(C)C",    "N-hydroxyamide"],
            ["C[N+](O)=O",             "C[N+](=O)O",                "C[N+](=O)[O-]",            "Nitro"],
            ["O=C1C=C(O)CC1",          "O=C1C=C(O)CC1",             "O=C1C=C([O-])CC1",         "O=C-C=C-OH"],
            ["C1CC1OO",                "OOC1CC1",                   "[O-]OC1CC1",               "Peroxide2"],
            ["C(=O)OO",                "O=COO",                     "O=CO[O-]",                 "Peroxide1"],
            ["Brc1cc(O)cc(Br)c1",      "Oc1cc(Br)cc(Br)c1",         "[O-]c1cc(Br)cc(Br)c1",     "Phenol"],
            ["CC(=O)c1ccc(S)cc1",      "CC(=O)c1ccc(S)cc1",         "CC(=O)c1ccc([S-])cc1",     "Phenyl_Thiol"],
            ["C=CCOc1ccc(C(=O)O)cc1",  "C=CCOc1ccc(C(=O)O)cc1",     "C=CCOc1ccc(C(=O)[O-])cc1", "Phenyl_carboxyl"],
            ["COP(=O)(O)OC",           "COP(=O)(O)OC",              "COP(=O)([O-])OC",          "Phosphate_diester"],
            ["CP(C)(=O)O",             "CP(C)(=O)O",                "CP(C)(=O)[O-]",            "Phosphinic_acid"],
            ["CC(C)OP(C)(=O)O",        "CC(C)OP(C)(=O)O",           "CC(C)OP(C)(=O)[O-]",       "Phosphonate_ester"],
            ["CC1(C)OC(=O)NC1=O",      "CC1(C)OC(=O)NC1=O",         "CC1(C)OC(=O)[N-]C1=O",     "Ringed_imide1"],
            ["O=C(N1)C=CC1=O",         "O=C1C=CC(=O)N1",            "O=C1C=CC(=O)[N-]1",        "Ringed_imide2"],
            ["O=S(OC)(O)=O",           "COS(=O)(=O)O",              "COS(=O)(=O)[O-]",          "Sulfate"],
            ["COc1ccc(S(=O)O)cc1",     "COc1ccc(S(=O)O)cc1",        "COc1ccc(S(=O)[O-])cc1",    "Sulfinic_acid"],
            ["CS(N)(=O)=O",            "CS(N)(=O)=O",               "CS([NH-])(=O)=O",          "Sulfonamide"],
            ["CC(=O)CSCCS(O)(=O)=O",   "CC(=O)CSCCS(=O)(=O)O",      "CC(=O)CSCCS(=O)(=O)[O-]",  "Sulfonate"],
            ["CC(=O)S",                "CC(=O)S",                   "CC(=O)[S-]",               "Thioic_acid"],
            ["C(C)(C)(C)(S)",          "CC(C)(C)S",                 "CC(C)(C)[S-]",             "Thiol"],
            ["Brc1cc[nH+]cc1",         "Brc1cc[nH+]cc1",            "Brc1ccncc1",               "Aromatic_nitrogen_unprotonated"],
            ["C=C(O)c1c(C)cc(C)cc1C",  "C=C(O)c1c(C)cc(C)cc1C",     "C=C([O-])c1c(C)cc(C)cc1C", "Vinyl_alcohol"],
            ["CC(=O)ON",               "CC(=O)O[NH3+]",             "CC(=O)ON",                 "Primary_hydroxyl_amine"],
            # Note testing Internal_phosphate_polyphos_chain and
            # Initial_phosphate_like_in_ATP_ADP here because no way to
            # generate monoprotic compounds to test them. See Other tests
            # people...
        ]

        smis_phos = [
            # [input smiles,   protonated,       deprotonated1,       deprotonated2,          category]
            ["O=P(O)(O)OCCCC", "CCCCOP(=O)(O)O", "CCCCOP(=O)([O-])O", "CCCCOP(=O)([O-])[O-]", "Phosphate"],
            ["CC(P(O)(O)=O)C", "CC(C)P(=O)(O)O", "CC(C)P(=O)([O-])O", "CC(C)P(=O)([O-])[O-]", "Phosphonate"],
        ]
        # fmt: on

        cats_with_two_prot_sites = [inf[4] for inf in smis_phos]

        # Load the average pKa values.
        average_pkas = {
            l.split()[0].replace("*", ""): float(l.split()[3])
            for l in ProtSubstructFuncs.load_substructre_smarts_file()
            if l.split()[0] not in cats_with_two_prot_sites
        }
        average_pkas_phos = {
            l.split()[0].replace("*", ""): [float(l.split()[3]), float(l.split()[6])]
            for l in ProtSubstructFuncs.load_substructre_smarts_file()
            if l.split()[0] in cats_with_two_prot_sites
        }

        print("Running Tests")
        print("=============")
        print("")

        print("Very Acidic (pH -10000000)")
        print("--------------------------")
        print("")

        args = {
            "min_ph": -10000000,
            "max_ph": -10000000,
            "pka_precision": 0.5,
            "label_states": True,
            "silent": True
        }

        for smi, protonated, deprotonated, category in smis:
            TestFuncs.test_check(args, smi, [protonated], ["PROTONATED"])

        # Test phosphates separately
        for smi, protonated, mix, deprotonated, category in smis_phos:
            TestFuncs.test_check(args, smi, [protonated], ["PROTONATED"])

        args["min_ph"] = 10000000
        args["max_ph"] = 10000000

        print(args)

        print("")
        print("Very Basic (pH 10000000)")
        print("------------------------")
        print("")

        for smi, protonated, deprotonated, category in smis:
            TestFuncs.test_check(args, smi, [deprotonated], ["DEPROTONATED"])

        for smi, protonated, mix, deprotonated, category in smis_phos:
            TestFuncs.test_check(args, smi, [deprotonated], ["DEPROTONATED"])

        print("")
        print("pH is Category pKa")
        print("------------------")
        print("")

        for smi, protonated, deprotonated, category in smis:
            avg_pka = average_pkas[category]

            args["min_ph"] = avg_pka
            args["max_ph"] = avg_pka

            TestFuncs.test_check(args, smi, [protonated, deprotonated], ["BOTH"])

        for smi, protonated, mix, deprotonated, category in smis_phos:

            avg_pka = average_pkas_phos[category][0]
            args["min_ph"] = avg_pka
            args["max_ph"] = avg_pka

            TestFuncs.test_check(args, smi, [mix, protonated], ["BOTH"])

            avg_pka = average_pkas_phos[category][1]
            args["min_ph"] = avg_pka
            args["max_ph"] = avg_pka

            TestFuncs.test_check(args, smi, [mix, deprotonated], ["DEPROTONATED", "DEPROTONATED"])

            avg_pka = 0.5 * (average_pkas_phos[category][0] + average_pkas_phos[category][1])
            args["min_ph"] = avg_pka
            args["max_ph"] = avg_pka
            args["pka_precision"] = 5  # Should give all three

            TestFuncs.test_check(args, smi, [mix, deprotonated, protonated], ["BOTH", "BOTH"])

        print("")
        print("Other Tests")
        print("-----------")
        print("")

        # Make sure no carbanion (old bug).
        smi = "Cc1nc2cc(-c3[nH]c4cc5ccccc5c5c4c3CCN(C(=O)O)[C@@H]5O)cc3c(=O)[nH][nH]c(n1)c23"
        output = Protonator(silent=True).protonate(smi)

        if "[C-]" in "".join(output).upper():
            msg = "Processing " + smi + " produced a molecule with a carbanion!"
            raise Exception(msg)
        else:
            print("(CORRECT) No carbanion: " + smi)

        # Make sure max number of variants is limited (old bug).
        smi = "CCCC[C@@H](C(=O)N)NC(=O)[C@@H](NC(=O)[C@@H](NC(=O)[C@@H](NC(=O)[C@H](C(C)C)NC(=O)[C@@H](NC(=O)[C@H](Cc1c[nH]c2c1cccc2)NC(=O)[C@@H](NC(=O)[C@@H](Cc1ccc(cc1)O)N)CCC(=O)N)C)C)Cc1nc[nH]c1)Cc1ccccc1"
        output = Protonator(silent=True).protonate(smi)
        if len(output) != 128:
            msg = "Processing " + smi + " produced more than 128 variants!"
            raise Exception(msg)
        else:
            print("(CORRECT) Produced 128 variants: " + smi)

        # Make sure ATP and NAD work at different pHs (because can't test
        # Internal_phosphate_polyphos_chain and
        # Initial_phosphate_like_in_ATP_ADP with monoprotic examples.
        specific_examples = [
            [
                "O=P(O)(OP(O)(OP(O)(OCC1OC(C(C1O)O)N2C=NC3=C2N=CN=C3N)=O)=O)O",  # input, ATP
                (
                    0.5,
                    "[NH3+]c1[nH+]c[nH+]c2c1[nH+]cn2C1OC(COP(=O)(O)OP(=O)(O)OP(=O)(O)O)C(O)C1O",
                ),
                (
                    1.0,
                    "[NH3+]c1[nH+]c[nH+]c2c1[nH+]cn2C1OC(COP(=O)(O)OP(=O)([O-])OP(=O)(O)O)C(O)C1O",
                ),
                (
                    2.6,
                    "[NH3+]c1[nH+]c[nH+]c2c1[nH+]cn2C1OC(COP(=O)([O-])OP(=O)([O-])OP(=O)([O-])O)C(O)C1O",
                ),
                (
                    7.0,
                    "Nc1ncnc2c1ncn2C1OC(COP(=O)([O-])OP(=O)([O-])OP(=O)([O-])[O-])C(O)C1O",
                ),
            ],
            [
                "O=P(O)(OP(O)(OCC1C(O)C(O)C(N2C=NC3=C(N)N=CN=C32)O1)=O)OCC(O4)C(O)C(O)C4[N+]5=CC=CC(C(N)=O)=C5",  # input, NAD
                (
                    0.5,
                    "NC(=O)c1ccc[n+](C2OC(COP(=O)(O)OP(=O)(O)OCC3OC(n4cnc5c([NH3+])ncnc54)C(O)C3O)C(O)C2O)c1",
                ),
                (
                    2.5,
                    "NC(=O)c1ccc[n+](C2OC(COP(=O)([O-])OP(=O)([O-])OCC3OC(n4cnc5c([NH3+])ncnc54)C(O)C3O)C(O)C2O)c1",
                ),
                (
                    7.4,
                    "NC(=O)c1ccc[n+](C2OC(COP(=O)([O-])OP(=O)([O-])OCC3OC(n4cnc5c(N)ncnc54)C(O)C3O)C(O)C2O)c1",
                ),
            ],
        ]
        for example in specific_examples:
            smi = example[0]
            for ph, expected_output in example[1:]:
                output = Protonator(min_ph=ph, max_ph=ph, pka_precision=0, silent=True).protonate(smi)
                if output[0].strip() == expected_output:
                    print(
                        "(CORRECT) "
                        + smi
                        + " at pH "
                        + str(ph)
                        + " is "
                        + output[0].strip()
                    )
                else:
                    msg = (
                        smi
                        + " at pH "
                        + str(ph)
                        + " should be "
                        + expected_output
                        + ", but it is "
                        + output[0].strip()
                    )
                    raise Exception(msg)

    @staticmethod
    def test_check(args, smiles, expected_output, labels):
        """Tests most ionizable groups. The ones that can only loose or gain a single proton.

        :param args: The arguments to pass to the Protonator constructor
        :param expected_output: A list of the expected SMILES-strings output.
        :param labels: The labels. A list containing combo of BOTH, PROTONATED,
                    DEPROTONATED.
        :raises Exception: Wrong number of states produced.
        :raises Exception: Unexpected output SMILES.
        :raises Exception: Wrong labels.
        """

        output = list(Protonator(**args).protonate(smiles))
        output = [[value] + output[1] if isinstance(output[1], list) else [value, output[1]] for value in output[0]]

        num_states = len(expected_output)

        if len(output) != num_states:
            msg = (
                smiles
                + " should have "
                + str(num_states)
                + " states at at pH "
                + str(args["min_ph"])
                + ": "
                + str(output)
            )
            print(msg)
            raise Exception(msg)

        if len(set([l[0] for l in output]) - set(expected_output)) != 0:
            msg = (
                smiles
                + " is not "
                + " AND ".join(expected_output)
                + " at pH "
                + str(args["min_ph"])
                + " - "
                + str(args["max_ph"])
                + "; it is "
                + " AND ".join([l[0] for l in output])
            )
            print(msg)
            raise Exception(msg)

        if len(set([l[1] for l in output]) - set(labels)) != 0:
            msg = (
                smiles
                + " not labeled as "
                + " AND ".join(labels)
                + "; it is "
                + " AND ".join([l[1] for l in output])
            )
            print(msg)
            raise Exception(msg)

        ph_range = sorted(list(set([args["min_ph"], args["max_ph"]])))
        ph_range_str = "(" + " - ".join("{0:.2f}".format(n) for n in ph_range) + ")"
        print(
            "(CORRECT) "
            + ph_range_str.ljust(10)
            + " "
            + smiles
            + " => "
            + " AND ".join([l[0] for l in output])
        )


def run(smiles: Union[str, List[str], Chem.Mol, List[Chem.Mol]],
        min_ph: float = 6.4,
        max_ph: float = 8.4,
        pka_precision: float = 1.0,
        max_variants: int = 128,
        label_states: bool = False,
        silent: bool = False):
    """Run dimorphite-dl protonation on a list of molecules.

    :param smiles: List of SMILES of the molecules to be protonated
    :param min_ph: minimum pH to consider
    :param max_ph: maximum pH to consider
    :param pka_precision: pKa precision factor
    :param max_variants: limit number of variants per input compound
    :param label_states: label protonated SMILES with target state (i.e., "DEPROTONATED", "PROTONATED", or "BOTH")
    :param silent: do not print any messages to the screen
    """
    if smiles is None:
        return [None]
    if not isinstance(smiles, (str, list)):
        raise ValueError('smiles must be a string of characters or a list of strings')
    if not isinstance(smiles, list):
        smiles = [smiles]
    # Convert to SMILES
    smiles = [x if isinstance(x, str) else Chem.MolToSmiles(x) for x in smiles]
    # Create protonator iterator
    protonator = Protonator(min_ph=min_ph, max_ph=max_ph, pka_precision=pka_precision,
                            max_variants=max_variants, label_states=label_states,
                            silent=silent)
    res = []
    for smi in smiles:
        try:
            protonated_smis = protonator.protonate(smi)
            res.append(protonated_smis[0] if len(protonated_smis) == 1 else protonated_smis)
        except:
            res.append(None)
    return res
