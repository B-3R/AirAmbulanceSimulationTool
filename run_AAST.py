# Air Ambulance Simulation Tool (AAST)
# Author: Benedikt Dreyer

from models.simulation import OpsModel
from models.vehicle import Vehicle
from models.node import Node
from config import config, config_demand, config_run, config_vehicle
from models.demand_synthesizer import demand_synthesizer
from utils.analysis import Distances, analysis_network_performance, print_network_performance, analysis_network_vehicles  #utilization, jobcost
from utils.sizing import sizing
import json
import os
import time
from datetime import datetime
from utils.visualization import plot_week_metric_distribution,PlotNetwork, plot_multiple_timing_pies,Replay, plot_network_performance_trend,plot_network_cost_bars,plot_network_performance_trend_line, plot_timing_pie, plot_2D,plot_network_performance_heatmap, plot_cost_pie, plot_cost_bar,histogram, plot_energy_level, plot_network_cost_trend
import random
import itertools
import statistics
import numpy as np
import math

def recombine_fleet(vehicles,config_run):
    if config_run['runtype'] in ['single','trend'] and config_run['fleet'] == None: #Recombine fleet as range of options
        ranges = {entry: range(vehicles[entry]['min'], vehicles[entry]['max'] + 1, vehicles[entry]['step']) for entry in vehicles.keys()}
        recombinations = [dict(zip(ranges.keys(), values)) for values in itertools.product(*ranges.values())]
        print(recombinations)
    elif config_run['runtype'] == 'analyse':
        recombinations = config_run['fleet']
        print(recombinations)
    elif config_run['runtype'] == 'single' and config_run['fleet'] != None:
        recombinations = config_run['fleet']
        print(recombinations)
    return recombinations

def initialize_nodes(config_run):
    ######### Create Nodes
    #go through list of nodes and initialize
    nodes = []

    locations = json.load(open(f'data\\{config_run['scenario']}\\hospitals.json', 'r'))

    filtered_pads = []
    bundeslaender = {'Germany': range(1,20),'Bavaria': [9], 'Test': [9]}
    num_total = 0
    num_lokal = 0
    num_regional = 0
    num_ueberregional = 0
     #Filter for Bavaria or Germany
    if config_run['Geography'] == 'DEU':
        id = 0
        for location in locations['hospitals']:
            if location['State'] in bundeslaender[config_run['scenario']]:
                num_total = num_total + 1
                if location['Class'] == 'lokal':
                    nodes.append(Node(id,location,'pad',config_run['chargerpower']['pad'],config_run['refuel']['pad']))
                    num_lokal = num_lokal + 1
                    id = id + 1
                elif location['Class'] == 'regional':
                    nodes.append(Node(id,location,'center',config_run['chargerpower']['center'],config_run['refuel']['center']))
                    num_regional = num_regional + 1
                    id = id + 1
                elif location['Class'] == 'ueberregional':
                    nodes.append(Node(id,location,'hub',config_run['chargerpower']['hub'],config_run['refuel']['hub']))
                    num_ueberregional = num_ueberregional + 1
                    id = id + 1
        pads = {'hospitals': filtered_pads}
        print(f"Total Nodes: {num_total}, Lokal: {num_lokal}, Regional: {num_regional}, Überregional: {num_ueberregional}")
    else:
        id = 0
        for location in locations['hospitals']:
            if 'EPSG3035_X' in location.keys():
                nodes.append(Node(id,location,'pad',config_run['chargerpower']['pad'],config_run['refuel']['pad']))
            id = id + 1

    return nodes

def initialize_demand(config_demand,nodes):
    # Fetch Demand File or generate new
    if config_demand['input'] == 'new':
        joblist = demand_synthesizer(config_demand,nodes)
    else:
        joblist = json.load(open(config_demand['input'], 'r'))
    return joblist['joblist']

