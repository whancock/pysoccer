'''
(c) 2015 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see the LICENSE.txt file included with this software for more information

authors: Arindam Bose (arindam.1993@gmail.com), Tucker Balch (trbalch@gmail.com)
'''


import numpy as np
from numpy.linalg.linalg import norm
from LinearAlegebraUtils import normalize, reflectVector, distBetween
from numpy import array
from SimTime import SimTime
from numpy import *

from random import seed, randint

import config


class Ball(object):
    '''
    classdocs
    '''


    def __init__(self, position):
        '''
        Constructor
        '''
        self.position = position.astype(double)
        self.startpos = position.astype(double)
        self.radius = 5
        self.uid = id(self)
        self.isDynamic = False
        self.velocity = array([0, 0, 0])

        self.kicked = False
        self.resetCounter = 0
        self.previousPos = array([0, 0, 0])

    def resetPosition(self):


        self.position = np.copy(self.startpos)
        yStart = randint(-50, 50)
        zStart = randint(-20, 20)

        self.velocity = array([0, 0, 0])
        self.position = array([0, yStart, zStart])
        
        self.previousPos = array([0, yStart, 0])
        self.kicked = False
        self.resetCounter = 0


    def getFuzzyPosition(self, range=10):
        return np.array([randint(int(num) - range, int(num) + range) for num in self.position])


        
    def draw(self,subplot):
        #draw a sphere of specified size at specified position
        u = np.linspace(0, 2 * np.pi, 25)
        v = np.linspace(0, np.pi, 25)

        x = self.radius * np.outer(np.cos(u), np.sin(v)) + self.position[0]
        y = self.radius * np.outer(np.sin(u), np.sin(v)) + self.position[1]
        z = self.radius * np.outer(np.ones(np.size(u)), np.cos(v)) + self.position[2]
        subplot.plot_surface(x, y, z,  rstride=4, cstride=4, linewidth = 0, color='w')
        
    def moveBall(self, position, speed):
        #move the ball to specified position at the specified speed, speed is distance per frame  
        if not self.isDynamic:
            moveVector = position - self.position
            moveVector = normalize(moveVector)
            self.position += moveVector * float(speed)
            
    def updatePhysics(self, world):
        if self.isDynamic:

            #move with velocity
            self.position += self.velocity * SimTime.fixedDeltaTime
#             print "Ballin to"+str(self.velocity * SimTime.fixedDeltaTime)
            self.velocity *= 0.99  

            if self.kicked:
                if np.array_equal(self.position, self.previousPos):
                    self.resetCounter += 1

            if self.resetCounter >= 5:
                self.resetPosition()

            #Handle collisions with world bounds
            if self.position[2] < -world.height:
                self.position[2] = -world.height + 0.1
                self.velocity = reflectVector(self.velocity, array([0, 0, 1]))
            if self.position[2] > world.height:
                self.position[2] = world.height - 0.1
                self.velocity = reflectVector(self.velocity, array([0, 0, -1]))
            if self.position[1] < -world.width:
                self.position[1] = -world.width + 0.1
                self.velocity = reflectVector(self.velocity, array([0, 1, 0]))
            if self.position[1] > world.width:
                self.position[1] = world.width - 0.1
                self.velocity = reflectVector(self.velocity, array([0, -1, 0]))
            if self.position[0] < -world.width:
                self.position[0] = -world.width + 0.1
                self.velocity = reflectVector(self.velocity, array([1, 0, 0]))
            if self.position[0] > world.width:
                self.position[0] = world.width - 0.1
                self.velocity = reflectVector(self.velocity, array([-1, 0, 0]))
            
            #collision of obstacles
            for obstacle in world.obstacles:
                nextPos = self.position + self.velocity
                if distBetween(nextPos, obstacle.position) < self.radius + obstacle.radius:
                    normal = normalize(nextPos - obstacle.position)
                    self.velocity = reflectVector(self.velocity, normal)
                    
            
            #stop when ball hits agents
            for agent in world.agents:
                nextPos = self.position + self.velocity
                if distBetween(nextPos, agent.position) < self.radius + agent.colRadius:
                    self.velocity = array([0, 0, 0])
                    
            #clamp ball speed
            mag = np.linalg.norm(self.velocity)
            if mag > 200:
                self.velocity = normalize(self.velocity) * 200
                
            
            
    def kick(self, direction, intensity):

        self.kicked = True

        directionNorm = normalize(direction)
        if self.isDynamic:
            self.velocity = directionNorm * intensity
        
    def getUID(self):
        return self.uid
    
    def setUID(self, uid):
        self.uid = uid
        
    
    