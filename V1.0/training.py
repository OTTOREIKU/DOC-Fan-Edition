import random
from config import STD_REST_FATG, STD_REST_MOOD, SPA_REST_FATG, SPA_REST_MOOD, FACILITY_BONUS_PER_LVL

class TrainingFacility:
    def __init__(self):
        pass

    def train(self, horse, action, upgrades, hof_buffs):
        turf_lvl = upgrades.get('turf_track_lvl', 1)
        dirt_lvl = upgrades.get('dirt_track_lvl', 1)
        pool_lvl = upgrades.get('pool_lvl', 1)
        has_vet = upgrades.get('vet_clinic', False)
        has_spa = upgrades.get('luxury_spa', False)
        
        c_val = getattr(horse, 'condition', 50.0)
        
        active_titles = horse.titles + hof_buffs
        injury_divider = 2.0 if "Dream Weaver" in active_titles else 1.0
        
        training_multi = 1.0
        if "Classic Heritage" in active_titles: training_multi += 0.10
        if "DOC Legend" in active_titles: training_multi += 0.05
            
        dirt_mastery_multi = 1.15 if "Dirt Mastery" in active_titles else 1.0

        if action == '4':
            if horse.fatigue >= 90:
                # --- PULL RESTING STATS FROM CONFIG ---
                rest_fatg = SPA_REST_FATG if has_spa else STD_REST_FATG
                rest_mood = SPA_REST_MOOD if has_spa else STD_REST_MOOD
                horse.fatigue = max(0.0, horse.fatigue - rest_fatg)
                horse.condition = min(100.0, c_val + rest_mood) 
                return f"\n⚠️ {horse.name} is too exhausted even for a walk! Forcing rest."
            
            room_spd = 1.0 - (horse.cur_speed / horse.pot_speed) if horse.pot_speed > 0 else 0
            room_sta = 1.0 - (horse.cur_stamina / horse.pot_stamina) if horse.pot_stamina > 0 else 0
            room_grt = 1.0 - (horse.cur_grit / horse.pot_grit) if horse.pot_grit > 0 else 0
            
            s_gain = max(0.1, 0.35 * room_spd) * training_multi
            st_gain = max(0.1, 0.35 * room_sta) * training_multi
            g_gain = max(0.1, 0.35 * room_grt) * training_multi
            
            horse.cur_speed = min(horse.pot_speed, horse.cur_speed + s_gain)
            horse.cur_stamina = min(horse.pot_stamina, horse.cur_stamina + st_gain)
            horse.cur_grit = min(horse.pot_grit, horse.cur_grit + g_gain)
            
            fatg_gain = random.uniform(2.0, 5.0)
            if upgrades.get('advanced_walker'):
                fatg_gain *= 0.7
            horse.fatigue += fatg_gain
            
            horse.condition = min(100.0, c_val + random.uniform(8.0, 15.0))
            
            res = f"\n🌳 Light Paddock Walk:\n   +{s_gain:.2f} Spd | +{st_gain:.2f} Sta | +{g_gain:.2f} Grt\n   Your horse enjoyed the relaxed exercise! Mood stabilized."
            
            injury_chance = (0.005 + (max(0, horse.fatigue - 70) / 400.0)) / injury_divider
            if random.random() < injury_chance:
                base_inj = 1
                horse.injury_weeks = max(1, base_inj - 1) if has_vet else base_inj
                if not hasattr(horse, 'lifetime_injuries'): horse.lifetime_injuries = 0
                horse.lifetime_injuries += 1 
                res += f"\n🚑 {horse.name} tripped awkwardly in the paddock! They must rest."
            return res

        elif action == '5':
            # --- PULL RESTING STATS FROM CONFIG ---
            rest_fatg = SPA_REST_FATG if has_spa else STD_REST_FATG
            rest_mood = SPA_REST_MOOD if has_spa else STD_REST_MOOD
            horse.fatigue = max(0.0, horse.fatigue - rest_fatg)
            horse.condition = min(100.0, c_val + rest_mood) 
            msg = f"\n> {horse.name} rested. Fatigue is now {horse.fatigue:.1f}. Mood improved!"
            if has_spa: msg += "\n✨ (Luxury Spa bonuses applied!)"
            return msg

        elif action in ['1', '2', '3']:
            room_spd = 1.0 - (horse.cur_speed / horse.pot_speed) if horse.pot_speed > 0 else 0
            room_sta = 1.0 - (horse.cur_stamina / horse.pot_stamina) if horse.pot_stamina > 0 else 0
            room_grt = 1.0 - (horse.cur_grit / horse.pot_grit) if horse.pot_grit > 0 else 0
            
            s_gain, st_gain, g_gain = 0, 0, 0
            
            if action == '1': 
                # --- FACILITY BONUS FROM CONFIG ---
                turf_multi = 1.0 + ((turf_lvl - 1) * FACILITY_BONUS_PER_LVL)
                s_gain = max(0.2, 1.8 * room_spd * turf_multi)
                st_gain = max(0.1, 0.4 * room_sta)
                t_name = "Turf Gallop"
            elif action == '2': 
                pool_multi = 1.0 + ((pool_lvl - 1) * FACILITY_BONUS_PER_LVL)
                st_gain = max(0.2, 1.8 * room_sta * pool_multi)
                g_gain = max(0.1, 0.4 * room_grt)
                t_name = "Hill Sprints"
            elif action == '3': 
                dirt_multi = 1.0 + ((dirt_lvl - 1) * FACILITY_BONUS_PER_LVL)
                g_gain = max(0.2, 1.8 * room_grt * dirt_multi * dirt_mastery_multi)
                s_gain = max(0.1, 0.4 * room_spd)
                t_name = "Dirt Track"
                
            s_gain *= training_multi
            st_gain *= training_multi
            g_gain *= training_multi
            
            horse.cur_speed = min(horse.pot_speed, horse.cur_speed + s_gain)
            horse.cur_stamina = min(horse.pot_stamina, horse.cur_stamina + st_gain)
            horse.cur_grit = min(horse.pot_grit, horse.cur_grit + g_gain)
            
            fatg_gain = random.uniform(15.0, 22.0)
            if upgrades.get('advanced_walker'):
                fatg_gain *= 0.7  
            horse.fatigue += fatg_gain
            
            horse.condition = max(0.0, c_val - random.uniform(1.0, 4.0)) 
            
            res = f"\n🏋️ {t_name} Complete:\n   +{s_gain:.2f} Spd | +{st_gain:.2f} Sta | +{g_gain:.2f} Grt"
            
            if training_multi > 1.0 or (action == '3' and dirt_mastery_multi > 1.0):
                res += "\n   ✨ Legacy buffs amplified your training results!"
            
            injury_chance = (0.01 + (max(0, horse.fatigue - 60) / 300.0)) / injury_divider
            if random.random() < injury_chance:
                base_inj = random.randint(1, 3)
                horse.injury_weeks = max(1, base_inj - 1) if has_vet else base_inj
                if not hasattr(horse, 'lifetime_injuries'): horse.lifetime_injuries = 0
                horse.lifetime_injuries += 1 
                res += f"\n🚑 {horse.name} pulled a muscle during training! They must rest."
                if has_vet: res += " (Vet Clinic reduced recovery time!)"
                
            return res

        return "\nInvalid Action."