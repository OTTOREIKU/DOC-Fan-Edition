import time
import random
import os
from spawner import HorseSpawner

# --- IMPORT CONFIG SETTINGS ---
from config import BASE_PURSES, RACE_FATIGUE_RANGE, BUFF_MATH_MODE, GENERATION_MULTIPLIERS

class RaceEngine:
    def __init__(self):
        self.spawner = HorseSpawner()
        self.base_purses = BASE_PURSES
        
        self.conditions = [
            {"name": "Firm/Fast", "icon": "☀️", "speed_mod": 1.0, "stam_mod": 1.0, "purse_mod": 1.0, "weight": 50},
            {"name": "Good",      "icon": "⛅", "speed_mod": 0.95, "stam_mod": 1.10, "purse_mod": 1.15, "weight": 30},
            {"name": "Yielding",  "icon": "🌧️", "speed_mod": 0.90, "stam_mod": 1.25, "purse_mod": 1.35, "weight": 15},
            {"name": "Heavy",     "icon": "⛈️", "speed_mod": 0.80, "stam_mod": 1.50, "purse_mod": 1.60, "weight": 5}
        ]

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _get_condition_by_name(self, name):
        for c in self.conditions:
            if c["name"] == name: return c
        return self.conditions[0]

    def format_time(self, seconds):
        m = int(seconds // 60)
        s = seconds - (m * 60)
        return f"{m}:{s:05.2f}"

    def _get_handicap_marker(self, val, all_vals):
        unique = sorted(list(set(all_vals)), reverse=True)
        if not unique: return ""
        rank = unique.index(val)
        if rank == 0: return "◎"
        elif rank == 1: return "○"
        elif rank == 2: return "▲"
        else: return "△"

    def _show_tip_sheet(self, runners):
        self.clear_screen()
        print("\n" + "📋"*32)
        print("PRE-RACE TIP SHEET (HANDICAPPING)".center(64))
        print("📋"*32 + "\n")
        
        spds = [h.cur_speed for h in runners]
        stas = [h.cur_stamina for h in runners]
        grts = [h.cur_grit for h in runners]
        conds = [getattr(h, 'condition', 50.0) for h in runners]
        
        print("   Horse Name         |  SPD  |  STA  |  GRT  |  CND  ")
        print("-" * 58)
        for i, h in enumerate(runners):
            is_plr = "⭐" if i == 0 else "  "
            name = h.name[:16].ljust(16)
            spd_m = self._get_handicap_marker(h.cur_speed, spds)
            sta_m = self._get_handicap_marker(h.cur_stamina, stas)
            grt_m = self._get_handicap_marker(h.cur_grit, grts)
            cnd_m = self._get_handicap_marker(getattr(h, 'condition', 50.0), conds)
            
            print(f" {is_plr} {name} |   {spd_m}   |   {sta_m}   |   {grt_m}   |   {cnd_m}   ")
            
        print("-" * 58)
        print(" Legend: ◎ Best | ○ 2nd | ▲ 3rd | △ 4th+")
        input("\nPress Enter to return to gates...")

    def generate_race_card(self, race_class: str, special_event=None):
        card = []
        if special_event:
            cond = self._get_condition_by_name(special_event["forced_condition"]) if special_event["forced_condition"] else random.choice(self.conditions)
            card.append({
                "is_special": True, "event_data": special_event,
                "distance": special_event["distance"], "surface": special_event["surface"],
                "condition": cond, "purse": special_event["purse"] 
            })
            
        distances = [1000, 1200, 1600, 2000, 2400, 3000]
        surfaces = ["Turf", "Turf", "Dirt"] 
        
        while len(card) < 3:
            cond = random.choice([c for c in self.conditions for _ in range(c["weight"])])
            base_p = self.base_purses[race_class] * random.uniform(0.9, 1.2)
            final_purse = int(base_p * cond["purse_mod"])
            
            card.append({
                "is_special": False, "distance": random.choice(distances), "surface": random.choice(surfaces),
                "condition": cond,
                "purse": final_purse
            })
        return card

    def run_race(self, player_horse, selected_race, has_monitor=False, has_saddles=False, paste_used=False, hof_buffs=None, stable_mgr=None, chosen_jockey=None):
        if hof_buffs is None: hof_buffs = []
        distance, surface = selected_race["distance"], selected_race["surface"]
        purse, cond = selected_race["purse"], selected_race["condition"]
        is_special = selected_race.get("is_special", False)
        
        race_title = selected_race["event_data"]["name"] if is_special else f"THE {player_horse.race_class} STAKES"
        
        j_arch = chosen_jockey.get("archetype") if chosen_jockey else None
        j_lvl = chosen_jockey.get("level", 0) if chosen_jockey else 0
        
        opponents = []
        boss_in_race = None
        
        if player_horse.race_class in ["G2", "G1"] and random.random() < 0.15:
            boss = self.spawner.generate_boss_opponent(player_horse)
            opponents.append(boss)
            boss_in_race = boss
            
        while len(opponents) < 5:
            opponents.append(self.spawner.generate_ai_opponent(player_horse))
            
        all_runners = [player_horse] + opponents
        
        while True:
            self.clear_screen()
            print("\n" + "🏁"*32)
            print(f"{race_title.upper()} | {distance}m {surface}".center(64))
            print(f"Condition: {cond['icon']} {cond['name']} | PURSE: ${purse:,}".center(64))
            print("🏁"*32)
            
            print("\n [1] Proceed to Starting Gates")
            print(" [2] View Tip Sheet (Handicapping)")
            c = input("\nSelect option (1-2): ")
            if c == '2':
                self._show_tip_sheet(all_runners)
            elif c == '1':
                break
        
        win_streak = 0
        for race in reversed(getattr(player_horse, 'race_history', [])):
            if race.get('placement') == 1: win_streak += 1
            else: break
                
        effective_stats = {}
        for horse in all_runners:
            c_val = getattr(horse, "condition", 50.0)
            
            if horse.id == player_horse.id and j_arch == "The Whisperer" and j_lvl >= 7 and c_val < 40.0:
                c_val = 50.0 
                
            if c_val >= 80: c_mod = 1.10
            elif c_val >= 60: c_mod = 1.05
            elif c_val >= 40: c_mod = 1.0
            elif c_val >= 20: c_mod = 0.95
            else: c_mod = 0.90
            
            if horse.id != player_horse.id:
                spd_val = horse.cur_speed * c_mod
                sta_val = horse.cur_stamina * c_mod
                grt_val = horse.cur_grit * c_mod
            else:
                mod_cond = c_mod - 1.0
                # --- PULL DEBUFF FROM CONFIG. DEFAULTS TO 1.0 FOR UNDEFINED GENS ---
                gen_multiplier = GENERATION_MULTIPLIERS.get(getattr(horse, 'generation', 0), 1.0)
                mod_gen = gen_multiplier - 1.0
                
                mod_beer = 0.02 if getattr(horse, 'draft_beer_buff', False) else 0.0
                mod_mom = min(0.06, win_streak * 0.02) if win_streak > 0 else 0.0
                
                j_flat_spd = 0.0; j_flat_sta = 0.0; j_flat_grt = 0.0
                syn_spd_list = []; syn_sta_list = []; syn_grt_list = []
                
                if j_arch and j_arch != "Apprentice":
                    base_bonus = 1.0 if j_lvl < 5 else (2.0 if j_lvl < 9 else 3.0)
                    
                    if j_arch in ["The Aggressor", "The Turf Glider"]: j_flat_spd += base_bonus
                    elif j_arch in ["The Tactician", "The Mudlark"]: j_flat_sta += base_bonus
                    elif j_arch in ["The Iron Rider", "The Dirt Grinder"]: j_flat_grt += base_bonus
                    elif j_arch == "The Showman": 
                        j_flat_spd += (base_bonus * 0.5); j_flat_sta += (base_bonus * 0.5); j_flat_grt += (base_bonus * 0.5)
                        
                    if j_lvl >= 3:
                        if j_arch == "The Aggressor" and player_horse.running_style in ["Front-runner", "Start Dash"]:
                            syn_spd_list.append(0.05)
                        elif j_arch == "The Tactician" and player_horse.running_style in ["Last Spurt", "Stretch-runner"]:
                            syn_sta_list.append(0.05)
                        elif j_arch == "The Iron Rider" and player_horse.running_style == "Almighty":
                            syn_grt_list.append(0.05)
                        elif j_arch == "The Mudlark" and cond['name'] in ["Yielding", "Heavy"]:
                            syn_spd_list.append(0.05); syn_sta_list.append(0.05); syn_grt_list.append(0.05)
                        elif j_arch == "The Turf Glider" and surface == "Turf":
                            syn_spd_list.append(0.05)
                        elif j_arch == "The Dirt Grinder" and surface == "Dirt":
                            syn_grt_list.append(0.05)
                        elif j_arch == "The Showman" and player_horse.race_class == "G1":
                            syn_spd_list.append(0.10); syn_sta_list.append(0.10); syn_grt_list.append(0.10)
                            
                    if j_arch == "The Caretaker" and getattr(player_horse, "condition", 50.0) >= 80.0:
                        syn_spd_list.append(0.05); syn_sta_list.append(0.05); syn_grt_list.append(0.05)
                    if j_arch == "The Whisperer" and getattr(player_horse, "trust", 50.0) == 100.0:
                        syn_spd_list.append(0.05); syn_sta_list.append(0.05); syn_grt_list.append(0.05)
                        
                    if j_lvl >= 10:
                        syn_spd_list.append(0.03); syn_sta_list.append(0.03); syn_grt_list.append(0.03)

                # --- ⚙️ PULL TOGGLE FROM CONFIG ⚙️ ---
                if BUFF_MATH_MODE == "additive":
                    pool_spd = 1.0 + mod_cond + mod_gen + mod_beer + mod_mom + sum(syn_spd_list)
                    pool_sta = 1.0 + mod_cond + mod_gen + mod_beer + mod_mom + sum(syn_sta_list)
                    pool_grt = 1.0 + mod_cond + mod_gen + mod_beer + mod_mom + sum(syn_grt_list)
                    
                    spd_val = (horse.cur_speed + j_flat_spd) * max(0.1, pool_spd)
                    sta_val = (horse.cur_stamina + j_flat_sta) * max(0.1, pool_sta)
                    grt_val = (horse.cur_grit + j_flat_grt) * max(0.1, pool_grt)
                    
                else: 
                    spd_val = horse.cur_speed * (1.0 + mod_cond) * (1.0 + mod_gen) * (1.0 + mod_beer) * (1.0 + mod_mom)
                    sta_val = horse.cur_stamina * (1.0 + mod_cond) * (1.0 + mod_gen) * (1.0 + mod_beer) * (1.0 + mod_mom)
                    grt_val = horse.cur_grit * (1.0 + mod_cond) * (1.0 + mod_gen) * (1.0 + mod_beer) * (1.0 + mod_mom)
                    
                    spd_val += j_flat_spd
                    sta_val += j_flat_sta
                    grt_val += j_flat_grt
                    
                    for m in syn_spd_list: spd_val *= (1.0 + m)
                    for m in syn_sta_list: sta_val *= (1.0 + m)
                    for m in syn_grt_list: grt_val *= (1.0 + m)
            
            effective_stats[horse.id] = {
                "spd": spd_val,
                "sta": sta_val,
                "grt": grt_val,
                "cond_val": c_val,
                "trust_val": getattr(horse, 'trust', 50.0)
            }
            
        positions = {horse.id: 0.0 for horse in all_runners}
        
        staminas = {horse.id: 100.0 for horse in all_runners}
        max_staminas = {horse.id: 100.0 for horse in all_runners} 
        
        if paste_used:
            staminas[player_horse.id] = 150.0
            max_staminas[player_horse.id] = 150.0
            
        max_stamina_player = max_staminas[player_horse.id] 
        weather_penalty = cond["stam_mod"]
        
        if j_arch == "The Mudlark" and j_lvl >= 7 and weather_penalty > 1.0:
            weather_penalty = 1.0 
            
        has_iron = "Iron Breaker" in player_horse.titles or "Iron Breaker" in hof_buffs
        if has_iron and weather_penalty > 1.0: weather_penalty = 1.0 + ((weather_penalty - 1.0) / 2.0)
        if "Iron Lungs" in hof_buffs and weather_penalty > 1.0: weather_penalty = max(1.0, weather_penalty * 0.85)

        if cond['name'] == 'Firm/Fast' and ("Sun God" in player_horse.titles or "Sun God" in hof_buffs):
            weather_penalty = min(1.0, weather_penalty * 0.85) 
            
        has_void_walker = "Void Walker" in player_horse.titles or "Void Walker" in hof_buffs
        has_phantom_terror = "Phantom Terror" in player_horse.titles or "Phantom Terror" in hof_buffs
        has_golden_emperor = "Golden Emperor" in player_horse.titles or "Golden Emperor" in hof_buffs

        whip_count = 0; hold_count = 0 
        track_length = 40 
        
        has_shadow = "Shadow Slayer" in player_horse.titles or "Shadow Slayer" in hof_buffs
        has_storm = "Storm Chaser" in player_horse.titles or "Storm Chaser" in hof_buffs
        
        finished_order = []
        player_action_log = [] 
        
        tick_count = 0
        crossing_ticks = {}
        last_moves = {}

        tensions = {horse.id: 0.0 for horse in all_runners}
        horse_strains = {horse.id: 0 for horse in all_runners}
        fought_bit = False
        
        avg_spd = max(1.0, sum(effective_stats[h.id]["spd"] for h in all_runners) / len(all_runners))
        avg_grt = max(1.0, sum(effective_stats[h.id]["grt"] for h in all_runners) / len(all_runners))
        target_turns = 12.0 + (distance / 250.0) 
        target_mpt = distance / target_turns
        race_pace_scaler = target_mpt / avg_spd

        while True:
            self.clear_screen()
            remaining = max(0, distance - positions[player_horse.id])
            is_start = positions[player_horse.id] == 0.0
            pct_left = remaining / distance
            fought_bit = False
            
            print("\n" + "🏁"*32)
            print(f"{race_title.upper()} | {distance}m {surface}".center(64))
            print(f"Condition: {cond['icon']} {cond['name']} | PURSE: ${purse:,}".center(64))
            print("🏁"*32)
            
            for horse in all_runners:
                if horse in finished_order: progress = 1.0
                else: progress = positions[horse.id] / distance
                
                pos = min(track_length - 1, int(progress * track_length))
                track = ["-"] * track_length
                
                if horse.boss_title: track[pos] = "🔥" 
                else: track[pos] = "🐴" if horse.id == player_horse.id else "🐎"
                    
                style_abbr = horse.running_style[:4].upper() 
                
                c_val = effective_stats[horse.id]["cond_val"]
                if c_val >= 80: arrow = "↑"
                elif c_val >= 60: arrow = "↗"
                elif c_val >= 40: arrow = "→"
                elif c_val >= 20: arrow = "↘"
                else: arrow = "↓"
                
                print(f" {arrow} {horse.name[:10]:<10} [{style_abbr}] |{''.join(track)}|")
            print("="*64)
            
            current_stam = staminas[player_horse.id]
            if has_monitor:
                stam_str = f"Stamina: {current_stam:.0f} / {max_stamina_player:.0f}"
            else:
                stam_display = f"{(current_stam / max_stamina_player) * 100 if max_stamina_player > 0 else 0:.0f}%"
                stam_str = f"Stamina: {stam_display}"
                
            print(f" Distance: {remaining:.0f}m | {stam_str}".center(64))
            
            p_tension = tensions[player_horse.id]
            p_strain = horse_strains[player_horse.id]
            
            tension_bars = "■" * int(min(p_tension, 3.0) * 4)
            strain_bars = "■" * p_strain
            print(f"🔋 TENSION: [{tension_bars.ljust(12, '-')}]  |  💢 STRAIN: [{strain_bars.ljust(4, '-')}]".center(64))
            
            print(f"⭐ Style: {player_horse.running_style} ⭐".center(64)) 
            
            if chosen_jockey and j_arch != "Apprentice":
                print(f"✨ JOCKEY: {chosen_jockey['name']} ({j_arch} Lv.{j_lvl}) ✨".center(64))
            
            if win_streak >= 1:
                bonus_pct = min(6, win_streak * 2) 
                print(f"🔥 MOMENTUM: {win_streak} Win Streak (+{bonus_pct}%)! 🔥".center(64))
            
            if paste_used: 
                print("⚡ Electrolyte Paste (+100 Stam) ⚡".center(64))
            if getattr(player_horse, 'draft_beer_buff', False):
                print("🍺 LIQUID COURAGE: +2% All Stats! 🍺".center(64))
            
            p_wp, p_dp = False, False
            p_style = player_horse.running_style
            
            if p_style == "Front-runner":
                if 0.60 <= pct_left <= 0.75: p_wp = True
                elif 0.30 <= pct_left <= 0.45: p_dp = True
            elif p_style == "Start Dash":
                if 0.70 <= pct_left <= 0.85: p_wp = True
                elif 0.40 <= pct_left <= 0.55: p_dp = True
            elif p_style == "Stretch-runner":
                if 0.40 <= pct_left <= 0.55: p_wp = True
                elif 0.15 <= pct_left <= 0.30: p_dp = True
            elif p_style == "Last Spurt":
                if 0.30 <= pct_left <= 0.45: p_wp = True
                elif 0.10 <= pct_left <= 0.25: p_dp = True
            else: 
                if 0.50 <= pct_left <= 0.65: p_wp = True
                elif 0.20 <= pct_left <= 0.35: p_dp = True

            if is_start:
                print("\n" + "--- 🏇 GATES OPENING! ".ljust(64, "-"))
                print(" [1] ROCKET START (Massive burst, heavy drain)")
                print(" [2] SUPER START  (Strong burst, medium drain)")
                print(" [3] SNAP START   (Quick break, low drain)")
                print(" [4] COAST        (Conserve stamina out of the gate)")
                action = input("\nSelect Gate Command (1-4): ")
                
                if action == '1': player_action_log.extend([(1.0, '4'), (1.0, '4'), (1.0, '4')])
                elif action == '2': player_action_log.extend([(1.0, '4'), (1.0, '4')])
                elif action == '3': player_action_log.append((1.0, '4'))
                elif action == '4': player_action_log.append((1.0, '2'))
                
            else:
                print("\n" + "--- 🏇 JOCKEY COMMANDS ".ljust(64, "-"))
                if p_wp: print(" ⚡ SWEET SPOT: WHIPPING POINT (WP) REACHED! ⚡".center(64))
                if p_dp: print(" 🔥 SWEET SPOT: DASH POINT (DP) REACHED! 🔥".center(64))
                
                print(" [1] HOLD  (Pull back, charge TENSION with Grit)")
                print(" [2] COAST (Run naturally, clear STRAIN fast)") 
                print(" [3] URGE  (Moderate pace, steady drain)")
                print(" [4] WHIP  (Burst speed, consumes TENSION, builds STRAIN)") 
                action = input("\nSelect Command (1-4): ")
                player_action_log.append((pct_left, action))
            
            if action not in ['1', '2', '3', '4']: action = '2' 

            if not is_start:
                if p_style in ["Last Spurt", "Stretch-runner"] and pct_left > 0.60 and action in ['3', '4']:
                    if random.random() < 0.25: 
                        fought_bit = True
                        print(f"\n💢 {player_horse.name} is fighting the bit! (You told a Closer to sprint early!) 💢".center(64))
                        time.sleep(1.2)
                elif p_style in ["Front-runner", "Start Dash"] and pct_left > 0.70 and action == '1':
                    if random.random() < 0.25: 
                        fought_bit = True
                        print(f"\n💢 {player_horse.name} is fighting the bit! (You held back a Front-runner!) 💢".center(64))
                        time.sleep(1.2)
                elif action == '4' and p_tension > 0.5:
                    print(f"\n🚀 TENSION UNLEASHED! MASSIVE BURST! 🚀".center(64))
                    time.sleep(0.8)
                elif action == '4' and p_strain >= 3:
                    print(f"\n⚠️ MUSCLES BURNING! STRAIN OVERLOAD! ⚠️".center(64))
                    time.sleep(0.8)

            tick_count += 1

            for horse in all_runners:
                if horse in finished_order: continue 

                modifier = 0.8; stamina_drain = 0.0
                surface_mod = 1.05 if horse.preferred_surface == surface else 0.95
                
                h_pct_left = (distance - positions[horse.id]) / distance
                style = horse.running_style
                h_strain = horse_strains[horse.id]
                h_tension = tensions[horse.id]
                h_fought_bit = False
                
                h_spd = effective_stats[horse.id]["spd"]
                h_sta = max(1.0, effective_stats[horse.id]["sta"])
                h_grt = effective_stats[horse.id]["grt"]
                
                sta_drain_ratio = h_spd / h_sta
                
                is_wp, is_dp = False, False
                if style == "Front-runner":
                    if 0.60 <= h_pct_left <= 0.75: is_wp = True
                    elif 0.30 <= h_pct_left <= 0.45: is_dp = True
                elif style == "Start Dash":
                    if 0.70 <= h_pct_left <= 0.85: is_wp = True
                    elif 0.40 <= h_pct_left <= 0.55: is_dp = True
                elif style == "Stretch-runner":
                    if 0.40 <= h_pct_left <= 0.55: is_wp = True
                    elif 0.15 <= h_pct_left <= 0.30: is_dp = True
                elif style == "Last Spurt":
                    if 0.30 <= h_pct_left <= 0.45: is_wp = True
                    elif 0.10 <= h_pct_left <= 0.25: is_dp = True
                else: 
                    if 0.50 <= h_pct_left <= 0.65: is_wp = True
                    elif 0.20 <= h_pct_left <= 0.35: is_dp = True

                if horse.id == player_horse.id: 
                    horse_action = action
                    if fought_bit: h_fought_bit = True
                else:
                    stam_pct = staminas[horse.id] / max_staminas[horse.id] if max_staminas[horse.id] > 0 else 0
                    
                    if positions[horse.id] == 0.0:
                        if style in ["Start Dash", "Front-runner"]: horse_action = random.choice(['1', '2'])
                        elif style == "Almighty": horse_action = random.choice(['2', '3'])
                        else: horse_action = random.choice(['3', '4'])
                    else:
                        if h_strain >= 2: 
                            horse_action = '2' if random.random() < 0.7 else '1'
                        elif h_pct_left <= (300/distance) and staminas[horse.id] > 0: 
                            horse_action = '4' if h_tension > 0.5 or stam_pct > 0.1 else '3'
                        elif is_wp or is_dp: 
                            horse_action = '4' if stam_pct > 0.15 else '3'
                        else:
                            if style in ["Last Spurt", "Stretch-runner"] and h_pct_left > 0.5:
                                horse_action = '1' 
                            elif style in ["Front-runner", "Start Dash"] and h_pct_left > 0.6:
                                horse_action = '3' 
                            else:
                                horse_action = '2' if stam_pct < 0.4 else '3'

                if positions[horse.id] == 0.0: 
                    if horse_action == '1': modifier, stamina_drain = 3.5, 20.0
                    elif horse_action == '2': modifier, stamina_drain = 2.5, 12.0
                    elif horse_action == '3': modifier, stamina_drain = 1.5, 5.0
                    elif horse_action == '4': modifier, stamina_drain = 0.8, -3.0
                    
                    if horse.id == player_horse.id and style == "Front-runner":
                        if "Wind Rider" in player_horse.titles or "Wind Rider" in hof_buffs:
                            stamina_drain *= 0.5 
                            
                else: 
                    if horse_action == '1': 
                        modifier, stamina_drain = 0.4, -6.0 
                        if horse.id == player_horse.id: hold_count += 1
                        
                        if not h_fought_bit:
                            relative_grit = h_grt / avg_grt
                            tension_gain = 0.70 if (horse.id == player_horse.id and has_phantom_terror) else 0.35
                            
                            if horse.id == player_horse.id and j_arch == "The Tactician" and j_lvl >= 7:
                                tension_gain *= 1.30
                                
                            tensions[horse.id] = min(3.0, h_tension + (tension_gain * relative_grit))
                            
                        horse_strains[horse.id] = max(0, h_strain - 1)

                    elif horse_action == '2': 
                        modifier, stamina_drain = 0.8, -3.0 
                        horse_strains[horse.id] = max(0, h_strain - 2) 

                    elif horse_action == '3': 
                        modifier, stamina_drain = 1.0, 4.0
                        horse_strains[horse.id] = max(0, h_strain - 1)

                    elif horse_action == '4': 
                        modifier = 1.3 + (h_tension * 0.6) 
                        stamina_drain = 10.0 
                        
                        if horse.id == player_horse.id and j_arch == "The Dirt Grinder" and j_lvl >= 7 and surface == "Dirt":
                            modifier *= 1.15 
                            
                        if horse.id == player_horse.id and j_arch == "The Aggressor" and j_lvl >= 7 and h_pct_left >= 0.50:
                            stamina_drain *= 0.75 
                            
                        tensions[horse.id] = 0.0 
                        
                        if horse.id == player_horse.id: whip_count += 1
                        
                        if h_strain > 0:
                            modifier -= (h_strain * 0.20)
                            stamina_drain *= (1.0 + (h_strain * 0.40))
                            
                        horse_strains[horse.id] = min(4, h_strain + 1)
                        
                        if is_dp:
                            modifier += 0.5 
                            stamina_drain *= 0.50
                        elif is_wp:
                            modifier += 0.3 
                            stamina_drain *= 0.70

                if h_fought_bit:
                    modifier *= 0.7
                    stamina_drain = max(15.0, stamina_drain * 3.0)
                    tensions[horse.id] = 0.0

                if horse.id != player_horse.id:
                    modifier *= 0.95 

                if staminas[horse.id] <= 0:
                    if horse.id == player_horse.id and stamina_drain > 0: 
                        print("⚠️ EXHAUSTED! Stamina depleted! Speed reduced! ⚠️".center(64))
                    modifier = 0.55 
                    if stamina_drain > 0: stamina_drain = 0.0 
                    
                    if horse.id == player_horse.id and j_arch == "The Iron Rider" and j_lvl >= 7 and h_pct_left <= (400/distance):
                        modifier += (h_grt / max(1.0, h_spd)) * 0.50

                if horse.id == player_horse.id and has_shadow and h_pct_left <= (400/distance):
                    modifier += 0.10
                    
                if horse.id == player_horse.id and has_void_walker and h_pct_left <= (400/distance):
                    modifier += 0.15 
                    
                if horse.id == player_horse.id and has_storm and staminas[horse.id] <= 0:
                    modifier += (h_grt / (h_spd * 0.5)) 

                if h_pct_left <= (400/distance) and modifier >= 1.0 and staminas[horse.id] > 0:
                    trust_multiplier = 0.5 + (effective_stats[horse.id]["trust_val"] / 100.0)
                    modifier += (h_grt / h_spd) * trust_multiplier 

                move_amt = h_spd * modifier * surface_mod * cond["speed_mod"] * race_pace_scaler 
                last_moves[horse.id] = move_amt
                positions[horse.id] += move_amt
                
                if stamina_drain > 0: 
                    actual_drain = stamina_drain * sta_drain_ratio * weather_penalty 
                else: 
                    actual_drain = stamina_drain / weather_penalty 
                    
                staminas[horse.id] -= actual_drain
                staminas[horse.id] = min(max(-10.0, staminas[horse.id]), max_staminas[horse.id]) 
            
            just_finished = [h for h in all_runners if positions[h.id] >= distance and h not in finished_order]
            if just_finished:
                for h in just_finished:
                    over = positions[h.id] - distance
                    amt = max(0.1, last_moves.get(h.id, 1.0))
                    crossing_ticks[h.id] = tick_count - (over / amt)
                
                just_finished.sort(key=lambda h: crossing_ticks[h.id])
                for h in just_finished:
                    finished_order.append(h)

            if player_horse in finished_order:
                break
                
            if all(h in finished_order for h in opponents):
                self.clear_screen()
                print("\n" + "🏁"*32)
                print(f"{race_title.upper()} | {distance}m {surface}".center(64))
                print("\n" + "⚠️ All opponents have crossed the line!".center(64))
                print(f"🐎 {player_horse.name} slowly limps across the finish...".center(64))
                time.sleep(2)
                amt = max(0.1, last_moves.get(player_horse.id, 1.0))
                crossing_ticks[player_horse.id] = tick_count + ((distance - positions[player_horse.id]) / amt)
                finished_order.append(player_horse)
                break
            
            time.sleep(0.5) 
            
        for h in all_runners:
            if h not in finished_order:
                amt = max(0.1, last_moves.get(h.id, 1.0))
                crossing_ticks[h.id] = tick_count + ((distance - positions[h.id]) / amt)
                finished_order.append(h)
                
        finished_order.sort(key=lambda h: crossing_ticks[h.id])
        leaderboard = finished_order
        winner = leaderboard[0]

        base_m_s = 17.0 if surface == "Turf" else 16.6
        if cond['name'] == 'Good': base_m_s *= 0.98
        elif cond['name'] == 'Yielding': base_m_s *= 0.95
        elif cond['name'] == 'Heavy': base_m_s *= 0.90
        
        winner_time = distance / (base_m_s + random.uniform(-0.2, 0.2))
        winner_tick = crossing_ticks[winner.id]
        
        times = {}
        for h in leaderboard:
            tick_diff = max(0.0, crossing_ticks[h.id] - winner_tick)
            h_time = winner_time + (tick_diff * 0.25) 
            times[h.id] = h_time

        print("\n" + "🏆"*32)
        print(f"RACE OVER! The Winner is {winner.name}!".center(64))
        print("🏆"*32)
        
        print("\n  Pos | Horse Name         | Time    | Gap ")
        print("-" * 64)
        for i, h in enumerate(leaderboard):
            t_str = self.format_time(times[h.id])
            if i == 0: 
                gap_str = "-"
            else: 
                time_diff = times[h.id] - winner_time
                if time_diff <= 0.05: gap_str = "Nose"
                elif time_diff <= 0.15: gap_str = "Neck"
                elif time_diff <= 0.30: gap_str = "1/2"
                elif time_diff > 10.0: gap_str = "Dist" 
                else: gap_str = f"+{time_diff:.2f}s"
                
            print(f"  {i+1:<3} | {h.name[:18].ljust(18)} | {t_str} | {gap_str}")
            
        if stable_mgr:
            key = f"{distance}_{surface}"
            records = stable_mgr.load_data().get("national_records", {})
            old_rec = records.get(key, {}).get("time", 9999.9)
            if times[winner.id] < old_rec:
                print(f"\n🌟 NEW NATIONAL RECORD! {winner.name} ran {self.format_time(times[winner.id])}! 🌟")
                stable_mgr.update_national_record(key, times[winner.id], winner.name)
                time.sleep(1.5)

        player_placement = len(all_runners)
        for i, h in enumerate(leaderboard):
            if h.id == player_horse.id:
                player_placement = i + 1
                break
        
        earned_titles = []
        if is_special and player_placement == 1: earned_titles.append(selected_race["event_data"]["title"])
        if boss_in_race and player_placement == 1: earned_titles.append(boss_in_race.boss_title)
            
        history_entry = {
            "age": player_horse.age, "month": player_horse.month, "week": player_horse.week,
            "race_name": race_title, "distance": distance, "surface": surface,
            "condition": cond['name'], "placement": player_placement, "purse": purse,
            "field": [f"#{i+1} {h.name[:12]}" for i, h in enumerate(leaderboard)]
        }
        
        if not hasattr(player_horse, 'race_history'): player_horse.race_history = []
        player_horse.race_history.append(history_entry)
        
        if has_golden_emperor:
            purse = int(purse * 1.5)
            
        winnings, did_win = self._process_post_race(player_horse, player_action_log, player_placement, purse, surface, hof_buffs, chosen_jockey)
        return (winnings, did_win, player_placement), earned_titles, boss_in_race.name if boss_in_race else None, whip_count, hold_count

    def _process_post_race(self, horse, action_log, placement, purse, surface, hof_buffs, chosen_jockey):
        if getattr(horse, 'draft_beer_buff', False):
            horse.draft_beer_buff = False
            
        j_arch = chosen_jockey.get("archetype") if chosen_jockey else None
        j_lvl = chosen_jockey.get("level", 0) if chosen_jockey else 0
        
        fatigue_gain = random.uniform(*RACE_FATIGUE_RANGE)
        
        if surface == "Turf" and ("Turf Sovereign" in horse.titles or "Turf Sovereign" in hof_buffs):
            fatigue_gain *= 0.75 
            
        if j_arch == "The Turf Glider" and j_lvl >= 7 and surface == "Turf":
            fatigue_gain *= 0.75
            
        horse.fatigue = min(100.0, horse.fatigue + fatigue_gain)
        horse.condition = max(0.0, getattr(horse, 'condition', 50.0) - random.uniform(15.0, 25.0))
        horse.races_run += 1 
        
        if j_arch == "The Mercenary" and j_lvl >= 3:
            purse = int(purse * 1.25)
        
        winnings = 0
        did_win = (placement == 1)
        
        if placement == 1:
            horse.wins += 1
            winnings = purse
            print(f"\n🏆 {horse.name} takes the victory! Base Purse: ${winnings:,}")
            if horse.race_class == "Maiden": horse.race_class = "G3"
            elif horse.race_class == "G3" and horse.wins >= 3: horse.race_class = "G2"
            elif horse.race_class == "G2" and horse.wins >= 6 and horse.earnings >= 100000: horse.race_class = "G1"
            elif horse.race_class == "G1": horse.championships_won += 1 
        elif placement == 2:
            winnings = int(purse * 0.30)
            print(f"\n🥈 {horse.name} finished 2nd! Base Purse: ${winnings:,}")
        elif placement == 3:
            winnings = int(purse * 0.10)
            print(f"\n🥉 {horse.name} finished 3rd! Base Purse: ${winnings:,}")
        else:
            print(f"\n❌ {horse.name} finished {placement}th. Keep training!")

        if chosen_jockey and winnings > 0:
            cut = chosen_jockey.get("purse_cut", 0.0)
            if cut > 0:
                cut_amt = int(winnings * cut)
                winnings -= cut_amt
                print(f"   💸 Jockey Cut ({int(cut*100)}%): -${cut_amt:,}")
            print(f"   💰 Net to Owner: ${winnings:,}")
        elif winnings > 0:
            print(f"   💰 Net to Owner: ${winnings:,}")
            
        horse.earnings += winnings

        whips_start = sum(1 for p, a in action_log if p >= 0.85 and a == '4')
        whips_early = sum(1 for p, a in action_log if 0.6 <= p < 0.85 and a == '4')
        whips_late  = sum(1 for p, a in action_log if 0.25 <= p < 0.6 and a == '4')
        whips_spurt = sum(1 for p, a in action_log if p < 0.25 and a == '4')
        
        coasts_early = sum(1 for p, a in action_log if p >= 0.5 and a == '2')
        holds_early  = sum(1 for p, a in action_log if p >= 0.5 and a == '1')
        
        race_style = "Almighty"
        if whips_start >= 2 and whips_late <= 2 and whips_spurt <= 2:
            race_style = "Start Dash"
        elif (whips_start + whips_early) > (whips_late + whips_spurt) and (coasts_early > 0 or holds_early > 0):
            race_style = "Front-runner"
        elif whips_spurt >= 4 and (holds_early > 2 or coasts_early > 3):
            race_style = "Last Spurt"
        elif (whips_late + whips_spurt) > (whips_start + whips_early):
            race_style = "Stretch-runner"
            
        if not hasattr(horse, 'style_points'): horse.style_points = {}
        
        if race_style != horse.running_style:
            horse.style_points[race_style] = horse.style_points.get(race_style, 0) + 1
            if horse.style_points[race_style] >= 3:
                print(f"\n✨ STYLE SHIFT! {horse.name} has adapted to the [{race_style}] style based on your riding!")
                horse.running_style = race_style
                horse.style_points = {}
        else:
            horse.style_points = {} 
                
        return winnings, did_win