import random

class JockeyManager:
    @staticmethod
    def select_jockey(my_horse, selected_race, stable_mgr, upgrades, settings, clear_screen_func):
        """Handles the Jockey Selection UI and returns the chosen jockey dict (or None if cancelled)."""
        if not settings.get("jockey_system", True):
            # SYSTEM OFF: Returns a completely neutral rider with exactly 0% cut.
            return {"id": "apprentice", "name": "Standard Rider", "archetype": "Apprentice", "level": 0, "fee": 0, "purse_cut": 0.0}
            
        if not upgrades.get("jockey_guild", False):
            print("\n🏇 Your horse will be ridden by an Apprentice Rider (5% purse cut, no stat bonuses).")
            print("   (Unlock the Jockey Guild in the Store to hire professionals!)")
            input("Press Enter to head to the starting gate...")
            return {"id": "apprentice", "name": "Apprentice Rider", "archetype": "Apprentice", "level": 0, "fee": 0, "purse_cut": 0.05}

        while True:
            clear_screen_func()
            print("\n" + "🏇"*32)
            print("JOCKEY SELECTION".center(64))
            print("🏇"*32)
            print(f" Race  : {selected_race['distance']}m {selected_race['surface']} | Track: {selected_race['condition']['name']}")
            print(f" Horse : {my_horse.name} | Style: {my_horse.running_style}")
            print("-" * 64)
            
            roster = stable_mgr.get_jockey_roster()
            for idx, j in enumerate(roster):
                fee = 2500 if j["level"] < 2 else 0
                fee_str = f"${fee:,}" if fee > 0 else "WAIVED"
                cut = 10
                if j["level"] >= 10: cut = 5
                elif j["level"] >= 8: cut = 7
                
                focus = ""
                if j["archetype"] in ["The Aggressor", "The Turf Glider"]: focus = "Speed"
                elif j["archetype"] in ["The Tactician", "The Mudlark"]: focus = "Stamina"
                elif j["archetype"] in ["The Iron Rider", "The Dirt Grinder"]: focus = "Grit"
                elif j["archetype"] == "The Caretaker": focus = "Mood"
                elif j["archetype"] == "The Whisperer": focus = "Trust"
                elif j["archetype"] == "The Showman": focus = "Balanced"
                elif j["archetype"] == "The Mercenary": focus = "Greed"
                
                print(f" [{idx+1}] {j['name']} (Lv.{j['level']} {j['archetype']}) | Focus: {focus}")
                print(f"     Fee: {fee_str} | Purse Cut: {cut}% | Affin. XP: {j.get('xp', 0)}")
                
            print(f" [{len(roster)+1}] Apprentice Rider (Lv.0) | Focus: None")
            print(f"     Fee: $0 | Purse Cut: 5% | No Bonuses")
            print("-" * 64)
            print(" [Q] Cancel Race Entry")
            
            j_choice = input("\nSelect a Jockey: ").upper()
            if j_choice == 'Q' or j_choice == 'C':
                return None 
            elif j_choice.isdigit():
                choice_idx = int(j_choice) - 1
                if 0 <= choice_idx < len(roster):
                    selected_j = roster[choice_idx]
                    fee = 2500 if selected_j["level"] < 2 else 0
                    if stable_mgr.get_credits() < fee:
                        print(f"\n❌ You don't have enough funds to pay the ${fee:,} booking fee!")
                        input("Press Enter to continue...")
                        continue
                    else:
                        if fee > 0: stable_mgr.add_credits(-fee)
                        chosen_jockey = selected_j.copy() 
                        cut = 10
                        if chosen_jockey["level"] >= 10: cut = 5
                        elif chosen_jockey["level"] >= 8: cut = 7
                        chosen_jockey["purse_cut"] = cut / 100.0
                        chosen_jockey["fee"] = fee
                        return chosen_jockey
                elif choice_idx == len(roster):
                    return {"id": "apprentice", "name": "Apprentice Rider", "archetype": "Apprentice", "level": 0, "purse_cut": 0.05, "fee": 0}

    @staticmethod
    def apply_pre_race_buffs(my_horse, chosen_jockey):
        if not chosen_jockey or chosen_jockey["id"] == "apprentice": 
            return
            
        if chosen_jockey["archetype"] == "The Caretaker":
            boost = 10.0 if chosen_jockey["level"] < 5 else 15.0
            my_horse.condition = min(100.0, getattr(my_horse, 'condition', 50.0) + boost)
        elif chosen_jockey["archetype"] == "The Whisperer":
            boost = 10.0 if chosen_jockey["level"] < 5 else 15.0
            my_horse.trust = min(100.0, getattr(my_horse, 'trust', 50.0) + boost)

    @staticmethod
    def apply_post_race_effects(my_horse, chosen_jockey, did_win, is_special_race, stable_mgr):
        """Handles XP Leveling, Fatigue reduction, and returns the Injury multiplier."""
        injury_multiplier = 1.0
        
        if not chosen_jockey or chosen_jockey["id"] == "apprentice":
            return injury_multiplier
            
        # 1. Post-Race XP Progression (NOW ONLY TRIGGERS ON SPECIAL EVENT WINS)
        if did_win and is_special_race:
            roster = stable_mgr.get_jockey_roster()
            for j in roster:
                if j["id"] == chosen_jockey["id"]:
                    j["wins"] = j.get("wins", 0) + 1
                    j["xp"] = j.get("xp", 0) + 1
                    
                    # --- DOUBLED XP THRESHOLDS ---
                    level_thresholds = {1: 2, 2: 6, 3: 10, 4: 16, 5: 24, 6: 34, 7: 46, 8: 60, 9: 76, 10: 100}
                    current_lvl = j["level"]
                    if current_lvl < 10 and j["xp"] >= level_thresholds.get(current_lvl, 999):
                        j["level"] += 1
                        print(f"\n🌟 JOCKEY LEVEL UP! {j['name']} is now Affinity Level {j['level']}!")
                        if j["level"] == 3: print(f"   🔓 Unlocked Archetype Synergy!")
                        if j["level"] == 7: print(f"   🔓 Unlocked Signature Move!")
                    
                    stable_mgr.save_jockey(j)
                    break

        # 2. Fatigue Reduction Buffs (Lv 4+ General, or Caretaker Lv 3+)
        if chosen_jockey.get("level", 0) >= 4:
            my_horse.fatigue = max(0.0, my_horse.fatigue - 5.0)
        if chosen_jockey.get("archetype") == "The Caretaker" and chosen_jockey.get("level", 0) >= 3:
            my_horse.fatigue = max(0.0, my_horse.fatigue - 10.0)

        # 3. Caretaker Lv 7 Injury Protection
        if chosen_jockey.get("archetype") == "The Caretaker" and chosen_jockey.get("level", 0) >= 7:
            injury_multiplier = 0.25 
            
        return injury_multiplier