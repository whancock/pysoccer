from Agent import Agent
from Ball import Ball
from Obstacle import Obstacle
from LinearAlegebraUtils import getYPRFromVector
import numpy as np
from Action import Stun, Kick

class SoccerBrain(object):


	def __init__(self):      
		pass

	def takeStep(self, agent, facingGoal, myTeam=[], enemyTeam=[], balls=[], obstacles=[]):

		actions = []
		deltaPos = np.array([1, 0, 0])
		deltaRot = getYPRFromVector(balls[0].position)

		for ball in balls:

			if facingGoal: #we are facing the goal
				if ball.position[0] >= 0: #we are facing the ball
					actions.append(Kick(ball, np.array([1, 0, 0]), 100))

		return deltaPos, deltaRot, actions