from lxml import html
import requests
from fractions import gcd

page = requests.get('http://fivethirtyeight.com/features/how-fivethirtyeight-is-forecasting-the-2016-ncaa-tournament/')
tree = html.fromstring(page.content)

#This will create a list of objects marked as 'text':
text = tree.xpath('//td[@class="text"]/text()')
#This will create a list of objects marked as 'rank':
rank = tree.xpath('//td[@class="rank"]/text()')
#This will create a list of objects marked as 'number':
number = tree.xpath('//td[@class="number"]/text()')
#This will create a list of objects marked as 'number highlight':
numberHighlight = tree.xpath('//td[@class="number highlight"]/text()')

teams = {}

numberOfTeams = gcd(len(text), len(rank))
numberOfTeams = gcd(numberOfTeams, len(number))
numberOfTeams = gcd(numberOfTeams, len(numberHighlight))

team = []
region = []
seed = []
elo = []
composite = []
finalFourProb = []
champProb = []

for i in range(numberOfTeams * 6):
	div2 = False
	div3 = False

	if i % 2 == 0:
		div2 = True
		j = i / 2
		if j % 3 == 0:
			elo = number[j]
		elif j % 3 == 1:
			composite = number[j]
		elif j % 3 == 2:
			finalFourProb = number[j].rstrip('%')
	
	if i % 3 == 0:
		div3 = True
		j = i / 3
		if j % 2 == 0:
			team = text[j]
		elif j % 2 == 1:
			region = text[j]
	
	if div2 and div3:
		j = i / 6
		seed = rank[j]
		champProb = numberHighlight[j].rstrip('%')

	teams[team] = ((region, seed), (elo, composite), (finalFourProb, champProb))

for team in teams:
	print team, teams[team], '\n'