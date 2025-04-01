def calc_leg_cost_variable(aircraft,hovertime,cruiserange): #Calculates the cost of a specific leg

    if aircraft['type'] == 'aircraft':

        flight_hours = (cruiserange / (aircraft['v_cruise']*3600)) + hovertime/3600

        # Energy Calculation (takeoff taken as reference for all hover segments)
        if aircraft['states']['OCCUPIED']['takeoff']['source'] == 'battery':
            E_hover_elec = aircraft['P_hover'] * hovertime
            E_hover_fuel = 0
        elif aircraft['states']['OCCUPIED']['takeoff']['source'] == 'generator':
            E_hover_elec = 0
            E_hover_fuel = aircraft['P_hover'] * hovertime
        else:
            print('ERROR - hover energy calculation failed')

        if aircraft['states']['OCCUPIED']['cruise']['source'] == 'battery':
            E_cruise_elec = aircraft['P_cruise'] * cruiserange / aircraft['v_cruise']
            E_cruise_fuel = 0
        elif aircraft['states']['OCCUPIED']['cruise']['source'] == 'generator':
            E_cruise_elec = 0
            E_cruise_fuel = aircraft['P_cruise'] * cruiserange / aircraft['v_cruise']
        else:
            print('ERROR - cruise energy calculation failed')

        E_electric = E_hover_elec + E_cruise_elec
        E_fuel = E_hover_fuel + E_cruise_fuel

        # Energy Cost
        electricity_cost = aircraft['electricity'] * E_electric / 3600000
        fuel_cost = (aircraft['Jet-A']/0.8) * (aircraft['SFC_gen']/3600000) * E_fuel
        energy_cost = fuel_cost + electricity_cost

        # General Maintenance cost
        total_cost = aircraft['purchase_cost']
        mro_components = 0

        for component in aircraft['maintenance']:
            if aircraft['maintenance'][component]['cycle'] != 'dl':
                aircraft['maintenance'][component].update({'component_cost': total_cost*aircraft['maintenance'][component]['cost']})
                mro_components = mro_components + (aircraft['maintenance'][component]['component_cost'] / aircraft['maintenance'][component]['cycle'])
                mro_components = mro_components - (aircraft['maintenance'][component]['component_cost'] / aircraft['design_life'])
        
        mro_components = flight_hours *  mro_components
        
        mro_effort = flight_hours *  aircraft['mro_wage'] * aircraft['mro_effort']

        # Battery replacement

        if aircraft['f_hybrid'] < 1:
            eq_full_cycle = E_electric / aircraft['E_bat_usable']

            battery_missions_life = aircraft['bat_cycle_life'] / eq_full_cycle

            bat_FH_life = battery_missions_life * flight_hours

            replacement_cost_bat = aircraft['bat_cost'] * (1-aircraft['bat_resale']) * aircraft['E_bat_total'] / 3600000

            mro_bat = flight_hours *((replacement_cost_bat / bat_FH_life) - (replacement_cost_bat / aircraft['design_life']))
        else:
            mro_bat = 0

        #Summing up
        mro_cost = (1+aircraft['mro_profit']) * (mro_effort + mro_components + mro_bat)
        variable_cost = mro_cost + energy_cost

        individual_cost_mission = {
        'electricity': round(electricity_cost,2),
        'fuel': round(fuel_cost,2),
        'battery': round(mro_bat,2),
        'mechanic': round(mro_effort,2),
        'components': round(mro_components,2)
        }

        individual_cost_FH = {
        'electricity': round(electricity_cost / flight_hours,2),
        'fuel': round(fuel_cost / flight_hours,2),
        'battery': round(mro_bat / flight_hours,2),
        'mechanic': round(mro_effort / flight_hours,2),
        'components': round(mro_components / flight_hours,2)
        }
    
    elif aircraft['type'] == 'road': # TODO add road vehicle cost calculation and integrate in overall calculation and generic model
        if hovertime > 0:
            print('ERROR in Cost Calc - road vehicles do not hover')
        flight_hours = (cruiserange / (aircraft['v_cruise']*3600)) + hovertime/3600

        v_fuel = aircraft['fuel_consumption'] * cruiserange / (1000*100) # per 100 km
        fuel_cost = aircraft['diesel'] * v_fuel
        energy_cost = fuel_cost
        #Summing up
        mro_cost = aircraft['maintenance_cost'] * cruiserange / (1000) # per km
        variable_cost = mro_cost + energy_cost
        individual_cost_FH = {}
        individual_cost_mission = {}

    cost = {
        'Variable Mission Cost': round(variable_cost,2),
        'Mission Energy Cost': round(energy_cost,2),
        'Mission MRO Cost': round(mro_cost,2),
        'breakdown_mission': individual_cost_mission,
        'Variable Flight Hour Cost': round(variable_cost / flight_hours,2),
        'Flight Hour Energy Cost': round(energy_cost / flight_hours,2),
        'Flight Hour MRO Cost': round(mro_cost / flight_hours,2),
        'breakdown_FH': individual_cost_FH
    }

    return cost

