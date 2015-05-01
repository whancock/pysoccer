from Agent import Agent
from Ball import Ball
from Obstacle import Obstacle
from LinearAlegebraUtils import getYPRFromVector
import numpy as np
from Action import Stun, Kick

from NavUtils import snapVector, getTeamAvoidance

class AntiflockBrain(object):


	def __init__(self):      
		pass

	def takeStep(self, agent, facingGoal, myTeam=[], enemyTeam=[], balls=[], obstacles=[]):

		movedir = np.array([0,0,0])

		ballPosition = balls[0].getFuzzyPosition(100)
		# ballPosition = balls[0].position
		# ballPosition = (np.random.rand(3) * 200) - 100


		movedir += ballPosition


		actions = []
		deltaPos = np.array([1, 0, 0])
		

		# degrade our knowledge to direction of ball, not location
		# deltaRot = snapVector(deltaRot)



		# if I am closest to the ball, keep going, else move away from teammates
		myBallDist = np.linalg.norm(ballPosition)
		teamMinDist = min(np.linalg.norm(mate.position - ballPosition) for mate in myTeam)

		if not myBallDist < teamMinDist:
			movedir += 1.0 * getTeamAvoidance(myTeam)


		
		




		if facingGoal: #we are facing the goal

			if ballPosition[0] >= 0: #we are facing the ball
				actions.append(Kick(balls[0], np.array([1, 0, 0]), 100))

		deltaRot = getYPRFromVector(movedir)


		return deltaPos, deltaRot, actions