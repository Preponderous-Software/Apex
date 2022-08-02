from config import Config
from simulation import Simulation

class Apex:
    def __init__(self):
        self.config = Config()

    def createAndRunSimulation(self):
        simulation = Simulation(self.config)
        return simulation.run()

    def run(self):
        while self.createAndRunSimulation() == "restart":
            if self.config.reinitializeConfigUponRestart:
                self.config = Config()

apex = Apex()
apex.run()