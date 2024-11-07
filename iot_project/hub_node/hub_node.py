import csv
file_path = 'iot_project\hub_node\hub_node.csv'

def read_from_csv(file_path):
    rooms = {}
    with open(file_path, mode='r') as file:
        counter = csv.reader(file)
        next(counter)
        for row in counter:
            room_id = row[0]
            person_ids = row[1].split(',')
            names = row[2].split(',')
            rooms[room_id] = {'person_ids': person_ids, 'names':names}
    return rooms


def roomlist(file_path):
            rooms = read_from_csv(file_path)
            for room_id, data in rooms.items():
                print(f"Room {room_id}:")
                if data['person_ids'] and data['names']:
                    for person_ids, names in zip(data['person_ids'], data['names']):
                        print(f"    - Person ID: {person_ids.strip()}, Name: {names.strip()}")



roomlist(file_path)
