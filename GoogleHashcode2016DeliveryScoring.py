#!/usr/bin/env python

import matplotlib.pyplot as plt

fin = open('mother_of_all_warehouses.in')
fout = open('mother_of_all_warehouses.out')

class Warehouse:
    def __init__(self, id, location, inventory):
        self.id = id
        self.loc = location
        self.inv = inventory

    def getLocation(self):
        print('My location is ', self.loc)

class Order:
    def __init__(self, id, location, size, producttypes, general_weights):
        self.id = id
        self.loc = location
        self.size = size
        # it is actually the index of the product type
        self.prods = producttypes
        self.prodvariety = len(set(producttypes))
        self.weight = sum(general_weights[pt] for pt in producttypes)

class Drone:
    def __init__(self, id, location, inventory):
        self.id = id
        self.loc = location
        self.inv = inventory


class Lommand:
    def __init__(self, drone, warehouse, producttype, quantity):
        self.drone = drone
        self.warehouse = warehouse
        self.ptype = producttype
        self.quant = quantity
        self.letter = 'L'

class Dommand:
    def __init__(self, drone, order, productype, quantity):
        self.drone = drone
        self.order = order
        self.ptype = productype
        self.quant = quantity
        self.letter = 'D'


rows_no, columns_no, drones_no, T, maxPayload = [int(x) for x in fin.readline().split()]
product_type_no = int(fin.readline())
weights = [int(w) for w in fin.readline().split()]
warehouse_no = int(fin.readline())
warehouses = []
for id in range(warehouse_no):
    wloc = [int(xy) for xy in fin.readline().split()]
    wtokens = [int(token) for token in fin.readline().split()]
    assert len(wtokens) == product_type_no
    wh = Warehouse(id, wloc, wtokens)
    warehouses.append(wh)

order_no = int(fin.readline())
orders = []
for id in range(order_no):
    oloc = [int(xy) for xy in fin.readline().split()]
    otot = int(fin.readline())
    oitemids = [int(typ) for typ in fin.readline().split()]
    assert len(oitemids) == otot
    order = Order(id, oloc, otot, oitemids, weights)
    orders.append(order)


# orders.sort(key=lambda o:o.prodvariety)
# ourweights = [o.weight for o in orders]
# prodTypeVar = [o.prodvariety for o in orders]
# plt.scatter(prodTypeVar, ourweights)
# plt.xlabel('Different Order Types (#)')
# plt.ylabel('Total Order Weight')
# plt.savefig('plots/orderweights_vs_typedifference.png', dpi=300)
# plt.show()
# import sys
# sys.exit(0)

# initially, all drones are available at the warehouse id 0, list of pids
drones = [Drone(did, warehouses[0].loc[:], {}) for did in range(drones_no)]

commands_no = int(fout.readline())
# each drone has a list of commands
commands = {did:[] for did in range(drones_no)}
for _ in range(commands_no):
    line = fout.readline().split()
    did = int(line[0])
    cmd = line[1]
    if cmd == 'L':
        wid = int(line[2])
        pid = int(line[3])
        quant = int(line[4])
        drone = drones[did]
        warehouse = warehouses[wid]
        command = Lommand(drone, warehouse, pid, quant)
        commands[did].append(command)
    elif cmd == 'U':
        raise Exception('Not implemented')
    elif cmd == 'D':
        oid = int(line[2])
        pid = int(line[3])
        quant = int(line[4])
        drone = drones[did]
        order = orders[oid]
        command = Dommand(drone, order, pid, quant)
        commands[did].append(command)
    elif cmd == 'W':
        wlen = int(line[2])
        commands[did].append([cmd, wlen])
        raise Exception('Not Implemented')
    else:
        raise Exception('Error')

    #did, cmd, wid, pid, quant = [int(x) for x in fout.readline().split()]

timeline = [[] for _ in range(T)]

#print('drones', json.dumps(drones, indent=2))
timeline[0] = drones

def all_weight(dinv):
    tot = 0
    for pid, quant in dinv.items():
        tot += weights[pid] * quant
    return tot

import math
def calc_dst(src, dst):
    sqrt = math.sqrt( (src[0]-dst[0])**2 + (src[1]-dst[1])**2 )
    return math.ceil(sqrt)

def calc_score(t):
    return math.ceil(float(T-t)/T * 100)

