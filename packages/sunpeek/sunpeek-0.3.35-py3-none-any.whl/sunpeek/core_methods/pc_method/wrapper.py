import datetime as dt
from typing import Union, Any, List, Optional
import itertools
from enum import Enum

from sunpeek.common.utils import sp_logger
from sunpeek.components import Plant
from sunpeek.components.base import AlgoCheckMode
from sunpeek.core_methods import CoreAlgorithm, CoreStrategy
from sunpeek.serializable_models import ProblemReport, PCMethodProblem, AlgoProblem, ProblemType
from sunpeek.core_methods.pc_method.main import PCMethod
from sunpeek.core_methods.pc_method import AvailablePCFormulae, AvailablePCMethods
from sunpeek.core_methods.common.main import AlgoResult

def run_performance_check(plant: Plant,
                          method: Optional[List[Union[None, str, AvailablePCMethods]]] = None,
                          formula: Optional[List[Union[None, int, AvailablePCFormulae]]] = None,
                          use_wind: Optional[List[Union[None, bool]]] = None,
                          # Settings:
                          safety_pipes: Optional[float] = None,
                          safety_uncertainty: Optional[float] = None,
                          safety_others: Optional[float] = None,
                          interval_length: Optional[dt.timedelta] = None,
                          min_data_in_interval: Optional[int] = None,
                          max_gap_in_interval: Optional[dt.timedelta] = None,
                          max_nan_density: Optional[float] = None,
                          min_intervals_in_output: Optional[int] = None,
                          check_accuracy_level: Optional[str] = None,
                          ) -> AlgoResult:
    """Run Performance Check analysis with given settings, trying all possible strategies in order.
    """
    kwds = {
        'safety_pipes': safety_pipes,
        'safety_uncertainty': safety_uncertainty,
        'safety_others': safety_others,
        'interval_length': interval_length,
        'min_data_in_interval': min_data_in_interval,
        'max_gap_in_interval': max_gap_in_interval,
        'max_nan_density': max_nan_density,
        'min_intervals_in_output': min_intervals_in_output,
        'check_accuracy_level': check_accuracy_level,
    }

    pc_algo = PCAlgo(plant, methods=method, formulae=formula, use_wind=use_wind, **kwds)
    algo_result = pc_algo.run()
    return algo_result


def get_pc_problemreport(plant: Plant,
                         method: Optional[List[Union[None, str, AvailablePCMethods]]] = None,
                         formula: Optional[List[Union[None, int, AvailablePCFormulae]]] = None,
                         use_wind: Optional[List[Union[None, bool]]] = None,
                         # Settings:
                         safety_pipes: Optional[float] = None,
                         safety_uncertainty: Optional[float] = None,
                         safety_others: Optional[float] = None,
                         interval_length: Optional[dt.timedelta] = None,
                         min_data_in_interval: Optional[int] = None,
                         max_gap_in_interval: Optional[dt.timedelta] = None,
                         max_nan_density: Optional[float] = None,
                         min_intervals_in_output: Optional[int] = None,
                         check_accuracy_level: Optional[str] = None,
                         ) -> ProblemReport:
    """Report which strategies of the Performance Check analysis can be run with given plant and settings,
    without actually running calculations.
    """
    kwds = {
        'safety_pipes': safety_pipes,
        'safety_uncertainty': safety_uncertainty,
        'safety_others': safety_others,
        'interval_length': interval_length,
        'min_data_in_interval': min_data_in_interval,
        'max_gap_in_interval': max_gap_in_interval,
        'max_nan_density': max_nan_density,
        'min_intervals_in_output': min_intervals_in_output,
        'check_accuracy_level': check_accuracy_level,
    }

    pc_algo = PCAlgo(plant, methods=method, formulae=formula, use_wind=use_wind, **kwds)
    return pc_algo.get_config_problems()


def list_pc_problems(plant: Plant,
                     method: Optional[List[Union[None, str, AvailablePCMethods]]] = None,
                     formula: Optional[List[Union[None, int, AvailablePCFormulae]]] = None,
                     use_wind: Optional[List[Union[None, bool]]] = None,
                     ) -> List[PCMethodProblem]:
    """Report which strategies of the Performance Check analysis can be run with given plant config,
    without actually running calculations.
    """
    pc_algo = PCAlgo(plant, methods=method, formulae=formula, use_wind=use_wind)
    out = []
    for strategy in pc_algo.strategies:
        report = strategy.get_problem_report(AlgoCheckMode.config_only)
        out.append(PCMethodProblem(strategy.pc.mode.value,
                                   strategy.pc.formula.id,
                                   strategy.pc.formula.use_wind,
                                   report.success,
                                   report.parse()))
    return out


