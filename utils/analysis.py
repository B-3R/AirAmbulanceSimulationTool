import numpy as np
from utils.visualization import histogram
from utils.cost import calc_leg_cost_variable, calc_cost_fixed
import statistics


def analysis_network_performance(result):
    analysis= {}
    
    joblist = result['joblist']

    transport_distances = []
    transport_variable_cost = []
    first_distances = []
    first_variable_cost = []
    return_distances = []
    return_variable_cost = []

    c_energy = []
    c_mro = []
    c_crew = []
    c_insurance = []
    c_depreciation = []
    c_financing = []

    unassigned_distances = []
    scheduled_distances = []
    timing_transports = {}

    loadingtimes = []
    unloadingtimes = []
    load_chargingtimes = []
    unload_chargingtimes = []
    first_chargingtimes = []

    for job in joblist:
        if 'success' in job and job['success'] == 'completed':

            vehicledata = result['vehicles'][0]['vehicledata']

            for vehicle in result['vehicles']:
                if vehicle['id'] == job['pickupvehicle']:
                    vehicledata = vehicle['vehicledata']
                    

            for leg in job['legs']:
                if leg['type'] == 'first_leg':

                    first_distances.append(leg['distance'])
                    leg['variable cost'] = calc_leg_cost_variable(vehicledata,leg['hovertime'],leg['distance'])['Variable Mission Cost']
                    first_variable_cost.append(leg['variable cost'])

                elif leg['type'] == 'transport_leg':
                    transport_distances.append(leg['distance'])
                    for time,value in leg['task_timing'].items():
                        if time not in timing_transports:
                            timing_transports[time] = []
                        timing_transports[time].append(value)

                    leg['variable cost'] = calc_leg_cost_variable(vehicledata,leg['hovertime'],leg['distance'])['Variable Mission Cost']
                    transport_variable_cost.append(leg['variable cost'])

                elif leg['type'] == 'return_leg':
                    return_distances.append(leg['distance'])

                    leg['variable cost'] = calc_leg_cost_variable(vehicledata,leg['hovertime'],leg['distance'])['Variable Mission Cost']
                    return_variable_cost.append(leg['variable cost'])
                
                variable_cost = calc_leg_cost_variable(vehicledata,leg['hovertime'],leg['distance'])
                c_energy.append(variable_cost['Mission Energy Cost'])
                c_mro.append(variable_cost['Mission MRO Cost'])

            if 'actualpickup' in job:
                job['t_pickup_wait'] = job['actualpickup'] - job['triggertime']
                job['t_pickup_delay'] = job['actualpickup'] - job['pickuptime']
                job['t_transport'] = job['actualdelivery'] - job['actualpickup']
                job['t_job_to_completion'] = job['actualdelivery'] - job['triggertime']

            loadingtimes.append(job['loadingtime'])
            unloadingtimes.append(job['unloadingtime'])
            load_chargingtimes.append(job['load_chargingtime'])
            unload_chargingtimes.append(job['unload_chargingtime'])
            first_chargingtimes.append(job['first_chargingtime'])
            
        elif 'success' in job and job['success'] == 'not assigned':
            unassigned_distances.append(job['distance'])
        elif 'success' in job and job['success'] == 'scheduled':
            for leg in job['legs']:
                if leg['type'] == 'transport_leg':
                    scheduled_distances.append(leg['distance'])
        else:
            print(job['type'])
            print(job['status'])
            if 'success' not in job:
                print(job)
            else:
                print(job['success'])
        #else:
            #print(job) #returns the 'doing' jobs
    
    fixed_costs = calc_cost_fixed(result)
    analysis['Fixed Costs'] = fixed_costs

    crew_workhours = fixed_costs['crew_workhours']

    year_percent = result['config_run']['duration'] / (365*24*3600)
    analysis['Staff'] = (crew_workhours / year_percent)/(120*12) #120 12h shifts per crew member
    num_bases = len([node for node in result['nodes'] if node['type'] == 'base'])
    analysis['Bases'] = num_bases
    analysis['Patients_Transported'] = len(transport_distances)
    analysis['Patients_Unassigned'] = len(unassigned_distances)

    c_crew = fixed_costs['breakdown']['Crew Cost']
    c_insurance = fixed_costs['breakdown']['Insurance Cost']
    c_depreciation = fixed_costs['breakdown']['Depreciation Cost']
    c_financing = fixed_costs['breakdown']['Financing Cost']

    analysis['Total legs'] = transport_distances + first_distances + return_distances
    analysis['First legs'] = first_distances
    analysis['Transport legs'] = transport_distances
    analysis['Return legs'] = return_distances
    analysis['Unassigned jobs'] = unassigned_distances
    analysis['Scheduled Transport jobs'] = scheduled_distances #other first and return legs can also be scheduled but are not included here

    analysis['Number Total Legs'] = len(analysis['Total legs'])
    analysis['Total Kilometers'] = sum(analysis['Total legs'])/1000

    transport_legs = len(analysis['Transport legs'])
    patient_km = sum(analysis['Transport legs'])/1000
    analysis['Patient-Kilometers'] = patient_km

    analysis['Cost_Breakdown'] = {'Crew': round(c_crew),'MRO': round(sum(c_mro)), 'Depreciation': round(c_depreciation),'Energy': round(sum(c_energy)),  'Insurance': round(c_insurance),  'Financing': round(c_financing)}
    analysis['Cost_Breakdown_Mission'] = {'Crew': round(c_crew/transport_legs),'MRO': round(sum(c_mro)/transport_legs), 'Depreciation': round(c_depreciation/transport_legs),'Energy': round(sum(c_energy)/transport_legs),  'Insurance': round(c_insurance/transport_legs),  'Financing': round(c_financing/transport_legs)}
    analysis['Cost_Breakdown_PKM'] = {'Crew': c_crew/patient_km,'MRO': sum(c_mro)/patient_km, 'Depreciation': c_depreciation/patient_km,'Energy': sum(c_energy)/patient_km,  'Insurance': c_insurance/patient_km,  'Financing': c_financing/patient_km}

    analysis['First legs variable cost'] = first_variable_cost
    analysis['Return legs variable cost'] = return_variable_cost
    analysis['Transport legs variable cost'] = transport_variable_cost

    analysis['Mission Cost Comparison'] = {'First Legs': round(sum(first_variable_cost)), 'Transport Legs': round(sum(transport_variable_cost)), 'Return Legs': round(sum(return_variable_cost)), 'Fixed Costs': round(analysis['Fixed Costs']['Fixed Network Cost'])}
    analysis['Total Variable Cost'] = sum(transport_variable_cost)+ sum(first_variable_cost) + sum(return_variable_cost)

    analysis['Total Cost of Operation per Week'] = (analysis['Total Variable Cost'] + analysis['Fixed Costs']['Fixed Network Cost'])
    analysis['Total Cost of Operation per Year'] = analysis['Total Cost of Operation per Week'] * 52
    analysis['Cost per Mission'] = analysis['Total Cost of Operation per Week'] / len(analysis['Transport legs'])
    analysis['Cost per Patient-Kilometer'] = round(analysis['Total Cost of Operation per Week'] / (patient_km),2)
    analysis['Cost per Leg'] = analysis['Total Cost of Operation per Week'] / len(analysis['Total legs'])
    
    analysis['Transport Leg Time Segments'] = timing_transports

    analysis['Demand Coverage'] = round(len(analysis['Transport legs']) / (len(analysis['Scheduled Transport jobs']) + len(analysis['Transport legs']) + len(analysis['Unassigned jobs'])),2)
    print(f'Total Legs: {len(analysis['Total legs'])}')
    print(f'Transport Legs: {len(analysis['Transport legs'])}')
    print(f'Total Jobs: {len(analysis['Scheduled Transport jobs']) + len(analysis['Transport legs']) + len(analysis['Unassigned jobs'])}')
    print(f'Demand Coverage: {analysis["Demand Coverage"]*100}%')

    analysis['Pickup Waiting Time'] = round(statistics.median([job['t_pickup_wait'] for job in joblist if 't_pickup_wait' in job])/60,2)
    analysis['Mean Pickup Wait'] = round(statistics.mean([job['t_pickup_wait'] for job in joblist if 't_pickup_wait' in job]))
    analysis['Median Transport Time'] = round(statistics.median([job['t_transport'] for job in joblist if 't_transport' in job]))
    analysis['Median Job to Completion Time'] = round(statistics.median([job['t_job_to_completion'] for job in joblist if 't_job_to_completion' in job])/60,2)

    analysis['Average Transport Leg Distance'] = round(statistics.mean(analysis['Transport legs'])/1000,2)
    analysis['Average Leg Distance'] = round(statistics.mean(analysis['Total legs'])/1000,2)

    result['joblist'] = joblist
    result['analysis'] = analysis
    return result

