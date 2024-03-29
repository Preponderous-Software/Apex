import time
import pygame
from lib.graphiklib.graphik import Graphik
from simulation.config import Config
from simulation.simulation import Simulation

from entity.chicken import Chicken
from entity.cow import Cow
from entity.fox import Fox
from entity.grass import Grass
from entity.pig import Pig
from entity.rabbit import Rabbit

from entity.wolf import Wolf


# @author Daniel McCoy Stephenson
# @since July 31st, 2022
class Apex:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.initializeGameDisplay()
        pygame.display.set_icon(pygame.image.load('src/media/icon/icon.PNG'))
        self.graphik = Graphik(self.gameDisplay)
        self.debug = False
        self.paused = False
        self.simCount = 0
        self.initializeSimulation()
        self.tickLengths = []
    
    def initializeGameDisplay(self):
        if self.config.fullscreen:
            self.gameDisplay = pygame.display.set_mode((self.config.displayWidth, self.config.displayHeight), pygame.FULLSCREEN)
        else:
            self.gameDisplay = pygame.display.set_mode((self.config.displayWidth, self.config.displayHeight), pygame.RESIZABLE)
    
    # Creates and initializes a new simulation. Only one simulation can exist at a time.
    def initializeSimulation(self):
        name = "Simulation " + str(self.simCount)
        self.simulation = Simulation(name, self.config, self.gameDisplay)
        self.simulation.initializeEntities()
        self.simulation.placeEntities()
        self.simulation.environment.printInfo()
        self.simCount += 1
        self.initializeCaption()
    
    def initializeCaption(self):
        caption = "Apex - " + self.simulation.name + " - " + str(self.simulation.environment.getGrid().getColumns()) + "x" + str(self.simulation.environment.getGrid().getRows())
        if self.config.muted:
            caption += " (muted)"
        pygame.display.set_caption(caption)

    # Draws the environment that belongs to the simulation in its entirety.
    def drawEnvironment(self):
        for location in self.simulation.environment.getGrid().getLocations():
            self.drawLocation(location, location.getX() * self.simulation.locationWidth, location.getY() * self.simulation.locationHeight, self.simulation.locationWidth, self.simulation.locationHeight)

    # Returns the color that a location should be displayed as.
    def getColorOfLocation(self, location):
        if location == -1:
            color = self.config.black
        else:
            color = self.config.brown
            if location.getNumEntities() > 0:
                topEntity = location.getEntities()[-1]
                oldestLivingEntity = self.simulation.livingEntities[0]
                if self.config.highlightOldestEntity and topEntity.getID() == oldestLivingEntity.getID():
                    color = self.config.highlightColor
                else:
                    color = topEntity.getColor()
        return color

    # Draws a location at a specified position.
    def drawLocation(self, location, xPos, yPos, width, height):
        color = self.getColorOfLocation(location)
        self.graphik.drawRectangle(xPos, yPos, width, height, color)
    
    # Draws locations to the left of a given location.
    def drawLocationsToTheLeftOfLocation(self, location, grid, xpos, ypos, width, height):
        tempLoc = location
        while tempLoc != -1:
            xpos = xpos - width
            ypos = ypos
            self.drawLocation(grid.getLeft(tempLoc), xpos, ypos, width, height)
            tempLoc = grid.getLeft(tempLoc)
    
    # Draws locations to the right of a given location.
    def drawLocationsToTheRightOfLocation(self, location, grid, xpos, ypos, width, height):
        tempLoc = location
        while tempLoc != -1:
            xpos = xpos + width
            ypos = ypos
            self.drawLocation(grid.getRight(tempLoc), xpos, ypos, width, height)
            tempLoc = grid.getRight(tempLoc)
    
    # Draws a row of locations starting at a given location.
    def drawRow(self, location, grid, xpos, ypos, width, height):
        self.drawLocation(location, xpos, ypos, width, height)
        xBackup = xpos
        self.drawLocationsToTheLeftOfLocation(location, grid, xpos, ypos, width, height)
        xpos = xBackup
        self.drawLocationsToTheRightOfLocation(location, grid, xpos, ypos, width, height)
    
    # Draws rows of locations starting above a given location.
    def drawRowsAboveLocation(self, location, grid, xpos, ypos, width, height):
        nextLocation = grid.getUp(location)
        while nextLocation != -1:
            ypos = ypos - height
            self.drawRow(nextLocation, grid, xpos, ypos, width, height)
            nextLocation = grid.getUp(nextLocation)

    # Draws rows of locations starting below a given location.
    def drawRowsBelowLocation(self, location, grid, xpos, ypos, width, height):
        nextLocation = grid.getDown(location)
        while nextLocation != -1:
            ypos = ypos + height
            self.drawRow(nextLocation, grid, xpos, ypos, width, height)
            nextLocation = grid.getDown(nextLocation)

    # Draws the immediate area around an entity.
    def drawAreaAroundEntity(self, entity):
        locationID = entity.getLocationID()
        grid = self.simulation.environment.getGrid()
        location = grid.getLocation(locationID)
        x, y = self.gameDisplay.get_size()
        width = x/(self.config.localViewSize*2 + 1)
        height = y/(self.config.localViewSize*2 + 1)
        xpos = width*self.config.localViewSize
        ypos = height*self.config.localViewSize
        yBackup = ypos
        self.drawRow(location, grid, xpos, ypos, width, height)
        self.drawRowsAboveLocation(location, grid, xpos, ypos, width, height)
        ypos = yBackup
        self.drawRowsBelowLocation(location, grid, xpos, ypos, width, height)

    def addStatToText(self, text, key, value):
        text.append(key)
        text.append(value)
        text.append("")

    # Draws some statistics to the screen, which are updated each tick. This can be laggy.
    def displayStats(self):
        startingX = 100
        startingY = 10
        text = []
        if self.config.limitTickSpeed:
            self.addStatToText(text, "Tick Speed:", str(self.config.tickSpeed))
        self.addStatToText(text, "Num Ticks:", str(self.simulation.numTicks))
        self.addStatToText(text, "Entities:", str(len(self.simulation.entities)))
        self.addStatToText(text, "Living Entities:", str(self.simulation.getNumLivingEntities()))
        self.addStatToText(text, "Grass:", str(self.simulation.getNumberOfEntitiesOfType(Grass)))
        self.addStatToText(text, "Excrement:", str(self.simulation.getNumExcrement()))
        self.addStatToText(text, "Chickens:", str(self.simulation.getNumberOfLivingEntitiesOfType(Chicken)))
        self.addStatToText(text, "Pigs:", str(self.simulation.getNumberOfLivingEntitiesOfType(Pig)))
        self.addStatToText(text, "Cows:", str(self.simulation.getNumberOfLivingEntitiesOfType(Cow)))
        self.addStatToText(text, "Wolves:", str(self.simulation.getNumberOfLivingEntitiesOfType(Wolf)))
        self.addStatToText(text, "Foxes:", str(self.simulation.getNumberOfLivingEntitiesOfType(Fox)))
        self.addStatToText(text, "Rabbits:", str(self.simulation.getNumberOfLivingEntitiesOfType(Rabbit)))

        buffer = self.config.textSize

        for i in range(0, len(text)):
            self.graphik.drawText(text[i], startingX, startingY + buffer*i, self.config.textSize, self.config.black)

    # Defines the controls of the application.
    def handleKeyDownEvent(self, key):
        if key == pygame.K_d:
            if self.debug == True:
                self.debug = False
            else:
                self.debug = True
        if key == pygame.K_q:
            self.simulation.cleanup()
            self.simulation.running = False
        if key == pygame.K_r:
            self.simulation.cleanup()
            return "restart"
        if key == pygame.K_c:
            chicken = Chicken("player-created-chicken")
            self.simulation.environment.addEntity(chicken)
            self.simulation.addEntity(chicken)
        if key == pygame.K_p:
            pig = Pig("player-created-pig")
            self.simulation.environment.addEntity(pig)
            self.simulation.addEntity(pig)
        if key == pygame.K_k:
            cow = Cow("player-created-cow")
            self.simulation.environment.addEntity(cow)
            self.simulation.addEntity(cow)
        if key == pygame.K_w:
            wolf = Wolf("player-created-wolf")
            self.simulation.environment.addEntity(wolf)
            self.simulation.addEntity(wolf)
        if key == pygame.K_f:
            fox = Fox("player-created-fox")
            self.simulation.environment.addEntity(fox)
            self.simulation.addEntity(fox)
        if key == pygame.K_b:
            rabbit = Rabbit("player-created-rabbit")
            self.simulation.environment.addEntity(rabbit)
            self.simulation.addEntity(rabbit)
        if key == pygame.K_RIGHTBRACKET:
            if self.config.tickSpeed < self.config.maxTickSpeed:
                self.config.tickSpeed += 1
        if key == pygame.K_LEFTBRACKET:
            if self.config.tickSpeed > 1:
                self.config.tickSpeed -= 1
        if key == pygame.K_l:
            if self.config.limitTickSpeed:
                self.config.limitTickSpeed = False
            else:
                self.config.limitTickSpeed = True
        if key == pygame.K_SPACE or key == pygame.K_ESCAPE:
            if self.paused:
                self.paused = False
            else:
                self.paused = True
        if key == pygame.K_v:
            if self.config.localView:
                self.config.localView = False
            else:
                self.config.localView = True
        if key == pygame.K_h:
            if self.config.highlightOldestEntity:
                self.config.highlightOldestEntity = False
            else:
                self.config.highlightOldestEntity = True
        if key == pygame.K_UP:
            if self.config.localViewSize < self.config.maxLocalViewSize:
                self.config.localViewSize += 1
        if key == pygame.K_DOWN:
            if self.config.localViewSize > 1:
                self.config.localViewSize -= 1
        if key == pygame.K_F11:
            if self.config.fullscreen:
                self.config.fullscreen = False
            else:
                self.config.fullscreen = True
            self.initializeGameDisplay()
        if key == pygame.K_m:
            if self.config.muted:
                self.config.muted = False
            else:
                self.config.muted = True
            self.initializeCaption()

    # Prints some stuff to the screen and restarts the simulation. Utilizes initializeSimulation()
    def restartSimulation(self):
        self.simulation.cleanup()
        self.tickLengths.append(self.simulation.numTicks)
        if self.config.randomizeGridSizeUponRestart:
            self.config.randomizeGridSize()
            self.config.randomizeGrassGrowTime()
            self.config.calculateValues()
        self.initializeSimulation()
        if self.paused:
            self.paused = False

    # Gets the average tick length for the current simulation.
    def getAverageTickLength(self):
        if len(self.tickLengths) == 0:
            return 0
        sum = 0
        for tickLength in self.tickLengths:
            sum += tickLength
        return sum/len(self.tickLengths)

    # Shuts down the application.
    def quitApplication(self):
        self.simulation.cleanup()
        self.tickLengths.append(self.simulation.numTicks)
        print("average simulation length:", self.getAverageTickLength(), "ticks")
        pygame.quit()
        quit()

    # Invokes the simulation screen loop.
    def simulationScreen(self):
        while self.simulation.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitApplication()
                elif event.type == pygame.KEYDOWN:
                    result = self.handleKeyDownEvent(event.key)
                    if result == "restart":
                        self.restartSimulation()
                elif event.type == pygame.VIDEORESIZE:
                    self.simulation.initializeLocationWidthAndHeight()
            
            if not self.paused:
                self.simulation.update()
                self.gameDisplay.fill(self.config.black)
                if self.simulation.getNumLivingEntities() != 0:
                    if self.config.localView:
                        self.drawAreaAroundEntity(self.simulation.livingEntities[0])
                    else:
                        self.drawEnvironment()

                    if self.debug:
                        self.displayStats()

            pygame.display.update()
            if (self.config.limitTickSpeed):
                time.sleep((self.config.maxTickSpeed - self.config.tickSpeed)/self.config.maxTickSpeed)
            
            if not self.paused:
                self.simulation.numTicks += 1
            
            if self.paused:
                x, y = self.gameDisplay.get_size()
                self.graphik.drawText("PAUSED", x/2, y/2, 50, self.config.black)

            if (self.config.endSimulationUponAllLivingEntitiesDying):
                if self.simulation.getNumLivingEntities() == 0:
                    self.running = False
                    time.sleep(1)
                    if (self.config.autoRestart):
                        self.restartSimulation()
                        
        self.quitApplication()

    # Runs the application.
    def run(self):
        self.simulationScreen()

apex = Apex()
apex.run()