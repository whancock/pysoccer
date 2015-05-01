'''
(c) 2015 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see the LICENSE.txt file included with this software for more information

authors: Arindam Bose (arindam.1993@gmail.com), Tucker Balch (trbalch@gmail.com)
'''


import numpy as np
import matplotlib.pyplot as plt
from numpy import *
from World import *
from Agent import Agent
from Obstacle import *
from pylab import *
from Ball import Ball
from LinearAlegebraUtils import distBetween
from RunAtBallBrain import RunAtBallBrain
from Team import Team
from SimTime import SimTime

from SoccerBrain import SoccerBrain
from BetterBrain import BetterBrain

from random import seed, randint, shuffle
import config



#Called once for initialization
'''
Usage guidelines:
1. Define globals required for the simulation in the __init__ constructor, here we define a bunch of waypoints for the ball
2. Initialize the globals in the setup() method. 
'''

class Simulator(object):
    def __init__(self, world, simTime, fps, imageDirName):
        self.world = world
        self.simTime = simTime
        self.fps = fps
        self.imageDirName = imageDirName

        self.ascore = 0
        self.bscore = 0

        self.loopcount = 0
      
    def setup(self):    
        #setup directory to save the images
        try:
            os.mkdir(self.imageDirName)
        except:
            print self.imageDirName + " subdirectory already exists. OK."

  
         #define teams which the agents can be a part of
        teamA = Team("A", '#ff99ff', 1)
        teamB = Team("B", '#ffcc99', -1)
        

        yPos = [75, 25, -25, -75]

        for idx in range(4):

            agentPos = array([-60, yPos[idx], 0])
            agentRot = array([0, 0, 0])

            agentBrain = SoccerBrain()
            agent = Agent(teamA, agentPos, agentRot, agentBrain, 5, 5, idx)

            self.world.agents.append(agent)



        for idx in range(4):

            agentPos = array([60, yPos[idx], 0])
            agentRot = array([-180, 0, 0])

            agentBrain = BetterBrain()
            agent = Agent(teamB, agentPos, agentRot, agentBrain, 5, 5, idx)

            self.world.agents.append(agent)



        
        #define a ball

        ball = Ball(np.array([0,0,0]))
        ball.isDynamic = True
        ball.resetPosition()
        
        #add the ball to the world
        self.world.balls.append(ball)
        
#called at a fixed 30fps always
    def fixedLoop(self):

        shuffle(self.world.agents)
        for agent in self.world.agents:
            agent.moveAgent(self.world)


        for ball in self.world.balls:
            ball.updatePhysics(self.world)

        scored = False
        ball = self.world.balls[0]

        if ball.position[0] <= -90:
            #team b scored
            print 'team b scored'
            print self.ascore, self.bscore
            self.bscore += 1
            scored = True
            self.loopcount = 0


        elif ball.position[0] >= 90:
            print 'team a scored'
            print self.ascore, self.bscore
            self.ascore += 1
            scored = True
            self.loopcount = 0

        if scored:
            for agent in self.world.agents:
                agent.resetPosition()

            ball.resetPosition()
        else:
            self.loopcount += 1

        if self.loopcount >= 2000:
            print 'reset'
            for agent in self.world.agents:
                agent.resetPosition()
            self.world.balls[0].resetPosition()
            self.loopcount = 0


    
#Called at specifed fps
    def loop(self, ax):       
        self.world.draw(ax)
       
                
    def run(self):
        #Run setup once
        self.setup()
        
        #Setup loop
        timeStep = 1/double(30)
        frameProb = double(self.fps) / 30
        currTime = double(0)
        SimTime.fixedDeltaTime = timeStep
        SimTime.deltaTime = double(1/ self.fps)
        drawIndex = 0
        physicsIndex = 0
        while(currTime < self.simTime):
            self.fixedLoop()
            SimTime.time = currTime
            currProb = double(drawIndex)/double(physicsIndex+1)
            if currProb < frameProb:
                self.drawFrame(drawIndex)  
                drawIndex+=1
            physicsIndex+=1
            currTime+=double(timeStep)
     
        # print "Physics ran for "+str(physicsIndex)+" steps"
        # print "Drawing ran for "+str(drawIndex)+" steps"
            
    def drawFrame(self, loopIndex):
        fig = plt.figure(figsize=(16,12))
        ax = fig.add_subplot(111, projection='3d') 
        ax.view_init(elev = 30)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")    
        fname = self.imageDirName + '/' + str(int(100000000+loopIndex)) + '.png' # name the file 
        # fname = self.imageDirName + '/moo.png' # name the file 
        self.loop(ax)
        plt.gca().set_ylim(ax.get_ylim()[::-1])
        savefig(fname, format='png', bbox_inches='tight')
        print 'Written Frame No.'+ str(loopIndex)+' to '+ fname
        plt.close()


#Simulation runs here
#set the size of the world
world = World(config.field_length, config.field_width, config.field_height)
#specify which world to simulate, total simulation time, and frammerate for video
sim = Simulator(world, 2000, 30, "images")
#run the simulation
sim.run()

'''
To create a video using the image sequence, execute the following command in command line.
>ffmpeg -framerate 30 -i "1%08d.png" -r 30 outPut.mp4
                    ^                    ^
                Framerate mtached with simulator
Make sure to set your current working directory to /images and have ffmpeg in your path.
'''

    