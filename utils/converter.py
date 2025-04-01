import json
from pyproj import Transformer

def convertDEhospitals():

    hospitals = json.load(open(f'data\\Germany\\hospitals_input.json', 'r'))
    hospitals_converted = {'hospitals':[]}

    for type in hospitals:
        for hospital in hospitals[type]:
            latitude, longitude = Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True).transform(hospital[0],hospital[1])
            hospitals_converted['hospitals'].append({
                "Hospital": "",
                "Latitude": latitude,
                "Longitude": longitude,
                "Class": type,
                "State": hospital[2],
                "EPSG3035_X": hospital[0],
                "EPSG3035_Y": hospital[1]
            })

    with open(f'data\\Germany\\hospitals.json', 'w') as f:
            json.dump(hospitals_converted, f, indent=4)

def convertIThospitals():
    file = json.load(open(f'data\\Italia\\hospitals.json', 'r'))

    for hospital in file['hospitals']:
        if type(hospital['geometry']) == dict:
            x, y = convertCoordinates(hospital['geometry']['coordinates'][1],hospital['geometry']['coordinates'][0])
            hospital.update({
                "EPSG3035_X": x,
                "EPSG3035_Y": y
            })

    with open(f'data\\Italia\\hospitals_new.json', 'w') as f:
            json.dump(file, f, indent=4)
    print('done')

    
def convertCoordinates(lat,lon):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y


if __name__ == '__main__':
     #print(convertCoordinates(50.63584550104508, 3.0691350726881694))
     convertIThospitals()