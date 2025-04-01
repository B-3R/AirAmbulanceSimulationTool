import json
import random
import os
from datetime import datetime
import numpy as np
from scipy.stats import truncnorm
import time

def demand_synthesizer(config_demand,nodes,zufallsstromzahl):
    random.seed(zufallsstromzahl)
    np.random.seed(zufallsstromzahl)

    joblist = {'config': config_demand}

    if config_demand['type'] == 'random':
        jobs = []
        for i in range(0,config_demand['total_demand']):
            job = {}
            job['triggertime'] = random.choice(range(0,config_demand['timeframe']))+config_demand['starttime']
            job['loadingtime'] = np.random.normal(600,120)
            job['unloadingtime'] = np.random.normal(600,120)
            job['pickup'] = random.choice(nodes).position
            job['target'] = job['pickup']
            job['type'] = 'patient carrying'
            while job['target'] == job['pickup']:
                job['target'] = random.choice(nodes).position
            job['id'] = f'{job['pickup']}.{job['target']}.{job['triggertime']}'
            jobs.append(job)

    if config_demand['type'] == 'realistic':
        jobs = []

        for i in range(0,config_demand['total_demand']):
            job = {}
            #TRIGGERTIME first assign a time based on week distribution - DONE
            weekdays = [i for i in config_demand['weekdays'].keys()]
            weekday_probability = [config_demand['weekdays'][i] for i in weekdays]
            weekday = random.choices(weekdays, weekday_probability)[0]

            daytype = 'weekday' if weekday in range(0,5) else 'weekend'

            hours = [i for i in config_demand['hourly'][daytype].keys()]
            hour_probability = [config_demand['hourly'][daytype][i] for i in hours]
            hour = random.choices(hours, hour_probability)[0]

            timeslot_start = weekday * 24 * 3600 + hour * 3600
            timeslot_end = timeslot_start + 3600

            job['triggertime'] = random.choice(range(timeslot_start,timeslot_end))

            #ROUTE TYPE - DONE
            routetypes = [i for i in config_demand['routetypes'].keys()]
            routetype_probability = [config_demand['routetypes'][i] for i in routetypes]
            routetype = random.choices(routetypes, routetype_probability)[0]
            job['routetype'] = routetype

            #PICKUP random DONE
            node1 = random.choice(nodes)
            while (node1.type not in['hub','base'] and routetype in ['upwards','downwards','centers']) or (node1.type in ['hub','base'] and routetype == 'local'):  # Keep choosing until a hub is found
                node1 = random.choice(nodes)
                
            #TARGET for up and downwards do distance distribution - DONE
            if routetype in ['upwards','downwards']:
                while True:
                    targetdistance = np.random.normal(config_demand['mean distance'], config_demand['std distance'])
                    if targetdistance > 5000:
                        break
                closest = np.inf # m to closest node
                for node in nodes:
                    distance = np.sqrt((node1.position[0] - node.position[0])**2 + (node1.position[1] - node.position[1])**2)
                    if abs(targetdistance - distance) < closest and distance > config_demand['min distance'] and node.type not in ['hub','base'] :
                        node2 = node
                        closest = abs(targetdistance - distance)
                
            elif routetype in ['centers']:
                node2 = random.choice(nodes)
                distance = np.sqrt((node1.position[0] - node2.position[0])**2 + (node1.position[1] - node2.position[1])**2)
                while node2.type not in ['hub','base']  or distance < config_demand['min distance']:  # Keep choosing until a hub is found
                    node2 = random.choice(nodes)
                    distance = np.sqrt((node1.position[0] - node2.position[0])**2 + (node1.position[1] - node2.position[1])**2)
                job['pickup'] = node1.position
                job['target'] = node2.position
                job['pickupID'] = node1.id
                job['targetID'] = node2.id
            elif routetype in ['local']:
                node2 = random.choice(nodes)
                distance = np.sqrt((node1.position[0] - node2.position[0])**2 + (node1.position[1] - node2.position[1])**2)
                while node2.type in ['hub','base']  or distance < config_demand['min distance']:  # Keep choosing until a hub is found
                    node2 = random.choice(nodes)
                    distance = np.sqrt((node1.position[0] - node2.position[0])**2 + (node1.position[1] - node2.position[1])**2)
                job['pickup'] = node1.position
                job['target'] = node2.position
                job['pickupID'] = node1.id
                job['targetID'] = node2.id
                
                
            #DIRECTION for up and downwards - DONE
            if routetype in ['downwards']:
                if node1.type in ['hub','base'] :
                    job['pickup'] = node1.position
                    job['target'] = node2.position
                    job['pickupID'] = node1.id
                    job['targetID'] = node2.id
                else:
                    job['pickup'] = node2.position
                    job['target'] = node1.position
                    job['pickupID'] = node2.id
                    job['targetID'] = node1.id

            elif routetype in ['upwards']:
                if node1.type in ['hub','base'] :
                    job['pickup'] = node2.position
                    job['target'] = node1.position
                    job['pickupID'] = node2.id
                    job['targetID'] = node1.id
                else:
                    job['pickup'] = node1.position
                    job['target'] = node2.position
                    job['pickupID'] = node1.id
                    job['targetID'] = node2.id

            #LOADING TIME - DONE
            a, b = (config_demand['loadingtime']['min'] - config_demand['loadingtime']['mean']) / config_demand['loadingtime']['std'], np.inf  # Lower bound, upper bound (in standard normal space)
            job['loadingtime'] = abs(truncnorm.rvs(a, b, loc=config_demand['loadingtime']['mean'], scale=config_demand['loadingtime']['std']))
            job['unloadingtime'] = abs(truncnorm.rvs(a, b, loc=config_demand['loadingtime']['mean'], scale=config_demand['loadingtime']['std']))

            job['type'] = 'patient carrying'
            job['id'] = f'{job['pickup']}.{job['target']}.{job['triggertime']}'
            job['distance'] = abs(np.sqrt((job['pickup'][0] - job['target'][0])**2 + (job['pickup'][1] - job['target'][1])**2))
            jobs.append(job)
        

    joblist['joblist'] = jobs

    if False:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join('data','data_log', f"joblist_{timestamp}.json")
        with open(filepath, 'w') as f:
            json.dump(joblist, f, indent=4)
    return joblist

if __name__ == '__main__':
    import sys
    import os

    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(parent_dir) 

    from config import config_run, config_demand,config
    from utils.analysis import analysis_demand_profiles
    from utils.visualization import plot_demand_distribution, plot_demand_map
    from run_AAST import initialize_nodes

    config_run = config_run[config]

    nodes = initialize_nodes(config_run)
    joblist = {}
    timestart = time.time()
    joblist = demand_synthesizer(config_demand,nodes,0)
    timeend = time.time()
    print(f"Time elapsed: {timeend-timestart}")
    if True:
        for i in range(5):
            print(i+1)
            joblist['joblist'].extend(demand_synthesizer(config_demand,nodes,i+1)['joblist'])
        analysis_demand_profiles(joblist['joblist'])
        plot_demand_distribution(joblist['joblist'],config_demand)
    else:
        plot_demand_map(joblist['joblist'], nodes, config_run)

    if False:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join('data',config_run['scenario'], f"joblist_{timestamp}.json")
        with open(filepath, 'w') as f:
            json.dump(joblist, f, indent=4)