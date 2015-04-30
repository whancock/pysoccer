'''
(c) 2015 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see the LICENSE.txt file included with this software for more information

authors: Arindam Bose (arindam.1993@gmail.com), Tucker Balch (trbalch@gmail.com)
'''

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from pylab import *
import os

class World(object):
    
    def __init__(self, width, length, height):
        self.agents=[]
        self.obstacles=[]
        self.balls=[]
        self.width = width
        self.height = height
        self.length = length
        
    def draw(self, ax):
        
 
        ax.set_xlim3d(-self.width,self.width)
        ax.set_ylim3d(-self.length,self.length)
        ax.set_zlim3d(-self.height,self.height)
        for agent in self.agents:
            agent.draw(ax)
        for obstacle in self.obstacles:
            obstacle.draw(ax)
        for ball in self.balls:
            ball.draw(ax)
        return ax
        
        


        