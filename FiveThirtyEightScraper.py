import sys
from lxml import html
import requests
from fractions import gcd

webURL = ''
teams = {}
bracket = {'East': {1: {}, 2: {}, 3: {}, 4: {}},
           'West': {1: {}, 2: {}, 3: {}, 4: {}},
           'Midwest': {1: {}, 2: {}, 3: {}, 4: {}},
           'South': {1: {}, 2: {}, 3: {}, 4: {}}}

def parse_args():
	global webURL

	if len(sys.argv) == 2:
		if sys.argv[1] == 'default':
			webURL = 'http://fivethirtyeight.com/features/how-fivethirtyeight-is-forecasting-the-2016-ncaa-tournament/'
		else:
			webURL = sys.argv[1]
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
	teams.pop('Holy Cross', None)
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
					bracket[region][1][seed] = (team1, team2)

def probSim(roundNumber):
	for region in bracket:
		relevantMatchups = bracket[region][roundNumber]

		for matchup in relevantMatchups:
			team1ELO = teams[relevantMatchups[matchup][0]][1][0]
			team2ELO = teams[relevantMatchups[matchup][1]][1][0]

			probOfTeam1Win = 1/(10 ** (float(team2ELO - team1ELO) / 400)  + 1)

			print team1ELO, team2ELO, relevantMatchups[matchup], probOfTeam1Win


def main():
	parse_args()
	scraper()
	createBracket()
	probSim(1)

if __name__ == '__main__':
	main()

