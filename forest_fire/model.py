from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import Grid
from mesa.time import RandomActivation
from mesa.batchrunner import BatchRunner
from collections import deque
from datetime import datetime
from os import sep
import sys
from agent import TreeCell # remove . from .agent to run batch_run

class ForestFire(Model):
    """
    Simple Forest Fire model.
    """

    def __init__(self, forest_size=100, tree_density=0.70, airfighter_density=0.3, firemans=0.20):
        sys.setrecursionlimit(3900)
        self.gridsize = forest_size
        """
        Create a new forest fire model.
        Args:
            width, height: The size of the grid to model
            density: What fraction of grid cells have a tree in them.
        """
        # Set up model objects
        self.schedule = RandomActivation(self)
        self.grid = Grid(forest_size, forest_size, torus=False)

        self.tree_density = tree_density
        self.airfighter_density = airfighter_density
        self.firemans_density =  0.0025 * firemans
        if firemans <= 0.04:
            self.firemans_density = 0.30
        elif firemans >= 0.05 and firemans < 0.15: 
            self.firemans_density = 0.45
        elif firemans >= 0.15 and firemans <= 0.24:
            self.firemans_density = 0.60
        else:
            self.firemans_density = 0.75

        self.datacollector = DataCollector(
            {
                "Fine": lambda m: self.count_type(m, "Fine") + self.count_type(m, "AirFighter"),
                "On Fire": lambda m: self.count_type(m, "On Fire"),
                "Burned Out": lambda m: self.count_type(m, "Burned Out"),
                "Safe Area": lambda m: self.count_type(m, "Safe Area"),
                "Clusters": lambda m: self.cluster_count,
            }
        )

        self.datacollector_model = DataCollector(
            {
                "Forest Density": lambda m: self.tree_density,
                "AirFighter Density": lambda m: airfighter_density,
                "Saved Area": lambda m: (self.count_type(m, "Safe Area") + self.count_type(m, "AirFighter")) / (self.count_type(m, "Fine") + self.count_type(m, "AirFighter") + self.count_type(m, "Safe Area") + self.count_type(m, "Burned Out")),
                "Burned Area": lambda m: self.count_type(m, "Burned Out") / (self.count_type(m, "Fine") + self.count_type(m, "AirFighter") + self.count_type(m, "Safe Area") + self.count_type(m, "Burned Out")),
                "Natural Area": lambda m: self.count_type(m, "Fine") / (self.count_type(m, "Fine") + self.count_type(m, "AirFighter") + self.count_type(m, "Safe Area") + self.count_type(m, "Burned Out")),
            }
        )

        self.alltrees = newMatrix(self.gridsize)
        self.cluster_count = 0

        self.firemans98 = []
        self.firemans94 = []
        self.firemans86 = []
        self.firemans70 = []
        self.firemans40 = []

        # Place a tree in each cell with Prob = density
        for (contents, x, y) in self.grid.coord_iter():
            if self.random.random() < self.firemans_density:
                # Create a AirFighter
                new_fman = TreeCell((x, y), self, self.firemans_density)
                new_fman.condition = "AirFighter"
                new_fman.firemans = 0.92
                self.grid._place_agent((x, y), new_fman)
                self.schedule.add(new_fman)
                self.alltrees[x][y] = new_fman

            elif self.random.random() < tree_density:
                # Create a tree
                new_tree = TreeCell((x, y), self, self.firemans_density)
                # Set all trees in the first column on fire.
                if x == 0:
                    new_tree.condition = "On Fire"
                elif self.firemans98.count((x,y)):
                    new_tree.firemans = 0.80
                elif self.firemans94.count((x,y)):
                    new_tree.firemans = 0.74
                elif self.firemans86.count((x,y)):
                    new_tree.firemans = 0.71
                elif self.firemans70.count((x,y)):
                    new_tree.firemans = 0.58
                elif self.firemans40.count((x,y)):
                    new_tree.firemans = 0.33

                self.grid._place_agent((x,y), new_tree)
                self.schedule.add(new_tree)
                self.alltrees[x][y] = new_tree
        
        self.agents_total = 0
        for tree in self.schedule.agents:
            self.agents_total += 1
        self.count_clusters()

        self.running = True
        self.datacollector.collect(self)


    def count_clusters(self):
        self.minitrees = newMatrix(self.gridsize)
        for x in range(0,self.gridsize):
            for y in range(0,self.gridsize):
                tree = self.alltrees[x][y]
                if (type(tree) == TreeCell) and ((tree.condition == "Fine") or (tree.condition == "Safe Area") or (tree.condition == "AirFighter")):
                    self.minitrees[x][y] = 1
        self.cluster_count = countIslands(self.minitrees)


    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()

        self.count_clusters()
        # collect data
        self.datacollector.collect(self)

        # Halt if no more fire
        if self.count_type(self, "On Fire") == 0:
            self.running = False
            
            self.datacollector_model.collect(self)
    
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

