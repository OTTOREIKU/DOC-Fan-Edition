import random
from menus import clear_screen, dna_scanner, show_compendium, get_active_hof_buffs, show_race_history
from store import Store 
from random_events import EventManager 
from jockeys import JockeyManager
from config import STD_REST_FATG, STD_REST_MOOD, SPA_REST_FATG, SPA_REST_MOOD

def get_condition_arrow(cond):
    if cond >= 80: return "↑ Peak"
    elif cond >= 60: return "↗ Good"
    elif cond >= 40: return "→ Normal"
    elif cond >= 20: return "↘ Poor"
    else: return "↓ Terrible"

def get_trust_hearts(trust):
    filled = int(trust // 10)
    if trust == 100: filled = 10
    return "❤️" * filled + "🖤" * (10 - filled)

def evaluate_career_titles(horse):
    earned = []
    
    if horse.races_run >= 20 and getattr(horse, 'lifetime_injuries', 0) == 0: earned.append("Iron Horse")
    if horse.races_run >= 10 and horse.wins == horse.races_run: earned.append("Invincible")
    if horse.races_run >= 30: earned.append("Workhorse")
    
    turf_wins = sum(1 for r in getattr(horse, 'race_history', []) if r.get('surface') == 'Turf' and r.get('placement') == 1)
    dirt_wins = sum(1 for r in getattr(horse, 'race_history', []) if r.get('surface') == 'Dirt' and r.get('placement') == 1)
    if turf_wins >= 3 and dirt_wins >= 3: earned.append("Globetrotter")
    
    g1_wins_early = sum(1 for r in getattr(horse, 'race_history', []) if r.get('age', 9) <= 3 and r.get('placement') == 1 and r.get('purse', 0) >= 50000)
    if g1_wins_early >= 3: earned.append("Triple Crown")
    
    if horse.earnings >= 1000000: earned.append("High Roller")
    
    sprint_wins = sum(1 for r in getattr(horse, 'race_history', []) if r.get('distance', 0) <= 1200 and r.get('placement') == 1)
    if sprint_wins >= 5: earned.append("Sprint Specialist")
    
    marathon_wins = sum(1 for r in getattr(horse, 'race_history', []) if r.get('distance', 0) >= 2400 and r.get('placement') == 1)
    if marathon_wins >= 5: earned.append("Marathon Legend")
    
    late_g1_wins = sum(1 for r in getattr(horse, 'race_history', []) if r.get('age', 0) >= 6 and r.get('placement') == 1 and r.get('purse', 0) >= 50000)
    if late_g1_wins >= 2: earned.append("Late Bloomer")
    
    new_titles = [t for t in earned if t not in horse.titles]
    if new_titles:
        print("\n" + "🏅"*32)
        print("CAREER ACHIEVEMENTS UNLOCKED UPON RETIREMENT!".center(64))
        for t in new_titles:
            horse.titles.append(t)
            print(f" -> [{t}]".center(64))
        print("🏅"*32 + "\n")
        input("Press Enter to continue...")

def handle_post_race_interaction(horse, placement, whips, holds, fatigue, chosen_jockey=None):
    print("\n" + "🐴"*32)
    
    context = "Neutral"
    
    if fatigue >= 85.0:
        context = "Exhausted"
        state_text = "Head hanging low, sides heaving. They are dead on their feet."
        options = ["Give Space", "Deep Grooming", "Gentle Apology", "Hand-Grazing"]
    elif whips >= 5 and placement > 1:
        if chosen_jockey and chosen_jockey.get("archetype") == "The Whisperer" and chosen_jockey.get("level", 0) >= 3:
            context = "Overwhelmed"
            state_text = "Looking defeated, but The Whisperer kept them from becoming resentful of the whip."
            options = ["Vocal Praise", "Deep Grooming", "Gentle Apology", "Give Space"]
        else:
            context = "Resentful"
            state_text = "Ears pinned back and glaring. They resented the harsh ride."
            options = ["Gentle Apology", "Give Space", "Firm Correction", "Hand-Grazing"]
    elif holds >= 3 and placement in [2, 3, 4]:
        context = "Frustrated"
        state_text = "Agitated and tossing their head. They got boxed in and wanted to run."
        options = ["Hand-Grazing", "Give Space", "Firm Correction", "Vocal Praise"]
    elif placement == 1:
        context = "Fired Up"
        state_text = "Dancing around the enclosure! They know they just won!"
        options = ["Vocal Praise", "Hand-Grazing", "Give Space", "Deep Grooming"]
    else:
        context = "Overwhelmed"
        state_text = "Looking defeated and unsure of themselves after a tough run."
        options = ["Vocal Praise", "Deep Grooming", "Gentle Apology", "Give Space"]

    p_type = getattr(horse, 'personality', 'Willing')
    legacy_map = {"Honest": "Willing", "Coward": "Anxious", "Sloppy": "Willing", "Rough": "Hot-Blooded", "Imposing": "Alpha"}
    if p_type in legacy_map:
        p_type = legacy_map[p_type]
        horse.personality = p_type 

    print(f"🐎 {horse.name} [\033[96m{p_type}\033[0m]")
    print(f"   State: \033[93m{state_text}\033[0m")
    print(f"   Race stats: Whips: {whips} | Holds: {holds} | Fatigue: {fatigue:.1f}%")
    print("-" * 64)
    print("What will you do in the saddling enclosure?")
    
    print(f" [1] {options[0].ljust(18)} [3] {options[2].ljust(18)}")
    print(f" [2] {options[1].ljust(18)} [4] {options[3].ljust(18)}")
    
    choice = input("\nSelect horsemanship action (1-4): ")
    selected_action = options[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= 4 else options[1]
    
    reactions = {
        "Vocal Praise":    {"Willing": 15, "Hot-Blooded": -5, "Anxious": 10, "Stoic": -5, "Alpha": 0},
        "Deep Grooming":   {"Willing": 10, "Hot-Blooded": -10, "Anxious": 20, "Stoic": -5, "Alpha": -5},
        "Give Space":      {"Willing": 5, "Hot-Blooded": 15, "Anxious": -10, "Stoic": 20, "Alpha": 10},
        "Hand-Grazing":    {"Willing": 10, "Hot-Blooded": 15, "Anxious": 5, "Stoic": 10, "Alpha": 10},
        "Gentle Apology":  {"Willing": 15, "Hot-Blooded": -10, "Anxious": 20, "Stoic": -5, "Alpha": -15},
        "Firm Correction": {"Willing": -20, "Hot-Blooded": 10, "Anxious": -30, "Stoic": -10, "Alpha": 15},
    }
    
    base_trust_change = reactions.get(selected_action, {}).get(p_type, 0)
    
    if selected_action == "Firm Correction" and context not in ["Resentful", "Frustrated"]:
        base_trust_change -= 20 
    if selected_action == "Gentle Apology" and context == "Exhausted":
        base_trust_change += 5
        
    streak = getattr(horse, 'bad_interaction_streak', 0)
    
    if base_trust_change > 0:
        trust_change = base_trust_change
        horse.bad_interaction_streak = 0 
        print(f"\n💖 Excellent horsemanship! {selected_action} was exactly what a {p_type} horse needed.")
        horse.condition = min(100.0, horse.condition + 15.0)
        
    elif base_trust_change < 0:
        if chosen_jockey and chosen_jockey.get("level", 0) >= 6:
            trust_change = 0
            print(f"\n🐴 A poor choice, but {chosen_jockey['name']} expertly handled the horse for you. No trust lost!")
        else:
            trust_change = base_trust_change - (streak * 5.0) 
            horse.bad_interaction_streak = streak + 1
            print(f"\n💢 Terrible decision. A {p_type} horse actively hates {selected_action} in this state.")
            if streak > 0: print(f"⚠️ {horse.name} is losing all respect for you! (Bonus Penalty applied)")
            horse.condition = max(0.0, horse.condition - 15.0)
    else:
        trust_change = 0
        print(f"\n🐴 You chose {selected_action}. {horse.name} doesn't seem to care much either way.")
        
    horse.trust = max(0.0, min(100.0, getattr(horse, 'trust', 50.0) + trust_change))
    print("🐴"*32)
    input("\nPress Enter to continue to Feeding...")

def manage_active_horse(my_horse, facility, race_engine, stable_mgr, events_db, spawner):
    event_mgr = EventManager() 
    
    while True:
        clear_screen()
        upgrades = stable_mgr.get_upgrades()
        hof_buffs = get_active_hof_buffs(stable_mgr)
        settings = stable_mgr.get_settings()
        
        if my_horse.week == 1:
            if upgrades.get('advanced_walker'):
                my_horse.fatigue = max(0.0, my_horse.fatigue - 35.0)
            elif upgrades.get('auto_walker'):
                my_horse.fatigue = max(0.0, my_horse.fatigue - 20.0)
        
        if my_horse.month > 12:
            my_horse.month, my_horse.week = 1, 1
            my_horse.age += 1
            print(f"\n🎂 Happy Birthday! {my_horse.name} is now Age {my_horse.age}!")
            
            if my_horse.age == 4:
                if my_horse.gender == "Colt":
                    my_horse.gender = "Stallion"
                    print(f"🐎 {my_horse.name} has fully matured into a Stallion!")
                elif my_horse.gender == "Filly":
                    my_horse.gender = "Mare"
                    print(f"🐎 {my_horse.name} has fully matured into a Mare!")
            
            if my_horse.age > 8:
                print(f"\n👴 {my_horse.name} is too old to race. Retiring to the Farm.")
                evaluate_career_titles(my_horse) 
                my_horse.is_retired = True
                stable_mgr.save_horse(my_horse)
                input("\nPress Enter to return...")
                return 

        max_w = 5 if my_horse.month in [3, 6, 9, 12] else 4
        countdown = max_w - my_horse.week
        countdown_str = f"(Race in {countdown})" if countdown > 0 else "(Race Week!)"

        print("\n" + "📅"*32)
        print(f"AGE {my_horse.age} | MONTH {my_horse.month} | WEEK {my_horse.week} {countdown_str}".center(64))
        print("📅"*32)
        
        print(f" Name  : {my_horse.name} [{my_horse.race_class}]")
        print(f" Style : {my_horse.running_style} | Pref: {my_horse.preferred_surface}")
        print(f" Vitals: Fatigue {my_horse.fatigue:.1f}% | Mood: {get_condition_arrow(getattr(my_horse, 'condition', 50.0))}")
        print(f" Record: {my_horse.wins}-{my_horse.races_run - my_horse.wins} | Trust: {get_trust_hearts(getattr(my_horse, 'trust', 50.0))}")
        print(f" Stats : Spd {my_horse.cur_speed:.1f} | Sta {my_horse.cur_stamina:.1f} | Grt {my_horse.cur_grit:.1f}")
        print("-" * 64)
        
        if my_horse.injury_weeks > 0:
            print(f"⚕️  {my_horse.name} is INJURED ({my_horse.injury_weeks} weeks remaining).")
            inv = stable_mgr.get_inventory()
            action = input("Press [Enter] to Rest, or [2] to use Miracle Salve: ")
            if action == '2' and inv.get('salve', 0) > 0:
                stable_mgr.add_item('salve', -1)
                my_horse.injury_weeks = 0
                print(f"✨ {my_horse.name} is instantly cured!")
                stable_mgr.save_horse(my_horse)
                input("\nPress Enter to continue...")
                continue
            else:
                rest_fatg = SPA_REST_FATG if upgrades.get('luxury_spa') else STD_REST_FATG
                rest_mood = SPA_REST_MOOD if upgrades.get('luxury_spa') else STD_REST_MOOD
                
                my_horse.fatigue = max(0.0, my_horse.fatigue - rest_fatg)
                my_horse.condition = min(100.0, getattr(my_horse, 'condition', 50.0) + rest_mood) 
                
                my_horse.injury_weeks -= 1
                my_horse.week += 1
                my_horse.current_race_card = [] 
                
                max_w = 5 if my_horse.month in [3, 6, 9, 12] else 4
                if my_horse.week > max_w: 
                    my_horse.week = 1
                    my_horse.month += 1
                    stable_mgr.refresh_all_markets(spawner)
                    stable_mgr.decrement_stud_timer(spawner) 
                    
                    payout = stable_mgr.process_academy_payouts()
                    if payout > 0:
                        print(f"\n🎓 The Riding Academy generated ${payout:,} this month!")
                        
                    trained, finished = stable_mgr.auto_train_benched(my_horse.id)
                    if trained or finished:
                        if trained: print(f"\n👨‍🏫 Assistant Trainer passively trained: {', '.join(trained)}")
                        if finished:
                            for fh in finished: print(f"🎓 {fh} has finished its assistant training program!")
                        input("Press Enter to continue...")

                stable_mgr.save_horse(my_horse) 
                continue

        if my_horse.week == max_w:
            special_event = events_db.get_event(my_horse)
            if special_event and my_horse.race_class in special_event["req_classes"]:
                print(f"⭐ SPECIAL EVENT AVAILABLE: {special_event['name']} ⭐")
            
            if not my_horse.current_race_card:
                my_horse.current_race_card = race_engine.generate_race_card(
                    my_horse.race_class, 
                    special_event if my_horse.race_class in (special_event["req_classes"] if special_event else []) else None
                )
                stable_mgr.save_horse(my_horse) 
            
            print("🏁"*32)
            print("IT IS RACE WEEK!".center(64))
            print("🏁"*32)
            
            print(" [1] View Race Card          [8] View Compendium")
            print(" [2] Rest in Stable          [9] View Race History")
            print(" [3] Retire Horse            [I] Open Inventory")
            print(" [7] Run DNA Scanner         [S] Visit Store")
            print("-" * 64)
            print(" [Q] Back to Stable")
            
            action = input("\nSelect option: ").upper()
            
            if action == 'Q': stable_mgr.save_horse(my_horse); return
            elif action == 'S': 
                Store(stable_mgr).enter()
                continue
            elif action == '7':
                dna_scanner(my_horse, upgrades, stable_mgr) 
                continue
            elif action == '8':
                show_compendium(stable_mgr) 
                continue
            elif action == '9':
                show_race_history(my_horse)
                continue
            elif action == '3':
                if my_horse.age < 4:
                    print(f"\n❌ {my_horse.name} is only Age {my_horse.age}! Horses must be at least Age 4 to retire to the Farm.")
                    input("\nPress Enter to continue...")
                    continue
                confirm = input("Are you sure? Retired horses can NEVER race again! (Y/N): ")
                if confirm.upper() == 'Y':
                    evaluate_career_titles(my_horse) 
                    my_horse.is_retired = True
                    stable_mgr.save_horse(my_horse)
                    print(f"\n🏡 {my_horse.name} has been retired to the Farm.")
                    input("\nPress Enter to return...")
                    return
                continue
            elif action == 'I':
                while True:
                    clear_screen()
                    inv = stable_mgr.get_inventory()
                    cred = stable_mgr.get_credits()
                    
                    print("\n" + "🎒"*32)
                    print("STABLE INVENTORY".center(64))
                    print("🎒"*32)
                    print(f"💰 Funds: ${cred:,}\n".center(64))
                    
                    print(f" [1] Premium Oats       : x{inv.get('oats', 0)}  (-30 Fatigue, +10 Mood)")
                    print(f" [2] Peppermint Treats  : x{inv.get('mints', 0)} (+25 Mood)")
                    print(f" [3] Sprint Vitamins    : x{inv.get('vit_spd', 0)} (+0.5 Speed Potential)")
                    print(f" [4] Endurance Vitamins : x{inv.get('vit_sta', 0)} (+0.5 Stamina Potential)")
                    print(f" [5] Power Vitamins     : x{inv.get('vit_grt', 0)} (+0.5 Grit Potential)")
                    
                    print(f" [6] Fruit Basket       : x{inv.get('fruit_basket', 0)}  (+1.0 All Stats)")
                    print(f" [7] Draft Beer         : x{inv.get('draft_beer', 0)}  (Max Trust/Mood, +Fatigue)")
                    print(f" [8] Golden Alfalfa     : x{inv.get('gold_alfalfa', 0)}  (Zero Fatigue)")
                    
                    print("-" * 64)
                    print(f" [ ] Miracle Salve      : x{inv.get('salve', 0)}  (Used when injured)")
                    print(f" [ ] Electrolyte Paste  : x{inv.get('paste', 0)}  (Used before races)")
                    print(f" [ ] Track Bribe        : x{inv.get('bribe', 0)}  (Used before races)")
                    print(f" [ ] Breeding Supp.     : x{inv.get('breed_supp', 0)} (Used in breeding)")
                    print("-" * 64)
                    print(" [Q] Back to Stable")
                    
                    use_choice = input("\nSelect option: ").upper()
                    
                    if use_choice == 'Q': break
                    elif use_choice == '1':
                        if inv.get('oats', 0) > 0:
                            stable_mgr.add_item('oats', -1)
                            my_horse.fatigue = max(0.0, my_horse.fatigue - 30.0)
                            my_horse.condition = min(100.0, getattr(my_horse, 'condition', 50.0) + 10.0)
                            stable_mgr.save_horse(my_horse)
                            print(f"\n🍎 {my_horse.name} ate the oats! Fatigue dropped to {my_horse.fatigue:.1f}% and Mood improved!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Premium Oats!")
                            input("Press Enter to continue...")
                    elif use_choice == '2':
                        if inv.get('mints', 0) > 0:
                            stable_mgr.add_item('mints', -1)
                            my_horse.condition = min(100.0, getattr(my_horse, 'condition', 50.0) + 25.0)
                            stable_mgr.save_horse(my_horse)
                            print(f"\n🍬 {my_horse.name} loved the mints! Mood improved significantly!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Peppermint Treats!")
                            input("Press Enter to continue...")
                    elif use_choice == '3':
                        if inv.get('vit_spd', 0) > 0:
                            if my_horse.cur_speed >= my_horse.pot_speed:
                                print(f"\n❌ {my_horse.name} has already reached their maximum genetic Speed!")
                            else:
                                stable_mgr.add_item('vit_spd', -1)
                                my_horse.cur_speed = min(my_horse.pot_speed, my_horse.cur_speed + 0.5)
                                stable_mgr.save_horse(my_horse)
                                print(f"\n⚡ {my_horse.name} ate the Sprint Vitamins! Speed increased!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Sprint Vitamins!")
                            input("Press Enter to continue...")
                    elif use_choice == '4':
                        if inv.get('vit_sta', 0) > 0:
                            if my_horse.cur_stamina >= my_horse.pot_stamina:
                                print(f"\n❌ {my_horse.name} has already reached their maximum genetic Stamina!")
                            else:
                                stable_mgr.add_item('vit_sta', -1)
                                my_horse.cur_stamina = min(my_horse.pot_stamina, my_horse.cur_stamina + 0.5)
                                stable_mgr.save_horse(my_horse)
                                print(f"\n🛡️ {my_horse.name} ate the Endurance Vitamins! Stamina increased!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Endurance Vitamins!")
                            input("Press Enter to continue...")
                    elif use_choice == '5':
                        if inv.get('vit_grt', 0) > 0:
                            if my_horse.cur_grit >= my_horse.pot_grit:
                                print(f"\n❌ {my_horse.name} has already reached their maximum genetic Grit!")
                            else:
                                stable_mgr.add_item('vit_grt', -1)
                                my_horse.cur_grit = min(my_horse.pot_grit, my_horse.cur_grit + 0.5)
                                stable_mgr.save_horse(my_horse)
                                print(f"\n🔥 {my_horse.name} ate the Power Vitamins! Grit increased!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Power Vitamins!")
                            input("Press Enter to continue...")
                    elif use_choice == '6':
                        if inv.get('fruit_basket', 0) > 0:
                            stable_mgr.add_item('fruit_basket', -1)
                            my_horse.cur_speed = min(my_horse.pot_speed, my_horse.cur_speed + 1.0)
                            my_horse.cur_stamina = min(my_horse.pot_stamina, my_horse.cur_stamina + 1.0)
                            my_horse.cur_grit = min(my_horse.pot_grit, my_horse.cur_grit + 1.0)
                            stable_mgr.save_horse(my_horse)
                            print(f"\n🧺 {my_horse.name} devoured the Fruit Basket! Massive stat gains across the board!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Champion's Fruit Baskets!")
                            input("Press Enter to continue...")
                    elif use_choice == '7':
                        if inv.get('draft_beer', 0) > 0:
                            stable_mgr.add_item('draft_beer', -1)
                            
                            if getattr(my_horse, 'trust', 50.0) >= 100.0 and getattr(my_horse, 'condition', 50.0) >= 100.0:
                                my_horse.draft_beer_buff = True
                                print(f"\n🍺 GULP GULP GULP... {my_horse.name} is fully confident! They gained Liquid Courage (+2% All Stats for next race)!")
                            else:
                                print(f"\n🍺 GULP GULP GULP... {my_horse.name} drank the whole bucket! Trust and Mood maxed out, but they look a little sleepy.")
                                
                            my_horse.trust = 100.0
                            my_horse.condition = 100.0
                            my_horse.bad_interaction_streak = 0
                            my_horse.fatigue = min(100.0, my_horse.fatigue + 15.0)
                            stable_mgr.save_horse(my_horse)
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Draft Beer!")
                            input("Press Enter to continue...")
                    elif use_choice == '8':
                        if inv.get('gold_alfalfa', 0) > 0:
                            stable_mgr.add_item('gold_alfalfa', -1)
                            my_horse.fatigue = 0.0
                            my_horse.condition = min(100.0, my_horse.condition + 50.0)
                            stable_mgr.save_horse(my_horse)
                            print(f"\n🌾 The legendary Golden Alfalfa! {my_horse.name}'s muscles instantly recover. Fatigue is completely gone!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Golden Alfalfa!")
                            input("Press Enter to continue...")
                    else:
                        input("\nInvalid choice. Press Enter...")
                continue
                
            elif action == '1':
                if my_horse.fatigue >= 80:
                    print(f"\n⚠️ {my_horse.name} is exhausted! Forcing rest.")
                    rest_fatg = SPA_REST_FATG if upgrades.get('luxury_spa') else STD_REST_FATG
                    rest_mood = SPA_REST_MOOD if upgrades.get('luxury_spa') else STD_REST_MOOD
                    
                    my_horse.fatigue = max(0.0, my_horse.fatigue - rest_fatg)
                    my_horse.condition = min(100.0, getattr(my_horse, 'condition', 50.0) + rest_mood)
                    input("\nPress Enter to continue...")
                    
                    my_horse.week = 1
                    my_horse.month += 1
                    my_horse.current_race_card = []
                    stable_mgr.refresh_all_markets(spawner)
                    stable_mgr.decrement_stud_timer(spawner) 
                    
                    payout = stable_mgr.process_academy_payouts()
                    if payout > 0: print(f"\n🎓 The Riding Academy generated ${payout:,} this month!")
                        
                    trained, finished = stable_mgr.auto_train_benched(my_horse.id)
                    if trained or finished:
                        if trained: print(f"\n👨‍🏫 Assistant Trainer passively trained: {', '.join(trained)}")
                        if finished:
                            for fh in finished: print(f"🎓 {fh} has finished its assistant training program!")
                        input("Press Enter to continue...")
                        
                    stable_mgr.save_horse(my_horse)
                    continue
                else:
                    while True:
                        clear_screen()
                        print("\n" + "🎫"*32)
                        print(f"MONTH {my_horse.month} RACE CARD ({my_horse.race_class})".center(64))
                        print("🎫"*32)
                        for i, race in enumerate(my_horse.current_race_card):
                            evt = "⭐ " if race.get("is_special") else ""
                            cond = race['condition']
                            print(f" [{i + 1}] {evt}{race['distance']}m | {race['surface']} | {cond['icon']} {cond['name']} | Purse: ${race['purse']:,}")
                        
                        inv = stable_mgr.get_inventory()
                        print("-" * 64)
                        print(" [R] Reroll Card (Requires Track Bribe) | [Q] Cancel")
                        r_choice = input("\nSelect race (1-3) or option: ").upper()
                        
                        if r_choice == 'R':
                            if inv.get('bribe', 0) > 0:
                                stable_mgr.add_item('bribe', -1)
                                print("💸 You bribed the officials. Rerolling card...")
                                my_horse.current_race_card = race_engine.generate_race_card(
                                    my_horse.race_class, 
                                    special_event if my_horse.race_class in (special_event["req_classes"] if special_event else []) else None
                                )
                                stable_mgr.save_horse(my_horse)
                                input("Press Enter to continue...")
                                continue
                            else: 
                                print("❌ You don't have any Track Bribes!")
                                input("Press Enter to continue...")
                                continue
                        elif r_choice in ['1', '2', '3']:
                            selected_race = my_horse.current_race_card[int(r_choice) - 1]
                            
                            chosen_jockey = JockeyManager.select_jockey(my_horse, selected_race, stable_mgr, upgrades, settings, clear_screen)
                            if not chosen_jockey:
                                continue 
                                
                            JockeyManager.apply_pre_race_buffs(my_horse, chosen_jockey)
                            
                            paste_used = False
                            if inv.get('paste', 0) > 0:
                                p = input("\nUse Electrolyte Paste for +100 Stamina? (Y/N): ").upper()
                                if p == 'Y': stable_mgr.add_item('paste', -1); paste_used = True
                                
                            try:
                                race_results = race_engine.run_race(
                                    my_horse, selected_race, upgrades.get('heart_monitor', False), 
                                    upgrades.get('premium_saddles', False), paste_used, hof_buffs, stable_mgr, chosen_jockey
                                )
                            except TypeError:
                                print("\n[SYSTEM] Please upload 'race_engine.py' next to fully activate the Jockey System!")
                                race_results = race_engine.run_race(
                                    my_horse, selected_race, upgrades.get('heart_monitor', False), 
                                    upgrades.get('premium_saddles', False), paste_used, hof_buffs, stable_mgr
                                )
                                
                            (winnings, did_win, placement), earned_titles, boss_encountered, true_whips, true_holds = race_results
                            
                            if boss_encountered:
                                stable_mgr.add_seen_boss(boss_encountered)
                                print(f"\n🔥 You raced against a Legendary Rival: {boss_encountered}! Check the Compendium for details.")
                            
                            if winnings > 0: stable_mgr.add_credits(winnings)
                            
                            for t in earned_titles:
                                if t and t not in my_horse.titles:
                                    my_horse.titles.append(t)
                                    print(f"\n🏆 LEGENDARY ACCOMPLISHMENT! {my_horse.name} earned the title: {t}!")
                            
                            injury_multiplier = JockeyManager.apply_post_race_effects(my_horse, chosen_jockey, did_win, selected_race.get('is_special', False), stable_mgr)
                            
                            injury_chance = 0.01 + (max(0, my_horse.fatigue - 50) / 400.0)
                            if "Dream Weaver" in my_horse.titles or "Dream Weaver" in hof_buffs:
                                injury_chance /= 2.0 
                                
                            injury_chance *= injury_multiplier 
                                
                            if random.random() < injury_chance: 
                                base_inj = random.randint(1, 2)
                                my_horse.injury_weeks = max(1, base_inj - 1) if upgrades.get("vet_clinic") else base_inj
                                if not hasattr(my_horse, 'lifetime_injuries'): my_horse.lifetime_injuries = 0
                                my_horse.lifetime_injuries += 1 
                                
                            input("\nPress Enter to continue to the Saddling Enclosure...")
                            
                            handle_post_race_interaction(my_horse, placement, true_whips, true_holds, my_horse.fatigue, chosen_jockey)
                                
                            race_drops = {"fruit_basket": 0, "draft_beer": 0, "gold_alfalfa": 0}
                            
                            if did_win and (selected_race["purse"] >= 100000 or selected_race.get("is_special", False)):
                                if random.random() < 0.35: 
                                    drop = random.choice(["fruit_basket", "draft_beer", "gold_alfalfa"])
                                    
                                    multiplier = 1
                                    if chosen_jockey and chosen_jockey.get("archetype") == "The Mercenary" and chosen_jockey.get("level", 0) >= 7:
                                        multiplier = 2
                                        print(f"\n💰 The Mercenary (Lv.7) intimidated the fan into handing over a SECOND gift!")
                                        
                                    stable_mgr.add_item(drop, multiplier)
                                    race_drops[drop] += multiplier
                                    drop_names = {"fruit_basket": "Champion's Fruit Basket 🧺", "draft_beer": "Draft Beer 🍺", "gold_alfalfa": "Golden Alfalfa 🌾"}
                                    print(f"\n🎁 A wealthy fan was so impressed by your win, they gifted you: {multiplier}x {drop_names[drop]}!")
                            
                            print("\n" + "--- 🍎 POST-RACE FEEDING 🥕 ".ljust(64, "-"))
                            
                            print(" [1] Apple (Spd) | [2] Carrot (Sta) | [3] Sugar (Grt)")
                            
                            if race_drops["fruit_basket"] > 0: print(" [F] Fruit Basket (Just Received!) - +1.0 All Stats")
                            if race_drops["draft_beer"] > 0: print(" [B] Draft Beer (Just Received!) - Max Trust & Mood, +15% Fatg")
                            if race_drops["gold_alfalfa"] > 0: print(" [G] Golden Alfalfa (Just Received!) - Zero Fatigue, +50 Mood")
                            
                            if not hasattr(my_horse, 'favorite_food'): my_horse.favorite_food = random.choice(["1", "2", "3"])
                            f_choice = input("\nSelect feed (1-3, or special letter): ").upper()
                            
                            if f_choice == 'F' and race_drops["fruit_basket"] > 0:
                                stable_mgr.add_item("fruit_basket", -1)
                                my_horse.cur_speed = min(my_horse.pot_speed, my_horse.cur_speed + 1.0)
                                my_horse.cur_stamina = min(my_horse.pot_stamina, my_horse.cur_stamina + 1.0)
                                my_horse.cur_grit = min(my_horse.pot_grit, my_horse.cur_grit + 1.0)
                                print("\n🧺 They devoured the Fruit Basket! Massive stat gains across the board!")
                            elif f_choice == 'B' and race_drops["draft_beer"] > 0:
                                stable_mgr.add_item("draft_beer", -1)
                                
                                if getattr(my_horse, 'trust', 50.0) >= 100.0 and getattr(my_horse, 'condition', 50.0) >= 100.0:
                                    my_horse.draft_beer_buff = True
                                    print("\n🍺 GULP GULP GULP... They are fully confident! They gained Liquid Courage (+2% All Stats for next race)!")
                                else:
                                    print("\n🍺 GULP GULP GULP... They drank the whole bucket! Trust and Mood maxed out, but they look a little sleepy.")
                                    
                                my_horse.trust = 100.0
                                my_horse.condition = 100.0
                                my_horse.bad_interaction_streak = 0
                                my_horse.fatigue = min(100.0, my_horse.fatigue + 15.0)
                            elif f_choice == 'G' and race_drops["gold_alfalfa"] > 0:
                                stable_mgr.add_item("gold_alfalfa", -1)
                                my_horse.fatigue = 0.0
                                my_horse.condition = min(100.0, my_horse.condition + 50.0)
                                print("\n🌾 The legendary Golden Alfalfa! Their muscles instantly recover. Fatigue is completely gone!")
                            else:
                                if f_choice not in ['1', '2', '3']: f_choice = random.choice(['1', '2', '3']) 
                                food_boost = 1.5 if did_win else 0.5
                                
                                if f_choice == my_horse.favorite_food:
                                    print("\n💖 They LOVED it! You hit their exact flavor profile! (2x Stat Gain & Massive Mood Boost!)")
                                    food_boost *= 2.0
                                    my_horse.condition = min(100.0, getattr(my_horse, 'condition', 50.0) + 30.0)
                                else:
                                    print("\n🐴 They ate it, but it clearly wasn't their favorite. (Small Mood Boost)")
                                    my_horse.condition = min(100.0, getattr(my_horse, 'condition', 50.0) + 10.0)
                                    
                                t_stat = "cur_speed" if f_choice == '1' else "cur_stamina" if f_choice == '2' else "cur_grit"
                                c_val = getattr(my_horse, t_stat)
                                p_val = getattr(my_horse, t_stat.replace('cur_', 'pot_'))
                                room = 1.0 - (c_val / p_val) if p_val > 0 else 0
                                gain = food_boost * max(0.01, room)
                                setattr(my_horse, t_stat, c_val + gain)
                                
                                reward_text = "✨ WINNER'S BONUS APPLIED!" if did_win else ""
                                print(f"✨ +{gain:.2f} {t_stat.replace('cur_', '').capitalize()}! {reward_text}")
                            
                            event_mgr.trigger_event(my_horse, stable_mgr, "race", did_win)
                            
                            input("\nPress Enter to return to Stable...")
                            break 
                        elif r_choice == 'Q' or r_choice == 'C':
                            break
                    if r_choice == 'Q' or r_choice == 'C': continue 
                    
                    my_horse.week = 1
                    my_horse.month += 1
                    my_horse.current_race_card = []
                    stable_mgr.refresh_all_markets(spawner)
                    stable_mgr.decrement_stud_timer(spawner) 
                    
                    payout = stable_mgr.process_academy_payouts()
                    if payout > 0: print(f"\n🎓 The Riding Academy generated ${payout:,} this month!")
                        
                    trained, finished = stable_mgr.auto_train_benched(my_horse.id)
                    if trained or finished:
                        if trained: print(f"\n👨‍🏫 Assistant Trainer passively trained: {', '.join(trained)}")
                        if finished:
                            for fh in finished: print(f"🎓 {fh} has finished its assistant training program!")
                        input("Press Enter to continue...")
                        
                    stable_mgr.save_horse(my_horse)
                    continue
                    
            elif action == '2':
                rest_fatg = SPA_REST_FATG if upgrades.get('luxury_spa') else STD_REST_FATG
                rest_mood = SPA_REST_MOOD if upgrades.get('luxury_spa') else STD_REST_MOOD
                
                my_horse.fatigue = max(0.0, my_horse.fatigue - rest_fatg)
                my_horse.condition = min(100.0, getattr(my_horse, 'condition', 50.0) + rest_mood) 
                
                msg = f"\n> {my_horse.name} rested. Fatigue is now {my_horse.fatigue:.1f}. Mood improved!"
                if upgrades.get('luxury_spa'): msg += "\n✨ (Luxury Spa bonuses applied!)"
                print(msg)
                
                if not event_mgr.trigger_event(my_horse, stable_mgr, "training", False):
                    input("\nPress Enter to continue...")
                
                my_horse.week = 1
                my_horse.month += 1
                my_horse.current_race_card = []
                stable_mgr.refresh_all_markets(spawner)
                stable_mgr.decrement_stud_timer(spawner) 
                
                payout = stable_mgr.process_academy_payouts()
                if payout > 0: print(f"\n🎓 The Riding Academy generated ${payout:,} this month!")
                    
                trained, finished = stable_mgr.auto_train_benched(my_horse.id)
                if trained or finished:
                    if trained: print(f"\n👨‍🏫 Assistant Trainer passively trained: {', '.join(trained)}")
                    if finished:
                        for fh in finished: print(f"🎓 {fh} has finished its assistant training program!")
                    input("Press Enter to continue...")
                    
                stable_mgr.save_horse(my_horse)
                continue
                
        else:
            print(" [1] Turf Gallop (Spd)       [7] Run DNA Scanner")
            print(" [2] Hill Sprints (Sta)      [8] View Compendium")
            print(" [3] Dirt Track (Grt)        [9] View Race History")
            print(" [4] Paddock Walk (Mood/All) [I] Open Inventory")
            print(" [5] Rest in Stable          [S] Visit Store")
            print(" [6] Retire Horse            ")
            print("-" * 64)
            print(" [Q] Back to Stable")

            action = input("\nSelect option: ").upper()
            
            if action == 'Q': stable_mgr.save_horse(my_horse); return
            elif action == 'S': 
                Store(stable_mgr).enter()
                continue
            elif action == '7':
                dna_scanner(my_horse, upgrades, stable_mgr) 
                continue
            elif action == '8':
                show_compendium(stable_mgr) 
                continue
            elif action == '9':
                show_race_history(my_horse)
                continue
            elif action == '6':
                if my_horse.age < 4:
                    print(f"\n❌ {my_horse.name} is only Age {my_horse.age}! Horses must be at least Age 4 to retire to the Farm.")
                    input("\nPress Enter to continue...")
                    continue
                confirm = input("Are you sure? Retired horses can NEVER race again! (Y/N): ")
                if confirm.upper() == 'Y':
                    evaluate_career_titles(my_horse) 
                    my_horse.is_retired = True
                    stable_mgr.save_horse(my_horse)
                    print(f"\n🏡 {my_horse.name} has been retired to the Farm.")
                    input("\nPress Enter to return...")
                    return
                continue
            elif action == 'I':
                while True:
                    clear_screen()
                    inv = stable_mgr.get_inventory()
                    cred = stable_mgr.get_credits()
                    
                    print("\n" + "🎒"*32)
                    print("STABLE INVENTORY".center(64))
                    print("🎒"*32)
                    print(f"💰 Funds: ${cred:,}\n".center(64))
                    
                    print(f" [1] Premium Oats       : x{inv.get('oats', 0)}  (-30 Fatigue, +10 Mood)")
                    print(f" [2] Peppermint Treats  : x{inv.get('mints', 0)} (+25 Mood)")
                    print(f" [3] Sprint Vitamins    : x{inv.get('vit_spd', 0)} (+0.5 Speed Potential)")
                    print(f" [4] Endurance Vitamins : x{inv.get('vit_sta', 0)} (+0.5 Stamina Potential)")
                    print(f" [5] Power Vitamins     : x{inv.get('vit_grt', 0)} (+0.5 Grit Potential)")
                    
                    print(f" [6] Fruit Basket       : x{inv.get('fruit_basket', 0)}  (+1.0 All Stats)")
                    print(f" [7] Draft Beer         : x{inv.get('draft_beer', 0)}  (Max Trust/Mood, +Fatigue)")
                    print(f" [8] Golden Alfalfa     : x{inv.get('gold_alfalfa', 0)}  (Zero Fatigue)")
                    
                    print("-" * 64)
                    print(f" [ ] Miracle Salve      : x{inv.get('salve', 0)}  (Used when injured)")
                    print(f" [ ] Electrolyte Paste  : x{inv.get('paste', 0)}  (Used before races)")
                    print(f" [ ] Track Bribe        : x{inv.get('bribe', 0)}  (Used before races)")
                    print(f" [ ] Breeding Supp.     : x{inv.get('breed_supp', 0)} (Used in breeding)")
                    print("-" * 64)
                    print(" [Q] Back to Stable")
                    
                    use_choice = input("\nSelect option: ").upper()
                    
                    if use_choice == 'Q': break
                    elif use_choice == '1':
                        if inv.get('oats', 0) > 0:
                            stable_mgr.add_item('oats', -1)
                            my_horse.fatigue = max(0.0, my_horse.fatigue - 30.0)
                            my_horse.condition = min(100.0, getattr(my_horse, 'condition', 50.0) + 10.0)
                            stable_mgr.save_horse(my_horse)
                            print(f"\n🍎 {my_horse.name} ate the oats! Fatigue dropped to {my_horse.fatigue:.1f}% and Mood improved!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Premium Oats!")
                            input("Press Enter to continue...")
                    elif use_choice == '2':
                        if inv.get('mints', 0) > 0:
                            stable_mgr.add_item('mints', -1)
                            my_horse.condition = min(100.0, getattr(my_horse, 'condition', 50.0) + 25.0)
                            stable_mgr.save_horse(my_horse)
                            print(f"\n🍬 {my_horse.name} loved the mints! Mood improved significantly!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Peppermint Treats!")
                            input("Press Enter to continue...")
                    elif use_choice == '3':
                        if inv.get('vit_spd', 0) > 0:
                            if my_horse.cur_speed >= my_horse.pot_speed:
                                print(f"\n❌ {my_horse.name} has already reached their maximum genetic Speed!")
                            else:
                                stable_mgr.add_item('vit_spd', -1)
                                my_horse.cur_speed = min(my_horse.pot_speed, my_horse.cur_speed + 0.5)
                                stable_mgr.save_horse(my_horse)
                                print(f"\n⚡ {my_horse.name} ate the Sprint Vitamins! Speed increased!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Sprint Vitamins!")
                            input("Press Enter to continue...")
                    elif use_choice == '4':
                        if inv.get('vit_sta', 0) > 0:
                            if my_horse.cur_stamina >= my_horse.pot_stamina:
                                print(f"\n❌ {my_horse.name} has already reached their maximum genetic Stamina!")
                            else:
                                stable_mgr.add_item('vit_sta', -1)
                                my_horse.cur_stamina = min(my_horse.pot_stamina, my_horse.cur_stamina + 0.5)
                                stable_mgr.save_horse(my_horse)
                                print(f"\n🛡️ {my_horse.name} ate the Endurance Vitamins! Stamina increased!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Endurance Vitamins!")
                            input("Press Enter to continue...")
                    elif use_choice == '5':
                        if inv.get('vit_grt', 0) > 0:
                            if my_horse.cur_grit >= my_horse.pot_grit:
                                print(f"\n❌ {my_horse.name} has already reached their maximum genetic Grit!")
                            else:
                                stable_mgr.add_item('vit_grt', -1)
                                my_horse.cur_grit = min(my_horse.pot_grit, my_horse.cur_grit + 0.5)
                                stable_mgr.save_horse(my_horse)
                                print(f"\n🔥 {my_horse.name} ate the Power Vitamins! Grit increased!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Power Vitamins!")
                            input("Press Enter to continue...")
                    elif use_choice == '6':
                        if inv.get('fruit_basket', 0) > 0:
                            stable_mgr.add_item('fruit_basket', -1)
                            my_horse.cur_speed = min(my_horse.pot_speed, my_horse.cur_speed + 1.0)
                            my_horse.cur_stamina = min(my_horse.pot_stamina, my_horse.cur_stamina + 1.0)
                            my_horse.cur_grit = min(my_horse.pot_grit, my_horse.cur_grit + 1.0)
                            stable_mgr.save_horse(my_horse)
                            print(f"\n🧺 {my_horse.name} devoured the Fruit Basket! Massive stat gains across the board!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Champion's Fruit Baskets!")
                            input("Press Enter to continue...")
                    elif use_choice == '7':
                        if inv.get('draft_beer', 0) > 0:
                            stable_mgr.add_item('draft_beer', -1)
                            
                            if getattr(my_horse, 'trust', 50.0) >= 100.0 and getattr(my_horse, 'condition', 50.0) >= 100.0:
                                my_horse.draft_beer_buff = True
                                print(f"\n🍺 GULP GULP GULP... {my_horse.name} is fully confident! They gained Liquid Courage (+2% All Stats for next race)!")
                            else:
                                print(f"\n🍺 GULP GULP GULP... {my_horse.name} drank the whole bucket! Trust and Mood maxed out, but they look a little sleepy.")
                                
                            my_horse.trust = 100.0
                            my_horse.condition = 100.0
                            my_horse.bad_interaction_streak = 0
                            my_horse.fatigue = min(100.0, my_horse.fatigue + 15.0)
                            stable_mgr.save_horse(my_horse)
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Draft Beer!")
                            input("Press Enter to continue...")
                    elif use_choice == '8':
                        if inv.get('gold_alfalfa', 0) > 0:
                            stable_mgr.add_item('gold_alfalfa', -1)
                            my_horse.fatigue = 0.0
                            my_horse.condition = min(100.0, my_horse.condition + 50.0)
                            stable_mgr.save_horse(my_horse)
                            print(f"\n🌾 The legendary Golden Alfalfa! {my_horse.name}'s muscles instantly recover. Fatigue is completely gone!")
                            input("Press Enter to continue...")
                        else:
                            print("\n❌ You don't have any Golden Alfalfa!")
                            input("Press Enter to continue...")
                    else:
                        input("\nInvalid choice. Press Enter...")
                continue
                
            elif action in ['1', '2', '3', '4', '5']:
                res = facility.train(my_horse, action, upgrades, hof_buffs)
                print("\n" + res)
                
                if not event_mgr.trigger_event(my_horse, stable_mgr, "training", False):
                    input("\nPress Enter to continue...")
                
                my_horse.week += 1
                max_w = 5 if my_horse.month in [3, 6, 9, 12] else 4
                if my_horse.week > max_w: 
                    my_horse.week = 1
                    my_horse.month += 1
                    stable_mgr.refresh_all_markets(spawner)
                    stable_mgr.decrement_stud_timer(spawner) 
                    
                    payout = stable_mgr.process_academy_payouts()
                    if payout > 0: print(f"\n🎓 The Riding Academy generated ${payout:,} this month!")
                        
                    trained, finished = stable_mgr.auto_train_benched(my_horse.id)
                    if trained or finished:
                        if trained: print(f"\n👨‍🏫 Assistant Trainer passively trained: {', '.join(trained)}")
                        if finished:
                            for fh in finished: print(f"🎓 {fh} has finished its assistant training program!")
                        input("Press Enter to continue...")
                        
                stable_mgr.save_horse(my_horse) 
                continue
            else:
                input("\nInvalid choice. Press Enter...")