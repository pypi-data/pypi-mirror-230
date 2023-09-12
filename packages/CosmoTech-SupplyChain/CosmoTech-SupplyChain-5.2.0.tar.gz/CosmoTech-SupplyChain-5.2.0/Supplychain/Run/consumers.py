class StockConsumer:
    """
    Python Consumer for stocks indicators at each time step.
    """

    def __init__(self):
        self.memory = list()

    def Consume(self, p_data):
        probe_output = self.engine.StocksProbeOutput.Cast(p_data)
        f = probe_output.GetFacts()
        timestep = int(probe_output.GetProbeRunDimension().GetProbeOutputCounter())
        for data in f:
            fact = [
                str(data.GetAttributeAsString("ID")),
                timestep,
                float(data.GetAttributeAsFloat64("Demand")),
                float(data.GetAttributeAsFloat64("RemainingQuantity")),
                float(data.GetAttributeAsFloat64("ServedQuantity")),
                float(data.GetAttributeAsFloat64("UnservedQuantity")),
                float(data.GetAttributeAsFloat64("ServiceLevel")),
                float(data.GetAttributeAsFloat64("Value")),
            ]
            self.memory.append(fact)


class PerformanceConsumer:
    """
    Python Consumer for performance indicators at the end of the simulation.
    """

    def __init__(self):
        self.memory = list()

    def Consume(self, p_data):
        probe_output = self.engine.PerformanceIndicatorsProbeOutput.Cast(p_data)
        f = probe_output.GetFacts()
        for data in f:
            fact = {
                "OPEX": float(data.GetAttributeAsFloat64("OPEX")),
                "Profit": float(data.GetAttributeAsFloat64("Profit")),
                "AverageStockValue": float(
                    data.GetAttributeAsFloat64("AverageStockValue")
                ),
                "ServiceLevelIndicator": float(
                    data.GetAttributeAsFloat64("ServiceLevelIndicator")
                ),
                "CO2Emissions": float(data.GetAttributeAsFloat64("CO2Emissions")),
                "TotalDemand": float(data.GetAttributeAsFloat64("TotalDemand")),
                "TotalServedQuantity": float(
                    data.GetAttributeAsFloat64("TotalServedQuantity")
                ),
                "ServiceLevelSatisfaction": data.GetTotalServedQuantity().GetAsFloat()
                / data.GetTotalDemand().GetAsFloat()
                * 100
                if data.GetTotalDemand().GetAsFloat() != 0
                else 0,
            }
            self.memory.append(fact)


class StocksFinalConsumer:
    """
    Python Consumer for stocks global indicators at the end of the simulation.
    """

    def __init__(self):
        self.memory = list()

    def Consume(self, p_data):
        probe_output = self.engine.StocksFinalProbeOutput.Cast(p_data)
        f = probe_output.GetFacts()
        for data in f:
            fact = {
                "ID": str(data.GetAttributeAsString("ID")),
                "TotalDemand": float(data.GetAttributeAsFloat64("TotalDemand")),
                "TotalServedQuantity": float(
                    data.GetAttributeAsFloat64("TotalServedQuantity")
                ),
                "ServiceLevelSatisfaction": 100
                * float(data.GetAttributeAsFloat64("ServiceLevelSatisfaction"))
                if float(data.GetAttributeAsFloat64("TotalDemand")) > 0
                else None,
                "CycleServiceLevel": float(data.GetAttributeAsFloat64("CycleServiceLevel")),
            }
            self.memory.append(fact)
