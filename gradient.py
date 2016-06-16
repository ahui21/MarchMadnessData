import random

villanovaFin = 0.28
oklahomaFin = 0.22
uncFin = 0.38
syracuseFin = 0.11

villanova1 = 0.54
oklahoma1 = 1 - villanova1
unc1 = 0.7
syracuse1 = 1 - unc1

offByLowest = 100.0

offByTable = []

def randomGenerate():
	global villanovaFin
	global oklahomaFin
	global uncFin
	global syracuseFin

	global villanova1
	global oklahoma1
	global unc1
	global syracuse1

	global offByLowest
	global offByTable

	villanova1 = 0.01 * (1 - random.random()) + villanova1
	oklahoma1 = 0.01 * (1 - random.random()) + oklahoma1
	unc1 = 0.01 * (1 - random.random()) + unc1
	syracuse1 = 0.01 * (1 - random.random()) + syracuse1


	aca = random.random()
	acc = 1 - aca
	ada = random.random()
	add = 1 - ada
	bcb = random.random()
	bcc = 1 - bcb
	bdb = random.random()
	bdd = 1 - bdb

	villanova = villanova1 * (unc1 * aca + syracuse1 * ada)
	oklahoma = oklahoma1 * (unc1 * bcb + syracuse1 * bdb)
	unc = unc1 * (villanova1 * acc + oklahoma1 * bcc)
	syracuse = syracuse1 * (villanova1 * add + oklahoma1 * bdd)

	offBy = abs(villanova - villanovaFin) + abs(oklahoma - oklahomaFin) + abs(unc - uncFin) + abs(syracuse - syracuseFin)

	if offBy < offByLowest:
		offByTable = [(villanova1, oklahoma1, unc1, syracuse1), (aca, ada, bcb, bdb), '\n']
		offByLowest = offBy
	elif offBy == offByLowest:
		offByTable.append((villanova1, oklahoma1, unc1, syracuse1), (aca, ada, bcb, bdb), '\n')

def main():
	for i in range(100000000):
		randomGenerate()

	print offByLowest
	for i in offByTable:
		print i

if __name__ == '__main__':
	main()