def allocate_fleet(fleet,nodes,config_run):
    for node in nodes: #reset nodes before every simulation run
        node.relative_demand = 0 #TODO does not need to be re-calculated, does not change
        node.hangars = {}
        node.vehicles = []
        if node.type == 'base':
            node.type = 'hub'
    hub_nodes = [node for node in nodes if node.type == 'hub']


    if config_run['fleet_allocation'] == 'demand-based':
        yearly_demand = json.load(open(f'data\\{config_run['scenario']}\\yearly_demand.json', 'r'))
        for job in yearly_demand['joblist']:
            closest_distance = np.inf
            for node in hub_nodes:
                distance = np.sqrt((job['pickup'][0] - node.position[0])**2 + (job['pickup'][1] - node.position[1])**2)
                if distance < closest_distance:
                    closest_node = node
                    closest_distance = distance
            closest_node.relative_demand += 1
        
        for node1 in hub_nodes:
            for node2 in hub_nodes:
                if node1 != node2:
                    distance = np.sqrt((node1.position[0] - node2.position[0])**2 + (node1.position[1] - node2.position[1])**2)
                    if distance < 40000:
                        if node1.relative_demand > node2.relative_demand:
                            node1.relative_demand = node2.relative_demand + node1.relative_demand
                            node2.relative_demand = 0
                        else:
                            node2.relative_demand = node1.relative_demand + node2.relative_demand
                            node1.relative_demand = 0

        for node in hub_nodes:
            node.relative_demand = node.relative_demand / len(yearly_demand['joblist'])
        sorted_nodes = sorted(hub_nodes, key=lambda obj: obj.relative_demand, reverse=True)

        for vehicle_type in fleet.keys():
            bases = []
            print(f"Allocating {fleet[vehicle_type]} {vehicle_type} vehicles to bases")
            num_vehicles = fleet[vehicle_type]
            for node in sorted_nodes:
                #print(f'Number of vehicles left: {num_vehicles}')
                base_vehicles = round(node.relative_demand * fleet[vehicle_type])
                if base_vehicles == 0: base_vehicles = 1
                #print(f"Base {node.id} gets {base_vehicles} {vehicle_type} vehicles")
                num_vehicles = num_vehicles - base_vehicles
                bases.append(node)
                node.hangars.update({vehicle_type: base_vehicles})
                node.type = 'base'
                node.chargerpower = config_run['chargerpower']['base']
                node.refuel = config_run['refuel']['base']
                if num_vehicles < 1:
                    break 
        
        if config_run['runtype'] == 'single':
            for node in hub_nodes:
                if node.type == 'base':
                    print(f"Node {node.id} has {node.hangars} vehicles")

        return
    
        for node in bases:
            print(f"Node {node.id} has {node.hangars} vehicles")
    
    elif config_run['fleet_allocation'] == 'random':
        for vehicle_type in fleet.keys():
            print(f"Allocating {fleet[vehicle_type]} {vehicle_type} vehicles to bases")
            for vehicle in range(1,fleet[vehicle_type]+1):
                selected_node = random.choice(hub_nodes)
                selected_node.hangars.update({vehicle_type: selected_node.hangars.get(vehicle_type, 0) + 1})
                selected_node.type = 'base'
                selected_node.chargerpower = config_run['chargerpower']['base']
                selected_node.refuel = config_run['refuel']['base']
    
        for node in nodes:
            if node.type == 'base':
                print(f"Node {node.id} has {node.hangars} vehicles")

    elif config_run['fleet_allocation'] == 'pre-set': #TODO for detailled analysis
        locations = json.load(open(f'data\\{config_run['scenario']}\\allocation.json', 'r'))

    return

def initialize_vehicles(nodes,vehicledata):
    base_nodes = [node for node in nodes if node.type == 'base']
    vehicles = []
    id = 0
    for node in base_nodes:
        for vehicle_type in node.hangars.keys():
            if vehicle_type in vehicledata.keys(): current_vehicledata = vehicledata[vehicle_type]
            else: current_vehicledata = None
            counter = 0
            for vehicle in range(node.hangars[vehicle_type]):
                if counter < 1 and vehicle_type != 'ambulance':
                    hours = [[0,24*3600]]
                elif counter < 2 and vehicle_type == 'ambulance':
                    hours = [[0,24*3600]]
                else:
                    hours = [[8*3600,20*3600]]
                counter += 1
                vehicles.append(Vehicle(id,node.id,node.position,current_vehicledata,hours))
                node.vehicles.append(id)
                id = id + 1
    return vehicles

def run_AAST(AAST,config_run):

    for i in range(int(config_run['duration']/config_run['timestep'])):
        AAST.step()

    joblist = [] #compile new joblist after simulation
    for vehicle in AAST.vehicles:
        for job in vehicle.joblist:
            joblist.append(job)
    for job in AAST.unassigned_jobs:
        joblist.append(job)
        
    results = {'config_run': config_run,
               "nodes": [node.__dict__ for node in AAST.nodes],
               "vehicles": [vehicle.__dict__ for vehicle in AAST.vehicles],
               "joblist": joblist,
               "vehicle_log": AAST.vehicle_log}
    return results

