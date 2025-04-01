import pprint
def sizing(vehicle):

    if vehicle['type'] != 'aircraft':
        print('ERROR only eVTOL vehicles are supported')
        return

    # MTOM
    MTOM = vehicle['payload']/vehicle['f_payload']
    vehicle['MTOM'] = MTOM

    # Energy Carrier Masses
    m_bat = MTOM * vehicle['f_energy'] * (1-vehicle['f_hybrid'])
    m_hybrid = MTOM * vehicle['f_energy'] * vehicle['f_hybrid']
    vehicle['m_bat'] = m_bat
    vehicle['m_hybrid'] = m_hybrid

    vehicle['purchase_cost'] = vehicle['MTOM'] * vehicle['cost_factor']

    # Hover Power (actuator disk theory)
    P_hover = MTOM*9.81*vehicle['v_downwash']*vehicle['f_control']/(2*vehicle['fm']*vehicle['eta_elec']) # optimum from impulse, ohne 0.5 nich downwash sondern v induced
    vehicle['P_hover'] = P_hover

    # Cruise Power
    P_cruise = MTOM*9.81*vehicle['v_cruise']/(vehicle['lift_to_drag']*vehicle['eta_prop']*vehicle['eta_elec'])
    vehicle['P_cruise'] = P_cruise

    print(f'P_hover: {P_hover/1000} kW')
    print(f'P_cruise: {P_cruise/1000} kW')

    # Energy Storage Parameters
    E_bat_total = 3600*vehicle['E_bat_spec']*m_bat
    E_bat_usable = 3600*vehicle['E_bat_spec']*m_bat*vehicle['DoD']
    P_bat_usable = m_bat*vehicle['P_bat_spec']

    print(f'E_bat_usable: {E_bat_usable/(3600*1000)} kWh')

    vehicle['E_bat_total'] = E_bat_total
    vehicle['E_bat_usable'] = E_bat_usable
    vehicle['P_bat_usable'] = P_bat_usable

    if vehicle['f_hybrid'] > 0:
        P_gen = vehicle['f_maneuver'] * P_cruise
        m_gen = vehicle['m_gen_spec'] * P_gen
        m_fuelandtank = m_hybrid - m_gen
        m_fueltank = m_fuelandtank * vehicle['f_fuel_tank']
        m_fuel = m_fuelandtank - m_fueltank
        E_gen_usable = 1000 * 3600 * m_fuel / vehicle['SFC_gen']
    else:
        P_gen = 0 
        m_gen = 0
        m_fueltank = 0
        m_fuel = 0
        E_gen_usable = 0

    vehicle['P_gen'] = P_gen
    vehicle['m_gen'] = m_gen
    vehicle['m_fueltank'] = m_fueltank
    vehicle['m_fuel'] = m_fuel
    vehicle['E_gen_usable'] = E_gen_usable

    print(f'E_gen_usable: {E_gen_usable/(3600*1000)} kWh')

    E_tot_usable = E_bat_usable + E_gen_usable
    P_tot_usable = P_bat_usable + P_gen

    vehicle['E_tot_usable'] = E_tot_usable
    vehicle['P_tot_usable'] = P_tot_usable

    # Check Hover Power available (hover and transition always performed only by batteries)
    P_bat_usable >= P_hover and print('battery HOVER power SUFFICIENT')
    P_bat_usable < P_hover and print('ERROR - battery HOVER power ***NOT SUFFICIENT***')

    # Check Cruise Power available (if hover available, cruise only on hover)
    vehicle['f_hybrid'] > 0 and P_gen >= P_cruise and print('hybrid CRUISE power SUFFICIENT')
    vehicle['f_hybrid'] > 0 and P_gen < P_cruise and print('ERROR - hybrid CRUISE power ***NOT SUFFICIENT***')
    vehicle['f_hybrid'] == 0 and P_bat_usable >= P_cruise and print('battery CRUISE power SUFFICIENT')
    vehicle['f_hybrid'] == 0 and P_bat_usable < P_cruise and print('ERROR - battery CRUISE power ***NOT SUFFICIENT***')

    # Calculate Ranges and Endurance
    t_hover_max = E_bat_usable/P_hover # based only on battery energy
    t_hover_min = vehicle['states']['OCCUPIED']['takeoff']['duration'] + vehicle['states']['OCCUPIED']['transition1']['duration'] + vehicle['states']['OCCUPIED']['transition2']['duration'] + vehicle['states']['OCCUPIED']['landing']['duration']
    vehicle['t_hover_max'] = t_hover_max
    vehicle['t_hover_min'] = t_hover_min

    if vehicle['f_hybrid'] > 0: t_endurance_max = E_gen_usable/P_cruise
    else: t_endurance_max = (E_tot_usable-t_hover_min*P_hover)/P_cruise
    vehicle['t_endurance_max'] = t_endurance_max
    
    R_cruise_max = t_endurance_max * vehicle['v_cruise']
    vehicle['R_cruise_max'] = R_cruise_max

    print(f'R_cruise_max: {R_cruise_max/1000} km')
        
    return vehicle


if __name__ == '__main__':
    import sys
    import os

    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(parent_dir) 

    from config import config_vehicle, config_run, config

    vehicle = config_vehicle[list(config_run[config]['vehicles'].keys())[0]]

    pprint.pprint(sizing(vehicle))

    '''
    for i in range(3,9,1):
        vehicle['f_hybrid'] = i/10
        print(sizing(vehicle)['R_cruise_max'])
    '''