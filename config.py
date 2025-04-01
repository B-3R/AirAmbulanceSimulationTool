#Configure the parameters in this file
#control iterations in vehicle and optimization in opt

config = 'Bavaria Single'

config_run = {
    'Test':{'scenario': 'Test', #Other: Paris, Germany, Bavaria, Test
            'Geography': 'DEU', #Other: FRA
            'starttime': 21000, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 7*24*3600,
            'chargerpower': {'pad': 200000, 'center': 200000, 'hub': 200000, 'base': 400000},
            'refuel': {'pad': False, 'center': False, 'hub': False, 'base': True},
            'timestep': 10,
            'save_data': False,
            'fleet_allocation': 'demand-based',
            'optimization_loops': 6,
            'vehicles':{'hybrid eVTOL':{'min':10,'max':10,'step': 1,'basesize':1}},#, {'type':'ambulance','min':10,'max':50}],
            'placement_opt': False,
            'animation': {'bool': True, 'framerate': 20, 'playbackspeed': 2000},
            'printnetwork': {'bool':True}},
    ############################################################################################################
    'Others Test':{'scenario': 'Italia', #FOR SINGLE RUN RESULTS ONLY
            'Geography': 'ITA', #Other: FRA
            'starttime': 0, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 1*24*3600,
            'chargerpower': {'pad': 0, 'center': 0, 'hub': 200000, 'base': 400000},
            'refuel': {'pad': False, 'center': False, 'hub': True, 'base': True}, #ATTENTION change for ambulance to all 
            'timestep': 10,
            'save_data': False,
            'runtype': 'single',
            'fleet_allocation': 'demand-based',
            'optimization_loops': 1,
            'vehicles':{'Hybrid eVTOL':{'min':25,'max':25,'step':10,'basesize':1}},#,'hybrid eVTOL':{'min':5,'max':5,'step':10,'basesize':1}},#'hybrid eVTOL':{'min':10,'max':10,'step':5,'basesize':1},
            'fleet': None, #to be recombined
            'animation': {'bool': True, 'framerate': 20, 'playbackspeed': 4000},
            'printnetwork': {'bool': True},
            'wages': {'pilot': 76, 'doctor': 69, 'paramedic': 35}},
    'Bavaria Single':{'scenario': 'Bavaria', #FOR SINGLE RUN RESULTS ONLY
            'Geography': 'DEU', #Other: FRA
            'starttime': 0, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 7*24*3600,
            'chargerpower': {'pad': 0, 'center': 0, 'hub': 200000, 'base': 400000},
            'refuel': {'pad': False, 'center': False, 'hub': True, 'base': True}, #ATTENTION change for ambulance to all 
            'timestep': 10,
            'save_data': False,
            'runtype': 'single',
            'fleet_allocation': 'demand-based',
            'optimization_loops': 6,
            'vehicles':{'Hybrid eVTOL':{'min':25,'max':25,'step':10,'basesize':1}},#,'hybrid eVTOL':{'min':5,'max':5,'step':10,'basesize':1}},#'hybrid eVTOL':{'min':10,'max':10,'step':5,'basesize':1},
            'fleet': None, #to be recombined
            'animation': {'bool': False, 'framerate': 20, 'playbackspeed': 4000},
            'printnetwork': {'bool': False},
            'wages': {'pilot': 76, 'doctor': 69, 'paramedic': 35}},
    'Bavaria Single Combined':{'scenario': 'Bavaria', #FOR SINGLE RUN RESULTS ONLY
            'Geography': 'DEU', #Other: FRA
            'starttime': 0, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 7*24*3600,
            'chargerpower': {'pad': 0, 'center': 0, 'hub': 200000, 'base': 400000},
            'refuel': {'pad': False, 'center': False, 'hub': True, 'base': True}, #ATTENTION change for ambulance to all 
            'timestep': 10,
            'save_data': False,
            'runtype': 'single',
            'fleet_allocation': 'demand-based',
            'optimization_loops': 6,
            'vehicles': {'Ambulance':0,'Hybrid eVTOL':0,'Helicopter':0},
            'fleet':[{'Ambulance':20,'Hybrid eVTOL': 10}],
            'animation': {'bool': True, 'framerate': 20, 'playbackspeed': 5000},
            'printnetwork': {'bool': False},
            'wages': {'pilot': 76, 'doctor': 69, 'paramedic': 35}},
    'Bavaria Trend':{'scenario': 'Bavaria', #Other: Paris, Germany, Bavaria, Test
            'Geography': 'DEU', #Other: FRA
            'starttime': 0, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 7*24*3600,
            'chargerpower': {'pad': 200000, 'center': 200000, 'hub': 200000, 'base': 400000},
            'refuel': {'pad': False, 'center': False, 'hub': True, 'base': True},
            'timestep': 10,
            'save_data': False,
            'runtype': 'trend',
            'fleet_allocation': 'demand-based',
            'optimization_loops': 6,
            'vehicles':{'Battery eVTOL':{'min':10,'max':40,'step':5,'basesize':1}},#'hybrid eVTOL':{'min':10,'max':10,'step':5,'basesize':1},
            'fleet': None, #to be recombined
            'animation': {'bool': False, 'framerate': 20, 'playbackspeed': 5000},
            'printnetwork': {'bool': False},
            'wages': {'pilot': 76, 'doctor': 69, 'paramedic': 35}},
    'Bavaria Trend Combined':{'scenario': 'Bavaria', #Other: Paris, Germany, Bavaria, Test
            'Geography': 'DEU', #Other: FRA
            'starttime': 0, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 7*24*3600,
            'chargerpower': {'pad': 0, 'center': 0, 'hub': 200000, 'base': 400000},
            'refuel': {'pad': False, 'center': False, 'hub': True, 'base': True},
            'timestep': 10,
            'save_data': False,
            'runtype': 'trend',
            'fleet_allocation': 'demand-based',
            'optimization_loops': 3,
            'vehicles':{'Ambulance':{'min':10,'max':40,'step':10,'basesize':1},'Hybrid eVTOL':{'min':5,'max':20,'step':5,'basesize':1}},
            'fleet': None, #to be recombined
            'animation': {'bool': False, 'framerate': 20, 'playbackspeed': 5000},
            'printnetwork': {'bool': False},
            'wages': {'pilot': 76, 'doctor': 69, 'paramedic': 35}},
    'Bavaria Analyse':{'scenario': 'Bavaria', #Other: Paris, Germany, Bavaria, Test
            'Geography': 'DEU', #Other: FRA
            'starttime': 0, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 7*24*3600,
            'chargerpower': {'pad': 0, 'center': 0, 'hub': 200000, 'base': 400000},
            'refuel': {'pad': False, 'center': False, 'hub': True, 'base': True},
            'timestep': 10,
            'save_data': False,
            'runtype': 'analyse',
            'fleet_allocation': 'demand-based',
            'optimization_loops': 6,
            'vehicles': {'Ambulance':0,'Hybrid eVTOL':0,'Battery eVTOL':0,'Helicopter':0},
            'fleet':[{'Ambulance': 50},{'Battery eVTOL': 20},{'Hybrid eVTOL': 25},{'Helicopter': 25},{'Ambulance':20,'Hybrid eVTOL': 10}],
            'animation': {'bool': False, 'framerate': 20, 'playbackspeed': 5000},
            'printnetwork': {'bool': False},
            'wages': {'pilot': 76, 'doctor': 69, 'paramedic': 35}},
    'Bavaria Analyse2':{'scenario': 'Bavaria', #Other: Paris, Germany, Bavaria, Test
            'Geography': 'DEU', #Other: FRA
            'starttime': 0, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 7*24*3600,
            'chargerpower': {'pad': 0, 'center': 0, 'hub': 200000, 'base': 400000},
            'refuel': {'pad': False, 'center': False, 'hub': True, 'base': True},
            'timestep': 10,
            'save_data': False,
            'runtype': 'analyse',
            'fleet_allocation': 'demand-based',
            'optimization_loops': 6,
            'vehicles': {'Ambulance':0,'Hybrid eVTOL':0,'Battery eVTOL':0,'Helicopter':0},
            'fleet':[{'Ambulance': 50},{'Hybrid eVTOL': 25},{'Ambulance':20,'Hybrid eVTOL': 10}],
            'animation': {'bool': False, 'framerate': 20, 'playbackspeed': 5000},
            'printnetwork': {'bool': False},
            'wages': {'pilot': 76, 'doctor': 69, 'paramedic': 35}},
    'Bavaria Analyse Combined':{'scenario': 'Bavaria', #Other: Paris, Germany, Bavaria, Test
            'Geography': 'DEU', #Other: FRA
            'starttime': 0, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 7*24*3600,
            'chargerpower': {'pad': 0, 'center': 0, 'hub': 200000, 'base': 400000},
            'refuel': {'pad': False, 'center': False, 'hub': True, 'base': True},
            'timestep': 10,
            'save_data': False,
            'runtype': 'analyse',
            'fleet_allocation': 'demand-based',
            'optimization_loops': 6,
            'vehicles': {'ambulance':0,'hybrid eVTOL':0,'helicopter':0},
            'fleet':[{'ambulance':40,'hybrid eVTOL': 10}],
            'animation': {'bool': False, 'framerate': 20, 'playbackspeed': 5000},
            'printnetwork': {'bool': False},
            'wages': {'pilot': 76, 'doctor': 69, 'paramedic': 35}},
    ############################################################################################################
    'Bavaria':{'scenario': 'Bavaria', #Other: Paris, Germany, Bavaria, Test
            'Geography': 'DEU', #Other: FRA
            'starttime': 0, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 7*24*3600,
            'timestep': 10,
            'save_data': False,
            'fleet_allocation': 'random',
            'optimization_loops': 1,
            'vehicles':{'hybrid eVTOL':{'min':10,'max':30,'step':10}},#, {'type':'ambulance','min':10,'max':50}],
            'placement_opt': False,
            'animation': {'bool': True, 'framerate': 20, 'playbackspeed': 5000},
            'printnetwork': {'bool': False}},
    'Germany':{'scenario': 'Germany', #Other: Paris, Germany, Bavaria, Test
            'Geography': 'DEU', #Other: FRA
            'starttime': 0, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 7*24*3600,
            'timestep': 10,
            'vehicle': 'battery eVTOL',
            'animation': {'bool': True, 'framerate': 20, 'playbackspeed': 60000},
            'printnetwork': {'bool': True}},
    'Paris':{'scenario': 'Paris', #Other: Paris, Germany, Bavaria, Test
            'Geography': 'FRA', #Other: FRA
            'starttime': 21600, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 3600,
            'timestep': 10,
            'vehicle': 'battery eVTOL',
            'animation': {'bool': True, 'framerate': 20, 'playbackspeed': 400},
            'printnetwork': {'bool': True}},
    'France':{'scenario': 'France', #Other: Paris, Germany, Bavaria, Test
            'Geography': 'FRA', #Other: FRA
            'starttime': 21600, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 3600,
            'timestep': 10,
            'vehicle': 'battery eVTOL',
            'animation': {'bool': False, 'framerate': 20, 'playbackspeed': 400},
            'printnetwork': {'bool': True}},
    'Italia':{'scenario': 'Italia', #Other: Paris, Germany, Bavaria, Test  
            'Geography': 'ITA', #Other: FRA
            'starttime': 21600, #Start time in seconds, eg 21600 for monday 06:00
            'duration': 3600,
            'timestep': 10,
            'vehicle': 'battery eVTOL',
            'animation': {'bool': False, 'framerate': 20, 'playbackspeed': 400},
            'printnetwork': {'bool': True}}
}