def analyse_trend_AAST(results):


    
    #metrics = ['Median Pickup Wait','Median Job to Completion Time','Utilization','Network Coverage','Average Cost per MISSION']
    metrics = ['Pickup Waiting Time','Vehicle Utilization','Demand Coverage','Cost per Patient-Kilometer']
    units = ['min','%','%','€/km']
    units_dict = dict(zip(metrics, units))
    
    if len(config_run['vehicles']) == 1:
        resultsforcomparison = ' '
        for result in results:
            resultsforcomparison += f'[\'{next(iter(result['fleet'].values()))}\',{result['analysis']['Pickup Waiting Time']},{result['analysis']['Cost per Patient-Kilometer']}],' 
        print(resultsforcomparison)
        #2D plot of network performance
        plot_network_performance_trend(results,metrics,units_dict)
        plot_network_performance_trend_line(results,metrics,units_dict)

    if len(config_run['vehicles']) == 2:
        resultsforcomparison = ' '
        for result in results:
            fleet_values = list(result['fleet'].values())
            first = fleet_values[0]
            second = fleet_values[1]
            resultsforcomparison += f'[\'{first}&{second}\',{result['analysis']['Pickup Waiting Time']},{result['analysis']['Cost per Patient-Kilometer']}],' 
        print(resultsforcomparison)
        #Heatmaps for each metric
        for i, metric in enumerate(metrics):
            plot_network_performance_heatmap(results, metric, units[i],i)

    return results

def analyse_individual_AAST(results):

    #Analysis of individual network - just multiple runs
    results[0] = analysis_network_performance(results[0])
    results[0] = analysis_network_vehicles(results[0])

    metrics = ['Pickup Waiting Time','Vehicle Utilization','Demand Coverage','Cost per Mission','Cost per Patient-Kilometer','Cost per Leg','Patient-Kilometers','Staff','Bases','Total Cost of Operation per Year','Total Cost of Operation per Week','Flight Hours','Total extra charging time','Extra charging time per Mission']

    print()
    for metric in metrics:
        metric_values = []
        for result in results:
            metric_values.append(round(float(result['analysis'][metric]),2))
        print(f"Results for {metric}: {metric_values}")
        if len(metric_values) > 1:
            print(f"Mean {metric}: {statistics.mean(metric_values)}")
            print(f"Median {metric}: {statistics.median(metric_values)}")
            print(f"Standard Deviation {metric}: {statistics.stdev(metric_values)}")
        print()

    table_metrics = ['Bases',
                     'Staff',
                     'Vehicle Utilization',
                     'Demand Coverage',
                     'Patients_Transported',
                     'Patients_Unassigned',
                     'Number Total Legs',
                     'Total Cost of Operation per Week',
                     'Cost per Patient-Kilometer',
                     'Cost per Mission',
                     'Cost per Leg',
                     'Pickup Waiting Time',
                     'Transporttime enroute per km',
                     'Median Job to Completion Time',
                     'Median En-Route',
                     'Flight Hours',
                     'Patient-Kilometers',
                     'Total Kilometers',
                     'Average Transport Leg Distance',
                     'Average Leg Distance',
                     'Transports per vehicle per shift']
    
    print('TABLE -----------------------------------------------')
    for metric in table_metrics:
        metric_values = []
        for result in results:
            metric_values.append(round(float(result['analysis'][metric]),2))
        print(f"{metric}: {statistics.median(metric_values)}")
    print('TABLE END -----------------------------------------------')

    median_wait_time = results[0]['analysis']['Pickup Waiting Time']

    print(f'Total Staff {results[0]["analysis"]["Staff"]}')

    if False: # Only use if fleetsize is one type
        plot_week_metric_distribution(results[0]['joblist'], results[0]['config_run']['config_demand'])


        #print(f'Cost breakdown: {results[0]["analysis"]["Cost_Breakdown"]}')
        print_network_performance(results[0])  

        plot_cost_bar([results[0]["analysis"]["Cost_Breakdown"]], ['Test'], [len(results[0]["analysis"]['Total legs'])], 'Cost Breakdown per leg')

        #plot_waiting_distribution_week()

        #for first vehicle plot energy level

        plot_energy_level(results[0]['vehicle_log'],config_run,9)


        histogram([job['t_pickup_wait']/60 for job in results[0]['joblist'] if 't_pickup_wait' in job], 'Time [min]', 'Job Occurrences', 'Pickup Wait Time', 'pickup_wait_time.png',True,1.5)
        histogram([job['t_pickup_delay']/60 for job in results[0]['joblist']  if 't_pickup_delay' in job], 'Time [min]', 'Job Occurrences', 'Pickup Delay Time', 'pickup_delay_time.png',True,1.5)

        plot_timing_pie(results[0]['analysis']['Transport Leg Time Segments'],'Transport Leg Time Segments')

        plot_2D(results[0]['analysis']['Transport legs'],results[0]['analysis']['Transport legs variable cost'],'Transport legs variable cost','Transport Distance','Variable Cost')

        plot_cost_pie(results[0]['analysis']['Fixed Costs']['breakdown'],'Fixed Cost Breakdown')

        plot_cost_pie(results[0]['analysis']['Mission Cost Comparison'],'Leg Cost Comparison')

        config_run['animation']['bool'] and Replay(nodes,results[0]['vehicle_log'],config_run,0)

    return results