def print_network_performance(result):

    joblist = result['joblist']

    analysis_labels = ['Total legs','First legs','Transport legs','Return legs','Unassigned jobs','Scheduled Transport jobs']
    analysis_items = [result['analysis']['Total legs'],
                      result['analysis']['First legs'],
                      result['analysis']['Transport legs'],
                        result['analysis']['Return legs'],
                        result['analysis']['Unassigned jobs'],
                        result['analysis']['Scheduled Transport jobs']]

    for key,value in zip(analysis_labels,analysis_items):
        if value != [] and len(value) > 1:
            print(f"{key} count: {len(value):20}")
            print(f"{key} distance max: {round(max(value)/1000,2):20} km")
            print(f"{key} distance min: {round(min(value)/1000,2):20} km")
            print(f"{key} distance mean: {round(statistics.mean(value)/1000,2):20} km")
            print(f"{key} distance median: {round(statistics.median(value)/1000,2):20} km")
            print(f"{key} distance sum: {round(sum(value)/1000):20} km")
            print('\n')

def analysis_network_vehicles(result):

    utilization_list = []
    occupied_list = []
    idle_list = []
    oos_list = []
    airtime = []
    transporttime_nroute = []
    extra_chargingtime = []
    total_ops_time = 0

    for vehicle in result['vehicles']:
        vehicle_idle = 0
        vehicle_occupied = 0
        vehicle_oos = 0
        time_counter = 0
        for _ in vehicle['log_state']:
            time_counter += 1
            if _ == 'IDLE':
                vehicle_idle += 1
                total_ops_time =  total_ops_time +  result['config_run']['timestep']
            elif _ == 'OCCUPIED':
                vehicle_occupied += 1
                total_ops_time =  total_ops_time +  result['config_run']['timestep']
            elif _ == 'OOS':
                vehicle_oos += 1
        occupied_list.append(vehicle_occupied/time_counter)
        idle_list.append(vehicle_idle/time_counter)
        oos_list.append(vehicle_oos/time_counter)
        utilization_list.append(vehicle_occupied / (vehicle_idle + vehicle_occupied))
        airtime.append(sum([_ for _ in vehicle['log_airtime']]))
        transporttime_nroute.append(sum([_ for _ in vehicle['log_transporttime_enroute']]))
        extra_chargingtime.append(sum([_ for _ in vehicle['log_chargingblocked']]))
        
    #print(utilization_list)

    result['analysis']['Transporttime enroute per km'] = round(sum(transporttime_nroute)*1000/(sum(result['analysis']['Transport legs'])),2)
    result['analysis']['Total extra charging time'] = round(sum(extra_chargingtime)/(60),2)
    result['analysis']['Extra charging time per Mission'] = round(sum(extra_chargingtime)/(60*len(result['analysis']['Transport legs'])),2)

    result['analysis']['Vehicle Utilization'] = round(statistics.mean(utilization_list),2)
    result['analysis']['Median En-Route'] = round(sum(airtime)/(60*len(result['analysis']['Transport legs'])),2)
    result['analysis']['Flight Hours'] = round(sum(airtime)/3600,2)
    result['analysis']['Transports per vehicle per shift'] = round(len(result['analysis']['Transport legs']) / (total_ops_time/(12*3600)),2)

    return result

