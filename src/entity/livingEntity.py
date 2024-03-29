from entity.drawableEntity import DrawableEntity


# @author Daniel McCoy Stephenson
# @since August 5th, 2022
class LivingEntity(DrawableEntity):
    def __init__(self, name, color, energy, edibleEntityTypes):
        DrawableEntity.__init__(self, name, color)
        self.energy = energy
        self.edibleEntityTypes = edibleEntityTypes
        self.targetEnergy = energy
    
    def getEnergy(self):
        return self.energy

    def addEnergy(self, amount):
        self.energy += amount
    
    def removeEnergy(self, amount):
        self.energy -= amount

    def needsEnergy(self):
        return self.energy < self.targetEnergy

    def canEat(self, entity):
        for entityType in self.edibleEntityTypes:
            if type(entity) is entityType:
                return True
        return False