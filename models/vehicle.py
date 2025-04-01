import numpy as np
import pprint
import matplotlib.pyplot as plt

def plot_error_leg(leg_origin, leg_destination, current_position, incorrect_position, cruise_vector,job_origin, job_destination):
    """
    Plots the leg's origin, destination, correct movement path, 
    current vehicle position, and the incorrectly jumped position.
    Also visualizes the cruise vector.
    """
    # Compute total distance
    total_distance = ((leg_destination[0] - leg_origin[0])**2 + 
                      (leg_destination[1] - leg_origin[1])**2) ** 0.5

    # Scale cruise vector to match total distance
    scaled_cruise_vector = [cruise_vector[0] * total_distance, cruise_vector[1] * total_distance]

    # Create the figure
    plt.figure(figsize=(6, 6))

    # Plot the leg (expected path)
    plt.plot([leg_origin[0], leg_destination[0]], [leg_origin[1], leg_destination[1]], 'k--', label="Leg Path")
        # Plot the leg (expected path)
    plt.plot([job_origin[0], job_destination[0]], [job_origin[1], job_destination[1]], 'k-', label="Transport Path")

    # Plot the points
    plt.scatter(*leg_origin, color='blue', label="Leg Origin", zorder=3)
    plt.scatter(*leg_destination, color='green',marker = 'D', label="Leg Destination", zorder=3)
    plt.scatter(*current_position, color='red', label="Cruise Position", zorder=3)
    plt.scatter(*incorrect_position, color='orange', label="Jumped Position", zorder=3)

    # Plot cruise vector from current position
    plt.quiver(current_position[0], current_position[1], 
               scaled_cruise_vector[0], scaled_cruise_vector[1], 
               angles='xy', scale_units='xy', scale=1, color='purple', label="Cruise Vector")

    # Labels and legend
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Travel Distance Error - Unexpected Jump")
    plt.legend()
    plt.grid(True)
    plt.show()


