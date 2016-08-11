# Gregory Kehne
#
# Given integers x_1,... x_n, the Least Common Multiple (LCM) is the smallest
# positive integer that is an integer multiple of every x_i. This definition is
# complicated when the x_i are allowed to be arbitrary real numbers, because
# it may no longer exist. The 'approximate LCM' of some real x_i over some
# specified range is the real number within that range that comes closest to
# (without exceeding) some integer multiple all x_i at once, where 'closest' is
# defined according to a specified cost function that is linear in x_i.
#
# The motivating example is cooking a recipe. Suppose that I want somewhere
# between 100 and 200 chocolate chip cookies, but I want to have as little
# waste ingredients as possible, measured in terms of ingredient cost. The
# flour, butter, sugar, chocolate chips, etc are all sold in quantites that
# equal some real multiple of chocolate chips, according to the specifics of
# my recipe. And although I can make 50\pi cookies, I cannot so easily buy \pi
# bags of chocolate chips. Given a .csv file that contains a table of the
# ingredients, the number of cookies that can be made with one unit of each,
# ingredient, and the price per cookie for each ingredient, this program gives
# the number of cookies you should make, the amount of each ingredient that
# should be purchased, the total cost, and the total waste.
#
# TO USE: Enter your data in columns 1-4, and enter the minimum and maximum
# values for the approximateLCM under the headings of column 5 and column 6.
# The program will then populate columns 8-13 with the optimal proportions
# and answers given the constraints.


import csv
from pulp import LpProblem, LpVariable, LpInteger, LpMinimize, value

# makes the new LP Problem
problem = LpProblem("Approximate LCM", LpMinimize)

# Name of the CSV containing the input data (must be in the format provided):
datafilename = "ALCMData.csv"

# reads the data from the CSV file into the LPP
variables, ingredients, servingsPerBlock, costsPerServing = [], [], [], []

lines = []  # keep track of the lines from the CSV file
header = []  # keep track of header

#  Open CSV file
with open(datafilename, 'rU') as thefile:
    data_reader = csv.reader(thefile)
    firstrow = True
    for row in data_reader:
        if firstrow:
            header.append(row)  # skip the row of column headers
        else:
            lines.append(row)
            variables.append(LpVariable("x_" + row[1], 0, None, LpInteger))
            ingredients.append(row[0])
            servingsPerBlock.append(float(row[2]))
            costsPerServing.append(float(row[3]))
        firstrow = False
    variables.append(LpVariable("s", 0))

# read in the upper and lower bounds for aLCM
minServe = lines[0][4]
maxServe = lines[0][5]

# serving constraints: specifies the interval in which the approximate
# LCM may lie
min_constraint = variables[-1] >= float(minServe)
max_constraint = variables[-1] <= float(maxServe)
problem += min_constraint
problem += max_constraint

# block constraints: there must be enough of each ingredient for the ultimate
# optimal number
for v in range(len(variables) - 1):
    min_constraint = variables[v] * servingsPerBlock[v] >= variables[-1]
    problem += min_constraint

pps = 0.0  # price per serving
for i in range(len(variables) - 1):
    pps += costsPerServing[i]

#  add objective function to be minimized (waste)
obj_fn = 0 * variables[0]
for i in range(len(variables) - 1):
    obj_fn += variables[i] * costsPerServing[i] * servingsPerBlock[i]
obj_fn -= variables[-1] * pps
problem += obj_fn  # add the objective funciton to the problem

problem.solve()  # runs the linear programming problem

# read off the aLCM
s = value(variables[-1])

mincost = 0.0
for i in range(len(variables) - 1):
    mincost += s * costsPerServing[i]

waste = value(obj_fn)
cost = waste + mincost

# for row in lines: # make all rows the right length
#   while len(row)<7: # for rows that were too short
#     if firstrow:
#       row+=[""]
#     else:
#      row+=["","",""]
#  print row

# add the output data to the rows that will be written to the .csv
for row in lines:
    row[7] = round(value(variables[int(row[1]) - 1]), 3)  # units of ing.s
    row[8] = round(value(variables[int(row[1]) - 1]) *
                   float(row[2]) * float(row[3]), 2)  # cost for each ing.
    row[9] = round(float(row[8]) - s * float(row[3]), 2)  # waste for each

lines[0][10] = s  # this is the aLCM
lines[0][11] = round(cost, 2)  # total cost
lines[0][12] = round(waste, 2)  # total waste

# write the new rows into the output .csv file, replace the header
header[0] = ["ingredient", "index", "servings/block", "price/serving",
             "min aLCM", "max aLCM", "", "units used", "cost", "waste",
             "aLCM", "total cost", "total waste"]
with open('ALCMOutput.csv', 'wb') as thefile:
    writer = csv.writer(thefile)
    writer.writerows(header)
    writer.writerows(lines)