config_demand = {'input': 'new',
                    #'input': 'data\\joblist_test.json',
                'type': 'realistic',
                'starttime': 0, #Start time in seconds, DEFAULT 0 = Monday Morning
                'total_demand': 660, #660 is bavarian demand
                'timeframe': 7*24*3600,
                'loadingtime': {'mean': 45*60, 'std': 15*60, 'min': 15*60},
                'min distance': 5000, #meters
                'mean distance': 60000, #meters
                'std distance': 30000, #meters
                'routetypes': {
                    'upwards': 0.45,
                    'downwards': 0.35,
                    'centers': 0.15,
                    'local': 0.05
                    },
                'weekdays': {
                    0: 0.16,
                    1: 0.16,
                    2: 0.16,
                    3: 0.16,
                    4: 0.16,
                    5: 0.10,
                    6: 0.10
                    },
                'hourly': {
                    'weekday': {0: 0.014,
                        1: 0.011,
                        2: 0.010,
                        3: 0.008,
                        4: 0.008,
                        5: 0.007,
                        6: 0.011,
                        7: 0.021,
                        8: 0.054,
                        9: 0.090,
                        10: 0.098,
                        11: 0.090,
                        12: 0.083,
                        13: 0.077,
                        14: 0.074,
                        15: 0.072,
                        16: 0.063,
                        17: 0.049,
                        18: 0.039,
                        19: 0.034,
                        20: 0.028,
                        21: 0.024,
                        22: 0.020,
                        23: 0.016},
                    'weekend': {0: 0.024,
                        1: 0.019,
                        2: 0.016,
                        3: 0.013,
                        4: 0.013,
                        5: 0.012,
                        6: 0.016,
                        7: 0.026,
                        8: 0.047,
                        9: 0.068,
                        10: 0.080,
                        11: 0.075,
                        12: 0.068,
                        13: 0.063,
                        14: 0.061,
                        15: 0.056,
                        16: 0.055,
                        17: 0.052,
                        18: 0.050,
                        19: 0.046,
                        20: 0.043,
                        21: 0.037,
                        22: 0.033,
                        23: 0.026}
                                    }
            }