def analysis_demand_profiles(joblist): #Analysis of demand before simulation, for FIT CHECK
    distances = []
    routetype = []
    transfer_times = []
    hospital_demand = {}
    for job in joblist:
        distances.append(job['distance']/1000)
        routetype.append(job['routetype'])
        transfer_times.append(job['loadingtime']/60)
        transfer_times.append(job['unloadingtime']/60)
        if f'{job['pickup'][0]}.{job['pickup'][1]}' not in hospital_demand:
            hospital_demand[f'{job['pickup'][0]}.{job['pickup'][1]}'] = 1
        else:
            hospital_demand[f'{job['pickup'][0]}.{job['pickup'][1]}'] += 1
        if f'{job['target'][0]}.{job['target'][1]}' not in hospital_demand:
            hospital_demand[f'{job['target'][0]}.{job['target'][1]}'] = 1
        else:
            hospital_demand[f'{job['target'][0]}.{job['target'][1]}'] += 1
        #if f'{job['target'][0]}.{job['target'][1]}' not in hospital_demand:
            #hospital_demand[f'{job['target'][0]}.{job['target'][1]}'] = 1
        #else:
            #hospital_demand[f'{job['target'][0]}.{job['target'][1]}'] += 1

    hospital_visits = []
    for hospital in hospital_demand:
        hospital_visits.append(hospital_demand[hospital])
    print(f'Total Demand: {sum(hospital_visits)}')
    print(f'Average Visits per Hospital: {sum(hospital_visits)/len(hospital_visits)}')
    print(f'Maximum Visits per Hospital: {max(hospital_visits)}')
    print(f'Visited more than once per day: {len([_ for _ in hospital_visits if _ > 356])}')
    print(f'Visited more than twice per day: {len([_ for _ in hospital_visits if _ > 2*356])}')
    print(f'Visited more than once per week: {len([_ for _ in hospital_visits if _ > 52])}')

    upwards = []
    downwards = []
    centers = []
    local = []

    for key,distance in zip(routetype,distances):
        if key == 'upwards':
            upwards.append(distance)
        elif key == 'downwards':
            downwards.append(distance)
        elif key == 'centers':
            centers.append(distance)
        elif key == 'local':
            local.append(distance)
    labels = ['upwards','downwards','centers','local']
    distances_separat = [upwards, downwards, centers, local]
    print(f'Upward: {len(distances_separat[0])} Downward: {len(distances_separat[1])} Centers: {len(distances_separat[2])} Local: {len(distances_separat[3])}')


    histogram(transfer_times, 'Transfer Time [min]', 'Job Occurrences', 'Demand Profile (Transfer Times)', 'demand_profile_transfer_times.png',False,1.5)
    histogram(distances_separat, 'Distance [km]', 'Job Occurrences', 'Demand Profile (Distances)', 'demand_profile_distances.png',False,1.5,legend=labels)
    histogram(distances, 'Transport Distance [km]', 'Job Occurrences', 'Demand Profile (Transport Distances)', 'demand_profile.png',False,1.5)
    histogram(hospital_visits, 'Visit Frequency', 'Hospitals', 'Demand Profile (Hospital Visit Frequency)', 'demand_profile_hospital_visits.png',False,1.5)
    return

