import random

class CalendarEvents:
    def __init__(self):
        # Database of special championship races
        self.events = [
            {
                "month": 3, 
                "week": 5, 
                "name": "The Spring Sprint",
                "req_classes": ["G3", "G2", "G1"], 
                "distance": 1000, 
                "surface": "Turf",
                "forced_condition": "Firm/Fast", 
                "purse": 100000,
                "title": "Spring Sprinter",
                "buff_name": "Wind Rider",
                "buff_desc": "Slightly reduces stamina drain for Front-runners out of the gate."
            },
            # --- AGE 3 EXCLUSIVE (The Classics) ---
            {
                "month": 4, 
                "week": 4,
                "name": "The DOC Guineas",
                "req_classes": ["G2", "G1"], 
                "distance": 1600, 
                "surface": "Turf",
                "forced_condition": "Firm/Fast", 
                "purse": 300000,
                "title": "Guineas Victor",
                "buff_name": "Guineas Heritage",
                "buff_desc": "10% discount on all consumables in the Store.",
                "age_req": [2, 3] # Allows late 2yos or 3yos
            },
            {
                "month": 6, 
                "week": 5, 
                "name": "The Midsummer Classic",
                "req_classes": ["G2", "G1"], 
                "distance": 2000, 
                "surface": "Turf",
                "forced_condition": "Firm/Fast", 
                "purse": 150000,
                "title": "Midsummer Champion",
                "buff_name": "Classic Heritage",
                "buff_desc": "+10% to all Training stat gains."
            },
            # --- AGE 4 & 5 ROTATING EVENTS (Month 8 Pool) ---
            {
                "month": 8, 
                "week": 4, 
                "name": "The Summer Grand Prix",
                "req_classes": ["G1"], 
                "distance": 2200, 
                "surface": "Turf",
                "forced_condition": "Good", 
                "purse": 500000,
                "title": "Summer Champion",
                "buff_name": "Turf Sovereign",
                "buff_desc": "Slightly reduces fatigue gained from racing on Turf.",
                "age_req": [4, 5]
            },
            {
                "month": 8, 
                "week": 4, 
                "name": "Super Dirt Grand Prix",
                "req_classes": ["G1"], 
                "distance": 2000, 
                "surface": "Dirt",
                "forced_condition": "Firm/Fast", 
                "purse": 500000,
                "title": "Dirt Sovereign",
                "buff_name": "Dirt Mastery",
                "buff_desc": "Permanently boosts Grit training gains for the stable.",
                "age_req": [4, 5]
            },
            {
                "month": 9, 
                "week": 5, 
                "name": "The Autumn Marathon",
                "req_classes": ["G2", "G1"], 
                "distance": 3000, 
                "surface": "Dirt",
                "forced_condition": "Good", 
                "purse": 200000,
                "title": "Marathon King",
                "buff_name": "Titanium Heart",
                "buff_desc": "Horses recover slightly more stamina when Coasting."
            },
            {
                "month": 10, 
                "week": 4, 
                "name": "The Mudder's Stakes",
                "req_classes": ["Maiden", "G3", "G2", "G1"], 
                "distance": 1600, 
                "surface": "Dirt",
                "forced_condition": "Heavy", 
                "purse": 200000,
                "title": "Mudder King",
                "buff_name": "Iron Lungs",
                "buff_desc": "Reduces severe weather stamina penalties by 15%."
            },
            # --- AGE 6+ FINAL CAREER EVENTS ---
            {
                "month": 11, 
                "week": 4, 
                "name": "The Japan Cup",
                "req_classes": ["G1"], 
                "distance": 2400, 
                "surface": "Turf",
                "forced_condition": "Firm/Fast", 
                "purse": 1000000,
                "title": "Japan Cup Winner",
                "buff_name": "Global Standard",
                "buff_desc": "A legendary victory that boosts all market horse sale prices.",
                "age_req": [6, 7, 8, 9, 10]
            },
            {
                "month": 12, 
                "week": 5, 
                "name": "The Derby Owners Cup",
                "req_classes": ["G1"], 
                "distance": 2400, 
                "surface": "Turf",
                "forced_condition": "Firm/Fast", 
                "purse": 2500000,
                "title": "DOC Champion",
                "buff_name": "DOC Legend",
                "buff_desc": "The ultimate achievement. +5% to all training gains for future generations.",
                "age_req": [7, 8, 9, 10]
            },
            # --- STANDARD DERBY (For horses that aren't 6+ yet) ---
            {
                "month": 12, 
                "week": 5, 
                "name": "The Grand Derby",
                "req_classes": ["G1"], 
                "distance": 2400, 
                "surface": "Turf",
                "forced_condition": None, # Random weather!
                "purse": 500000,
                "title": "Grand Derby Winner",
                "buff_name": "Derby Dynasty",
                "buff_desc": "New foals are born with much higher starting stats.",
                "age_req": [2, 3, 4, 5]
            }
        ]

    def get_event(self, horse):
        """Returns a dynamic event based on the horse's age, month, and week."""
        valid_events = []
        for event in self.events:
            if event["month"] == horse.month and event["week"] == horse.week:
                if "age_req" in event and horse.age not in event["age_req"]:
                    continue
                valid_events.append(event)
        
        if not valid_events:
            return None
            
        if len(valid_events) == 1:
            return valid_events[0]
            
        # Randomly select one if there is a rotation pool (like Age 4/5 Month 8)
        # We seed it with the horse's ID and Age so the event doesn't magically 
        # change if the player exits and re-enters the menu to reroll!
        random.seed(f"{horse.id}_{horse.age}_{horse.month}")
        chosen = random.choice(valid_events)
        random.seed() # reset RNG
        return chosen