config_vehicle = {
    'Battery eVTOL': {
        'size': True,
        'type': 'aircraft',

        # Sizing Parameters
        'payload': 600, #[kg]
        'f_hybrid': 0, #[-] Based on available energy mass fraction for either battery or fuel + gen
        'f_energy': 0.35, #[-] Energy Carrier Mass fraction
        'f_payload': 0.2, #[payload mass fraction]
        'lift_to_drag': 11, #[-]
        'fm': 0.85, #[-]
        'eta_prop': 0.8, #[-] propeller efficiency
        'eta_elec': 0.9, #[-] electric system efficiency
        'v_downwash': 37, #[m/s]
        'f_control': 1.1, #[-] factor for active control in hover flight
        'f_maneuver': 1.1, #[-] factor for additional power during maneuvers in cruise
        
        # Battery Parameters
        'E_bat_spec': 220, #[Wh/kg]
        'P_bat_spec': 2000, #[w/kg]
        'DoD': 0.8, #[-] depth of discharge
        'bat_cycle_life': 1000, #[-] battery equivalent cycles to 80% DoD
        'bat_cost': 1500, #[€/kWh]
        'bat_resale': 0.2, #[-] resale value
        'chargingpower': 400000, #[W] maximum admissable vehicle charging power

        # Generator Parameters
        'gen_type': 'VH-3-185', #[] Powerplant type for reference
        'm_gen_spec': 295/185000, #[kg/W]
        'f_fuel_tank': 0.05, #[-] fuel tank mass fraction of total fuel + tank mass
        'SFC_gen': 0.227, #[kg/kWh] specific fuel consumption


        # Performance Parameters
        'v_cruise': 70, #[m/s] average cruise speed

        # Operations
        'pilots': 1, #[-]
        'doctors': 1, #[-]
        'paramedics': 0, #[-]
        'states': {'OOS': {},
                   'IDLE': {},
                   'OCCUPIED':{
                        'waiting' : {'duration': 0, 'power': 0,'source': None},
                        'loading' : {'duration': 0, 'power': 0,'source': None},
                        'startup' : {'duration': 120, 'power': 0,'source': None}, # starting procedure including taxi
                        'takeoff': {'duration': 20, 'power': 'P_hover', 'source': 'battery'},
                        'transition1': {'duration': 20, 'power': 'P_hover', 'source': 'battery'},
                        'cruise': {'duration': 0, 'power': 'P_cruise', 'source': 'battery'},
                        'transition2': {'duration': 20, 'power': 'P_hover', 'source': 'battery'},
                        'landing': {'duration': 60, 'power': 'P_hover', 'source': 'battery'},
                        'unloading' : {'duration': 0, 'power': 0,'source': None},
                        'completion': {'duration': 120, 'power': 0,'source': None}}}, # shut down procedure including taxi

        # Cost
        'cost_factor': 1000, #[€/kg] to estimate component prices, below specified is cost as percentage of total cost
        'depreciation_period': 10, #[years]
        'interest_rate': 0.05, #[-]
        'insurance_rate': 0.015, #[-]
        'electricity': 0.4, #[€/kWh]
        'Jet-A': 2, #[€/l]

        # Maintenance
        'design_life': 12000, #[FH] aircraft design life
        'mro_effort': 1, #[h/FH] general maintenance effort per flight hour
        'mro_wage': 100, #[€/h] wage of MRO worker
        'mro_profit': 0.3, #[-] profit margin on wages and component replacement for MRO firm
        'maintenance': {'propellers': {'cycle': 2000, 'cost': 0.05},
                        'propulsion':{'cycle': 6000, 'cost': 0.2}, #motors, inverters,
                        'energy systems': {'cycle': 6000, 'cost': 0.1} #Wiring, low voltage systems, HV bus etc
                        },

    },
    'Hybrid eVTOL': {
        'size': True,
        'type': 'aircraft',

        # Sizing Parameters
        'payload': 600, #[kg]
        'f_hybrid': 0.6, #[-] Based on available energy mass fraction for either battery or fuel + gen
        'f_energy': 0.35, #[-] Energy Carrier Mass fraction
        'f_payload': 0.2, #[payload mass fraction]
        'lift_to_drag': 11, #[-]
        'fm': 0.85, #[-]
        'eta_prop': 0.8, #[-] propeller efficiency
        'eta_elec': 0.9, #[-] electric system efficiency
        'v_downwash': 37, #[m/s] certification requirement
        'f_control': 1.1, #[-] factor for active control in hover flight
        'f_maneuver': 1.1, #[-] factor for additional power during maneuvers in cruise
        
        # Battery Parameters
        'E_bat_spec': 220, #[Wh/kg]
        'P_bat_spec': 2000, #[w/kg]
        'DoD': 0.8, #[-] depth of discharge
        'bat_cycle_life': 1000, #[-] battery equivalent cycles to 80% DoD
        'bat_cost': 1500, #[€/kWh]
        'bat_resale': 0.2, #[-] resale value or due to refurbishment
        'chargingpower': 400000, #[W] maximum admissable vehicle charging power

        # Generator Parameters
        'gen_type': 'VH-3-185', #[] Powerplant type for reference
        'm_gen_spec': 295/185000, #[kg/W]
        'f_fuel_tank': 0.05, #[-] fuel tank mass fraction of total fuel + tank mass
        'SFC_gen': 0.227, #[kg/kWh] specific fuel consumption


        # Performance Parameters
        'v_cruise': 70, #[m/s] average cruise speed

        # Operations
        'pilots': 0, #[-]
        'doctors': 1, #[-]
        'paramedics': 1, #[-]
        'states': {'OOS': {},
                   'IDLE': {},
                   'OCCUPIED':{
                        'waiting' : {'duration': 0, 'power': 0,'source': None},
                        'loading' : {'duration': 0, 'power': 0,'source': None},
                        'startup' : {'duration': 120, 'power': 0,'source': None}, # starting procedure including taxi
                        'takeoff': {'duration': 20, 'power': 'P_hover', 'source': 'battery'},
                        'transition1': {'duration': 20, 'power': 'P_hover', 'source': 'battery'},
                        'cruise': {'duration': 0, 'power': 'P_cruise', 'source': 'generator'},
                        'transition2': {'duration': 20, 'power': 'P_hover', 'source': 'battery'},
                        'landing': {'duration': 60, 'power': 'P_hover', 'source': 'battery'},
                        'unloading' : {'duration': 0, 'power': 0,'source': None},
                        'completion': {'duration': 120, 'power': 0,'source': None}}}, # shut down procedure including taxi

        # Cost
        'cost_factor': 1500, #[€/kg] to estimate component prices, below specified is cost as percentage of total cost
        'depreciation_period': 10, #[years]
        'interest_rate': 0.05, #[-]
        'insurance_rate': 0.015, #[-]
        'electricity': 0.4, #[€/kWh]
        'Jet-A': 2, #[€/l]

        # Maintenance
        'design_life': 12000, #[FH] aircraft design life
        'mro_effort': 1.5, #[h/FH] general maintenance effort per flight hour
        'mro_wage': 100, #[€/h] wage of MRO worker
        'mro_profit': 0.3, #[-] profit margin on wages and component replacement for MRO firm
        'maintenance': {'propellers': {'cycle': 2000, 'cost': 0.05},
                        'propulsion':{'cycle': 6000, 'cost': 0.2}, #motors, inverters,
                        'energy systems': {'cycle': 6000, 'cost': 0.1}, #Wiring, low voltage systems, HV bus etc
                        'generator': {'cycle': 3600, 'cost': 0.15} #generator
                        },

    },
    'Helicopter': {
        'size': False,
        'type': 'aircraft',
        'f_hybrid': 1, # only fuel
        'v_cruise': 70, #[m/s]
        'purchase_cost': 5700000, #[€]
        'depreciation_period': 20, #[years]
        'interest_rate': 0.05, #[-]
        'insurance_rate': 0.015, #[-]
        'Jet-A': 2, #[€/l]
        'electricity': 0, #[€/kWh]
        
        'P_hover': 605000, #[W] based on SFC, vCruise, fuel consumption
        'P_cruise': 623000, #[W] based on SFC, vCruise, fuel consumption
        'E_bat_usable': 0,
        'E_gen_usable': 1600*1000*3600, #[J]
        'E_tot_usable': 1600*1000*3600, #[J]
        'SFC_gen': 0.35, #[kg/kWh] specific fuel consumption

        #Only as reference
        'R_cruise_max': 647000, #[m]
        'm_fuel_max': 560, #[kg]
        'chargingpower': 1,
        'SFC_hover': 212, #[kg/FH] bei eta 0.4 und diesel heizwert 11.8 kWh/kg
        'SFC_cruise': 218, #[kg/FH] bei eta 0.4 und diesel heizwert 11.8 kWh/kg
        'fuel_consumption': 15, #[l/100km]

        'pilots': 0, #[-]
        'doctors': 1, #[-]
        'paramedics': 1, #[-]
        'states': {'OOS': {},
                   'IDLE': {},
                   'OCCUPIED':{
                        'waiting' : {'duration': 0, 'power': 0,'source': None},
                        'loading' : {'duration': 0, 'power': 0,'source': None},
                        'startup' : {'duration': 120, 'power': 0,'source': None}, # starting procedure including taxi
                        'takeoff': {'duration': 20, 'power': 'P_hover', 'source': 'generator'},
                        'transition1': {'duration': 20, 'power': 'P_hover', 'source': 'generator'},
                        'cruise': {'duration': 0, 'power': 'P_cruise', 'source': 'generator'},
                        'transition2': {'duration': 20, 'power': 0, 'source': 'generator'},
                        'landing': {'duration': 60, 'power': 'P_hover', 'source': 'generator'},
                        'unloading' : {'duration': 0, 'power': 0,'source': None},
                        'completion': {'duration': 120, 'power': 0,'source': None}}}, # shut down procedure including taxi
        
        # Maintenance
        'design_life': 20000, #[FH] aircraft design life
        'mro_effort': 3, #[h/FH] general maintenance effort per flight hour
        'mro_wage': 100, #[€/h] wage of MRO worker
        'mro_profit': 0.3, #[-] profit margin on wages and component replacement for MRO firm
        'maintenance': {'propellers': {'cycle': 2000, 'cost': 0.05},
                        'propulsion':{'cycle': 6000, 'cost': 0.2}, #motors, inverters,
                        'energy systems': {'cycle': 6000, 'cost': 0.1}, #Wiring, low voltage systems, HV bus etc
                        'generator': {'cycle': 3600, 'cost': 0.15} #generator
                        },

    },
    'Ambulance': { 
        'size': False,
        'type': 'road',
        'f_hybrid': 1, # only fuel
        'v_cruise': 18/1.3, #[m/s] 18 m/s is 65 km/h with detour factor
        'purchase_cost': 320000, #[€]
        'depreciation_period': 6, #[years]
        'interest_rate': 0.05, #[-]
        'insurance_rate': 0.015, #[-]
        'diesel': 1.6, #[€/l]
        'maintenance_cost': 0.5, #[€/km]
        
        'P_hover': 0, #[W]
        'P_cruise': 36600, #[W] based on energy, speed, fuel tank volume
        'E_bat_usable': 0,
        'E_gen_usable': 301*1000*3600, #[J]
        'E_tot_usable': 301*1000*3600, #[J]

        #Only as reference
        'R_cruise_max': 533000, #[m] 80l tank
        'chargingpower': 1,
        'SFC': 0.212, #[kg/kWh] bei eta 0.4 und diesel heizwert 11.8 kWh/kg
        'fuel_consumption': 15, #[l/100km]

        'pilots': 0, #[-]
        'doctors': 1, #[-]
        'paramedics': 1, #[-]
        'states': {'OOS': {},
                   'IDLE': {},
                   'OCCUPIED':{
                        'waiting' : {'duration': 0, 'power': 0,'source': None},
                        'loading' : {'duration': 0, 'power': 0,'source': None},
                        'startup' : {'duration': 120, 'power': 0,'source': None}, # starting procedure including taxi
                        'takeoff': {'duration': 0, 'power': 'P_hover', 'source': 'generator'},
                        'transition1': {'duration': 0, 'power': 'P_hover', 'source': 'generator'},
                        'cruise': {'duration': 0, 'power': 'P_cruise', 'source': 'generator'},
                        'transition2': {'duration': 0, 'power': 0, 'source': 'generator'},
                        'landing': {'duration': 0, 'power': 'P_hover', 'source': 'generator'},
                        'unloading' : {'duration': 0, 'power': 0,'source': None},
                        'completion': {'duration': 120, 'power': 0,'source': None}}}, # shut down procedure including taxi
    },
}