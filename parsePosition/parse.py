import json


def convert_to_relative_coordinates(points: dict) -> list:
    if not points:
        return []

    origin = points[0]['position']
    ox, oy, oz = origin['x'], origin['y'], origin['z']

    relative_points = []
    for point in points:
        px, py, pz = point['position']['x'], point['position']['y'], point['position']['z']
        relative_position = {
            'x': px - ox,
            'y': py - oy,
            # 'z': pz - oz
        }
        relative_points.append({
            'position': relative_position,
            'orientationAngle': point['orientationAngle']
        })

    return relative_points


def to_relative_position(reference_point: dict, target_point: dict) -> dict:
    ref_pos = reference_point['position']
    tgt_pos = target_point['position']

    relative_position = {
        'x': tgt_pos['x'] - ref_pos['x'],
        'y': tgt_pos['y'] - ref_pos['y'],
        # 'z': tgt_pos['z'] - ref_pos['z']
    }

    return {
        'position': relative_position,
        # 'orientationAngle': target_point['orientationAngle']
    }


'''
convert_to_relative_coordinates:
{'position': {'x': 0, 'y': 0, 'z': 0}, 'orientationAngle': 'NaN'}
{'position': {'x': 0, 'y': -6000, 'z': 0}, 'orientationAngle': 'NaN'}
{'position': {'x': -6000, 'y': -8000, 'z': 0}, 'orientationAngle': 'NaN'}
{'position': {'x': -9000, 'y': -10000, 'z': 0}, 'orientationAngle': 'NaN'}
{'position': {'x': -9000, 'y': -22000, 'z': 0}, 'orientationAngle': 'NaN'}
---------------------
to_relative_position:
{'position': {'x': 0, 'y': 0, 'z': 0}, 'orientationAngle': 'NaN'}
{'position': {'x': 0, 'y': -6000, 'z': 0}, 'orientationAngle': 'NaN'}
{'position': {'x': -6000, 'y': -8000, 'z': 0}, 'orientationAngle': 'NaN'}
{'position': {'x': -9000, 'y': -10000, 'z': 0}, 'orientationAngle': 'NaN'}
{'position': {'x': -9000, 'y': -22000, 'z': 0}, 'orientationAngle': 'NaN'}
'''

if __name__ == '__main__':
    start = 1
    end = 5
    points = []
    first_point = None
    for i in range(start, end + 1):
        step = json.load(open(f'./STEP-{i}.json'))
        spose = step.get("step").get("sourcePoint").get("pose")
        dpose = step.get("step").get("destinationPoint").get("pose")
        if i == 1:
            first_point = spose
        if i != end:
            # print(spose)
            print(to_relative_position(first_point, spose))
            # points.append(spose)
        else:
            # print(dpose)
            print(to_relative_position(first_point, dpose))
            points.append(dpose)
    print("--------------------------")
    # rps = convert_to_relative_coordinates(points)
    # print("\n".join(map(str, rps)))
