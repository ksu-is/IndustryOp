from pulp import *
import numpy as np
import pandas as pd
from itertools import product

import gurobipy as gp
from gurobipy import GRB


items = ['Handbag', 'Travel Bag', 'Wallet']


profit = {
    'Handbag':60,
    'Travel Bag':76,
    'Wallet':30,
}


rm_mat1 = {
    'Handbag':8,
    'Travel Bag':10,
    'Wallet':6,
   
}
rm_mat2 = {
    'Handbag':16,
    'Travel Bag':22,
    'Wallet':10,
    
}
rm_mat3 = {
   'Handbag':3.5,
    'Travel Bag':4.5,
    'Wallet':2.3,
    
}

prb = LpProblem('maximize_profit',LpMaximize)

item_vars = LpVariable.dicts('items',items,0);item_vars

prb += lpSum(profit[i]*item_vars[i] for i in items)

prb += lpSum([rm_mat1[i]*item_vars[i] for i in items]) <=360
prb += lpSum([rm_mat2[i]*item_vars[i] for i in items]) <=150
prb += lpSum([rm_mat3[i]*item_vars[i] for i in items]) <=400




prb.writeLP('maximize_profit.lp')

prb.solve()

print("_________________________________________________________________________________")
print(f'Status: {LpStatus[prb.status]}')


for i in prb.variables():
    print(f'{i.name} : {i.varValue} per unit')
    print("_________________________________________________________________________________")
print(f'Maximum daily profits {value(prb.objective)}')
print("_________________________________________________________________________________")


retailers, salesPoints, luxbagsMarket = gp.multidict({
    (1): [11,34],
    (2): [47,411],
    (3): [44,82],
    (4): [25,157],
    (5): [10,5],
    (6): [26,183],
    (7): [26,14],
    (8): [54,215],
    (9): [18,102],
    (10): [51,21],
    (11): [20,54],
    (12): [105,0],
    (13): [7,6],
    (14): [16,96],
    (15): [34,118],
    (16): [100,112],
    (17): [50,535],
    (18): [21,8],
})


intl_retailers,  lbagMarket1 = gp.multidict({
    (1): 9, 
    (2): 13,
    (3): 14,
    (4): 17,
    (5): 18,
    (6): 19,
    (7): 23,
    (8): 21
})

# Create a dictionary to capture the oil market -in millions of gallons for region 2.

dom_retailers,  lbagMarket2 = gp.multidict({
    (9): 9,
    (10): 11,
    (11): 17,
    (12): 18,
    (13): 18,
    (14): 17,
    (15): 22,
    (16): 24,
    (17): 36,
    (18): 43
})


groupA,  retailerA = gp.multidict({
    (1): 1,
    (2): 1,
    (3): 1,
    (5): 1,
    (6): 1,
    (10): 1,
    (15): 1,
})


groupB,  retailerB = gp.multidict({
    (4): 1,
    (7): 1,
    (8): 1,
    (9): 1,
    (11): 1,
    (12): 1,
    (13): 1,
    (14): 1,
    (16): 1,
    (17): 1,
    (18): 1,
})


salesPoints40 = 300
salesPoints5 = 37.5
luxbagsMarket40 = 958
luxbagsMarket5 = 119.75
lbagMarket1_40 = 68.6
lbagMarket1_5 = 6.7
lbagMarket2_40 = 86
lbagMarket2_5 = 23.75
retailerA40 = 3.2
retailerA5 = 5.5
retailerB40 = 6
retailerB5 = 0.75

model = gp.Model('MarketAllocation')

allocate = model.addVars(retailers, vtype=GRB.BINARY, name="allocate")


salesPointsBop = model.addVar(ub= salesPoints5, name='salesPointsBop')
salesPointsEop = model.addVar(ub= salesPoints5, name='salesPointsEop')


luxbagsMarketBop = model.addVar(ub=luxbagsMarket5, name='luxBagsMarketBop')
luxbagsMarketEop = model.addVar(ub=luxbagsMarket5, name='luxBagsMarketEop')


lbagMarket1Bop = model.addVar(ub=lbagMarket1_5, name='lbagMarket1Bop')
lbagMarket1Eop = model.addVar(ub=lbagMarket1_5, name='lbagMarket1Eop')


lbagMarket2Bop = model.addVar(ub=lbagMarket2_5, name='lbagMarket2Bop')
lbagMarket2Eop = model.addVar(ub=lbagMarket2_5, name='lbagMarket2Eop')

retailerABop  = model.addVar(ub=retailerA5, name='retailerABop')
retailerAEop  = model.addVar(ub=retailerA5, name='retailerAEop')


retailerBBop  = model.addVar(ub=retailerB5, name='retailerBPop')
retailerBEop  = model.addVar(ub=retailerB5, name='retailerBEop')

SVConstr = model.addConstr((gp.quicksum(salesPoints[r]*allocate[r] for r in retailers) 
                            + salesPointsBop - salesPointsEop == salesPoints40), name='SVConstrs')


lmConstr = model.addConstr((gp.quicksum(luxbagsMarket[r]*allocate[r] for r in retailers) 
                            + luxbagsMarketBop - luxbagsMarketEop == luxbagsMarket40), name='lmConstr')

LB1Constr = model.addConstr((gp.quicksum(lbagMarket1[r]*allocate[r] for r in intl_retailers) 
                            + lbagMarket1Bop - lbagMarket1Eop == lbagMarket1_40), name='LB1Constr')

LB2Constr = model.addConstr((gp.quicksum(lbagMarket2[r]*allocate[r] for r in dom_retailers) 
                            + lbagMarket2Bop - lbagMarket2Eop == lbagMarket2_40), name='LB2Constr')

AConstr = model.addConstr((gp.quicksum(retailerA[r]*allocate[r] for r in groupA) 
                            + retailerABop - retailerAEop == retailerA40), name='AConstr')

BConstr = model.addConstr((gp.quicksum(retailerB[r]*allocate[r] for r in groupB) 
                            + retailerBBop - retailerBEop == retailerB40), name='BConstr')

obj = salesPointsBop + salesPointsEop+ luxbagsMarketBop + luxbagsMarketEop + lbagMarket1Bop + lbagMarket1Eop + lbagMarket2Bop + lbagMarket2Eop + retailerABop + retailerAEop + retailerBBop + retailerBEop 

model.setObjective(obj)



model.write('marketAllocation.lp')


model.optimize()

print("\n\n_________________________________________________________________________________")
print(f"The optimal allocation of Luxury Leather Bags to retailers is:")
print("_________________________________________________________________________________")
for r in retailers:
    if(allocate[r].x > 0.5):
        print(f"Retailer{r}")
print("_________________________________________________________________________________")