class PCStrategy(CoreStrategy):
    def __init__(self, pc: PCMethod):
        super().__init__(pc.plant)
        self.pc = pc
        self.name = f'Evaluation mode: { AvailablePCMethods.iso.value if pc.mode == AvailablePCMethods.iso else AvailablePCMethods.extended.value}, ' \
                    f'Formula: {pc.formula.id}, ' \
                    f'{"Using wind" if pc.formula.use_wind else "Ignoring wind"}'

    def _calc(self):
        return self.pc.run()  # results.PCMethodOutput

    def _report_problems(self, check_mode: AlgoCheckMode) -> ProblemReport:
        return self.pc.report_problems(check_mode)


class PCAlgo(CoreAlgorithm):

    def define_strategies(self, methods=None, formulae=None, use_wind=None, **kwargs) -> List[PCStrategy]:
        """Returns list of all possible PC method strategies in the order they will be executed.
        """

        def process_args(arg, arg_name, allowed_type) -> List[Any]:
            # Make sure arg is a list of allowed_type (bool or Enum). Remove None elements and duplicates.

            if isinstance(allowed_type, type) and issubclass(allowed_type, Enum):
                allowed_values = {x.value for x in allowed_type}
            elif allowed_type is bool:
                allowed_values = {True, False}
            else:
                raise TypeError("Invalid allowed_type: Must be either bool or an Enum class.")

            arg = arg if isinstance(arg, list) else [arg]
            for item in arg:
                if item not in allowed_values | {None}:
                    raise ValueError(f'Invalid input value "{item}" for "{arg_name}". '
                                     f'Expected: {", ".join(map(str, allowed_values))}.')

            # Remove None and duplicates
            processed = [x for x in arg if x is not None]
            processed = list(dict.fromkeys(processed))
            return processed

        all_methods = process_args(methods, 'methods', AvailablePCMethods)
        all_methods = all_methods if all_methods else [AvailablePCMethods.iso, AvailablePCMethods.extended]

        all_formulae = process_args(formulae, 'formulae', AvailablePCFormulae)
        all_formulae = all_formulae if all_formulae else [AvailablePCFormulae.two, AvailablePCFormulae.one]

        all_wind = process_args(use_wind, 'use_wind', bool)
        all_wind = all_wind if all_wind else [True, False]

        all_variants = list(itertools.product(*[all_methods, all_formulae, all_wind]))
        strategies = [pc_strategy_generator(self.component, m, e, w, **kwargs) for m, e, w in all_variants]

        return strategies


def pc_strategy_generator(plant: Plant,
                          method: AvailablePCMethods,
                          formula: AvailablePCFormulae,
                          use_wind: bool,
                          **kwargs) -> PCStrategy:
    pc = PCMethod.from_method(method, plant, formula, use_wind, **kwargs)

    return PCStrategy(pc)


def get_pc_successful_strategy(plant: Plant,
                               method: Optional[List[Union[None, str, AvailablePCMethods]]] = None,
                               formula: Optional[List[Union[None, int, AvailablePCFormulae]]] = None,
                               use_wind: Optional[List[Union[None, bool]]] = None,
                               # Settings:
                               safety_pipes: Optional[float] = None,
                               safety_uncertainty: Optional[float] = None,
                               safety_others: Optional[float] = None,
                               interval_length: Optional[dt.timedelta] = None,
                               min_data_in_interval: Optional[int] = None,
                               max_gap_in_interval: Optional[dt.timedelta] = None,
                               max_nan_density: Optional[float] = None,
                               min_intervals_in_output: Optional[int] = None,
                               check_accuracy_level: Optional[str] = None,
                               ) -> PCStrategy:
    """Report the first strategy of the Performance Check analysis that is successful with given plant and
    settings. Like `get_pc_problemreport()`, this does not actually run calculations.
    """
    kwds = {
        'safety_pipes': safety_pipes,
        'safety_uncertainty': safety_uncertainty,
        'safety_others': safety_others,
        'interval_length': interval_length,
        'min_data_in_interval': min_data_in_interval,
        'max_gap_in_interval': max_gap_in_interval,
        'max_nan_density': max_nan_density,
        'min_intervals_in_output': min_intervals_in_output,
        'check_accuracy_level': check_accuracy_level,
    }

    pc_algo = PCAlgo(plant, methods=method, formulae=formula, use_wind=use_wind, **kwds)
    strategy = pc_algo.successful_strategy

    return strategy  # noqa
