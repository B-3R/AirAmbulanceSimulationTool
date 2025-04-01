'''
     Each node represents either a base, pickup- or dropoff location.

     Differentiate Base and Pad (pads optional with charging or not, can be modelled, e.g. with the highest frequented ones first)
    
     Charging
     Landing pads
     Hangars

'''

class Node:
    def __init__(self,id,node,type,chargerpower,refuel):

        self.id = id
        self.position = [node['EPSG3035_X'],node['EPSG3035_Y']]
        self.hangars = {} #count of hangars
        self.vehicles = []
        self.relative_demand = 0 #o count the relative demand of node if node is hub type and allocate vehicles
        self.type = type
        self.chargerpower = chargerpower
        self.refuel = refuel