def analyse_multiple_AAST(results,fleet_combinations):
    #Have a number of plots where every selected network is side by side for more detailled analysis
    metrics = list(results[0]['analysis']['Cost_Breakdown_PKM'].keys())
    plot_network_cost_bars(results,metrics)

    plot_multiple_timing_pies(results,'Transport Leg Time Segments')


    if len(config_run['vehicles']) > 2:
        #Take mean of costs per fleet type

        for fleet in fleet_combinations:
            fleet_results = [result for result in results if result['fleet'] == fleet]
            cost_breakdown = [result["analysis"]["Cost_Breakdown"] for result in fleet_results]
            legs = [result["analysis"]['Total legs'] for result in fleet_results]
            labels = [f'{result["fleet"]}' for result in fleet_results]
        
        plot_cost_bar(cost_breakdown, labels, legs, 'Cost Breakdown per Leg')

        cost_breakdown = {}
        total_legs = {}
        labels = []
        cost_breakdown = [result["analysis"]["Cost_Breakdown"] for result in results]
        legs = [result["analysis"]['Total legs'] for result in results]
        labels = [f'{result["fleet"]}' for result in results]            
        plot_cost_bar(cost_breakdown, labels, legs, 'Cost Breakdown per Leg')
    return

def save_data(results):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join('data',config_run['scenario'], f"results_{timestamp}.json")
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":

    t = {}
    t['Total'] = [time.time()]
    t['Initialization'] = [time.time()]

    #GENERAL SETUP
    config_run = config_run[config] # select configuration
    config_run['config_demand'] = config_demand

    #SIZE VEHICLES IF NECESSARY
    vehicledata = {}
    for vehicle_type in config_run['vehicles'].keys():
        # Size vehicles if necessary
        if config_vehicle[vehicle_type]['size'] == True:
            vehicledata[vehicle_type] = sizing(config_vehicle[vehicle_type])
        else:
            vehicledata[vehicle_type] = config_vehicle[vehicle_type]

    #define fleet and nodes
    fleet_combinations = recombine_fleet(config_run['vehicles'],config_run)
    
    print(f"The simulation runs {int(config_run['duration']/config_run['timestep'])} steps")
    t['Initialization'].append(time.time())

    total_simulations = len(fleet_combinations) * config_run['optimization_loops']
    current_simulation = 0
    t_start = time.time()
    
    #LOOP, OPTIMIZATION and SIMULATION
    results = []
    for fleet in fleet_combinations:
        opt_loop = 0
        fleetresults = []
        
        while opt_loop < config_run['optimization_loops']:
            opt_loop = opt_loop + 1

            nodes = initialize_nodes(config_run)
            
            allocate_fleet(fleet,nodes,config_run)

            config_run['printnetwork']['bool'] and PlotNetwork(nodes,0,config_run) and print(Distances(nodes))

            joblist = demand_synthesizer(config_demand,nodes,opt_loop)['joblist']

            vehicles = initialize_vehicles(nodes,vehicledata)

            AAST = OpsModel(config_run,vehicles,nodes,joblist)

            run_results = run_AAST(AAST,config_run)
            run_results = analysis_network_performance(run_results)
            run_results = analysis_network_vehicles(run_results)
            run_results['fleet'] = fleet
            results.append(run_results)
            fleetresults.append(run_results)

            current_simulation += 1
            elapsed_time = time.time() - t_start

            avg_time_per_simulation = elapsed_time / current_simulation
            remaining_simulations = total_simulations - current_simulation
            expected_time_left = avg_time_per_simulation * remaining_simulations

            print(f"Simulation {current_simulation} of {total_simulations} completed - Average time per simulation: {avg_time_per_simulation:.2f}s")
            print(f"Elapsed time: {int(elapsed_time // 60)}:{int(elapsed_time % 60)} - Remaining: {int(expected_time_left // 60)}:{int(expected_time_left % 60)}")
            print('-------------------------------------------')
        analyse_individual_AAST(fleetresults)

    t['Total'].append(time.time())
    #ANALYSIS OF RESULTS
    len(results) == 1 and AAST.jumps > 0 and print(f"ERROR - {AAST.jumps} jumps detected")
    if config_run['runtype'] == 'single':
        analyse_individual_AAST(results)
    if config_run['runtype'] == 'trend':
        results = analyse_trend_AAST(results)
    if config_run['runtype'] == 'analyse':
        results = analyse_multiple_AAST(results,fleet_combinations)

    config_run['save_data'] and save_data(results)

    for key in t: print(f"{key} took {t[key][1]-t[key][0]:.6f} seconds")