def DistanceEPSG3035(Pos1, Pos2):
    distance = np.sqrt((Pos1[0] - Pos2[0])**2 + (Pos1[1] - Pos2[1])**2)
    return distance

def Distances(nodes):
    distances = {'bases':[],'pads':[],'network':[]}
    checked = []
    for node in nodes:
        checked.append(node)
        for node2 in nodes:
            if node.type == 'base' and node2.type == 'base' and node2 not in checked:
                distances['bases'].append(DistanceEPSG3035(node.position,node2.position))
                distances['network'].append(DistanceEPSG3035(node.position,node2.position))
            elif node.type == 'pad' and node2.type == 'pad' and node2 not in checked:
                distances['pads'].append(DistanceEPSG3035(node.position,node2.position))
                distances['network'].append(DistanceEPSG3035(node.position,node2.position))
            elif node2 not in checked:
                distances['network'].append(DistanceEPSG3035(node.position,node2.position))

    result = {}
    for type in distances:
        if len(distances[type]) > 2:
            result[f"maximum {type} distance"] = int(max(distances[type]))
            result[f"minimum {type} distance"] = int(min(distances[type]))
            result[f"average {type} distance"] = int(sum(distances[type])/len(distances[type]))
            result[f'number of {type} routes'] = len(distances[type])
    return result