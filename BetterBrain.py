from Agent import Agent
from Ball import Ball
from Obstacle import Obstacle
from LinearAlegebraUtils import getYPRFromVector
import numpy as np
from Action import Stun, Kick

from NavUtils import snapVector

class BetterBrain(object):


	def __init__(self):      
		pass

	def takeStep(self, agent, facingGoal, myTeam=[], enemyTeam=[], balls=[], obstacles=[]):


		ballPosition = balls[0].getFuzzyPosition(100)
		# ballPosition = balls[0].position
		# ballPosition = (np.random.rand(3) * 200) - 100

		# print ballPosition, balls[0].position


		actions = []
		deltaPos = np.array([1, 0, 0])
		deltaRot = getYPRFromVector(ballPosition)

		# degrade our knowledge to direction of ball, not location
		# deltaRot = snapVector(deltaRot)


		# if agent.agentId == 1:
		# 	# be the goalie
		# 	if abs(agent.position[0]) < 70:
		# 		# deltaRot[0] = -deltaRot[0]
		# 		deltaRot[0] += 180

		# if agent.agentId == 2:
		# 	if abs(agent.position[0]) < 50:
		# 		deltaRot[0] += 180

		# if agent.agentId == 3:
		# 	if abs(agent.position[0]) < 30:
		# 		deltaRot[0] += 180



		if facingGoal: #we are facing the goal

			if ballPosition[0] >= 0: #we are facing the ball
				actions.append(Kick(balls[0], np.array([1, 0, 0]), 100))


		return deltaPos, deltaRot, actions
