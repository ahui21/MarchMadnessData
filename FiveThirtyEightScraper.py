import sys
from lxml import html
import requests
from fractions import gcd
import random
import operator

webURL = ''
teams = {}
bracket = {'East': {1: {}, 2: {}, 3: {}, 4: {}, 5:{}},
           'West': {1: {}, 2: {}, 3: {}, 4: {}, 5:{}},
           'Midwest': {1: {}, 2: {}, 3: {}, 4: {}, 5:{}},
           'South': {1: {}, 2: {}, 3: {}, 4: {}, 5:{}}}
totalCount = {1: {}, 2: {}, 3: {}, 4: {}, 5:{}}
numOfTrials = 21

def parse_args():
	global webURL
	global numOfTrials

	if len(sys.argv) == 3:
		if sys.argv[1] == 'default':
			webURL = 'http://fivethirtyeight.com/features/how-fivethirtyeight-is-forecasting-the-2016-ncaa-tournament/'
		else:
			webURL = sys.argv[1]
		numOfTrials = int(sys.argv[2])
	else:
		raise ValueError('Incorrect number of arguments (%i) found.' % len(sys.argv))

def scraper():
	global teams
	global webURL

	page = requests.get(webURL)
	tree = html.fromstring(page.content)

	#This will create a list of objects marked as 'text':
	text = tree.xpath('//td[@class="text"]/text()')
	#This will create a list of objects marked as 'rank':
	rank = tree.xpath('//td[@class="rank"]/text()')
	#This will create a list of objects marked as 'number':
	number = tree.xpath('//td[@class="number"]/text()')
	#This will create a list of objects marked as 'number highlight':
	numberHighlight = tree.xpath('//td[@class="number highlight"]/text()')

	numberOfTeams = gcd(len(text), len(rank))
	numberOfTeams = gcd(numberOfTeams, len(number))
	numberOfTeams = gcd(numberOfTeams, len(numberHighlight))

	for i in range(len(text)):
		text[i] = str(text[i].replace(u"\u2018", "'").replace(u"\u2019", "'"))

	team = ""
	region = ""
	seed = 0
	elo = 0
	composite = 0.0
	finalFourProb = 0.0
	champProb = 0.0

	for i in range(numberOfTeams * 6):
		div2 = False
		div3 = False

		if i % 2 == 0:
			div2 = True
			j = i / 2
			if j % 3 == 0:
				elo = int(number[j])
			elif j % 3 == 1:
				composite = float(number[j])
			elif j % 3 == 2:
				negative = False
				if number[j][0] == "<":
					negative = True
				if negative:
					finalFourProb = float("-" + number[j][1:].rstrip('%'))
				else:
					finalFourProb = float(number[j].rstrip('%'))
		
		if i % 3 == 0:
			div3 = True
			j = i / 3
			if j % 2 == 0:
				team = text[j]
			elif j % 2 == 1:
				region = text[j]
		
		if div2 and div3:
			j = i / 6
			seed = int(rank[j])

			negative = False
			if numberHighlight[j][0] == "<":
				negative = True
			if negative:
				champProb = float("-" + numberHighlight[j][1:].rstrip('%'))
			else:
				champProb = float(numberHighlight[j].rstrip('%'))

		teams[team] = ((region, seed), (elo, composite), (finalFourProb, champProb))

	teams.pop('Fairleigh Dickinson', None)
	teams.pop('Vanderbilt', None)
	teams.pop('Southern', None)
	teams.pop('Tulsa', None)

def createBracket():
	global teams
	global bracket

	for team1 in teams:
		region = teams[team1][0][0]
		seed = teams[team1][0][1]

		if seed < 9:
			for team2 in teams:
				if teams[team2][0][0] == region and teams[team2][0][1] == 17 - seed:
					bracket[region][1][seed] = [team1, team2]

def runNumOfTrials(inputNumOfTrials):
	global totalCount

	for i in range(inputNumOfTrials):
		runFullBracket()

		for i in range(1, 6):
			for region in bracket:
				for j in bracket[region][i]:
					for k in bracket[region][i][j]:
						if k in totalCount[i]:
							totalCount[i][k] = totalCount[i][k] + 1
						else:
							totalCount[i][k] = 1

def runFullBracket():
	regionalRoundSim(1)
	regionalRoundSim(2)
	regionalRoundSim(3)
	regionalRoundSim(4)

def regionalRoundSim(roundNumber):
	for region in bracket:
		relevantMatchups = bracket[region][roundNumber]

		if roundNumber < 4:
			for i in range(2 ** (3 - roundNumber)):
				bracket[region][roundNumber + 1][i + 1] = []
		else:
			bracket[region][roundNumber + 1][1] = []

		for matchup in relevantMatchups:
			probOfTeam1Win = probSim(relevantMatchups[matchup])
			
			randomNum = random.random()

			numOfRounds = 2 ** (4 - roundNumber)
			nextRound = min(matchup, numOfRounds + 1 - matchup)

			if randomNum <= probOfTeam1Win:
				bracket[region][roundNumber + 1][nextRound].append(relevantMatchups[matchup][0])
			else:
				bracket[region][roundNumber + 1][nextRound].append(relevantMatchups[matchup][1])

def probSim(matchup):
	team1ELO = teams[matchup[0]][1][0]
	team2ELO = teams[matchup[1]][1][0]

	return 1/(10 ** (float(team2ELO - team1ELO) / 400)  + 1)

def printResults():
	global totalCount

	for i in range(1, 6):
		print '\n'
		sorted_rounds = sorted(totalCount[i].items(), key = operator.itemgetter(1), reverse = True)
		for i in sorted_rounds:
			print i

def main():
	parse_args()
	scraper()
	createBracket()
	runNumOfTrials(numOfTrials)
	printResults()

if __name__ == '__main__':
	main()

