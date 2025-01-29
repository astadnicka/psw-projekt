import json
import os

DATA_FILE = 'mushroompoints.json' 

class MushroomPoint:
    def __init__(self, latitude, longitude, name, description, rating=None, mushroom_id=None):
        self.latitude = latitude
        self.longitude = longitude
        self.name = name
        self.description = description
        self.rating = rating
        self.id = mushroom_id if mushroom_id else None

    # Serializacja obiektu do słownika (JSON)
    def to_dict(self):
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'name': self.name,
            'description': self.description,
            'rating': self.rating
        }

    @staticmethod
    def load_all():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return [MushroomPoint(**m) for m in data]
        return []

    @staticmethod
    def save_all(mushroompoints):
        with open(DATA_FILE, 'w') as f:
            json.dump([m.to_dict() for m in mushroompoints], f, indent=4)

    @staticmethod
    def get_by_id(mushroom_id):
        mushroompoints = MushroomPoint.load_all()
        return next((m for m in mushroompoints if m.id == mushroom_id), None)

    @staticmethod
    def add(mushroom):
        mushroompoints = MushroomPoint.load_all()
        mushroom.id = max([m.id for m in mushroompoints], default=0) + 1
        mushroompoints.append(mushroom)
        MushroomPoint.save_all(mushroompoints)

    @staticmethod
    def update(mushroom_id, new_data):
        mushroompoints = MushroomPoint.load_all()
        mushroom = MushroomPoint.get_by_id(mushroom_id)
        if mushroom:
            if 'name' in new_data:
                mushroom.name = new_data['name']
            if 'description' in new_data:
                mushroom.description = new_data['description']
            if 'rating' in new_data:
                mushroom.rating = new_data['rating']
            MushroomPoint.save_all(mushroompoints)
            return mushroom
        return None

    @staticmethod
    def delete(mushroom_id):
        mushroompoints = MushroomPoint.load_all()
        mushroompoints = [m for m in mushroompoints if m.id != mushroom_id]
        MushroomPoint.save_all(mushroompoints)
