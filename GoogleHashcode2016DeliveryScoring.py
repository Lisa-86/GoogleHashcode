import json



filename = 'example'
fin = open('busy_day.in')
rows_no, columns_no, drones_no, T, maxPayload = [int(x) for x in fin.readline().split()]
product_type_no = int(fin.readline())
weights = [int(w) for w in fin.readline().split()]
warehouse_no = int(fin.readline())
warehouses = []
for _ in range(warehouse_no):
    wloc = [int(xy) for xy in fin.readline().split()]
    wtokens = [int(token) for token in fin.readline().split()]
    assert len(wtokens) == product_type_no
    warehouse = {'wloc': wloc, 'winv': wtokens}
    warehouses.append(warehouse)

order_no = int(fin.readline())
orders = []
for _ in range(order_no):
    oloc = [int(xy) for xy in fin.readline().split()]
    otot = int(fin.readline())
    oitemids = [int(typ) for typ in fin.readline().split()]
    assert len(oitemids) == otot
    order = {'oloc' : oloc, 'oitemids': oitemids}
    orders.append(order)

#print(json.dumps(orders, indent=4))


fout = open('busydaycommands.txt')
commands_no = int(fout.readline())
# each drone has a list of commands
commands = {did:[] for did in range(drones_no)}
for _ in range(commands_no):
    line = fout.readline().split()
    did = int(line[0])
    cmd = line[1]
    if cmd == 'L' or cmd == 'U':
        wid = int(line[2])
        pid = int(line[3])
        quant = int(line[4])
        commands[did].append([cmd, wid, pid, quant])
    elif cmd == 'D':
        oid = int(line[2])
        pid = int(line[3])
        quant = int(line[4])
        commands[did].append([cmd, oid, pid, quant])
    elif cmd == 'W':
        wlen = int(line[2])
        commands[did].append([cmd, wlen])
    else:
        raise Exception('Error')

    #did, cmd, wid, pid, quant = [int(x) for x in fout.readline().split()]

timeline = [[] for _ in range(T)]

# initially, all drones are available at the warehouse id 0, list of pids
drones = [[did, warehouses[0]['wloc'], {}] for did in range(drones_no)]
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
        did = drone[0]
        cmd = commands[did]
        if len(cmd) == 0:
            print('DEL', did)
            drones.remove(drone)

    # sort to carry out unloading first
    drones_sorted = sorted(drones, key=lambda x:commands[x[0]][0][0], reverse=True)

    # for each available drone, issue the next command
    for did, dloc, dinv in drones_sorted:
        # get the drones command
        command = commands[did]
        fcmd = command[0]

        if fcmd[0] == 'W':
            # move the drone to the future
            wlen = fcmd[1]
            timeline[t + wlen].append([did, dloc, dinv])
            # remove the command
            commands[did] = commands[did][1:]
        elif fcmd[0] == 'U':
            cmd, wid, pid, quant = fcmd[0]
            # check that the drone has the item(s) on it
            dquant = dinv[pid]
            if dquant < quant:
                raise Exception('Nice try, this drone does not have enough items')

            # is the drone at the warehouse?
            wh = warehouses[wid]
            wloc = wh['wloc']
            if wloc != dloc:
                # drone is not there yet, allow it time for travel
                # however, we cannot remove this command
                # calc the distance (time)
                dst = calc_dst(dloc, wloc)
                timeline[t + dst].append([did, wloc, dinv])
                continue

            # drone is at the warehouse,
            # remove items from the drone
            dinv[pid] -= quant
            # add the items to the warehouse
            wh['winv'][pid] += quant
            # remove this command
            commands[did] = commands[did][1:]

        # if it is the load command, it has to travel to the warehouse,
        elif fcmd[0] == 'L':
            # check the travel time
            cmd, wid, pid, quant = fcmd
            # check location
            wh = warehouses[wid]
            wloc = wh['wloc']
            if wloc != dloc:
                # the drone is not at the warehouse, postpone until it arrives
                dst = calc_dst(dloc, wloc)
                timeline[t + dst].append([did, wloc, dinv])
                print('Fly', did, 'whloc', wloc, 'load', pid, 'willArrive', t + dst)
            elif wloc == dloc:
                # check if the item(s) is in the warehouse
                winv = wh['winv']
                no_in_wh = winv[pid]
                if not quant <= no_in_wh:
                    raise('Not enough items')

                # check if the drone can carry it
                if (quant * weights[pid]) + all_weight(dinv) > maxPayload:
                    raise ('Too heavy')

                # remove from warehouse
                winv[pid] -= quant
                # add it to the drone
                if not pid in dinv:
                    dinv[pid] = 0
                dinv[pid] += quant

                # this drone is loading, so it will be available on the next turn
                timeline[t + 1].append([did, dloc, dinv])

                # remove this command
                commands[did] = commands[did][1:]
                print('Did', did, 'load', pid, 'from', wid)

        elif fcmd[0] == 'D':
            cmd, oid, pid, quant = fcmd
            theorder = orders[oid]
            oloc = theorder['oloc']

            if dloc != oloc:
                # wait till it arrives
                dst = calc_dst(dloc, oloc)
                timeline[t + dst].append([did, oloc, dinv])
                print('Fly', did, 'to', oid, 'deliver', pid, 'willArrive', t + dst)
                continue

            # it is at the right location
            # does the drone have the right items?
            if dinv[pid] < quant:
                raise Exception('Drone does not have the right items for delivery')

            # remove from the drone
            dinv[pid] -= quant

            # remove it from the order
            oitemids = theorder['oitemids']
            for q in range(quant):
                oitemids.remove(pid)

            print('Did', did, 'delivered')

            # if order is done, score
            if len(oitemids) == 0:
                score = calc_score(t)
                final_score += score
                print('Did', did, 'oid', oid, 'SCORE', score)

            # remove this command
            commands[did] = commands[did][1:]

            # make drone available for the next turn
            timeline[t + 1].append([did, dloc, dinv])

# TODO summerise how many orders have been fulfilled
fulfilled = sum([len(order['oitemids']) == 0 for order in orders])
print('Fulfilled Orders', fulfilled)
print('Unfulfilled Orders', order_no - fulfilled)
print('Final Score', final_score)