def newMatrix (size):
    line = []
    for i in range(0,size):
        line.append(0)
    lines = []
    for i in range(0,size):
        lines.append(line.copy())
    return lines

row = [-1, -1, -1, 0, 1, 0, 1, 1]
col = [-1, 1, 0, -1, -1, 1, 0, 1]
 
def isSafe(mat, x, y, processed):
    return (x >= 0 and x < len(processed)) and (y >= 0 and y < len(processed[0])) and \
           mat[x][y] == 1 and not processed[x][y]
 
def BFS(mat, processed, i, j):
 
    q = deque()
    q.append((i, j))
    processed[i][j] = True
 
    while q:
        x, y = q.popleft()
 
        for k in range(len(row)):
            if isSafe(mat, x + row[k], y + col[k], processed):
                processed[x + row[k]][y + col[k]] = True
                q.append((x + row[k], y + col[k]))
 
def countIslands(mat):
    if not mat or not len(mat):
        return 0
 
    (M, N) = (len(mat), len(mat[0]))
    processed = [[False for x in range(N)] for y in range(M)]
 
    island = 0
    for i in range(M):
        for j in range(N):
            if mat[i][j] == 1 and not processed[i][j]:
                BFS(mat, processed, i, j)
                island = island + 1
 
    return island

def allclusters(model):
    return model.cluster_count

def statefine(model):
    return model.count_type(model, "Fine")

def statesafe(model):
    return (model.count_type(model, "Safe Area") + model.count_type(model, "Air Protection"))

def stateburn(model):
    return (model.count_type(model, "On Fire") + model.count_type(model, "Burned Out"))

def batch_run():
    fix_params = {
        'forest_size': 100,
        'tree_density': 0.65
    }
    variable_params = {
        'airfighter_density': [0.0, 0.1, 0.2, 0.4, 0.6, 0.8],
        'firemans': [0.0, 0.1, 0.2, 0.4, 0.6, 0.8]
    }
    experiments_per_parameter_configuration = 10
    max_steps_per_simulation = 10
    batch_run = BatchRunner(
        ForestFire,
        variable_params,
        fix_params,
        iterations = experiments_per_parameter_configuration,
        max_steps = max_steps_per_simulation,
        model_reporters = {
            "Clusters": allclusters,
            "Natural Area": statefine,
            "Saved Area": statesafe,
            "Burned Area": stateburn
        },
        agent_reporters = {
            "Condition": 'condition'
        }
    )
    batch_run.run_all()

    run_model_data = batch_run.get_model_vars_dataframe()
    run_agent_data = batch_run.get_agent_vars_dataframe() 

    now = datetime.now().strftime("%Y-%m-%d")
    file_name_suffix =  ("_iter_"+str(experiments_per_parameter_configuration)+
                        "_steps_"+str(max_steps_per_simulation)+now
                        )
    run_model_data.to_csv("model_data"+file_name_suffix+".csv")
    run_agent_data.to_csv("agent_data"+file_name_suffix+".csv")