final_score = 0
for t in range(T):
    #print('time', t)
    # get the available drones
    drones = timeline[t]
    #print('Drones', drones)

    # if there is no commands for the drone any more, remove the drone
    for drone in drones[::-1]:
        did = drone.id
        cmd = commands[did]
        if len(cmd) == 0:
            print('DEL', did)
            drones.remove(drone)

    # sort to carry out unloading first
    drones_sorted = sorted(drones, key=lambda drone:commands[drone.id][0].letter, reverse=True)

    # for each available drone, issue the next command
    for drone in drones_sorted:
        # get the drones command
        command = commands[drone.id]
        fcmd = command[0]

        if fcmd.letter == 'W':
            # move the drone to the future
            wlen = fcmd[1]
            timeline[t + wlen].append(drone)
            # remove the command
            commands[drone.id] = commands[drone.id][1:]
        elif fcmd.letter == 'U':
            cmd, wid, pid, quant = fcmd[0]
            # check that the drone has the item(s) on it
            dquant = drone.inv[pid]
            if dquant < quant:
                raise Exception('Nice try, this drone does not have enough items')

            # is the drone at the warehouse?
            wh = warehouses[wid]
            if wh.loc != drone.loc:
                # drone is not there yet, allow it time for travel
                # however, we cannot remove this command
                # calc the distance (time)
                dst = calc_dst(drone.loc, wh.loc)
                drone.loc = wh.loc[:]
                timeline[t + dst].append(drone)
                continue

            # drone is at the warehouse,
            # remove items from the drone
            drone.inv[pid] -= quant
            # add the items to the warehouse
            wh.inv[pid] += quant
            # remove this command
            commands[drone.id] = commands[drone.id][1:]

        # if it is the load command, it has to travel to the warehouse,
        elif fcmd.letter == 'L':
            # check location
            wh = fcmd.warehouse
            if wh.loc != drone.loc:
                # the drone is not at the warehouse, postpone until it arrives
                dst = calc_dst(drone.loc, wh.loc)
                drone.loc = wh.loc[:]
                timeline[t + dst].append(drone)
                # print('Fly', did, 'whloc', wloc, 'load', pid, 'willArrive', t + dst)
            elif wh.loc == drone.loc:
                # check if the item(s) is in the warehouse
                no_in_wh = wh.inv[fcmd.ptype]
                if not fcmd.quant <= no_in_wh:
                    raise('Not enough items')

                # check if the drone can carry it
                if (fcmd.quant * weights[fcmd.ptype]) + all_weight(drone.inv) > maxPayload:
                    raise ('Too heavy')

                # remove from warehouse
                wh.inv[fcmd.ptype] -= fcmd.quant
                # add it to the drone
                if not fcmd.ptype in drone.inv:
                    drone.inv[fcmd.ptype] = 0
                drone.inv[fcmd.ptype] += fcmd.quant

                # this drone is loading, so it will be available on the next turn
                timeline[t + 1].append(drone)

                # remove this command
                commands[drone.id] = commands[drone.id][1:]
                #print('Did', did, 'load', pid, 'from', wid)

        elif fcmd.letter == 'D':
            order = fcmd.order
            if drone.loc != order.loc:
                # wait till it arrives
                dst = calc_dst(drone.loc, order.loc)
                drone.loc = order.loc[:]
                timeline[t + dst].append(drone)
                #print('Fly', did, 'to', oid, 'deliver', pid, 'willArrive', t + dst)
                continue

            # it is at the right location
            # does the drone have the right items?
            if drone.inv[fcmd.ptype] < fcmd.quant:
                raise Exception('Drone does not have the right items for delivery')

            # remove from the drone
            drone.inv[fcmd.ptype] -= fcmd.quant

            # remove it from the order
            oitemids = order.prods
            for _ in range(fcmd.quant):
                oitemids.remove(fcmd.ptype)

            print('Did', drone.id, 'delivered')

            # if order is done, score
            if len(oitemids) == 0:
                score = calc_score(t)
                final_score += score
                print('Did', drone.id, 'oid', order.id, 'SCORE', score)

            # remove this command
            commands[drone.id] = commands[drone.id][1:]

            # make drone available for the next turn
            timeline[t + 1].append(drone)

# TODO summerise how many orders have been fulfilled
fulfilled = sum([len(order.prods) == 0 for order in orders])
print('Fulfilled Orders', fulfilled)
print('Unfulfilled Orders', order_no - fulfilled)
print('Final Score', final_score)