class Vehicle:
    def __init__(self,id,home,position,vehicledata,hours):
        self.vehicledata = vehicledata
        self.speed = vehicledata['v_cruise']
        self.E_usable_bat = vehicledata['E_bat_usable']
        self.E_usable_gen = vehicledata['E_gen_usable']
        self.E_current_bat = self.E_usable_bat
        self.E_current_gen = self.E_usable_gen

        self.current_P_bat = 0
        self.current_P_gen = 0
        self.current_P = 0
        self.current_P_charge = 0#TODO change for home base charging
        self.current_refuel = True

        self.chargingpower = vehicledata['chargingpower']
        #self.capacity
        self.hours = hours
        self.homeID = home
        self.home = position #as base position

        self.log_state = []
        self.log_task = []
        self.log_airtime = []
        self.log_transporttime_enroute = []
        self.log_chargingblocked = []

        self.id = id
        #self.chargingpower #maximum charging power the vehicle can handle

        self.last_job_end_position = self.home #sets end position of current job
        self.last_job_end_positionID = self.homeID #sets end position of current job
        self.last_job_end_E_bat = self.E_usable_bat
        self.last_job_end_E_gen = self.E_usable_gen
        self.last_job_end_time = 0 #sets end position of last scheduled job

        self.position = self.home # in coordinates
        self.positionID = self.homeID # in ID, only refreshed for when on ground

        self.joblist = [] #list of jobs to be done
        self.job = []
        self.job_previous = []
        self.leg = []
        self.currentleg = 0

        self.task_time = 0 #time spent in current task
        #to iterate through mission states
        self.states = vehicledata['states']
        self.state = 'OOS' #sets current state as OOS, OCCUPIED or IDLE
        self.task = 'waiting' #sets tasks for occupied vehicles, default = waiting
        self.state_time = 0 #time spent in current task
        self.in_air = 0 #track times where it is in air
    
    def update(self,timestep,time,nodes):

        self.current_P = self.current_P_bat + self.current_P_gen

        #refresh energy level
        self.E_current_bat = self.E_current_bat - self.current_P_bat*timestep
        self.E_current_gen = self.E_current_gen - self.current_P_gen*timestep

        #recharge/fuel if available and not fully charged
        if self.E_current_bat < self.E_usable_bat:
            self.E_current_bat = self.E_current_bat + self.current_P_charge*timestep
        if self.current_refuel == True:
            self.E_current_gen = self.E_usable_gen
            
        if self.state == 'IDLE':
            
            #check if there is a new job
            for index, job in enumerate(self.joblist): #always use latest job?
                if job['status'] == 'waiting': #TODO change triggertime to pickup time for scheduled?
                    self.job = job
                    self.job['status'] = 'doing'
                    self.job['vehicle_job'] = index
                    self.currentleg = 0
                    self.leg = job['legs'][0]
                    self.task = 'waiting'
                    self.state = 'OCCUPIED'
                    self.job_previous = self.joblist[index-1]
                    break
            
            if self.state == 'IDLE': #wenn kein neuer job, aktualisiere letzte energie und co für scheduling
                self.last_job_end_E_bat = self.E_current_bat
                self.last_job_end_E_gen = self.E_current_gen
                self.last_job_end_position = self.position
                self.last_job_end_positionID = self.positionID
                self.last_job_end_time = time
            #if not home (and no new job booked)-> return home if sufficient energy TODO check that vehicles cannot get stuck
            distance_to_home = np.sqrt((self.position[0] - self.home[0])**2 + (self.position[1] - self.home[1])**2)
            if self.state == 'IDLE' and distance_to_home > 500:
                E_home_bat, E_home_gen = self.leg_energy(self.position,self.home)
                if self.E_current_bat >= E_home_bat and self.E_current_gen >= E_home_gen:
                    returnjob = {
                        'id': f'{self.position}.{self.home}.{time}',
                        'pickup': self.position,
                        'target': self.home,
                        'pickupID': self.positionID,
                        'targetID': self.homeID,
                        'triggertime': time,
                        'pickuptime': time,
                        'pickupvehicle': self.id,
                        'jobendtime': time + self.leg_time(self.position,self.home),
                        'loadingtime': 0,
                        'unloadingtime': 0,
                        'first_chargingtime': 0,
                        'load_chargingtime': 0,
                        'unload_chargingtime': 0,
                        'type': 'return mission',
                        'success': 'scheduled'
                    }
                    self.schedule(returnjob,nodes)

            #if no other charging and low energy and no return home, charge with generator
            if self.state == 'IDLE' and self.positionID != self.homeID and self.E_current_bat < self.E_usable_bat and self.E_current_gen > 0 and self.current_P_charge == 0:
                E_transfer = self.vehicledata['P_gen']*timestep
                self.E_current_bat = self.E_current_bat + E_transfer
                self.E_current_gen = self.E_current_gen - E_transfer
        
        elif self.state == 'OCCUPIED':

            if self.leg['type'] == 'transport_leg':
                self.log_transporttime_enroute.append(self.in_air*timestep)

            self.task_time = self.task_time + timestep

            if self.task == 'waiting' and self.task_time >= self.states[self.state][self.task]['duration'] and self.task_time <= self.leg['first_chargingtime']:
                self.log_chargingblocked.append(timestep)
            elif self.task == 'loading' and self.task_time >= self.leg['loadingtime'] and self.task_time <= self.job['load_chargingtime']:
                self.log_chargingblocked.append(timestep)
            elif self.task == 'unloading' and self.task_time >= self.leg['unloadingtime'] and self.task_time <= self.job['unload_chargingtime']:
                self.log_chargingblocked.append(timestep)


            if self.task == 'waiting' and self.task_time >= self.states[self.state][self.task]['duration'] and self.task_time >= self.leg['first_chargingtime']:
                self.leg['task_timing'][self.task] = self.task_time
                if self.leg['loadingtime'] > 0: #TODO CHECK IF JOB OR LEG
                    self.job['actualpickup'] = time
                    self.task = 'loading'
                else:
                    self.task = 'takeoff'
                    self.in_air = 1
                    if self.vehicledata['f_hybrid'] < 1:
                        self.current_P_bat = self.vehicledata['P_hover']
                        self.current_P_gen = 0
                    else:
                        self.current_P_gen = self.vehicledata['P_hover']
                        self.current_P_bat = 0
                    self.current_P_charge = 0
                    self.current_refuel = False
                self.task_time = 0

            if self.task == 'loading'and self.task_time >= self.states[self.state][self.task]['duration']:
                if self.task_time >= self.leg['loadingtime'] and self.task_time >= self.job['load_chargingtime']:
                    self.leg['task_timing'][self.task] = self.task_time
                    self.task = 'takeoff'
                    self.in_air = 1
                    if self.vehicledata['f_hybrid'] < 1:
                        self.current_P_bat = self.vehicledata['P_hover']
                        self.current_P_gen = 0
                    else:
                        self.current_P_gen = self.vehicledata['P_hover']
                        self.current_P_bat = 0
                    self.current_P_charge = 0
                    self.current_refuel = False
                    self.task_time = 0

            if self.task == 'takeoff'and self.task_time >= self.states[self.state][self.task]['duration']:
                traveldistance = np.sqrt((self.leg['origin'][0] - self.position[0])**2 + (self.leg['origin'][1] - self.position[1])**2)
                if traveldistance > 2000:
                    plot_error_leg(self.leg['origin'], self.leg['destination'], self.position, self.leg['destination'], self.leg['cruise_vector'],self.job['pickup'],self.job['target'])
                    print('ERROR - WRONG TAKEOFF LOCATION')
                    print(f'cruise start location {self.position}')
                self.leg['task_timing'][self.task] = self.task_time
                self.leg['hovertime'] += self.task_time
                self.task = 'transition1'
                if self.vehicledata['f_hybrid'] < 1:
                        self.current_P_bat = self.vehicledata['P_hover']
                        self.current_P_gen = 0
                else:
                    self.current_P_gen = self.vehicledata['P_hover']
                    self.current_P_bat = 0
                self.task_time = 0

            if self.task == 'transition1'and self.task_time >= self.states[self.state][self.task]['duration']:
                self.leg['task_timing'][self.task] = self.task_time
                self.leg['hovertime'] += self.task_time
                self.task = 'cruise'
                if self.vehicledata['f_hybrid'] == 0:
                    self.current_P_bat = self.vehicledata['P_cruise']
                    self.current_P_gen = 0
                else:
                    self.current_P_gen = self.vehicledata['P_cruise']
                    self.current_P_bat = 0
                self.task_time = 0
            
            if self.task == 'cruise'and self.task_time >= self.states[self.state][self.task]['duration']:
                #refresh location and exit cruise when close to location
                distance_to_destination = np.sqrt((self.leg['destination'][0] - self.position[0])**2 + (self.leg['destination'][1] - self.position[1])**2)
                total_distance = np.sqrt((self.leg['destination'][0] - self.leg['origin'][0])**2 + (self.leg['destination'][1] - self.leg['origin'][1])**2)
                traveldistance = np.sqrt((self.leg['origin'][0] - self.position[0])**2 + (self.leg['origin'][1] - self.position[1])**2)

                if distance_to_destination <= (self.speed*timestep): #snap to destination
                    self.position = self.leg['destination']
                    self.positionID = self.leg['destinationID']
                    self.leg['task_timing'][self.task] = self.task_time
                    self.task = 'transition2'
                    if self.vehicledata['f_hybrid'] < 1:
                        self.current_P_bat = self.vehicledata['P_hover']
                        self.current_P_gen = 0
                    else:
                        self.current_P_gen = self.vehicledata['P_hover']
                        self.current_P_bat = 0
                    self.task_time = 0
                elif traveldistance > (total_distance + (self.speed*timestep)):
                    print('ERROR travel distance too large')
                    #plot_error_leg(self.leg['origin'], self.leg['destination'], self.position, self.leg['destination'], self.leg['cruise_vector'],self.job['pickup'],self.job['target'])
                    self.position = self.leg['destination']
                    self.positionID = self.leg['destinationID']
                    self.leg['task_timing'][self.task] = self.task_time
                    self.task = 'transition2'
                    if self.vehicledata['f_hybrid'] < 1:
                        self.current_P_bat = self.vehicledata['P_hover']
                        self.current_P_gen = 0
                    else:
                        self.current_P_gen = self.vehicledata['P_hover']
                        self.current_P_bat = 0
                    self.task_time = 0
                else:
                    self.position = [self.position[0]+self.speed*timestep*self.leg['cruise_vector'][0],self.position[1]+self.speed*timestep*self.leg['cruise_vector'][1]]

                new_distance_destination = np.sqrt((self.leg['destination'][0] - self.position[0])**2 + (self.leg['destination'][1] - self.position[1])**2)

                if (distance_to_destination - new_distance_destination) > distance_to_destination:
                    print('error - wrong cruise vector')

            if self.task == 'transition2'and self.task_time >= self.states[self.state][self.task]['duration']:
                self.leg['task_timing'][self.task] = self.task_time
                self.leg['hovertime'] += self.task_time
                self.task = 'landing'
                if self.vehicledata['f_hybrid'] < 1:
                        self.current_P_bat = self.vehicledata['P_hover']
                        self.current_P_gen = 0
                else:
                    self.current_P_gen = self.vehicledata['P_hover']
                    self.current_P_bat = 0
                self.task_time = 0

            if self.task == 'landing'and self.task_time >= self.states[self.state][self.task]['duration']:
                self.leg['task_timing'][self.task] = self.task_time
                self.leg['hovertime'] += self.task_time

                for node in nodes:
                    if node.id == self.positionID:
                        self.current_P_charge = node.chargerpower
                        self.current_refuel = node.refuel
                        break
                if self.vehicledata['type'] == 'road':
                    self.current_refuel = True

                if self.leg['unloadingtime'] > 0:
                    self.task = 'unloading'
                    self.in_air = 0
                    self.current_P_bat = 0
                    self.current_P_gen = 0
                else:
                    self.task = 'completion'
                    self.in_air = 0
                    self.current_P_bat = 0
                    self.current_P_gen = 0
                self.task_time = 0
            
            if self.task == 'unloading'and self.task_time >= self.states[self.state][self.task]['duration']:
                if self.task_time >= self.leg['unloadingtime'] and self.task_time >= self.job['unload_chargingtime']:
                    self.leg['task_timing'][self.task] = self.task_time
                    self.task = 'completion'
                    self.job['actualdelivery'] = time
                    self.task_time = 0

            if self.task == 'completion'and self.task_time >= self.states[self.state][self.task]['duration']:
                self.leg['task_timing'][self.task] = self.task_time
                self.job['legs'][self.currentleg]['status'] = 'completed'
                newleg = 0
                for leg in self.job['legs']:
                    if leg['status'] != 'completed' and newleg == 0: #start new leg

                        newleg = 1
                        self.leg = leg
                        self.currentleg = self.currentleg + 1
                        
                    #only start new leg if sufficient energy, otherwise stay charging - default: clear pad as soon as possible
                if newleg == 0: #if no more legs to go, finish job
                    self.job['status'] = 'completed'
                    self.job['success'] = 'completed'
                    if np.sqrt((self.job['target'][0] - self.position[0])**2 + (self.job['target'][1] - self.position[1])**2):
                        print('ERROR - wrong completion location')
                    self.state = 'IDLE'
                    for index, job in enumerate(self.joblist):
                        if job['id'] == self.job['id']:
                            self.joblist[index] = self.job # update joblist with new job data
                
                self.task = 'waiting'
                self.task_time = 0

        #Go OOS if shift is over or IDLE if shift started and was OOS before
        inshift = False
        DAYINSECONDS = 24*3600
        for shift in self.hours:
                if time%DAYINSECONDS < max(shift) and time%DAYINSECONDS > min(shift):
                    inshift = True
                    
        if inshift == False and self.state == 'IDLE':            
            self.state = 'OOS'
        elif inshift == True and self.state == 'OOS':
            self.state = 'IDLE'

        self.log_state.append(self.state)
        self.log_task.append(self.task)
        self.log_airtime.append(self.in_air*timestep)


    def pickupcheck(self,pickup,target,triggertime,pickupID,targetID,nodes): #to check at what time vehicle could be able to pick up patient for scheduling

        # FIRST STEP --- CALC ENERGIES
        #refresh energy levels at end of mission

        load_chargingtime = 1
        unload_chargingtime  = 1
        first_chargingtime = 1
        possible = False

        distance_pickup_jobend = np.sqrt((pickup[0] - self.last_job_end_position[0])**2 + (pickup[1] - self.last_job_end_position[1])**2)
        if distance_pickup_jobend > 500:
            E_first_bat, E_first_gen = self.leg_energy(self.last_job_end_position,pickup)
        else:
            E_first_bat = 0
            E_first_gen = 0
        E_transport_bat, E_transport_gen = self.leg_energy(pickup,target)
        #E_alternate_first_leg = self.alt_energy(target) #calc energy required to continue to alternate
        #E_alternate_transport = self.alt_energy(target) #calc energy required at alternate

        E_home_bat, E_home_gen = self.leg_energy(target,self.home)
        option_target_bat, option_target_gen = self.chargingenergy(60,targetID,nodes)

        #if available, check if vehicle has to top up before starting for time t_prep

        while possible != True and first_chargingtime < 15*60:
            E_load_bat, E_load_gen = self.chargingenergy(load_chargingtime,pickupID,nodes)
            E_unload_bat, E_unload_gen = self.chargingenergy(unload_chargingtime,targetID,nodes)
            E_prep_bat, E_prep_gen = self.chargingenergy(first_chargingtime,self.last_job_end_positionID,nodes)

            #Energy after first leg landing
            E_after_first_bat = min(self.last_job_end_E_bat + E_prep_bat, self.E_usable_bat) - E_first_bat
            E_after_first_gen = min(self.last_job_end_E_gen + E_prep_gen, self.E_usable_gen) - E_first_gen
            #Energy after transport leg landing (incl. optional recharge before transport leg)
            E_after_transport_bat = min(E_after_first_bat + E_load_bat, self.E_usable_bat) - E_transport_bat
            E_after_transport_gen = min(E_after_first_gen + E_load_gen, self.E_usable_gen) - E_transport_gen
            #Energy at job end time incl. optional recharge after mission leg
            E_after_mission_bat = min(E_after_transport_bat + E_unload_bat, self.E_usable_bat)
            E_after_mission_gen = min(E_after_transport_gen + E_unload_gen, self.E_usable_gen)

            #First check if energy is always bigger than 0
            if E_after_first_bat >= 0 and E_after_first_gen >= 0 and E_after_transport_bat >= 0 and E_after_transport_gen >= 0: #First check if all legs are possible
                possible = 'Returntrue'
                #Then check if vehicle can return home
                if E_after_mission_bat >= E_home_bat and E_after_mission_gen >= E_home_gen: # get home directly possible
                    possible = True
                if option_target_bat > 0 and E_home_bat <= self.E_usable_bat and E_home_gen <= E_after_mission_gen: #charging available at target and option for single leg return journey with only recharge
                    possible = True
                if option_target_gen > 0 and E_home_gen <= self.E_usable_gen and E_home_bat <= E_after_mission_bat: #refuelling available at target and option for single leg return journey with only refuel
                    possible = True
                if option_target_bat > 0 and option_target_gen > 0 and E_home_gen <= self.E_usable_gen and E_home_bat <= self.E_usable_bat: #charging and refuelling available at target and option for single leg return journey with recharge and refuel
                    possible = True
                if (E_home_gen + E_home_bat) <= (E_after_mission_gen + E_after_mission_bat) and (E_after_mission_gen + E_home_bat) <= E_home_gen: #power transfer at target
                    possible = True
                #todo check and plan two leg return trip
            if possible != True and self.vehicledata['f_hybrid'] < 1:
                if load_chargingtime <= 15*60 and (E_after_first_bat + E_load_bat) < self.E_usable_bat and E_load_bat > 0: #TODO in text: up to 15 min is always expected to be possible
                     load_chargingtime = load_chargingtime + 60
                elif unload_chargingtime <= 15*60 and (E_after_transport_bat + E_unload_bat) < self.E_usable_bat and E_unload_bat > 0: #TODO in text: up to 15 min is always expected to be possible
                    unload_chargingtime = unload_chargingtime + 60
                elif self.last_job_end_E_bat < self.E_usable_bat  and E_prep_bat > 0: #start mission with full battery
                    first_chargingtime = first_chargingtime + 60
                elif (E_after_transport_bat + E_unload_bat) < self.E_usable_bat and E_unload_bat > 0:
                    unload_chargingtime = unload_chargingtime + 60
                elif (E_after_first_bat + E_load_bat) < self.E_usable_bat and E_load_bat > 0:
                    load_chargingtime = load_chargingtime + 60
                else: 
                    break
            if self.vehicledata['f_hybrid'] == 1:
                break
                    
        # THIRD STEP --- CALC PICKUPTIME
        if possible:
            #calculate remaining charging time after current mission ends
            distance_pickup_jobend = np.sqrt((pickup[0] - self.last_job_end_position[0])**2 + (pickup[1] - self.last_job_end_position[1])**2)
            if distance_pickup_jobend > 500:
                t_first_leg = self.leg_time(self.last_job_end_position,pickup)
            else:
                t_first_leg = 0

            if self.last_job_end_time < triggertime: # vehicle will be free right away
                pickuptime = triggertime + first_chargingtime + t_first_leg
            else:
                pickuptime = self.last_job_end_time + first_chargingtime + t_first_leg
        else:
            pickuptime = np.inf

        return pickuptime, possible, first_chargingtime, load_chargingtime, unload_chargingtime

    def leg_energy(self,origin,destination):
        E_bat = 0
        E_gen = 0

        #time controlled takeoff and transition tasks
        for key,details in self.states['OCCUPIED'].items():
            if details['duration'] != [] and details['power'] != 0 and details['source'] == 'battery': 
                E_bat = E_bat + details['duration'] * self.vehicledata['P_hover']
            elif details['duration'] != [] and details['power'] != 0 and details['source'] == 'generator':
                E_gen = E_gen + details['duration'] * self.vehicledata['P_hover']
        
        #cruise energy
        cruise_distance = np.sqrt((origin[0] - destination[0])**2 + (origin[1] - destination[1])**2)
        if self.states['OCCUPIED']['cruise']['source'] == 'battery':
            E_bat = E_bat + self.vehicledata['P_cruise'] * cruise_distance / self.speed
        elif self.states['OCCUPIED']['cruise']['source'] == 'generator':
            E_gen = E_gen + self.vehicledata['P_cruise'] * cruise_distance / self.speed

        return E_bat, E_gen
    
    def leg_time(self,origin,destination):
        #excluding loading/unloading
        totaltime = 0
        for task in self.states['OCCUPIED']:
            if self.states['OCCUPIED'][task]['duration'] != []:
                totaltime = totaltime + self.states['OCCUPIED'][task]['duration']
        
        #cruise duration
        totaltime = totaltime + (np.sqrt((origin[0] - destination[0])**2 + (origin[1] - destination[1])**2) / self.speed)
        return totaltime

    def alt_energy(self,destination):
        return 10
    
    def calculate_cruise_vector(self,origin, destination):
    
        x = destination[0] - origin[0]
        y = destination[1] - origin[1]

        distance = np.sqrt(x**2 + y**2)
        
        if distance != 0:
            return [x / distance, y / distance]  # Normalize to unit vector
        else:
            return [0, 0]

    def schedule(self,job,nodes):

        job['legs'] = []
        transport_leg = {}

        #create mission plan
        #first leg to pickup (if pickup current location, skip)
        distance_pickup_jobend = np.sqrt((job['pickup'][0] - self.last_job_end_position[0])**2 + (job['pickup'][1] - self.last_job_end_position[1])**2)

        if distance_pickup_jobend > 500 and job['type'] == 'patient carrying': #plan a new leg if pickup distance is farther away
            first_leg = {}
            first_leg['type'] = 'first_leg'
            first_leg['origin'] = self.last_job_end_position
            first_leg['originID'] = self.last_job_end_positionID
            first_leg['destination'] = job['pickup']
            first_leg['destinationID'] = job['pickupID']
            first_leg['status'] = 'todo'
            first_leg['cruise_vector'] = self.calculate_cruise_vector(first_leg['origin'],first_leg['destination'])
            first_leg['first_chargingtime'] = job['first_chargingtime']
            first_leg['loadingtime'] = 0
            first_leg['unloadingtime'] = 0
            first_leg['distance'] = np.sqrt((first_leg['origin'][0] - first_leg['destination'][0])**2 + (first_leg['origin'][1] - first_leg['destination'][1])**2)
            first_leg['hovertime'] = 0
            first_leg['task_timing'] = {}
            job['legs'].append(first_leg)
            transport_leg['first_chargingtime'] = 0
        else:
            transport_leg['first_chargingtime'] = job['first_chargingtime']
        
        #transport leg
        if job['type'] == 'patient carrying':
            transport_leg['type'] = 'transport_leg'
        elif job['type'] == 'return mission':
            transport_leg['type'] = 'return_leg'
        transport_leg['origin'] = job['pickup']
        transport_leg['originID'] = job['pickupID']
        transport_leg['destination'] = job['target']
        transport_leg['destinationID'] = job['targetID']
        transport_leg['status'] = 'todo'
        transport_leg['cruise_vector'] = self.calculate_cruise_vector(transport_leg['origin'],transport_leg['destination'])
        transport_leg['loadingtime'] = job['loadingtime']
        transport_leg['unloadingtime'] = job['unloadingtime']
        transport_leg['distance'] = np.sqrt((transport_leg['origin'][0] - transport_leg['destination'][0])**2 + (transport_leg['origin'][1] - transport_leg['destination'][1])**2)
        transport_leg['hovertime'] = 0
        transport_leg['task_timing'] = {}
        job['legs'].append(transport_leg)
         #TODO CHARGING DURATION???

        job['status'] = 'waiting'
        self.joblist.append(job)
        
        self.last_job_end_position = job['target']
        self.last_job_end_positionID = job['targetID']
        self.last_job_end_time = job['jobendtime']

        #refresh energy levels at end of mission
        E_first_bat, E_first_gen = self.leg_energy(self.last_job_end_position,job['pickup'])
        E_load_bat, E_load_gen = self.chargingenergy(job['load_chargingtime'],job['pickupID'],nodes)
        E_prep_bat, E_prep_gen = self.chargingenergy(job['first_chargingtime'],self.last_job_end_positionID,nodes)
        E_transport_bat, E_transport_gen = self.leg_energy(job['pickup'],job['target'])
        E_unload_bat, E_unload_gen = self.chargingenergy(job['unload_chargingtime'],job['targetID'],nodes)

        self.last_job_end_E_bat = min(min(self.last_job_end_E_bat + E_prep_bat - E_first_bat + E_load_bat, self.E_usable_bat) - E_transport_bat + E_unload_bat, self.E_usable_bat)
        self.last_job_end_E_gen = min(min(self.last_job_end_E_gen + E_prep_gen - E_first_gen + E_load_gen, self.E_usable_bat) - E_transport_gen + E_unload_gen, self.E_usable_gen)
        
        return


    def chargingenergy(self,time,positionID,nodes): #gets energy acquired during charging at location
        E_gen = 0
        chargerpower = 0
        for node in nodes:
            if node.id == positionID:
                chargerpower = node.chargerpower
                if node.refuel == True:
                    E_gen = self.E_usable_gen
                elif self.vehicledata['type'] == 'road':
                    E_gen = self.E_usable_gen
        E_bat = time * min(self.chargingpower,chargerpower)
        return E_bat, E_gen