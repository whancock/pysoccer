'''
(c) 2015 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see the LICENSE.txt file included with this software for more information

authors: Arindam Bose (arindam.1993@gmail.com), Tucker Balch (trbalch@gmail.com)
'''

import numpy as np
from numpy import *
from numpy.linalg import *
from LinearAlegebraUtils import rotMatrixFromYPR, getYPRFromVector, normalize,clampRotation,\
    distBetween
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from Ball import Ball
from Obstacle import Obstacle
from SimTime import SimTime
from NavUtils import snapVector

class Agent(object):
    '''
    An Agent class which encapsulates the begaviour of the agent.
    classdocs
    '''


    def __init__(self, team, position, rotation, brain, colRadius, drawRadius, agent_id=None):
        self.position = position.astype(float)        #numpy array [x, y ,z]
        self.startpos = np.copy(self.position)
        self.rotation = rotation.astype(float)        #numpy array [yaw, pitch, roll] (in degrees)
        self.startrot = np.copy(self.rotation)
        self.colRadius = colRadius      #float size of collision sphere
        self.drawRadius = drawRadius    #float size of sphere to be drawn
        self.team = team                #provide team 'A' or team 'B'
        self.forward = dot(array([1, 0, 0]), rotMatrixFromYPR(rotation))    #unit vector in forward direction of agent
        self.right = dot(array([0, 1, 0]), rotMatrixFromYPR(rotation))      #unit vector in right direction of agent
        self.up = cross(self.forward, self.right)       #unit vector pointing upwards
        self.maxMove = double(0.6666)             #max distance the agent can move in each frame
        self.maxRot = array([5, 5, 5])           #max YPR in degrees the agent can rotate in each frame
        self.brain = brain
        self.uid = id(self)            #unique identifier
        self.isStunned = False
        self.lastStunned = float(-1)          #Last time agent was stunned
        self.stunDuration = float(-1)         #Duration for which I am stunned
        self.stunRange = 15
        self.agentId = agent_id

 
    def resetPosition(self):
        self.position = np.copy(self.startpos)
        self.rotation = np.copy(self.startrot)


    '''
    Plots a sphere of radius 10 with a left hand co-ordinate frame on the provided subplot.
    '''       
    def draw(self, subplot): 
        
        ##plots the sphere           
        u = np.linspace(0, 2 * np.pi, 25)
        v = np.linspace(0, np.pi, 25)

        x = self.drawRadius * np.outer(np.cos(u), np.sin(v)) + self.position[0]
        y = self.drawRadius * np.outer(np.sin(u), np.sin(v)) + self.position[1]
        z = self.drawRadius * np.outer(np.ones(np.size(u)), np.cos(v)) + self.position[2]
        if not self.isStunned:
            sphereColor = self.team.color
        else:
            sphereColor = 'r'
        subplot.plot_surface(x, y, z,  rstride=4, cstride=4, linewidth = 0, color=sphereColor)
        
        #plots the left handed co-ordinate Frame
        
        #plots the forward a red line
        fw = self.position + self.forward * (self.drawRadius + 10)
        x_fw = array([self.position[0], fw[0]])
        y_fw = array([self.position[1], fw[1]])
        z_fw = array([self.position[2], fw[2]])
        subplot.plot(x_fw, y_fw, z_fw, color='r')
        
        #plots the right as a blue line
        ri = self.position + self.right * (self.drawRadius + 10)
        x_ri = array([self.position[0], ri[0]])
        y_ri = array([self.position[1], ri[1]])
        z_ri = array([self.position[2], ri[2]])
        subplot.plot(x_ri, y_ri, z_ri, color='b')
        
        #plots up as a green Line
        up = self.position + self.up * (self.drawRadius + 10)
        x_up = array([self.position[0], up[0]])
        y_up = array([self.position[1], up[1]])
        z_up = array([self.position[2], up[2]])
        subplot.plot(x_up, y_up, z_up, color='g')
        
    '''
    Returns egocentric position of other object with respect to self
    '''
    def getEgoCentricOf(self, otherObject):
        otherPosition = otherObject.position;
        rotMat = rotMatrixFromYPR(self.rotation)
        rotMatInverse = inv(rotMat)
        posVector = otherPosition - self.position
        egoCentric = dot(posVector, rotMatInverse)
        return egoCentric
    
    '''
    Moves the agent, given information about the world, places restrictions on motion, called by the simulator.
    Logic is placed in Brain.takeStep() method.
    '''  
    def moveAgent(self, world):
        myTeam, enemyTeam, balls, obstacles = self.buildEgoCentricRepresentationOfWorld(world)

        if 90. < abs(self.rotation[0]) < 270.:
            agentFacing = -1
        else:
            agentFacing = 1

        facingGoal = agentFacing == np.sign(self.team.goal)

        deltaPos, deltaRot, actions = self.brain.takeStep(self, facingGoal, myTeam, enemyTeam, balls, obstacles)
        #handle movements
        if not self.isStunned:
            self.rotateAgent(deltaRot)
            self.translateAgent(deltaPos)
            
        #handle actions
        if not self.isStunned:
            for action in actions:
                #handle stun action
                if action.__class__.__name__ == 'Stun':
                    for agent in world.agents:
                        if agent.getUID() == action.agentUID:
                            if distBetween(self.position, agent.position) < self.stunRange:
                                agent.stun(action.duration)
                #handle kick action
                if action.__class__.__name__ == 'Kick':
                    for ball in world.balls:
                        if ball.getUID() == action.ballUID:
                            if distBetween(self.position, ball.position) < 20:
                                globalDirection = dot(action.direction, rotMatrixFromYPR(self.rotation))
                                ball.kick(globalDirection, action.intensity)
        #Unstun Self
        if self.isStunned:
            if not (self.lastStunned == -1 and self.stunDuration == -1):
                if SimTime.time - self.lastStunned > float(self.stunDuration):
                    self.isStunned = False
                    self.lastStunned = -1
                    self.stunDuration = -1

    '''
    Get Egocentric representation of the world
    '''
    
    def buildEgoCentricRepresentationOfWorld(self, world):
        myTeam = []
        enemyTeam = []
        balls = []
        obstacles =[]
        for agent in world.agents:
            if agent != self:
                agentToAppend = Agent(agent.team, self.getEgoCentricOf(agent), agent.rotation - self.rotation, agent.brain, agent.colRadius, agent.drawRadius)
                agentToAppend.setUID(agent.getUID())
                if agent.team == self.team:
                    myTeam.append(agentToAppend)
                else:
                    enemyTeam.append(agentToAppend)
        for ball in world.balls:
            ballToAppend = Ball(self.getEgoCentricOf(ball))
            ballToAppend.setUID(ball.getUID())
            balls.append(ballToAppend)
        for obstacle in world.obstacles:
            obstacleToAppend = Obstacle(self.getEgoCentricOf(obstacle), obstacle.radius)
            obstacles.append(obstacleToAppend)
        return myTeam, enemyTeam, balls, obstacles
    
    '''
    Rotate Agent by rotation specified as YPR
    '''
    def rotateAgent(self, rotation):
        #clamping
        if not self.isStunned:
            rotation = clampRotation(rotation, self.maxRot)
            self.rotation += rotation
            self.forward = normalize(dot(array([1, 0, 0]), rotMatrixFromYPR(self.rotation)))    
            self.right = normalize(dot(array([0, 1, 0]), rotMatrixFromYPR(self.rotation)))      
            self.up = normalize(cross(self.forward, self.right))
        
    def translateAgent(self, direction):
        #clamp the direction by normalizing
        if not self.isStunned:
            globaldirection = dot(direction, rotMatrixFromYPR(self.rotation))
            globaldirection = normalize(globaldirection) * self.maxMove
            self.position =self.position + globaldirection
            
    '''
    Stun self for duration
    '''
    def stun(self, duration):
        self.isStunned = True
        self.lastStunned = SimTime.time
        self.stunDuration = duration
        
    def setUID(self, uid):
        self.uid = uid
    
    def getUID(self):
        return self.uid

    