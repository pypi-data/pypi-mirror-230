from typing import Dict
from typing import List
from copy import deepcopy

from numpy import ndarray
import json
from h5py import File as h5File

from .variable import Variable
from .variable import check_values_match


class ValueCache:

    CACHE_POLICY_LATEST = "latest"

    CACHE_POLICY_FULL = "full"

    CACHE_POLICY = [CACHE_POLICY_LATEST,
                  CACHE_POLICY_FULL]

    def __init__(self,
                 inputVars: List[Variable],
                 outputVars: List[Variable],
                 policy: str = CACHE_POLICY_LATEST,
                 tol: float = 1e-9,
                 path: str = None) -> None:

        self.inputVars = inputVars

        self.outputVars = outputVars

        self.policy = policy

        self.tol = tol

        self.entries = []

        self.path = path

    def check_if_entry_exists(self, inputs: Dict[str, ndarray]):

        if not self.entries:

            return None

        for entry in reversed(self.entries):

            if check_values_match(self.inputVars,
                                  entry["inputs"],
                                  inputs,
                                  self.tol):

                return entry

        return None

    def add_entry(self,
                  inputs: Dict[str, ndarray],
                  outputs: Dict[str, ndarray] = None,
                  jac: Dict[str, Dict[str, ndarray]] = None) -> None:
        """

        Adds an entry in the cache for the given inputs.

        If an entry already exists, the existing output/jacobian values 
        are overriden by the ones provided.

        """

        newEntry = self.check_if_entry_exists(inputs)

        if newEntry is None:

            newEntry = {"inputs": {var.name: deepcopy(inputs[var.name]) for var in self.inputVars},
                        "outputs": {},
                        "jac": {}}

        if outputs is not None:
            newEntry["outputs"] = {var.name: deepcopy(
                outputs[var.name]) for var in self.outputVars}

        if jac is not None:

            for outVar in self.outputVars:

                if outVar.name in jac:

                    newEntry["jac"][outVar.name] = {}

                for inVar in self.inputVars:

                    if inVar.name in jac[outVar.name]:

                        newEntry["jac"][outVar.name][inVar.name] = deepcopy(
                            jac[outVar.name][inVar.name])
                                    
        if self.policy == self.CACHE_POLICY_LATEST:

            self.entries = []

        self.entries.append(newEntry)

    def load_entry(self, inputs: Dict[str, ndarray]):

        entry = self.check_if_entry_exists(inputs)

        if entry is not None:

            return deepcopy(entry["outputs"]), deepcopy(entry["jac"])

        return None, None

    def to_json(self, path: str):

        jsonObj = []

        for entry in self.entries:

            jsonObj.append({"inputs": {},
                            "outputs": {},
                            "jac": {}})
            
            for inVar in self.inputVars:

                jsonObj[-1]["inputs"][inVar.name] = entry["inputs"][inVar.name].tolist()

            for outVar in self.outputVars:

                jsonObj[-1]["outputs"][outVar.name] = entry["outputs"][outVar.name].tolist()
            
            for outVarName in entry["jac"]:
                
                jsonObj[-1]["jac"][outVarName] = {}
                
                for inVarName in entry["jac"][outVarName]:

                    jsonObj[-1]["jac"][outVarName][inVarName] = entry["jac"][outVarName][inVarName].tolist()

        jsonObj = json.dumps(jsonObj, indent=4)

        with open(path, "w") as file:

            file.write(jsonObj)

def cache_factory(inputVars: List[Variable],
                  outputVars: List[Variable],
                  cacheType: str = "memory",
                  cachePolicy: str = "latest",
                  tol: float = 1e-9,
                  cacheFile: str = None):
    
    if cacheType is None:

        return None
    
    if cacheType == "memory":

        return ValueCache(inputVars,
                   outputVars,
                   cachePolicy,
                   tol,
                   cacheFile)
    
    elif cacheType == "file":

        raise NotImplementedError

