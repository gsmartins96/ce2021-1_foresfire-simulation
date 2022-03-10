from mesa import Model
from mesa import Agent
from mesa.datacollection import DataCollector
from mesa.space import Grid
from mesa.time import RandomActivation
from random import randrange
from decimal import Decimal
from mesa.batchrunner import BatchRunner
from datetime import datetime

class TreeCell(Agent):
    """
    A tree cell.

    Attributes:
        x, y: Grid coordinates
        condition: Can be "Fine", "On Fire", or "Burned Out"
        unique_id: (x,y) tuple.

    unique_id isn't strictly necessary here, but it's good
    practice to give one to each agent anyway.
    """

    def __init__(self, pos, model, firemans):
        """
        Create a new tree.
        Args:
            pos: The tree's coordinates on the grid.
            model: standard model reference for agent.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.condition = "Fine"
        self.firemans = firemans

    def step(self):
        """
        If the tree is on fire, spread it to fine trees nearby.
        """
        fire = randrange(20,100)
        if self.condition == "On Fire" and Decimal(self.firemans * 100) <= fire:
            for neighbor in self.model.grid.neighbor_iter(self.pos):
                new_fire = randrange(0,100)
                if neighbor.condition == "Fine" and Decimal(neighbor.firemans * 100) <= fire:
                    neighbor.condition = "On Fire"
            self.condition = "Burned Out"
        elif self.condition != "Burned Out":
            self.condition = "Fine"

class ForestFire(Model):
    """
    Simple Forest Fire model.
    """

    def __init__(self, width=100, height=100, density=0.65, firemans=0.20):
        """
        Create a new forest fire model.

        Args:
            width, height: The size of the grid to model
            density: What fraction of grid cells have a tree in them.
        """
        # Set up model objects
        self.schedule = RandomActivation(self)
        self.grid = Grid(width, height, torus=False)
        if firemans <= 0.04:
            self.firemans_fire = 0.30
        elif firemans >= 0.05 and firemans < 0.15: 
            self.firemans_fire = 0.45
        elif firemans >= 0.15 and firemans <= 0.24:
            self.firemans_fire = 0.60
        else:
            self.firemans_fire = 0.75

        self.datacollector = DataCollector(
            {
                "Fine": lambda m: self.count_type(m, "Fine"),
                "On Fire": lambda m: self.count_type(m, "On Fire"),
                "Burned Out": lambda m: self.count_type(m, "Burned Out")
            }
        )

        # Place a tree in each cell with Prob = density
        for (contents, x, y) in self.grid.coord_iter():
            if self.random.random() < density:
                # Create a tree
                new_tree = TreeCell((x, y), self, self.firemans_fire)
                # Set all trees in the first column on fire.
                if x == 0:
                    new_tree.condition = "On Fire"
                self.grid._place_agent((x, y), new_tree)
                self.schedule.add(new_tree)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        # Halt if no more fire
        if self.count_type(self, "On Fire") == 0:
            self.running = False

    @staticmethod
    def count_type(model, tree_condition):
        """
        Helper method to count trees in a given condition in a given model.
        """
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == tree_condition:
                count += 1
        return count

def firemans(model):
    return model.firemans_fire

def fine(model):
    count = 0
    for tree in model.schedule.agents:
            if tree.condition == "Fine":
                count += 1
    return count

def onfire(model):
    count = 0
    for tree in model.schedule.agents:
            if tree.condition == "On Fire":
                count += 1
    return count

def condition(model):
    return model.condition

def batch_run():
    fix_params = {
        "width": 100, 
        "height": 100,
    }
    variable_params = {
        "density" : [0.5,0.7,0.9],
        "firemans": [0.04, 0.15, 0.24, 0.29]    
    }

    experiments_per_parameter_configuration = 10
    max_steps_per_simulation = 100
    batch_run = BatchRunner(
        ForestFire,
        variable_params,
        fix_params,   
        iterations = experiments_per_parameter_configuration,
        max_steps = max_steps_per_simulation,
        model_reporters = {        
            "firemans": firemans,
            "fine": fine,
            "onfire": onfire
        },
        agent_reporters = {
            "condition": "condition",
        }
    ) 

    batch_run.run_all()

    run_model_data = batch_run.get_model_vars_dataframe()
    run_agent_data = batch_run.get_agent_vars_dataframe() 

    now = datetime.now().strftime("%Y-%m-%d")
    file_name_suffix =  ("_iter_"+str(experiments_per_parameter_configuration)+
                        "_steps_"+str(max_steps_per_simulation)+"lower_firemans"+now
                        )
    run_model_data.to_csv("model_data"+file_name_suffix+".csv")
    run_agent_data.to_csv("agent_data"+file_name_suffix+".csv")