def calc_cost_fixed(result):
    #all fixed costs calculated per simulation timeframe

    year_percent = result['config_run']['duration'] / (365*24*3600)
    sim_days = result['config_run']['duration'] / (24*3600)

    # Crew cost
    pilot_hour_cost = result['config_run']['wages']['pilot']
    doctor_hour_cost = result['config_run']['wages']['doctor']
    paramedic_hour_cost = result['config_run']['wages']['paramedic']

    vehicles = result['vehicles']

    work_hours_pilot = 0
    work_hours_doctor = 0
    work_hours_paramedic = 0

    #TODO CHANGE FOR AMBULANCE

    for vehicle in vehicles:
        pilots = vehicle['vehicledata']['pilots']
        doctors = vehicle['vehicledata']['doctors']
        paramedics = vehicle['vehicledata']['paramedics']
        for shift in vehicle['hours']:
            work_hours_pilot += pilots*(shift[1]-shift[0])*sim_days/3600
            work_hours_doctor += doctors*(shift[1]-shift[0])*sim_days/3600
            work_hours_paramedic += paramedics*(shift[1]-shift[0])*sim_days/3600

    crew_cost = (work_hours_pilot * pilot_hour_cost) + (work_hours_doctor * doctor_hour_cost) + (work_hours_paramedic * paramedic_hour_cost)

    # Insurance Cost
    insurance_cost = 0
    
    for vehicle in result['vehicles']:
        insurance_cost += vehicle['vehicledata']['insurance_rate'] * vehicle['vehicledata']['purchase_cost'] * year_percent

    # Depreciation Cost
    depreciation_cost = 0
    for vehicle in result['vehicles']:
        depreciation_cost += (vehicle['vehicledata']['purchase_cost'] / vehicle['vehicledata']['depreciation_period'] )* year_percent

    # Financing Cost
    financing_cost = vehicle['vehicledata']['interest_rate'] * depreciation_cost

    # Infrastructure Cost
    infrastructure_cost = 0

    # Summing up
    fixed_cost = crew_cost + insurance_cost + depreciation_cost + financing_cost

    fixed_cost_breakdown = {    'Crew Cost': round(crew_cost,2),
    'Depreciation Cost': round(depreciation_cost,2),
    'Insurance Cost': round(insurance_cost,2),
    'Financing Cost': round(financing_cost,2),
    'Infrastructure Cost': round(infrastructure_cost,2)}

    cost = {
    'Fixed Network Cost': round(fixed_cost,2),
    'crew_workhours': work_hours_pilot + work_hours_doctor + work_hours_paramedic,
    'breakdown': fixed_cost_breakdown
    }

    return cost
    
if __name__ == '__main__':
    import sys
    import os

    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    sys.path.append(parent_dir) 

    from config import config_vehicle, config_run, config
    from utils.sizing import sizing
    from utils.visualization import plot_cost_pie

    #Take either general mission as input or overall values for the entire system
    #vehicledata = sizing(config_vehicle['hybrid eVTOL'])
    vehicledata = sizing(config_vehicle['battery eVTOL'])
    test_range = 80000
    test_hovertime = 240

    costs = calc_leg_cost_variable(vehicledata,test_hovertime,test_range)

    print(costs)
    plot_cost_pie(costs['breakdown_FH'],'Cost Structure Breakdown (per FH)')
    plot_cost_pie(costs['breakdown_mission'],'Cost Structure Breakdown (per mission)')