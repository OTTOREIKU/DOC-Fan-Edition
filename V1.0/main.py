import sys
import os
from spawner import HorseSpawner
from training import TrainingFacility
from save_manager import StableManager
from race_engine import RaceEngine
from breeding import BreedingBarn
from store import Store
from calendar_events import CalendarEvents
from art_generator import ArtGenerator 
from spawner import Horse 
from trade_center import TradeCenter 

# --- ADDED show_active_buffs_menu IMPORT ---
from menus import clear_screen, dna_scanner, show_compendium, show_hall_of_fame, farm_menu, get_active_hof_buffs, show_lineage, get_letter_grade, show_active_buffs_menu
from horse_manager import manage_active_horse 

def main():
    spawner = HorseSpawner()
    facility = TrainingFacility()
    stable_mgr = StableManager()
    race_engine = RaceEngine()
    barn = BreedingBarn()
    store = Store(stable_mgr) 
    events_db = CalendarEvents()
    trader = TradeCenter(stable_mgr) 
    
    while True:
        clear_screen()
        credits = stable_mgr.get_credits()
        upgrades = stable_mgr.get_upgrades()
        capacity = upgrades.get('stable_capacity', 4) 
        
        active_horses = [h for h in stable_mgr.get_saved_horses() if not h.is_retired and not getattr(h, 'is_npc', False) and not getattr(h, 'is_archived', False)]
        current_active = len(active_horses)
        
        print("\n" + "🏇"*32)
        print("A DERBY OWNERS CLUB (ALPHA)".center(64))
        print("🏇"*32)
        print(f"💰 Funds: ${credits:,} | 🏡 Active Stalls: {current_active}/{capacity}\n".center(64))
        
        print(" [1] The Market")
        print(" [2] Active Stable")
        print(" [3] Breeding Barn")
        print(" [4] The Farm & Riding Academy")
        print(" [5] The Store")
        print(" [6] Hall of Fame")
        print(" [7] Owner's Compendium")
        print(" [8] The Trading Hub") 
        print(" [9] Settings") 
        print("-" * 64)
        print(" [Q] Quit Game")
        
        choice = input("\nSelect option: ").upper()
        
        if choice == '1':
            current_market_gen = stable_mgr.get_highest_generation()
            
            while True:
                clear_screen()
                credits = stable_mgr.get_credits() 
                upgrades = stable_mgr.get_upgrades() 
                
                if current_active >= capacity:
                    print("❌ Your stable is FULL! Buy a Stall Expansion at the Store or sell/retire a horse.")
                    input("\nPress Enter to return...")
                    break
                    
                highest_unlocked = stable_mgr.get_highest_generation()
                if current_market_gen > highest_unlocked: current_market_gen = highest_unlocked
                if current_market_gen < 0: current_market_gen = 0
                
                market = stable_mgr.get_market_horses(current_market_gen)
                
                if not market:
                    market = [spawner.generate_market_horse(current_market_gen) for _ in range(3)]
                    stable_mgr.save_market_horses(market, current_market_gen)
                    
                print("\n" + "🐴"*32)
                print(f"THE MARKET (GEN {current_market_gen} TIER)".center(64))
                print("🐴"*32)
                print(f"Available Funds: ${credits:,}\n".center(64))
                
                for i, h in enumerate(market):
                    lock_icon = "🔒 [LOCKED]" if getattr(h, 'is_locked', False) else "🔓"
                    print(ArtGenerator.generate(h)) 
                    print(f"[{i+1}] {h.name} ({h.gender}) | Gen {h.generation} - ${h.price:,} {lock_icon}")
                    print(f"    Coat : \033[93m{h.phenotype}\033[0m")
                    print(f"    Style: {h.running_style} | Pref: {h.preferred_surface}")
                    
                    if upgrades.get('master_scanner', False):
                        s_g = get_letter_grade(h.pot_speed, h.generation)
                        st_g = get_letter_grade(h.pot_stamina, h.generation)
                        g_g = get_letter_grade(h.pot_grit, h.generation)
                        print(f"    Stats: Spd {h.cur_speed:.1f}/{h.pot_speed:.0f} {s_g} | Sta {h.cur_stamina:.1f}/{h.pot_stamina:.0f} {st_g} | Grt {h.cur_grit:.1f}/{h.pot_grit:.0f} {g_g}")
                    elif upgrades.get('pro_scanner', False):
                        print(f"    Stats: Spd {h.cur_speed:.1f}/{h.pot_speed:.0f} | Sta {h.cur_stamina:.1f}/{h.pot_stamina:.0f} | Grt {h.cur_grit:.1f}/{h.pot_grit:.0f}")
                    else:
                        print(f"    Base : Spd {h.cur_speed:.1f} | Sta {h.cur_stamina:.1f} | Grt {h.cur_grit:.1f}")
                    
                    print("-" * 64) 
                    
                print(" [L] Lock/Unlock Horse | [S] Scan DNA")
                if highest_unlocked > 0:
                    print(f" [P] Prev Gen Market ({max(0, current_market_gen - 1)}) | [N] Next Gen Market ({min(highest_unlocked, current_market_gen + 1)})")
                
                if upgrades.get('bribe_auctioneer', False):
                    can_bribe, used, timer, cost = stable_mgr.get_bribe_info(current_market_gen)
                    timer_str = f" | Resets in {timer}mo" if used > 0 else ""
                    if can_bribe:
                        print(f" [B] Bribe Auctioneer to Reroll Market (${cost:,}) | {3 - used}/3 Bribes{timer_str}")
                    else:
                        print(f" [B] Bribe Auctioneer (MAX BRIBES REACHED){timer_str}")

                print("\n [Q] Back")
                
                c = input("\nBuy (1-3) or Select Option: ").upper()
                
                if c == 'Q': break
                elif c == 'P' and highest_unlocked > 0:
                    if current_market_gen > 0: current_market_gen -= 1
                elif c == 'N' and highest_unlocked > 0:
                    if current_market_gen < highest_unlocked: current_market_gen += 1
                elif c == 'L':
                    lock_idx = input("Enter horse number to Lock/Unlock: ")
                    if lock_idx.isdigit() and 1 <= int(lock_idx) <= len(market):
                        idx = int(lock_idx) - 1
                        market[idx].is_locked = not getattr(market[idx], 'is_locked', False)
                        stable_mgr.save_market_horses(market, current_market_gen)
                elif c == 'S':
                    if not upgrades.get('pro_scanner', False):
                        print("\n❌ You need to purchase the Pro DNA Scanner from the Store first!")
                        input("Press Enter to continue...")
                    else:
                        scan_idx = input("Enter horse number to Scan: ")
                        if scan_idx.isdigit() and 1 <= int(scan_idx) <= len(market):
                            dna_scanner(market[int(scan_idx) - 1], upgrades, stable_mgr) 
                elif c == 'B' and upgrades.get('bribe_auctioneer', False):
                    success, msg = stable_mgr.apply_market_bribe(spawner, current_market_gen)
                    if success:
                        print(f"\n💸 {msg}")
                        market = stable_mgr.get_market_horses(current_market_gen)
                    else:
                        print(f"\n❌ {msg}")
                    input("Press Enter to continue...")
                elif c.isdigit() and 1 <= int(c) <= len(market):
                    h = market[int(c)-1]
                    if credits >= h.price: 
                        stable_mgr.add_credits(-h.price)
                        h.is_locked = False 
                        
                        for p_data in getattr(h, 'npc_parents_data', []):
                            stable_mgr.save_horse(Horse(**p_data))
                        h.npc_parents_data = [] 
                        
                        stable_mgr.save_horse(h)
                        market.pop(int(c)-1)
                        
                        scout_lvl = upgrades.get('scouting_network_lvl', 0)
                        from config import SCOUTING_NETWORK_TIERS
                        target_size = SCOUTING_NETWORK_TIERS.get(scout_lvl, SCOUTING_NETWORK_TIERS[0])["size"]
                        while len(market) < target_size:
                            market.append(spawner.generate_market_horse(current_market_gen, scout_lvl)) 
                        stable_mgr.save_market_horses(market, current_market_gen)
                        
                        print(f"\n🎉 You bought {h.name}!")
                        input("Press Enter to continue...")
                        break 
                    else:
                        print(f"\n❌ Insufficient funds! You need ${h.price - credits:,} more.")
                        input("\nPress Enter to continue...")
        
        elif choice == '2':
            while True:
                clear_screen()
                active_horses = [h for h in stable_mgr.get_saved_horses() if not h.is_retired and not getattr(h, 'is_npc', False) and not getattr(h, 'is_archived', False)]
                current_active = len(active_horses)
                upgrades = stable_mgr.get_upgrades()
                
                print("\n" + "🏡"*32)
                print(f"YOUR STABLE ({current_active}/{capacity} Stalls)".center(64))
                print("🏡"*32 + "\n")
                
                # --- CALCULATE TOTAL ACTIVE BUFFS ---
                turf_lvl = upgrades.get('turf_track_lvl', 1)
                dirt_lvl = upgrades.get('dirt_track_lvl', 1)
                pool_lvl = upgrades.get('pool_lvl', 1)
                at_lvl = upgrades.get('assistant_trainer_lvl', 0)
                
                buff_count = 0
                if turf_lvl > 1: buff_count += 1
                if dirt_lvl > 1: buff_count += 1
                if pool_lvl > 1: buff_count += 1
                if at_lvl > 0: buff_count += 1
                
                if upgrades.get('premium_saddles'): buff_count += 1
                if upgrades.get('advanced_walker'): buff_count += 1
                elif upgrades.get('auto_walker'): buff_count += 1
                if upgrades.get('vet_clinic'): buff_count += 1
                if upgrades.get('luxury_spa'): buff_count += 1
                
                active_hof = get_active_hof_buffs(stable_mgr)
                buff_count += len(active_hof)
                
                print(f" 🌟 Active Stable Buffs: {buff_count}")
                print("-" * 64 + "\n")
                
                if not active_horses:
                    print("Your stable is empty. Buy a horse from the market!")
                    input("\nPress Enter to continue...")
                    break
                    
                for i, h in enumerate(active_horses): 
                    print(f" [{i+1}] {h.name} ({h.gender}) | Gen {h.generation} | Class: {h.race_class} | Age: {h.age}")
                
                print("-" * 64)
                print(" [B] View Active Stable Buffs")
                print(" [Q] Back to Main Menu")
                
                c = input("\nSelect option or horse to manage: ").upper()
                if c == 'Q' or c == 'C': 
                    break
                elif c == 'B':
                    show_active_buffs_menu(stable_mgr)
                    continue
                
                if c.isdigit() and 1 <= int(c) <= len(active_horses): 
                    selected = active_horses[int(c)-1]
                    
                    return_to_main = False
                    while True:
                        clear_screen()
                        print("\n" + "🐴"*32)
                        print(f"MANAGING: {selected.name.upper()}".center(64))
                        print("🐴"*32 + "\n")
                        
                        print(" [1] Enter Calendar (Race & Train)")
                        print(" [2] Rename Horse")
                        print(" [3] Sell/Release Horse")
                        print(" [4] Run DNA Scanner") 
                        print(" [5] View Lineage (Parents)") 
                        print("-" * 64)
                        print(" [Q] Back to Stable | [M] Main Menu") 
                        
                        sub = input("\nSelect option: ").upper()
                        if sub == 'Q' or sub == 'C': 
                            break
                        elif sub == 'M':
                            return_to_main = True
                            break
                        elif sub == '1':
                            manage_active_horse(selected, facility, race_engine, stable_mgr, events_db, spawner)
                            break
                        elif sub == '2':
                            new_name = input("\nEnter new name: ").strip()
                            if new_name:
                                print(f"\n✨ {selected.name} is now known as {new_name}!")
                                selected.name = new_name
                                stable_mgr.save_horse(selected)
                                input("Press Enter to continue...")
                        elif sub == '3':
                            if selected.age < 3:
                                print(f"\n⚠️ {selected.name} is only Age {selected.age}! Horses must be at least Age 3 to be sold on the market.")
                                confirm = input(f"Do you want to Release them to a local rescue farm for $0 instead? (Y/N): ").upper()
                                if confirm == 'Y':
                                    stable_mgr.delete_horse(selected.id)
                                    print(f"\n👋 {selected.name} was successfully rehomed.")
                                    input("Press Enter to continue...")
                                    break
                            else:
                                base_val = (selected.cur_speed + selected.cur_stamina + selected.cur_grit) * 100
                                age_penalty = max(0.2, 1.0 - (selected.age * 0.15))
                                sell_price = int(base_val * age_penalty)
                                
                                active_buffs = get_active_hof_buffs(stable_mgr)
                                if "Global Standard" in selected.titles or "Global Standard" in active_buffs:
                                    sell_price = int(sell_price * 1.5)
                                    print("\n✨ GLOBAL STANDARD ACTIVE: 50% Boost to Sale Price! ✨")
                                
                                confirm = input(f"\nSell {selected.name} for ${sell_price:,}? This is PERMANENT! (Y/N): ").upper()
                                if confirm == 'Y':
                                    stable_mgr.add_credits(sell_price)
                                    stable_mgr.delete_horse(selected.id)
                                    print(f"\n💸 Sold {selected.name} for ${sell_price:,}!")
                                    input("Press Enter to continue...")
                                    break 
                        elif sub == '4': dna_scanner(selected, upgrades, stable_mgr) 
                        elif sub == '5': show_lineage(selected, stable_mgr) 
                        
                    if return_to_main:
                        break
            
        elif choice == '3':
            while True:
                clear_screen()
                upgrades = stable_mgr.get_upgrades()
                print("\n" + "💖"*32)
                print("THE BREEDING BARN".center(64))
                print("💖"*32 + "\n")
                
                print(" [1] Private Stable (Breed two of your own horses)")
                
                if upgrades.get("stud_syndicate"):
                    timer = stable_mgr.load_data().get('stud_timer', 0)
                    print(f" [2] National Stud Syndicate (Refreshes in {timer} Months)")
                else:
                    print(" [2] National Stud Syndicate [LOCKED - Purchase at Store]")
                    
                print("-" * 64)
                print(" [Q] Back")
                
                b_choice = input("\nSelect option: ").upper()
                if b_choice == 'Q': break
                elif b_choice == '2' and upgrades.get("stud_syndicate"):
                    barn.stud_farm_menu(stable_mgr, spawner, get_active_hof_buffs(stable_mgr))
                elif b_choice == '1':
                    clear_screen()
                    if current_active >= capacity:
                        print("❌ Your active stable is FULL! You cannot breed a new foal right now.")
                        input("\nPress Enter to return...")
                        continue
                        
                    saved = stable_mgr.get_saved_horses()
                    sires = [h for h in saved if (h.is_retired or h.age >= 4) and h.gender in ["Colt", "Stallion"] and not getattr(h, 'is_npc', False) and not getattr(h, 'is_archived', False) and not getattr(h, 'is_in_academy', False)]
                    dams = [h for h in saved if (h.is_retired or h.age >= 4) and h.gender in ["Filly", "Mare"] and not getattr(h, 'is_npc', False) and not getattr(h, 'is_archived', False) and not getattr(h, 'is_in_academy', False)]
                    
                    if not sires or not dams: 
                        print("Need 1 Male and 1 Female (Retired, or Active Age 4+) not deployed to the Academy to breed privately!")
                        input("\nPress Enter to continue...")
                        continue
                    
                    print("\n" + "💖"*32)
                    print("PRIVATE STABLE".center(64))
                    print("💖"*32)
                    
                    print("\n" + "--- SIRES ".ljust(64, "-"))
                    for i, s in enumerate(sires):
                        status = "(Farm)" if s.is_retired else f"(Active Age {s.age})"
                        print(f"[{i+1}] {s.name} {status}")
                        
                    s_c = input("\nSelect Sire: ")
                    
                    print("\n" + "--- DAMS ".ljust(64, "-"))
                    for i, d in enumerate(dams):
                        status = "(Farm)" if d.is_retired else f"(Active Age {d.age})"
                        print(f"[{i+1}] {d.name} {status}")
                        
                    d_c = input("\nSelect Dam: ")
                    
                    if s_c.isdigit() and d_c.isdigit():
                        sire = sires[int(s_c)-1]
                        dam = dams[int(d_c)-1]
                        
                        if upgrades.get("master_scanner"):
                            status = barn.evaluate_bloodline(sire, dam, stable_mgr)
                            if status == "inbred":
                                print("\n" + "⚠️ "*32)
                                print("WARNING: HIGH INBREEDING RISK DETECTED".center(64))
                                print("⚠️ "*32)
                            elif status == "linebred":
                                print("\n" + "✨"*32)
                                print("PERFECT LINEBREEDING MATCH DETECTED".center(64))
                                print("✨"*32)
                            else:
                                print("\n📡 DNA Radar: No negative genetic conflicts detected.")
                        
                        confirm = input(f"\nBreed {sire.name} and {dam.name}? (Y/N): ").upper()
                        if confirm == 'Y':
                            inv = stable_mgr.get_inventory()
                            use_supp = False
                            if inv.get('breed_supp', 0) > 0 and input("Use Breeding Supplement (2x Mutation Chance)? Y/N: ").upper() == 'Y':
                                stable_mgr.add_item('breed_supp', -1)
                                use_supp = True
                            
                            new_foal = barn.breed_horses(sire, dam, stable_mgr, get_active_hof_buffs(stable_mgr), use_supp)
                            stable_mgr.save_horse(new_foal)
                            input("\nPress Enter to continue...")
                
        elif choice == '4': farm_menu(stable_mgr)
        elif choice == '5': store.enter() 
        elif choice == '6': show_hall_of_fame(stable_mgr)
        elif choice == '7': show_compendium(stable_mgr) 
        elif choice == '8': trader.enter(capacity, current_active) 
        elif choice == '9':
            while True:
                clear_screen()
                print("\n" + "⚙️"*32)
                print("GAME SETTINGS".center(64))
                print("⚙️"*32 + "\n")
                
                settings = stable_mgr.get_settings()
                jockey_status = "ON" if settings.get("jockey_system", True) else "OFF"
                
                print(f" [1] Toggle Jockey Guild System (Currently: {jockey_status})")
                print("-" * 64)
                print(" [Q] Back")
                
                s_choice = input("\nSelect option: ").upper()
                if s_choice == 'Q' or s_choice == 'C': 
                    break
                elif s_choice == '1':
                    current_setting = settings.get("jockey_system", True)
                    stable_mgr.set_setting("jockey_system", not current_setting)
                    new_status = "ON" if not current_setting else "OFF"
                    print(f"\n✅ Jockey Guild System is now {new_status}!")
                    input("Press Enter to continue...")
                    
        elif choice == 'Q': sys.exit()

if __name__ == "__main__": main()