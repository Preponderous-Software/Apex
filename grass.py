import random
from entity import Entity


# @author Daniel McCoy Stephenson
# @since July 7th, 2022
class Grass(Entity):
    def __init__(self):
        Entity.__init__(self, "Grass", random.randrange(10, 20), False, [])
        self.color = ((0, random.randrange(130, 170), 0))
    
    # Returns the color of the entity.
    def getColor(self):
        return self.color