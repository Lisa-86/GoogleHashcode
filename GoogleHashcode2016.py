# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 14:28:01 2019

@author: podfe
"""
        
####SOLUTION TO EXAMPLE(MOST EFFICIENT?)        
#7
#0 L 0 2 1
#0 D 0 2 1
#1 L 0 0 4
#1 D 0 0 1
#1 D 1 0 3
#2 L 0 2 1
#2 D 2 2 1


''' for L and U commands:
    first digit = drone id
    second digit = command
    third digit = warehouse id
    fourth digit = product id
    fifth digit = quant
    
    for D commands:
    first digit = drone id
    second digit = command
    third digit = order id
    fourth digit = prod id
    fifth digit = quant
    
    for W commands
    first digit = drone id
    second digit = command
    thrid digit = duration '''

###First thing is to parse the input file so the computer can read the problem


import math
solutionlist = []

### make a function to check distance

def getDistance(source, dest):
    ans = math.sqrt((source[0] - dest[0])**2 + (source[1] - dest[1])**2)
    return math.ceil(ans)

### make a function to return the closest warehouse

def closestWh(dloc, whlist):
    closestwh = whlist[0]
    distance = 100000
    for wh in whlist:
        if getDistance(dloc, wh[0]) < distance:
            closestwh = wh
    return closestwh


### make a loading function


def whichItems(drone, wh, itemcounts):
    for prod in range(prodTypeNo):
        if wh[1][prod] == 0:
            continue
        if itemcounts[prod] == 0:
            continue
        
        maxquant = math.floor(maxload/weights[prod])
        #print('maxquant that the drone can carry', maxquant)
        if maxquant == 0:
            continue
        quant = min(maxquant, wh[1][prod], itemcounts[prod])
        itemcounts[prod] -= quant
        return quant, prod
    
    return None, None
    
## function to update drone inv from the wh
        
def invUpdateDrone(drone, quant, prod):
    for index, p in enumerate(drone[1]):
        if index == prod:
            drone[1][index] = p + quant
        
    
    
##make a function to update warehouse inv after the drone loads
        #and remove wh if this makes wh inv empty
        
def invUpdateWh(drone, wh):
    for index in range(prodTypeNo):
        wh[1][index] -= drone[1][index]
        
    if all(quant == 0 for quant in wh[1]):
        whlist.remove(wh)
        
### work out where the closest order is

def closestOrder(dloc, ordlist, drone):
    closestord = None
    distance = 100000
    for order in ordlist:
        #find out if the order has prods the drone has
        maxprod = max(drone[1])
        if drone[1].index(maxprod) in order[2]:
            
            # if drone inv matches prod of order then find the closest one
            getDistance(dloc, order[0])
            closestord = order
    return closestord

##update drone inv after delivery to order

def invUpdateDroneDel(drone, order):
    # work out what the drone is carrying
    quantity = max(drone[1])
    #print ('drone quant', quantity)
    prod = drone[1].index(quantity)
    #print ('current prod type', prod)
    #print ('order inv', order[2])
    
    #work out the min between what the drone carries and what the order requires
    ordquant = 0
    for prodtype in order[2]:
        if prodtype == prod:
            ordquant += 1
   # print ('ordquant ', ordquant)
    
    minprodquant = min(quantity, ordquant)
    
    # remove from the drone all items in order 2
    drone[1][prod] -= minprodquant 
        
    return prod, minprodquant
            
 
 ### update the order inv after delivery
        
def invUpdateOrderDel(order, quant, prod):
    #will remove the prod from ord inv the number of times in quant
    [order[2].remove(prod) for _ in range(quant)]
          
    if len(order[2]) == 0:
        ordlist.remove(order)
    
    
    


probfile = open ('busy_day.in')

### rows, cols, dronesno, T, maxload
firstline = probfile.readline().split()
rows, cols, dronesno, T, maxload = [int(i) for i in firstline]

### How many diff prod types
prodTypeNo = int(probfile.readline())

### How much each prod weighs
thirdline = probfile.readline().split()
weights = [int(i) for i in thirdline]


### WAREHOUSES
### No of warehouses and for each warehouse its loc and inv
noWhs = int(probfile.readline())

whlist = []
for w in range(noWhs):
    whloc = [int(x) for x in probfile.readline().split()]
    whinv = [int(x) for x in probfile.readline().split()]
    wh = [whloc, whinv, w]   
    whlist.append(wh)
  
### ORDERS
#No of orders and order location, no of prods and prod types

noOrds = int(probfile.readline())

ordlist = []
for o in range(noOrds):
    ordloc = [int(x) for x in probfile.readline().split()]
    size = int(probfile.readline())
    prodTypes = [int(x) for x in probfile.readline().split()]
    order = [ordloc, size, prodTypes, o]
    ordlist.append(order)

#### need to sort the order list to have the shortest orders first
    
ordlist.sort(key=lambda x:x[1])

#need to count through each order the quantity of each prod type
itemcounts = [0 for prod in range(prodTypeNo)]
for order in ordlist:
    for prod in order[2]:
        itemcounts[prod] += 1

#print (itemcounts)
        
    


### DRONES

dronelist = [] 
for d in range(dronesno):
    drone = [whlist[0][0][:], [0 for x in range(prodTypeNo)], d]
    dronelist.append(drone)

#print(dronelist)

###Build a timeline showing the locs and invs of the drones etc
    
timeline = [[] for x in range(T*2)]

timeline[0] = dronelist

for t in range(T):
    availDrones = timeline[t]
    if t == T-1:
        break
    
    ## check if any drones are available, if not then pass
    
    if len(timeline[t]) == 0:
        continue
    
    ## if drone is available then check inv
    else:
        for drone in availDrones:
            # if empty then go to the nearest wh
            #print ('drone', drone)
            if sum(drone[1]) == 0:
                nearwh = closestWh(drone[0], whlist)
                quantity, prodType = whichItems(drone, nearwh, itemcounts)
                if quantity == None or prodType == None:
                    continue
                
                #update the timeline to make the drones available again
                timeline[t + getDistance(drone[0],nearwh[0])].append(drone)
                
                #update the drone loc
                drone[0] = nearwh[0][:]
                
                ## write the load command into the other file
                solutionlist.append(str(drone[2]) + ' L ' + str(nearwh[2]) + ' ' + str(prodType) + ' ' + str(quantity)  + ' \n' )
            
                #update invs and poss del wh 
                invUpdateDrone(drone, quantity, prodType)
                invUpdateWh(drone, nearwh)
                
            else:   #DELIVER
                # Find an order that matches the drone inv
                closestorder = closestOrder(drone[0], ordlist, drone)
                if closestorder == None:
                    print('LOST A DRONE')
                    continue
                else:
                    
                    # go to order loc and update timeline
                    timeline[t + getDistance(drone[0], closestorder[0])].append(drone)
                    
                    #update drone loc
                    drone[0] = closestorder[0][:]
                    
                    # remove from drone inv
                    prod, minprodquant = invUpdateDroneDel(drone, closestorder)
                    
                    # remove from order and if empty delete ord from ordlist
                    invUpdateOrderDel(closestorder, minprodquant, prod)
                    
                    # write the order command
                    solutionlist.append(str(drone[2]) + ' D ' + str(closestorder[3]) + ' ' + str(prod) + ' ' + str(minprodquant) + ' \n')


fd = sum([len(fd) for fd in timeline[T:]])
#print('still flying', fd)
            
### NEED TO PROCESS THE ORDERLIST TO TAKE OUT THE PRODITEMS THAT arent needed

print('solution list', solutionlist)            

solution = open('busydaycommands.txt', 'w')

solution.write(str(len(solutionlist)) + '\n')

for comm in solutionlist:
    solution.write(str(comm))

solution.close()   

































