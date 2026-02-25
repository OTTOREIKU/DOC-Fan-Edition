import json
import os
from spawner import Horse
from config import ACADEMY_BASE_PAYOUT, ACADEMY_GEN_BONUS, SCOUTING_NETWORK_TIERS, BRIBE_COST_MULTIPLIERS, MAX_BRIBES_PER_CYCLE, BRIBE_RESET_MONTHS, MARKET_PRICE_BASE, GEN_PRICE_MULTIPLIER, ASSISTANT_TRAINER_MAX_STATS

class StableManager:
    def __init__(self, filename="stable.json"):
        self.filename = filename

    def _generate_jockey_roster(self):
        first_names = ["Jack", "Liam", "Marco", "Luis", "Carter", "Leo", "Julian", "Sam", "Victor", "Rey", "Mia", "Chloe", "Zoe", "Emma", "Elena"]
        last_names = ["Rossi", "Chen", "O'Connor", "Cruz", "Silva", "Hayes", "Gallagher", "Castillo", "Moreno", "Dawson", "Vargas", "Wong", "Stirling"]
        
        import random, uuid
        archetypes = [
            "The Aggressor", "The Tactician", "The Iron Rider", 
            "The Mudlark", "The Turf Glider", "The Dirt Grinder", 
            "The Caretaker", "The Whisperer", "The Showman", "The Mercenary"
        ]
        
        roster = []
        selected_archetypes = random.sample(archetypes, 5) 
        
        for arch in selected_archetypes:
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            jockey = {
                "id": str(uuid.uuid4())[:8],
                "name": name,
                "archetype": arch,
                "level": 1,
                "xp": 0,
                "wins": 0
            }
            roster.append(jockey)
        return roster

    def load_data(self):
        if not os.path.exists(self.filename):
            return {
                "credits": 15000, "horses": {}, 
                "upgrades": {
                    "pro_scanner": False, "heart_monitor": False, 
                    "turf_track_lvl": 1, "dirt_track_lvl": 1, "pool_lvl": 1, 
                    "auto_walker": False, "advanced_walker": False, "premium_saddles": False,
                    "assistant_trainer": False, "assistant_trainer_lvl": 0, "stud_syndicate": False, 
                    "master_scanner": False, "stable_capacity": 4,
                    "vet_clinic": False, "luxury_spa": False, "genetics_lab": False,
                    "jockey_guild": False, "scouting_network_lvl": 0
                },
                "inventory": {
                    "oats": 0, "salve": 0, "breed_supp": 0, "bribe": 0, "paste": 0, "mints": 0,
                    "vit_spd": 0, "vit_sta": 0, "vit_grt": 0,
                    "fruit_basket": 0, "draft_beer": 0, "gold_alfalfa": 0 
                },
                "market_horses": {}, 
                "stud_horses": [], 
                "stud_timer": 0,   
                "seen_bosses": [],
                "seen_mutations": [], 
                "national_records": {}, 
                "trade_blacklist": [],
                "settings": {"jockey_system": False}, 
                "jockey_roster": self._generate_jockey_roster(),
                "market_bribes_used": 0,
                "market_bribe_timer": 0
            }
        
        with open(self.filename, 'r') as f:
            data = json.load(f)
            
            if "upgrades" not in data: data["upgrades"] = {}
            for key, default in [("pro_scanner", False), ("heart_monitor", False), 
                                 ("turf_track_lvl", 1), ("dirt_track_lvl", 1), ("pool_lvl", 1), 
                                 ("auto_walker", False), ("advanced_walker", False), ("premium_saddles", False), 
                                 ("assistant_trainer", False), ("assistant_trainer_lvl", 0), ("stud_syndicate", False), 
                                 ("master_scanner", False), ("stable_capacity", 4),
                                 ("vet_clinic", False), ("luxury_spa", False), ("genetics_lab", False),
                                 ("jockey_guild", False), ("scouting_network_lvl", 0)]:
                if key not in data["upgrades"]: data["upgrades"][key] = default
                
            if "inventory" not in data: data["inventory"] = {}
            for key in ["oats", "salve", "breed_supp", "bribe", "paste", "mints", "vit_spd", "vit_sta", "vit_grt", "fruit_basket", "draft_beer", "gold_alfalfa"]:
                if key not in data["inventory"]: data["inventory"][key] = 0
            
            if "market_horses" not in data: 
                data["market_horses"] = {}
            elif isinstance(data["market_horses"], list):
                data["market_horses"] = {"0": data["market_horses"]}
                
            if "stud_horses" not in data: data["stud_horses"] = []
            if "stud_timer" not in data: data["stud_timer"] = 0
            if "seen_bosses" not in data: data["seen_bosses"] = []
            if "seen_mutations" not in data: data["seen_mutations"] = [] 
            if "national_records" not in data: data["national_records"] = {} 
            if "trade_blacklist" not in data: data["trade_blacklist"] = []
            
            if "settings" not in data: data["settings"] = {"jockey_system": False}
            if "jockey_system" not in data["settings"]: data["settings"]["jockey_system"] = False
            
            if "jockey_roster" not in data or not data["jockey_roster"]:
                data["jockey_roster"] = self._generate_jockey_roster()
                
            if "market_bribes_used" not in data: data["market_bribes_used"] = 0
            if "market_bribe_timer" not in data: data["market_bribe_timer"] = 0
                
            return data

    def save_data(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)
            
    def get_settings(self):
        return self.load_data().get("settings", {"jockey_system": False})
        
    def set_setting(self, key, value):
        data = self.load_data()
        if "settings" not in data: data["settings"] = {}
        data["settings"][key] = value
        self.save_data(data)

    def get_jockey_roster(self):
        return self.load_data().get("jockey_roster", [])

    def save_jockey(self, updated_jockey):
        data = self.load_data()
        roster = data.get("jockey_roster", [])
        for i, j in enumerate(roster):
            if j["id"] == updated_jockey["id"]:
                roster[i] = updated_jockey
                break
        data["jockey_roster"] = roster
        self.save_data(data)

    def save_horse(self, horse: Horse):
        data = self.load_data()
        data["horses"][horse.id] = horse.__dict__ 
        self.save_data(data)
        
    def delete_horse(self, horse_id: str):
        data = self.load_data()
        if horse_id in data["horses"]:
            del data["horses"][horse_id]
            self.save_data(data)

    def get_saved_horses(self):
        data = self.load_data()
        horses = []
        for horse_data in data.get("horses", {}).values():
            if "temp_fee" in horse_data: del horse_data["temp_fee"]
            
            if "titles" not in horse_data: horse_data["titles"] = []
            if "current_race_card" not in horse_data: horse_data["current_race_card"] = []
            if "race_history" not in horse_data: horse_data["race_history"] = [] 
            if "personality" not in horse_data: horse_data["personality"] = "Willing" 
            if "trust" not in horse_data: horse_data["trust"] = 50.0
            if "bad_interaction_streak" not in horse_data: horse_data["bad_interaction_streak"] = 0
            if "is_locked" not in horse_data: horse_data["is_locked"] = False
            if "lifetime_injuries" not in horse_data: horse_data["lifetime_injuries"] = 0
            if "style_points" not in horse_data: horse_data["style_points"] = {}
            if "is_npc" not in horse_data: horse_data["is_npc"] = False
            if "npc_parents_data" not in horse_data: horse_data["npc_parents_data"] = []
            
            if "is_archived" not in horse_data: horse_data["is_archived"] = False
            if "is_in_academy" not in horse_data: horse_data["is_in_academy"] = False
            if "draft_beer_buff" not in horse_data: horse_data["draft_beer_buff"] = False
            if "assistant_stats_gained" not in horse_data: horse_data["assistant_stats_gained"] = 0.0
            
            horses.append(Horse(**horse_data))
        return horses

    def get_highest_generation(self):
        horses = self.get_saved_horses()
        if not horses: return 0
        return max((getattr(h, 'generation', 0) for h in horses if not getattr(h, 'is_npc', False)), default=0)

    def get_horse_by_id(self, horse_id: str):
        if not horse_id: return None
        data = self.load_data()
        if horse_id in data.get("horses", {}):
            h = data["horses"][horse_id]
            if "temp_fee" in h: del h["temp_fee"] 
            
            if "titles" not in h: h["titles"] = []
            if "current_race_card" not in h: h["current_race_card"] = []
            if "race_history" not in h: h["race_history"] = [] 
            if "personality" not in h: h["personality"] = "Willing" 
            if "trust" not in h: h["trust"] = 50.0
            if "bad_interaction_streak" not in h: h["bad_interaction_streak"] = 0
            if "is_locked" not in h: h["is_locked"] = False
            if "lifetime_injuries" not in h: h["lifetime_injuries"] = 0
            if "style_points" not in h: h["style_points"] = {}
            if "is_npc" not in h: h["is_npc"] = False
            if "npc_parents_data" not in h: h["npc_parents_data"] = []
            
            if "is_archived" not in h: h["is_archived"] = False
            if "is_in_academy" not in h: h["is_in_academy"] = False
            if "draft_beer_buff" not in h: h["draft_beer_buff"] = False
            if "assistant_stats_gained" not in h: h["assistant_stats_gained"] = 0.0
            
            return Horse(**h)
        return None

    def is_blacklisted(self, horse_id):
        return horse_id in self.load_data().get("trade_blacklist", [])

    def add_to_trade_blacklist(self, horse_id):
        data = self.load_data()
        if "trade_blacklist" not in data: data["trade_blacklist"] = []
        data["trade_blacklist"].append(horse_id)
        self.save_data(data)

    def get_market_horses(self, gen: int):
        data = self.load_data()
        market_dict = data.get("market_horses", {})
        horses_data = market_dict.get(str(gen), [])
        
        horses = []
        for h in horses_data:
            if "temp_fee" in h: del h["temp_fee"] 
            
            if "is_locked" not in h: h["is_locked"] = False
            if "lifetime_injuries" not in h: h["lifetime_injuries"] = 0
            if "style_points" not in h: h["style_points"] = {}
            if "is_npc" not in h: h["is_npc"] = False
            if "npc_parents_data" not in h: h["npc_parents_data"] = []
            
            if "is_archived" not in h: h["is_archived"] = False
            if "is_in_academy" not in h: h["is_in_academy"] = False
            if "draft_beer_buff" not in h: h["draft_beer_buff"] = False
            if "assistant_stats_gained" not in h: h["assistant_stats_gained"] = 0.0
            
            horses.append(Horse(**h))
        return horses

    def save_market_horses(self, horses_list, gen: int):
        data = self.load_data()
        if "market_horses" not in data or isinstance(data["market_horses"], list):
            data["market_horses"] = {}
            
        data["market_horses"][str(gen)] = [h.__dict__ for h in horses_list]
        self.save_data(data)

    def refresh_all_markets(self, spawner):
        highest_gen = self.get_highest_generation()
        data = self.load_data()
        
        scout_lvl = data.get("upgrades", {}).get("scouting_network_lvl", 0)
        target_size = SCOUTING_NETWORK_TIERS.get(scout_lvl, SCOUTING_NETWORK_TIERS[0])["size"]
        
        if "market_horses" not in data or isinstance(data["market_horses"], list):
            data["market_horses"] = {}
            
        for gen in range(highest_gen + 1):
            gen_str = str(gen)
            current_market_data = data["market_horses"].get(gen_str, [])
            
            new_market = []
            for h_dict in current_market_data:
                h = Horse(**h_dict)
                if getattr(h, 'is_locked', False): new_market.append(h)
            
            while len(new_market) < target_size: 
                new_market.append(spawner.generate_market_horse(gen, scout_lvl))
            data["market_horses"][gen_str] = [h.__dict__ for h in new_market]
            
        self.save_data(data)

    def get_stud_horses(self):
        data = self.load_data()
        return [Horse(**h) for h in data.get("stud_horses", [])]

    def refresh_stud_farm(self, spawner):
        highest_gen = self.get_highest_generation()
        data = self.load_data()
        new_studs = []
        for _ in range(3): new_studs.append(spawner.generate_stud_horse(highest_gen, "Stallion").__dict__)
        for _ in range(3): new_studs.append(spawner.generate_stud_horse(highest_gen, "Mare").__dict__)
        data["stud_horses"] = new_studs
        data["stud_timer"] = 3
        self.save_data(data)

    def decrement_stud_timer(self, spawner):
        data = self.load_data()
        timer = data.get("stud_timer", 0)
        if timer <= 1:
            self.refresh_stud_farm(spawner)
        else:
            data["stud_timer"] = timer - 1
            
        bribe_timer = data.get("market_bribe_timer", 0)
        if bribe_timer > 0:
            bribe_timer -= 1
            if bribe_timer <= 0:
                data["market_bribes_used"] = 0
            data["market_bribe_timer"] = bribe_timer
            
        self.save_data(data)

    def get_bribe_info(self, gen):
        data = self.load_data()
        bribes_used = data.get("market_bribes_used", 0)
        timer = data.get("market_bribe_timer", 0)
        
        if bribes_used >= MAX_BRIBES_PER_CYCLE:
            return False, bribes_used, timer, 0
            
        p_mean = 50.0 + (gen * 10.0)
        avg_base_val = (p_mean * 0.60) * MARKET_PRICE_BASE
        avg_cost = int(avg_base_val * (GEN_PRICE_MULTIPLIER ** gen))
        
        idx = min(bribes_used, len(BRIBE_COST_MULTIPLIERS)-1)
        bribe_cost = int(avg_cost * BRIBE_COST_MULTIPLIERS[idx])
        
        return True, bribes_used, timer, bribe_cost

    def apply_market_bribe(self, spawner, gen):
        can_bribe, used, timer, cost = self.get_bribe_info(gen)
        if not can_bribe: return False, "Max bribes reached."
        
        data = self.load_data()
        if data["credits"] < cost: return False, "Not enough funds."
        
        data["credits"] -= cost
        if used == 0:
            data["market_bribe_timer"] = BRIBE_RESET_MONTHS
        data["market_bribes_used"] = used + 1
        
        scout_lvl = data.get("upgrades", {}).get("scouting_network_lvl", 0)
        target_size = SCOUTING_NETWORK_TIERS.get(scout_lvl, SCOUTING_NETWORK_TIERS[0])["size"]
        
        current_market = data.get("market_horses", {}).get(str(gen), [])
        new_market = [Horse(**h) for h in current_market if h.get("is_locked", False)]
        
        while len(new_market) < target_size:
            new_market.append(spawner.generate_market_horse(gen, scout_lvl))
            
        data["market_horses"][str(gen)] = [h.__dict__ for h in new_market]
        self.save_data(data)
        
        return True, "Market successfully rerolled!"

    # --- UPDATED TO ENFORCE TRAINING CAP AND RETURN FINISHED HORSES ---
    def auto_train_benched(self, active_horse_id):
        data = self.load_data()
        upgrades = data.get("upgrades", {})
        
        at_lvl = upgrades.get("assistant_trainer_lvl", 0)
        if at_lvl == 0 and upgrades.get("assistant_trainer", False):
            at_lvl = 1 
            
        if at_lvl == 0: 
            return [], []
            
        stat_boost = at_lvl * 0.1
        
        trained_horses = []
        finished_horses = []
        
        for h_id, h_data in data["horses"].items():
            if h_id != active_horse_id and not h_data.get("is_retired", False) and not h_data.get("is_npc", False):
                gained = h_data.get("assistant_stats_gained", 0.0)
                remaining_cap = ASSISTANT_TRAINER_MAX_STATS - gained
                
                if remaining_cap <= 0.001:
                    continue 
                    
                p_spd = h_data.get("pot_speed", 0)
                p_sta = h_data.get("pot_stamina", 0)
                p_grt = h_data.get("pot_grit", 0)
                
                req_spd = max(0, min(p_spd - h_data["cur_speed"], stat_boost))
                req_sta = max(0, min(p_sta - h_data["cur_stamina"], stat_boost))
                req_grt = max(0, min(p_grt - h_data["cur_grit"], stat_boost))
                
                total_req = req_spd + req_sta + req_grt
                
                if total_req > 0:
                    if total_req > remaining_cap:
                        scale = remaining_cap / total_req
                        req_spd *= scale
                        req_sta *= scale
                        req_grt *= scale
                        total_req = remaining_cap
                        
                    h_data["cur_speed"] += req_spd
                    h_data["cur_stamina"] += req_sta
                    h_data["cur_grit"] += req_grt
                    h_data["assistant_stats_gained"] = gained + total_req
                    h_data["condition"] = min(100.0, h_data.get("condition", 50.0) + 5.0)
                    
                    if h_data["assistant_stats_gained"] >= ASSISTANT_TRAINER_MAX_STATS - 0.001:
                        finished_horses.append(h_data.get("name", "Unknown"))
                    else:
                        trained_horses.append(h_data.get("name", "Unknown"))
                        
        self.save_data(data)
        return trained_horses, finished_horses

    def process_academy_payouts(self):
        data = self.load_data()
        total_payout = 0
        for h_id, h in data.get("horses", {}).items():
            if h.get("is_in_academy", False) and not h.get("is_archived", False):
                trust = h.get("trust", 50.0)
                mood = h.get("condition", 50.0)
                gen = h.get("generation", 0)
                
                payout = int(ACADEMY_BASE_PAYOUT + ((trust + mood) * 100) + (gen * ACADEMY_GEN_BONUS))
                total_payout += payout
                
        if total_payout > 0:
            data["credits"] += total_payout
            self.save_data(data)
            return total_payout
        return 0

    def get_seen_bosses(self): return self.load_data().get("seen_bosses", [])
    def add_seen_boss(self, boss_name):
        data = self.load_data()
        if boss_name not in data["seen_bosses"]:
            data["seen_bosses"].append(boss_name)
            self.save_data(data)

    def get_seen_mutations(self): return self.load_data().get("seen_mutations", [])
    def add_seen_mutation(self, mut_name):
        data = self.load_data()
        if "seen_mutations" not in data: data["seen_mutations"] = []
        if mut_name not in data["seen_mutations"]:
            data["seen_mutations"].append(mut_name)
            self.save_data(data)

    def update_national_record(self, key, time_sec, horse_name):
        data = self.load_data()
        if "national_records" not in data: data["national_records"] = {}
        data["national_records"][key] = {"time": time_sec, "holder": horse_name}
        self.save_data(data)

    def get_credits(self): return self.load_data()["credits"]
    def add_credits(self, amount: int):
        data = self.load_data()
        data["credits"] += amount
        self.save_data(data)

    def get_upgrades(self): return self.load_data()["upgrades"]
    def set_upgrade(self, upgrade_key, value):
        data = self.load_data()
        data["upgrades"][upgrade_key] = value
        self.save_data(data)

    def get_inventory(self): return self.load_data()["inventory"]
    def add_item(self, item_key, amount):
        data = self.load_data()
        if item_key not in data["inventory"]: data["inventory"][item_key] = 0
        data["inventory"][item_key] += amount
        self.save_data(data)