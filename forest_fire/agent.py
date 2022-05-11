from mesa import Agent

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
        self.firemans = 0

    def step(self):
        """
        If the tree is on fire, spread it to fine trees nearby.
        """
        if self.condition == "On Fire":
            for neighbor in self.model.grid.neighbor_iter(self.pos):
                if (neighbor.condition == "AirFighter"):
                    neighbor.condition = "Safe Area"
                if (neighbor.condition == "Fine") or ((neighbor.condition == "Safe Area")):
                    if self.random.random() > neighbor.firemans:
                        neighbor.condition = "On Fire"
                    else:
                        neighbor.condition = "Safe Area"
            self.condition = "Burned Out"
