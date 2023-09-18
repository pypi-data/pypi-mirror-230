from os.path import join
from typing import Dict
from typing import List
from typing import Tuple
from warnings import warn

from numpy import ndarray
from numpy import zeros
from numpy import abs
from numpy import mean
import matplotlib.pyplot as plt

from pymdo.core.discipline import Discipline
from pymdo.core.tools import SeperateInputsAndOutputs
from pymdo.core.derivative_assembler import DerivativeAssembler


class MDANotEvaluatedError(Exception):
    def __init__(self, _mdaName: str) -> None:
        self.message = f"{_mdaName} is not yet evaluated"
        super().__init__(self.message)


class MDANotConverged(Warning):
    def __init__(self, _mdaName: str, _nMaxIter: int, _res: float, _relTol: float) -> None:
        self.message = f"{_mdaName} has not converged in {_nMaxIter} iterations, (residual) {_res} > (tolerance) {_relTol}"
        super().__init__(self.message)


class MDA(Discipline):
    """

    Base MDA class 

    """

    MDA_SUCCESS = True

    MDA_FAIL = False

    MDA_STATUS = [MDA_SUCCESS,
                  MDA_FAIL]

    def __init__(self,
                 disciplines: List[Discipline],
                 name: str,
                 nIterMax: int = 15,
                 relaxFact: float = 0.9,
                 relTol: float = 0.0001
                 ) -> None:

        self.disciplines: List[Discipline] = disciplines
        """ Disciplines to be included in the analysis """

        self.nIterMax = nIterMax
        """ Maximum number of iterations """

        self.relaxFact = relaxFact
        """ Relaxation factor """

        self.relTol = relTol
        """ Relative tolerance """

        self.residualLog: List[Dict[str, float]] = []
        """ Residual log from last evaluation """

        self.mdaStatus: bool = self.MDA_FAIL
        """ Whether the last execution converged """

        inputVars, outputVars = SeperateInputsAndOutputs(self.disciplines)

        super().__init__(name,
                         inputVars,
                         outputVars)

    def set_options(self, nIterMax: int = 15, relaxFact: float = 0.9, relTol: float = 0.0001) -> None:
        self.nIterMax = nIterMax
        self.relaxFact = relaxFact
        self.relTol = relTol

    def _eval(self) -> None:
        raise NotImplementedError

    def eval(self, inputValues: Dict[str, ndarray] = None) -> Dict[str, ndarray]:
        """ 

        Evaluate the MDA with the given inputs.

        All inputs (and outputs) not provided are set to zero.
        If they are not provided directly, but set in default values,
        those values are used. Finally, the default MDA values are overriden
        by default discipline values, if they are set.

        """

        for varList in [self.inputVars, self.outputVars]:
            for var in varList:
                if var.name not in self.defaultInputs:
                    self.defaultInputs[var.name] = zeros(var.size,
                                                            self._floatDataType)

        for disc in self.disciplines:
            self.defaultInputs.update(disc.defaultInputs)

        return super().eval(inputValues)

    def _differentiate(self) -> None:

        for disc in self.disciplines:

            disc.differentiate()

        assembler = DerivativeAssembler(self.disciplines,
                                        self.outputVars,
                                        self.diffInputs,
                                        self.diffOutputs)

        self.jac = assembler.dFdX()
        
    def _compute_residual(self,
                         curOutputValues: Dict[str, ndarray],
                         prevOutputValues: Dict[str, ndarray]) -> ndarray:
        """
        
        Compute the residual namely the difference:
        
        _curOutputValues - _prevOutputValues

        for all coupling/output variables, and return it.

        The residual log is also updated, 
        but only a residual metric for each variable (and a total) is stored.

        The status is set to MDA_SUCCESS,
        if the total residual metric is below the specified tolerance.
        
        """

        residual: ndarray = zeros(self.sizeOutputs,
                                     self._floatDataType)
        
        residualMetric: Dict[str, float] = {}

        totalRes: float = 0.0

        r = 0

        for outVar in self.outputVars:

            residual[r: r + outVar.size] = curOutputValues[outVar.name] - prevOutputValues[outVar.name]

            residualMetric[outVar.name] = abs(mean(residual[r: r + outVar.size]) 
                                                 / mean(curOutputValues[outVar.name]))

            totalRes += residualMetric[outVar.name]

            r += outVar.size

        residualMetric["total"] = totalRes

        self.residualLog.append(residualMetric)

        if totalRes <= self.relTol:
            self.mdaStatus = self.MDA_SUCCESS

        return residual

    def plot_residual(self, varNames: List[str] = None, show: bool = True, save: bool = False, path = "") -> None:
        """

        Plot the residual metric log for all provided variable names.

        Use the name "total", to plot the total MDA residual metric 

        """

        if varNames == None:
            varNames = [var.name for var in self.outputVars]
            varNames += ["total"]

        if not self.residualLog:
            raise MDANotEvaluatedError(self.name)

        fig, ax = plt.subplots(1, 1)

        for varName in varNames:
            ax.plot([i for i in range(len(self.residualLog))],
                    [self.residualLog[i][varName]
                     for i in range(len(self.residualLog))],
                    label=varName)

        ax.set_title(f"{self.name} residual metric")
        ax.set_ylabel("Residual metric")
        ax.set_xlabel("Iterations")
        ax.legend()

        if save:
            plt.savefig(fname=join(path, self.name))

        if show:
            plt.show()

        return ax

    def _terminate_condition(self) -> bool:

        if self.mdaStatus == self.MDA_SUCCESS:
            """ If converged, exit early """
            return True

        curIter: int = len(self.residualLog)
        """ Current iteration """

        curRes: float = 0.0 if not self.residualLog else self.residualLog[-1]["total"]
        """ Current (total) residual metric """


        if curIter == self.nIterMax:

            if self.mdaStatus == self.MDA_FAIL:
                """ Iteration limit reached, and MDA has not converged """

                message = f"{self.name} has not converged in {self.nIterMax} iterations, (residual) {curRes} > (tolerance) {self.relTol}"
            
                warn(message)

            return True

        return False