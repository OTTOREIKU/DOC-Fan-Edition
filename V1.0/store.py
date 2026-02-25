import os
from calendar_events import CalendarEvents

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class Store:
    def __init__(self, stable_mgr):
        self.stable_mgr = stable_mgr
        
    def _get_facility_cost(self, level):
        return {1: 25000, 2: 75000, 3: 150000, 4: 300000}.get(level, 0)
        
    def _get_assistant_trainer_cost(self, level):
        return {1: 100000, 2: 300000, 3: 750000, 4: 1250000, 5: 2000000}.get(level, 0)

    # --- NEW SCOUTING NETWORK COST ---
    def _get_scouting_cost(self, level):
        return {1: 150000, 2: 300000, 3: 750000, 4: 2000000, 5: 10000000}.get(level, 0)

    def _get_active_buffs(self):
        buffs = set()
        events = CalendarEvents().events
        for h in self.stable_mgr.get_saved_horses():
            if h.is_retired:
                for title in h.titles:
                    for e in events:
                        if e.get("title") == title: buffs.add(e.get("buff_name"))
        return list(buffs)

    def enter(self):
        while True:
            clear_screen()
            credits = self.stable_mgr.get_credits()
            upgrades = self.stable_mgr.get_upgrades()
            buffs = self._get_active_buffs()
            
            discount = 0.9 if "Guineas Heritage" in buffs else 1.0
            def get_price(base): return int(base * discount)
            
            print("\n" + "🏪"*32)
            print("THE OWNER'S SHOP".center(64))
            print("🏪"*32)
            print(f"💰 Available Funds: ${credits:,}\n".center(64))
            
            print("--- FACILITY UPGRADES ".ljust(64, "-"))
            
            cap = upgrades.get('stable_capacity', 4)
            stall_cost = cap * 25000 
            if cap < 10: print(f" [1] Stall Expansion (Current: {cap}) - ${stall_cost:,}\n     -> Adds +1 slot to your active stable")
            else: print(" [1] Stall Expansion - MAXED OUT\n     -> Adds +1 slot to your active stable")

            turf_lvl = upgrades.get('turf_track_lvl', 1)
            t_cost = self._get_facility_cost(turf_lvl)
            if turf_lvl < 5: print(f" [2] Turf Track Upgrade (Lvl {turf_lvl} -> {turf_lvl+1}) - ${t_cost:,}\n     -> Boosts Speed training gains by 5%")
            else: print(" [2] Turf Track Upgrade - MAXED OUT\n     -> Boosts Speed training gains by 20%")

            dt_lvl = upgrades.get('dirt_track_lvl', 1)
            dt_cost = self._get_facility_cost(dt_lvl)
            if dt_lvl < 5: print(f" [3] Dirt Track Upgrade (Lvl {dt_lvl} -> {dt_lvl+1}) - ${dt_cost:,}\n     -> Boosts Grit training gains by 5%")
            else: print(" [3] Dirt Track Upgrade - MAXED OUT\n     -> Boosts Grit training gains by 20%")

            pool_lvl = upgrades.get('pool_lvl', 1)
            p_cost = self._get_facility_cost(pool_lvl)
            if pool_lvl < 5: print(f" [4] Swim Pool Upgrade  (Lvl {pool_lvl} -> {pool_lvl+1}) - ${p_cost:,}\n     -> Boosts Stamina training gains by 5%")
            else: print(" [4] Swim Pool Upgrade  - MAXED OUT\n     -> Boosts Stamina training gains by 20%")

            at_lvl = upgrades.get('assistant_trainer_lvl', 0)
            if at_lvl == 0 and upgrades.get('assistant_trainer'):
                at_lvl = 1 
                
            at_cost = self._get_assistant_trainer_cost(at_lvl + 1)
            if at_lvl < 5: print(f" [5] Assistant Trainer  (Lvl {at_lvl} -> {at_lvl+1}) - ${at_cost:,}\n     -> Passively trains benched horses (+{(at_lvl+1)*0.1:.1f}/mo)")
            else: print(f" [5] Assistant Trainer  - MAXED OUT\n     -> Passively trains benched horses (+0.5/mo)")

            # --- NEW SCOUTING NETWORK SHOP UI ---
            sn_lvl = upgrades.get('scouting_network_lvl', 0)
            sn_cost = self._get_scouting_cost(sn_lvl + 1)
            if sn_lvl < 5: print(f" [6] Scouting Network   (Lvl {sn_lvl} -> {sn_lvl+1}) - ${sn_cost:,}\n     -> Boosts Market size and starting stats")
            else: print(f" [6] Scouting Network   - MAXED OUT\n     -> Boosts Market size and starting stats")

            print("\n" + "--- TECH & GEAR (PERMANENT) ".ljust(64, "-"))
            
            ps_status = "OWNED" if upgrades.get('premium_saddles') else "$250,000"
            pd_status = "OWNED" if upgrades.get('pro_scanner') else "$150,000"
            hm_status = "OWNED" if upgrades.get('heart_monitor') else "$100,000"
            aw_status = "OWNED" if upgrades.get('auto_walker') else "$150,000"
            aw2_status = "OWNED" if upgrades.get('advanced_walker') else "$500,000"
            ss_status = "OWNED" if upgrades.get('stud_syndicate') else "$900,000"
            md_status = "OWNED" if upgrades.get('master_scanner') else "$1,500,000"
            jg_status = "OWNED" if upgrades.get('jockey_guild') else "$750,000"
            ba_status = "OWNED" if upgrades.get('bribe_auctioneer') else "$300,000"

            print(f" [7] Premium Saddles ({ps_status})".ljust(38) + "- Slight stat boost during races")
            print(f" [8] Pro DNA Scanner ({pd_status})".ljust(38) + "- Reveals genetics & true potentials")
            print(f" [9] Heart Monitor ({hm_status})".ljust(38) + "- Shows exact numerical stamina in races")
            print(f"[10] Auto-Walker ({aw_status})".ljust(38) + "- Passively reduces fatigue each week")
            
            if upgrades.get('auto_walker'):
                print(f"[11] Advanced Walker ({aw2_status})".ljust(38) + "- Extra weekly recovery & less training fatigue")
            else:
                print(f"[11] Advanced Walker (LOCKED)".ljust(38) + "- Requires standard Auto-Walker first")
                
            print(f"[12] Stud Syndicate ({ss_status})".ljust(38) + "- Unlocks the national breeding market")
            print(f"[13] Master DNA Scanner ({md_status})".ljust(38) + "- Reveals mutations & bloodline traits")
            print(f"[14] Jockey Guild License ({jg_status})".ljust(38) + "- Hire professional riders for races")
            # --- NEW BRIBE TECH ITEM ---
            print(f"[15] Bribe the Auctioneer ({ba_status})".ljust(38) + "- Unlocks the ability to reroll market")

            print("\n" + "--- THE MILLIONAIRE'S CLUB ".ljust(64, "-"))
            vc_status = "OWNED" if upgrades.get('vet_clinic') else "$2,500,000"
            ls_status = "OWNED" if upgrades.get('luxury_spa') else "$5,000,000"
            gl_status = "OWNED" if upgrades.get('genetics_lab') else "$10,000,000"
            print(f"[16] Veterinary Clinic ({vc_status})".ljust(38) + "- Halves injury duration")
            print(f"[17] Luxury Spa ({ls_status})".ljust(38) + "- Rest recovers massive energy")
            print(f"[18] Genetics Lab ({gl_status})".ljust(38) + "- Perfect DNA predictions")

            print("\n" + "--- CONSUMABLES ".ljust(64, "-"))
            if discount < 1.0:
                print("✨ GUINEAS HERITAGE ACTIVE: 10% Discount applied! ✨")
                
            print(f"[19] Premium Oats (${get_price(5000):,})".ljust(38) + "- Reduces fatigue by 30")
            print(f"[20] Peppermint Treats (${get_price(2000):,})".ljust(38) + "- Instantly boosts Mood by 25")
            print(f"[21] Miracle Salve (${get_price(5000):,})".ljust(38) + "- Instantly cures any injury")
            print(f"[22] Electrolyte Paste (${get_price(25000):,})".ljust(38) + "- +100 Max Stamina for one race")
            print(f"[23] Track Bribe (${get_price(10000):,})".ljust(38) + "- Rerolls a horse's race card")
            print(f"[24] Breeding Supp. (${get_price(50000):,})".ljust(38) + "- 2x Mutation chance on breed")
            print(f"[25] Sprint Vitamins (${get_price(50000):,})".ljust(38) + "- Grants +0.5 Speed")
            print(f"[26] Endurance Vitamins (${get_price(50000):,})".ljust(38) + "- Grants +0.5 Stamina")
            print(f"[27] Power Vitamins (${get_price(50000):,})".ljust(38) + "- Grants +0.5 Grit")
            
            print("-" * 64)
            print(" [Q] Back")

            choice = input("\nSelect option: ").upper()
            
            if choice == 'Q': break
            elif choice == '1' and cap < 10: self._buy_upgrade('stable_capacity', stall_cost, cap + 1)
            elif choice == '2' and turf_lvl < 5: self._buy_upgrade('turf_track_lvl', t_cost, turf_lvl + 1)
            elif choice == '3' and dt_lvl < 5: self._buy_upgrade('dirt_track_lvl', dt_cost, dt_lvl + 1)
            elif choice == '4' and pool_lvl < 5: self._buy_upgrade('pool_lvl', p_cost, pool_lvl + 1)
            elif choice == '5' and at_lvl < 5: self._buy_upgrade('assistant_trainer_lvl', at_cost, at_lvl + 1)
            elif choice == '6' and sn_lvl < 5: self._buy_upgrade('scouting_network_lvl', sn_cost, sn_lvl + 1)
            elif choice == '7' and not upgrades.get('premium_saddles'): self._buy_upgrade('premium_saddles', 250000, True)
            elif choice == '8' and not upgrades.get('pro_scanner'): self._buy_upgrade('pro_scanner', 150000, True)
            elif choice == '9' and not upgrades.get('heart_monitor'): self._buy_upgrade('heart_monitor', 100000, True)
            elif choice == '10' and not upgrades.get('auto_walker'): self._buy_upgrade('auto_walker', 150000, True)
            elif choice == '11' and not upgrades.get('advanced_walker'):
                if not upgrades.get('auto_walker'):
                    print("\n❌ You must purchase the standard Auto-Walker first!")
                    input("Press Enter to continue...")
                else:
                    self._buy_upgrade('advanced_walker', 500000, True)
            elif choice == '12' and not upgrades.get('stud_syndicate'): self._buy_upgrade('stud_syndicate', 900000, True)
            elif choice == '13' and not upgrades.get('master_scanner'): self._buy_upgrade('master_scanner', 1500000, True)
            elif choice == '14' and not upgrades.get('jockey_guild'): self._buy_upgrade('jockey_guild', 750000, True)
            elif choice == '15' and not upgrades.get('bribe_auctioneer'): self._buy_upgrade('bribe_auctioneer', 300000, True)
            elif choice == '16' and not upgrades.get('vet_clinic'): self._buy_upgrade('vet_clinic', 2500000, True)
            elif choice == '17' and not upgrades.get('luxury_spa'): self._buy_upgrade('luxury_spa', 5000000, True)
            elif choice == '18' and not upgrades.get('genetics_lab'): self._buy_upgrade('genetics_lab', 10000000, True)
            elif choice == '19': self._buy_item('oats', get_price(5000), "Premium Oats")
            elif choice == '20': self._buy_item('mints', get_price(2000), "Peppermint Treats")
            elif choice == '21': self._buy_item('salve', get_price(5000), "Miracle Salve")
            elif choice == '22': self._buy_item('paste', get_price(25000), "Electrolyte Paste")
            elif choice == '23': self._buy_item('bribe', get_price(10000), "Track Bribe")
            elif choice == '24': self._buy_item('breed_supp', get_price(50000), "Breeding Supplement")
            elif choice == '25': self._buy_item('vit_spd', get_price(50000), "Sprint Vitamins")
            elif choice == '26': self._buy_item('vit_sta', get_price(50000), "Endurance Vitamins")
            elif choice == '27': self._buy_item('vit_grt', get_price(50000), "Power Vitamins")
            else:
                print("\n❌ Invalid selection or you already maxed this out!")
                input("Press Enter to continue...")

    def _buy_upgrade(self, upgrade_key, cost, new_value):
        credits = self.stable_mgr.get_credits()
        if credits >= cost:
            self.stable_mgr.add_credits(-cost)
            self.stable_mgr.set_upgrade(upgrade_key, new_value)
            print(f"\n🎉 Upgrade purchased successfully!")
        else:
            print(f"\n❌ Not enough funds! You need ${cost - credits:,} more.")
        input("Press Enter to continue...")

    def _buy_item(self, item_key, unit_cost, item_name):
        qty_str = input(f"\nHow many [{item_name}] would you like to buy? (Enter number or 'C' to cancel): ")
        if qty_str.upper() == 'C': return
        if not qty_str.isdigit() or int(qty_str) <= 0:
            print("\n❌ Invalid quantity entered.")
            input("Press Enter to continue...")
            return
            
        qty = int(qty_str)
        total_cost = unit_cost * qty
        credits = self.stable_mgr.get_credits()
        
        if credits >= total_cost:
            self.stable_mgr.add_credits(-total_cost)
            self.stable_mgr.add_item(item_key, qty)
            print(f"\n🛍️ Purchased {qty}x {item_name} for ${total_cost:,}!")
        else:
            print(f"\n❌ Not enough funds! You need ${total_cost - credits:,} more for that quantity.")
        input("Press Enter to continue...")