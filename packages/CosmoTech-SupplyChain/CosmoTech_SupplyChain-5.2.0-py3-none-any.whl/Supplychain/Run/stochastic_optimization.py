import pandas
from typing import Union
import comets as co
import numpy as np

from Supplychain.Wrappers.simulator import CosmoEngine
from Supplychain.Generic.adx_and_file_writer import ADXAndFileWriter
from Supplychain.Generic.timer import Timer
from Supplychain.Run.simulation import run_simple_simulation
from Supplychain.Run.uncertainty_analysis_comets import UncertaintyAnalyzer
from Supplychain.Wrappers.environment_variables import EnvironmentVariables


class StochasticOptimizer:
    """
    Object in charge of performing an optimization on the results of an uncertainty analysis.
    It is possible to run an optimization without uncertainties if the dataset has ActivateUncertainties set to false.
    The main method of the StochasticOptimizer is run, which returns the results of the optimization.

    Args:
        simulation_name (str): Name of simulation, used by the probes
        KPI (str): Which KPI is objective of the optimization. Choose among "Profit", OPEX, AverageStockValue, ServiceLevelIndicator, ServiceLevelSatisfaction, CO2Emissions, TotalServedQuantity, IndividualServiceLevelSatisfaction.
        stat (str, optional): Which statistics of the KPI we care about. Choose among mean, std,	sem,	quantile 5%,	quantile 10%,	... ,	quantile 95%. Defaults to "mean".
        optimization_mode (str, optional): Optimization mode, choose among "maximize"/"minimize"/"target". Defaults to "maximize".
        target_value (float, optional): Target value to reach if optimization_mode is "target". Defaults to 0. Note service levels are expressed between 0 and 100.
        service_level_of_stocks (list, optional): If KPI is IndividualServiceLevelSatisfaction, choose for which stocks we want to optimize the service level. Defaults to [], which means for all stocks.
        decision_variables_entity_type (str, optional): Entity type for which we have levers (decision variables) we want to change. Defaults to "Stock".
        decision_variables_entities (list, optional): Choose which particular entities have levers we want to change, defaults to all entities of type above. Defaults to [].
        decision_variable_attribute (str, optional): Choose attribute which is a decision variable (lever) for the optimization. Defaults to "OrderQuantitySchedule".
        decision_variable_attribute_schedulable (bool, optional): Whether the chosen attribute is schedulable. Defaults to True.
        decision_variable_min (float, optional): Minimum value that the attribute can take (same for all entities), defines search space for the optimization. Defaults to 0.
        decision_variable_max (float, optional): Maximum value that the attribute can take (same for all entities), defines search space for the optimization. Defaults to 100.
        simulation_path (str): Name of the simulation file. Defaults to "Simulation".
        amqp_consumer_adress (Union[str, None], optional): Adress of consumer to send probe results to. Defaults to None.
        sample_size_uncertainty_analysis (int, optional): Number of simulations runs by the uncertainty analysis. Defaults to 100.
        batch_size_uncertainty_analysis (int, optional): Number of simulations runs that are run in a same batch by the uncertainty analysis. Defaults to 100.
        max_iterations_for_optim (int, optional): Max number of run of an uncertainty analysis during the optimization. Defaults to 100.
        max_duration_of_optim (int, optional): Max duration (s) of the optim, the optim runs until either this duration, or max_iterations_for_optim is reached. Defaults to 3600*10 (10h).
        optimization_algorithm (str, optional): Name of optimization algorithm. Defaults to NGOpt.
        optim_batch_size (int, optional): Choose batch size of optimization (highly dependent of algorithm choice). Defaults to 1.
        n_jobs (int, optional): Choose number of cpus used in parallel by the optimization. Note that the uncertainty analysis is also parallelized independently. Defaults to 1. Use -1 for all cpus available.
    """

    def __init__(
        self,
        simulation_name: str,
        KPI: str = "Profit",
        stat: str = "mean",
        optimization_mode: str = "maximize",
        target_value: float = 0,
        service_level_of_stocks: list = [],
        decision_variables_entity_type="Stock",
        decision_variables_entities: list = [],
        decision_variable_attribute: str = "SafetyQuantitySchedule",
        decision_variable_attribute_schedulable: bool = True,
        decision_variable_min: float = 0,
        decision_variable_max: float = 100,
        simulation_path: str = "Simulation",
        amqp_consumer_adress: Union[str, None] = None,
        sample_size_uncertainty_analysis: int = 25,
        batch_size_uncertainty_analysis: int = 25,
        max_iterations_for_optim: int = 1000,
        max_duration_of_optim: int = 3600 * 10,  # 10h
        optimization_algorithm: str = "NGOpt",
        optim_batch_size: int = 1,
        n_jobs: int = 1,
        n_jobs_ua: int = -1,
    ):
        self.simulation_name = simulation_name
        self.KPI = KPI
        self.stat = stat
        self.optimization_mode = optimization_mode
        self.target_value = target_value
        self.service_level_of_stocks = service_level_of_stocks
        if isinstance(decision_variables_entity_type, str):
            decision_variables_entity_type = [decision_variables_entity_type]
        self.decision_variables_entity_type = decision_variables_entity_type
        self.decision_variables_entities = decision_variables_entities
        self.decision_variable_attribute = decision_variable_attribute
        self.decision_variable_attribute_schedulable = (
            decision_variable_attribute_schedulable
        )
        self.decision_variable_min = decision_variable_min
        self.decision_variable_max = decision_variable_max
        self.simulation_path = simulation_path
        self.amqp_consumer_adress = amqp_consumer_adress
        self.sample_size_uncertainty_analysis = sample_size_uncertainty_analysis
        self.batch_size_uncertainty_analysis = batch_size_uncertainty_analysis
        self.max_iterations_for_optim = max_iterations_for_optim
        self.max_duration_of_optim = max_duration_of_optim
        self.optimization_algorithm = optimization_algorithm
        self.optim_batch_size = optim_batch_size
        self.n_jobs_optim = n_jobs
        self.n_jobs_ua = n_jobs_ua

    def initialize(self):
        """
        Initialize the optimization by collecting information from the simulator, creating the optimization space and task.
        """
        # Collect simulator information
        cosmo_interface = co.CosmoInterface(
            self.simulation_path, custom_sim_engine=CosmoEngine
        )
        cosmo_interface.initialize()

        if self.decision_variables_entities == []:
            entities = []
            for entity_type in self.decision_variables_entity_type:
                entities.append(self._get_entities(cosmo_interface, entity_type))

        else:
            entities = [self.decision_variables_entities]
        datapaths = []
        for entities_grouped_by_type in entities:
            datapaths += self._get_list_of_datapaths(
                cosmo_interface,
                entities_grouped_by_type,
                self.decision_variable_attribute,
            )

        list_of_init_values = self._get_init_value(
            cosmo_interface,
            datapaths,
            (self.decision_variable_max - self.decision_variable_min) / 2,
        )
        self.ActivateUncertainties = cosmo_interface.get_outputs(
            ["Model::@ActivateUncertainties"]
        )["Model::@ActivateUncertainties"]

        list_of_types = self._get_type(datapaths)
        cosmo_interface.terminate()

        # If uncertainties are not activated in the model, set standard parameters of uncertainty analysis
        if not self.ActivateUncertainties:
            self.sample_size_uncertainty_analysis = 1
            self.batch_size_uncertainty_analysis = 1
            self.stat = "mean"

        # Create decision variable space
        self.space = self._create_optim_space(
            datapaths,
            list_of_init_values,
            list_of_types,
            self.decision_variable_min,
            self.decision_variable_max,
        )

        # Create uncertainty analyzer
        consumers = ["Performances"]
        if self.KPI == "IndividualServiceLevelSatisfaction":
            consumers.append("StocksFinal")

        self.ua = UncertaintyAnalyzer(
            simulation_name=self.simulation_name,
            simulation_path=self.simulation_path,
            amqp_consumer_adress=None,
            sample_size=self.sample_size_uncertainty_analysis,
            batch_size=self.batch_size_uncertainty_analysis,
            consumers=consumers,
            cold_inputs={},
            validation_folder=None,
            n_jobs=self.n_jobs_ua,
        )

        # Initialize uncertainty analysis
        self.ua.initialize_simulator_interface()
        self.ua.collect_simulation_parameters()
        self.ua.create_encoder()
        self.ua.create_get_outcomes()
        self.ua.create_sampling()

        # Declare task running the uncertainty analysis
        def task(
            input_parameter_set,
            ua=self.ua,
            activateuncertainties=self.ActivateUncertainties,
            decision_variable_attribute_schedulable=self.decision_variable_attribute_schedulable,
            _compute_objective=_compute_objective,
            KPI=self.KPI,
            stat=self.stat,
            optimization_mode=self.optimization_mode,
            target_value=self.target_value,
            service_level_of_stocks=self.service_level_of_stocks,
        ):
            if activateuncertainties:
                np.random.seed()
            else:
                np.random.seed(0)

            new_input_parameter_set = {}
            if decision_variable_attribute_schedulable:
                for key, value in input_parameter_set.items():
                    new_input_parameter_set[key] = {0: value}  # Transform to schedule
            else:
                new_input_parameter_set = input_parameter_set

            ua.create_task(new_input_parameter_set)
            ua.run_experiment()
            ua.reformat_results()

            objective = _compute_objective(
                ua.results,
                KPI=KPI,
                stat=stat,
                optimization_mode=optimization_mode,
                target_value=target_value,
                service_level_of_stocks=service_level_of_stocks,
            )
            return objective

        self.task = task

    def run(self):
        """Run the optimization

        Returns:
            Tuple: (kpi_results, optimal_decision_variables, optimal_decision_variables_df, optimization_history)
                kpi_results is a dictionary containing key Objective (the optimal value of the objective function) and kay KPI (the optimal value of the KPI, may be different from the objective)
                optimal_decision_variables is a dictionary (ParameterSet) with keys that are datapaths of decision variables, and values that are their recommended value by the optimization.
                    It may be used to launch a new uncertainty analysis with the optimal decision variables.
                optimal_decision_variables_df is a pandas dataframe containing the recommended choice of decision variables, with columns  Datapath, Value, Attribute, Entity.
                optimization_history is a pandas dataframe containing the optimization metrics, with columns ObjectiveValue, KPIValue, Iteration, KPI, Stat, optimization_mode, target_value.
        """
        with Timer("[Run stochastic optimization]") as t:
            self.initialize()

            opt = co.Optimization(
                space=self.space,
                task=self.task,
                objective="Objective",
                maximize=(self.optimization_mode == "maximize"),
                algorithm=self.optimization_algorithm,
                batch_size=self.optim_batch_size,
                stop_criteria={
                    "max_evaluations": self.max_iterations_for_optim,
                    "max_duration": self.max_duration_of_optim,
                },
                n_jobs=self.n_jobs_optim,
                save_optimization_history=True,
            )

            opt.run()

            kpi_results = self._reformat_kpi_results(opt)
            optimization_history = self._reformat_optimization_history(
                opt.optimization_history
            )
            optimal_decision_variables = opt.results["Optimal variables"]
            optimal_decision_variables_df = self._reformat_decision_variables_results(
                optimal_decision_variables
            )

            if self.optimization_algorithm == "NGOpt" and self.optim_batch_size == 1:
                del opt.optimizationalgorithm

            t.display_message("Running simple simulation to fill ADX")
            # Put back log level to Info for final simulation
            # Reduce log level to Error during optimization
            logger = CosmoEngine.LoggerManager.GetInstance().GetLogger()
            logger.SetLogLevel(logger.eInfo)

        return (
            kpi_results,
            optimal_decision_variables,
            optimal_decision_variables_df,
            optimization_history,
        )

    def _create_optim_space(
        self, datapaths, list_of_init_values, list_of_types, minimum, maximum
    ):
        space = []
        for datapath, init, type in zip(datapaths, list_of_init_values, list_of_types):
            space.append(
                {
                    "name": datapath,
                    "type": str(type),
                    "bounds": [minimum, maximum],
                    "init": init,
                }
            )
        return space

    def _get_init_value(self, cosmo_interface, list_of_datapaths, default):
        list_of_init_values = []
        inits = cosmo_interface.get_outputs(list_of_datapaths)
        for datapath in list_of_datapaths:
            if isinstance(inits[datapath], dict):
                if 0 not in inits[datapath]:
                    list_of_init_values.append(default)
                else:
                    if (
                        inits[datapath][0] <= self.decision_variable_max
                        and inits[datapath][0] >= self.decision_variable_min
                    ):
                        list_of_init_values.append(inits[datapath][0])
                    else:
                        list_of_init_values.append(default)
            else:
                if (
                    inits[datapath] <= self.decision_variable_max
                    and inits[datapath] >= self.decision_variable_min
                ):
                    list_of_init_values.append(inits[datapath])
                else:
                    list_of_init_values.append(default)
        return list_of_init_values

    def _get_list_of_datapaths(self, cosmo_interface, list_of_entities, attribute):
        # Retrieve the datapath of attributes for all entities in list_of_entities
        list_of_datapaths = []

        datapaths = cosmo_interface.get_datapaths()

        for entity in list_of_entities:
            list_of_datapaths.append(
                list(
                    filter(
                        lambda x: str("{Entity}" + entity + f"::@{attribute}") in x,
                        datapaths,
                    )
                )[0]
            )

        return list_of_datapaths

    def _get_entities(self, cosmo_interface, decision_variables_entity_type):
        # Retrieve the name of all the entities whose type corresponds to the one selected by the user

        list_of_entities = sorted(
            entity.GetName()
            for entity in cosmo_interface.sim.GetModel().FindEntitiesByType(
                decision_variables_entity_type
            )
        )

        if list_of_entities == []:
            raise ValueError(
                f"No entity of type {decision_variables_entity_type} is present in the instance, the optimization is not supported."
            )

        return list_of_entities

    def _reformat_decision_variables_results(self, decision_variables):
        results = pandas.DataFrame(
            [
                {"Datapath": key, "Value": value}
                for (key, value) in decision_variables.items()
            ]
        )
        results["Attribute"] = self.decision_variable_attribute
        results["Entity"] = results["Datapath"].apply(
            lambda x: x.split("{Entity}")[-1].split("::@")[0]
        )
        results["SimulationRun"] = EnvironmentVariables.simulation_id
        return results

    def _reformat_optimization_history(self, list_of_results):
        rows = []
        if self.KPI != "IndividualServiceLevelSatisfaction":
            for ((iteration, objective), kpivalue) in zip(
                enumerate(list_of_results["mean_objective"]),
                list_of_results["mean_task_outputs"],
            ):
                rows.append(
                    {
                        "ObjectiveValue": objective,
                        "KPIValue": kpivalue["KPI"],
                        "Iteration": iteration,
                        "KPI": self.KPI,
                        "Stat": self.stat,
                        "optimization_mode": self.optimization_mode,
                        "target_value": self.target_value,
                        "SimulationRun": EnvironmentVariables.simulation_id,
                    }
                )
        else:
            for ((iteration, objective), kpivalue) in zip(
                enumerate(list_of_results["mean_objective"]),
                list_of_results["all_task_outputs"],
            ):
                rows.append(
                    {
                        "ObjectiveValue": objective,
                        "KPIValue": np.mean(kpivalue[0]["KPI"]),
                        "Iteration": iteration,
                        "KPI": self.KPI,
                        "Stat": self.stat,
                        "optimization_mode": self.optimization_mode,
                        "target_value": self.target_value,
                        "SimulationRun": EnvironmentVariables.simulation_id,
                    }
                )
        return pandas.DataFrame(rows)

    def _reformat_kpi_results(self, opt):
        results = self.task(opt.results["Optimal variables"])
        results["SimulationRun"] = EnvironmentVariables.simulation_id
        return pandas.DataFrame(results, index=[0])

    def _get_type(self, list_of_datapaths):
        """
        Returns the type of each of the decision variable
        """
        type_mapping = {
            "OpeningTimeSchedule": "float",
            "OrderPointSchedule": "float",
            "OrderQuantitySchedule": "float",
            "SafetyQuantitySchedule": "float",
            "SourcingProportionSchedule": "float",
            "ReviewPeriod": "int",
            "Advance": "int",
        }
        list_of_types = []
        for datapaths in list_of_datapaths:
            list_of_types.append(type_mapping[self.decision_variable_attribute])
        return list_of_types


# Implementing a function instead of a method to be able to use it in the multiprocessing module
def _compute_objective(
    results, KPI, stat, optimization_mode, target_value, service_level_of_stocks
):
    if KPI != "IndividualServiceLevelSatisfaction":
        results["Performances"] = results["Performances"].set_index("KPI")
        kpi = results["Performances"].loc[KPI, stat]
        if optimization_mode == "target":
            objective = {"Objective": (kpi - target_value) ** 2, "KPI": kpi}
        else:
            objective = {"Objective": kpi, "KPI": kpi}
    else:
        df_service = results["StocksFinal"][
            results["StocksFinal"]["Indicator"] == "ServiceLevelSatisfaction"
        ]
        if service_level_of_stocks != []:
            df_service = df_service[df_service["StockId"].isin(service_level_of_stocks)]
        vector_of_service_levels = df_service[stat].to_numpy()
        if optimization_mode == "target":
            distance_to_target = (vector_of_service_levels - target_value) ** 2
            objective = {
                "Objective": np.max(distance_to_target),  # np.sum(distance_to_target)
                "KPI": list(vector_of_service_levels),
            }
        else:
            objective = {
                "Objective": np.sum(vector_of_service_levels),
                "KPI": list(vector_of_service_levels),
            }
    return objective
