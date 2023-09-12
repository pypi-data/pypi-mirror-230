from typing import Union
from Supplychain.Wrappers.simulator import CosmoEngine


def run_simple_simulation(simulation_name: str,
                          simulation_path: str = 'Simulation',
                          amqp_consumer_adress: Union[str, None] = None,
                          modifications: Union[dict, None] = None) -> bool:
    simulator = CosmoEngine.LoadSimulator(simulation_path)

    if modifications:
        for datapath, stringvalue in modifications.items():
            simulator.FindAttribute(datapath).SetAsString(stringvalue)

    if amqp_consumer_adress is not None:
        # Remove old consumers
        for consumer in simulator.GetConsumers():
            simulator.DestroyConsumer(consumer)

        # Instantiate consumers using AMQP to send data to the cloud service
        simulator.InstantiateAMQPConsumers(simulation_name, amqp_consumer_adress)

    # Run simulation
    simulator.Run()
    return simulator.IsFinished()
