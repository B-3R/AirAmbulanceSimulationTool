import numpy as np
import pprint

class OpsModel:
    def __init__(self,config_simulation,vehicles,nodes,joblist):
        self.time = config_simulation['starttime']
        self.timestep = config_simulation['timestep']

        self.vehicles = vehicles
        self.nodes = nodes
        self.joblist = joblist

        self.unassigned_jobs = []
        self.vehicle_log = []
        self.jumps = 0

        


    def step(self):
        # advance time to current time
        self.time = self.time + self.timestep

        vehicles = self.vehicles
        nodes = self.nodes
        joblist = self.joblist

        # update each vehicle status, position and parameters (nodes updated by vehicles)
        vehiclelog = []
        for vehicle in vehicles:
            position_old = vehicle.position
            task_old = vehicle.task
            vehicle.update(self.timestep,self.time,nodes)
            vehiclelog.append([vehicle.id,vehicle.position,vehicle.state,vehicle.task,vehicle.E_current_bat,vehicle.E_current_gen,vehicle.current_P])
            position_new = vehicle.position
            traveldistance = np.sqrt((position_new[0] - position_old[0])**2 + (position_new[1] - position_old[1])**2)
            if traveldistance > (vehicle.speed * self.timestep*1.1):
                print(f'ERROR - vehicle {vehicle.id} jumped {traveldistance}m (max. {vehicle.speed * self.timestep}m per timestep) from {position_old} to {position_new} at time {self.time}s')
                #print(f'Previous task: {task_old} Current task: {vehicle.task}')
                self.jumps = self.jumps + 1
                #print(f'current leg: {vehicle.leg['type']}')
                #pprint.pprint(vehicle.job)
                #pprint.pprint(vehicle.job_previous)
            if vehicle.E_current_bat < 0: print(f'ERROR - vehicle {vehicle.id} battery empty at time {self.time}s - {vehicle.E_current_bat/3600000} kWh - {vehicle.task} {vehicle.currentleg}{vehicle.job}')
            if vehicle.E_current_gen < 0: print(f'ERROR - vehicle {vehicle.id} fuel empty at time {self.time}s')

        self.vehicle_log.append(vehiclelog)

        #fetch and distribute new demand
        for job in joblist:
            if job['triggertime'] <= self.time and job['triggertime'] > (self.time-self.timestep):
                pickuptime = np.inf
                pickupvehicle = None
                jobendtime = 0
                
                for vehicle in vehicles:
                    if vehicle.state != 'OOS':# and DistanceEPSG3035(job['pickup'],vehicle.position) < vehicle.range: #excludes vehicles that are anyways occupied longer
                        
                        pickuptime_new, possible, first_chargingtime_new, load_chargingtime_new, unload_chargingtime_new = vehicle.pickupcheck(job['pickup'],job['target'],job['triggertime'],job['pickupID'],job['targetID'],self.nodes)
                        if possible == True:
                            #check if vehicle can be back before end of shift
                            jobendtime_new = pickuptime_new + vehicle.leg_time(job['pickup'],job['target']) + max(job['loadingtime'],load_chargingtime_new) + max(job['unloadingtime'],unload_chargingtime_new)
                            returnlegtime = vehicle.leg_time(job['target'],vehicle.home) #TODO charging before return leg!!!
                            returntime = jobendtime_new + returnlegtime #time when vehicle is back at the base

                            #TODO check if I can get home on the remaining energy or if charging is available

                            inshift = False
                            DAYINSECONDS = 24*3600
                            for shift in vehicle.hours:
                                if returntime%DAYINSECONDS < max(shift) and returntime%DAYINSECONDS > min(shift):
                                    inshift = True

                            if pickuptime_new < pickuptime and inshift == True:
                                jobendtime = jobendtime_new
                                pickuptime = pickuptime_new
                                pickupvehicle = vehicle
                                first_chargingtime = first_chargingtime_new
                                load_chargingtime = load_chargingtime_new
                                unload_chargingtime = unload_chargingtime_new

                if pickupvehicle is not None and pickuptime < (self.time+90*60):
                    job['pickupvehicle'] = pickupvehicle.id
                    job['pickuptime'] = pickuptime
                    job['jobendtime'] = jobendtime
                    job['success'] = 'scheduled'
                    job['first_chargingtime'] = first_chargingtime
                    job['load_chargingtime'] = load_chargingtime
                    job['unload_chargingtime'] = unload_chargingtime
                    pickupvehicle.schedule(job,nodes)
                else:
                    job['success'] = 'not assigned'
                    job['distance'] = np.sqrt((job['pickup'][0] - job['target'][0])**2 + (job['pickup'][1] - job['target'][1])**2)
                    self.unassigned_jobs.append(job) #TODO jobs die nicht complete und nicht unassigned sind fallen aus der statistik weil noch doing



