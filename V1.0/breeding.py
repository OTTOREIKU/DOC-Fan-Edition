import random
from spawner import Horse
from genetics import CoatGenetics
from random_events import EventManager 

# --- IMPORT CONFIG VARIABLES ---
from config import MUTATION_CHANCE, TITLE_INHERIT_CHANCE, LINEBREEDING_BONUS, INBREEDING_STAM_PENALTY, MARKET_PRICE_BASE, STUD_FEE_BASE, GEN_PRICE_MULTIPLIER

class BreedingBarn:
    def __init__(self):
        self.genetics = CoatGenetics()
        self.leg_types = ["Front-runner", "Start Dash", "Last Spurt", "Stretch-runner", "Almighty"]
        
    def _get_training_completion(self, horse):
        spd_comp = horse.cur_speed / horse.pot_speed if horse.pot_speed > 0 else 0
        sta_comp = horse.cur_stamina / horse.pot_stamina if horse.pot_stamina > 0 else 0
        grt_comp = horse.cur_grit / horse.pot_grit if horse.pot_grit > 0 else 0
        return min(1.0, (spd_comp + sta_comp + grt_comp) / 3.0)

    def _get_ancestors(self, horse_id, stable_mgr, max_depth, current_depth=1):
        if current_depth > max_depth or not horse_id: return set()
        horse = stable_mgr.get_horse_by_id(horse_id)
        if not horse: return set()
        
        ancestors = set()
        if horse.sire_id: 
            ancestors.add(horse.sire_id)
            ancestors.update(self._get_ancestors(horse.sire_id, stable_mgr, max_depth, current_depth + 1))
        if horse.dam_id:
            ancestors.add(horse.dam_id)
            ancestors.update(self._get_ancestors(horse.dam_id, stable_mgr, max_depth, current_depth + 1))
        return ancestors

    def evaluate_bloodline(self, sire, dam, stable_mgr):
        sire_parents = {sire.sire_id, sire.dam_id} - {None}
        dam_parents = {dam.sire_id, dam.dam_id} - {None}
        
        is_inbred = False
        is_linebred = False
        
        if sire.id in dam_parents or dam.id in sire_parents: is_inbred = True
        elif sire_parents and dam_parents and not sire_parents.isdisjoint(dam_parents): is_inbred = True
        
        if not is_inbred:
            sire_ancestors = self._get_ancestors(sire.id, stable_mgr, max_depth=3)
            dam_ancestors = self._get_ancestors(dam.id, stable_mgr, max_depth=3)
            if not sire_ancestors.isdisjoint(dam_ancestors):
                is_linebred = True
                
        if is_inbred: return "inbred"
        if is_linebred: return "linebred"
        return "safe"

    def breed_horses(self, sire, dam, stable_mgr, hof_buffs=None, use_supplement=False):
        if hof_buffs is None: hof_buffs = []
        
        foal_dna = self.genetics.cross_dna(sire.genotype, dam.genotype)
        foal_phenotype = self.genetics.get_phenotype(foal_dna)
        foal_gen = min(sire.generation, dam.generation) + 1
        
        status = self.evaluate_bloodline(sire, dam, stable_mgr)
        is_inbred = (status == "inbred")
        is_linebred = (status == "linebred")
        
        # --- PULLED FROM CONFIG ---
        is_gold = foal_gen >= 3 and foal_dna.get('Cr', []) == ['Cr', 'Cr'] and random.random() < MUTATION_CHANCE
        is_chimera = foal_gen >= 5 and 'E' in foal_dna.get('E', []) and 'e' in foal_dna.get('E', []) and random.random() < MUTATION_CHANCE
        is_solar = foal_gen >= 6 and foal_dna.get('Ch', []) == ['Ch', 'Ch'] and foal_dna.get('E', []) == ['e', 'e'] and random.random() < MUTATION_CHANCE
        is_abyssal = foal_gen >= 7 and foal_dna.get('Z', []) == ['Z', 'Z'] and random.random() < MUTATION_CHANCE
        is_ghost = foal_gen >= 8 and foal_dna.get('Rn', []) == ['Rn', 'Rn'] and foal_dna.get('G', []) == ['G', 'G'] and random.random() < MUTATION_CHANCE
        
        if is_ghost: foal_phenotype = f"{random.choice(['Spectral', 'Banshee', 'Wraith'])} Ghost Walker (MYTHIC COAT)"
        elif is_abyssal: foal_phenotype = f"{random.choice(['Void', 'Oceanic', 'Cosmic'])} Abyssal Prism (MYTHIC COAT)"
        elif is_solar: foal_phenotype = f"{random.choice(['Nova', 'Corona', 'Plasma'])} Solar Flare (LEGENDARY COAT)"
        elif is_chimera: foal_phenotype = f"{random.choice(['Sanguine', 'Eclipse', 'Golden'])} Chimera (LEGENDARY COAT)"
        elif is_gold: foal_phenotype = f"{random.choice(['Aureate', 'Rose', 'Platinum'])} Gold-Dipped (LEGENDARY COAT)"

        inherited_titles = []
        if is_inbred: inherited_titles.append("Inbred") 
        
        # --- LEGENDARY TRAIT INHERITANCE ONLY ---
        legendary_traits = [
            "Shadow Slayer", "Storm Chaser", "Iron Breaker", "Dream Weaver", 
            "Sun God", "Void Walker", "Phantom Terror", "Golden Emperor",
            "Nightmare Weaver", "Thunderous Iron", "Track Sovereign"
        ]
        
        for t in sire.titles + dam.titles:
            # If it's a career achievement or standard race title, skip it
            if t not in legendary_traits:
                continue
                
            pass_chance = TITLE_INHERIT_CHANCE
            if t in ["Nightmare Weaver", "Thunderous Iron"]: pass_chance = TITLE_INHERIT_CHANCE * 2.0
            elif t in ["Track Sovereign"]: pass_chance = TITLE_INHERIT_CHANCE * 3.3
            
            if random.random() < pass_chance and t not in inherited_titles:
                inherited_titles.append(t)
                
        fused = False
        if "Shadow Slayer" in inherited_titles and "Dream Weaver" in inherited_titles:
            inherited_titles.remove("Shadow Slayer"); inherited_titles.remove("Dream Weaver")
            inherited_titles.append("Nightmare Weaver"); fused = True
        if "Storm Chaser" in inherited_titles and "Iron Breaker" in inherited_titles:
            inherited_titles.remove("Storm Chaser"); inherited_titles.remove("Iron Breaker")
            inherited_titles.append("Thunderous Iron"); fused = True
        if "Nightmare Weaver" in inherited_titles and "Thunderous Iron" in inherited_titles:
            inherited_titles.remove("Nightmare Weaver"); inherited_titles.remove("Thunderous Iron")
            inherited_titles.append("Track Sovereign"); fused = True

        base_pot_spd = (sire.pot_speed + dam.pot_speed) / 2.0
        base_pot_sta = (sire.pot_stamina + dam.pot_stamina) / 2.0
        base_pot_grt = (sire.pot_grit + dam.pot_grit) / 2.0
        
        variance_low = -0.05
        variance_high = 0.15 if use_supplement else 0.08
        
        # --- PULLED FROM CONFIG ---
        inbreeding_penalty_spd = 0.90 if is_inbred else 1.0
        inbreeding_penalty_sta = INBREEDING_STAM_PENALTY if is_inbred else 1.0
        linebreeding_bonus = LINEBREEDING_BONUS if is_linebred else 1.0
        
        foal_pot_spd = base_pot_spd * random.uniform(1.0 + variance_low, 1.0 + variance_high) * inbreeding_penalty_spd * linebreeding_bonus
        foal_pot_sta = base_pot_sta * random.uniform(1.0 + variance_low, 1.0 + variance_high) * inbreeding_penalty_sta * linebreeding_bonus
        foal_pot_grt = base_pot_grt * random.uniform(1.0 + variance_low, 1.0 + variance_high) * inbreeding_penalty_spd * linebreeding_bonus
        
        sire_comp = self._get_training_completion(sire)
        dam_comp = self._get_training_completion(dam)
        avg_comp = (sire_comp + dam_comp) / 2.0
        starting_pct = 0.10 + (0.20 * avg_comp) 
        
        foal_cur_spd = foal_pot_spd * starting_pct * random.uniform(0.95, 1.05)
        foal_cur_sta = foal_pot_sta * starting_pct * random.uniform(0.95, 1.05)
        foal_cur_grt = foal_pot_grt * starting_pct * random.uniform(0.95, 1.05)

        style_roll = random.random()
        if style_roll < 0.40: foal_style = sire.running_style
        elif style_roll < 0.80: foal_style = dam.running_style
        else: foal_style = random.choice(self.leg_types)
        foal_surface = random.choice([sire.preferred_surface, dam.preferred_surface])
        
        print("\n" + "="*64)
        print(f"💖 BREEDING COMPLETE 💖".center(64))
        print("="*64)
        print(f" Sire Training Completion: {sire_comp*100:.1f}%")
        print(f" Dam Training Completion : {dam_comp*100:.1f}%")
        
        if is_inbred:
            print(f"\n ⚠️ WARNING: INBREEDING DEPRESSION!")
            print(" You bred closely related horses. Max Stamina severely reduced.")
        elif is_linebred:
            print(f"\n ✨ HYBRID VIGOR: SUCCESSFUL LINEBREEDING!")
            print(" Careful ancestry planning has boosted all potential stats!")
            
        print(f"\n -> Foal Starting Base: {starting_pct*100:.1f}% of Maximum Potential")
        
        if is_ghost or is_abyssal or is_solar or is_chimera or is_gold:
            print(f"\n✨🧬 INCREDIBLE! A CHASE MUTATION HAS OCCURRED!")
            print(f"The Foal's Coat is {foal_phenotype}!")
        if fused:
            print(f"\n🔥 MYTHIC FUSION! Parent titles merged into a stronger form!")
        if inherited_titles:
            print(f"\n⭐ LEGENDARY GENETICS! Foal inherited traits:")
            print(f"   {', '.join(inherited_titles)}")
        print("="*64)
        
        foal_name = input("\nEnter a name for your new foal: ").strip()
        if not foal_name: foal_name = f"Gen {foal_gen} Foal"
        
        # --- PULLED FROM CONFIG ---
        market_value = int((foal_cur_spd + foal_cur_sta + foal_cur_grt) * MARKET_PRICE_BASE * (GEN_PRICE_MULTIPLIER ** foal_gen))

        new_foal = Horse(
            name=foal_name, gender=random.choice(["Colt", "Filly"]), genotype=foal_dna, phenotype=foal_phenotype,
            pot_speed=foal_pot_spd, pot_stamina=foal_pot_sta, pot_grit=foal_pot_grt,
            cur_speed=foal_cur_spd, cur_stamina=foal_cur_sta, cur_grit=foal_cur_grt,
            preferred_surface=foal_surface, running_style=foal_style, generation=foal_gen,
            sire_id=sire.id, dam_id=dam.id, price=market_value, favorite_food=random.choice(["1", "2", "3"]),
            condition=random.uniform(40.0, 60.0), 
            personality=random.choice(["Willing", "Hot-Blooded", "Anxious", "Stoic", "Alpha"]), 
            trust=random.uniform(40.0, 60.0), titles=inherited_titles
        )
        
        event_mgr = EventManager()
        event_mgr.trigger_breeding_event(new_foal, stable_mgr)

        return new_foal

    def stud_farm_menu(self, stable_mgr, spawner, hof_buffs):
        import os
        from art_generator import ArtGenerator
        from menus import dna_scanner, get_letter_grade
        
        upgrades = stable_mgr.get_upgrades() 
        
        if not stable_mgr.get_stud_horses():
            stable_mgr.refresh_stud_farm(spawner)
            
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" + "🏛️"*32)
            print("NATIONAL STUD SYNDICATE".center(64))
            print("🏛️"*32)
            print(f" Refreshes in: {stable_mgr.load_data().get('stud_timer', 0)} Months\n".center(64))
            
            saved = stable_mgr.get_saved_horses()
            valid_horses = [h for h in saved if (h.is_retired or h.age >= 4) and not getattr(h, 'is_npc', False) and not getattr(h, 'is_archived', False)]
            
            if not valid_horses:
                print("You have no eligible horses (Age 4+ or Retired) to bring to the Syndicate!")
                input("\nPress Enter to return...")
                return
                
            print("Select your horse to breed:")
            for i, h in enumerate(valid_horses):
                status = "(Farm)" if h.is_retired else f"(Active Age {h.age})"
                print(f" [{i+1}] {h.name} ({h.gender}) {status}")
            print("-" * 64)
            print(" [Q] Back")
            
            p_choice = input("\nSelect option: ").upper()
            if p_choice == 'Q' or p_choice == 'C': return
            if p_choice.isdigit() and 1 <= int(p_choice) <= len(valid_horses):
                my_horse = valid_horses[int(p_choice)-1]
                target_gender = "Stallion" if my_horse.gender in ["Filly", "Mare"] else "Mare"
                
                studs = [h for h in stable_mgr.get_stud_horses() if h.gender == target_gender]
                
                while True:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\n" + "🏛️"*32)
                    print(f"AVAILABLE {target_gender.upper()}S".center(64))
                    print("🏛️"*32)
                    print(f"💰 Your Funds: ${stable_mgr.get_credits():,}\n".center(64))
                    
                    for i, s in enumerate(studs):
                        # --- PULLED FROM CONFIG ---
                        fee = int((s.cur_speed + s.cur_stamina + s.cur_grit) * STUD_FEE_BASE * (GEN_PRICE_MULTIPLIER ** s.generation))
                        setattr(s, 'temp_fee', fee) 
                        
                        print(ArtGenerator.generate(s))
                        print(f" [{i+1}] {s.name} (Gen {s.generation}) - SYNDICATE FEE: ${fee:,}")
                        print(f"     Coat : \033[93m{s.phenotype}\033[0m")
                        
                        if upgrades.get('master_scanner', False):
                            s_g = get_letter_grade(s.pot_speed, s.generation)
                            st_g = get_letter_grade(s.pot_stamina, s.generation)
                            g_g = get_letter_grade(s.pot_grit, s.generation)
                            print(f"     Stats: Spd {s.cur_speed:.1f}/{s.pot_speed:.0f} {s_g} | Sta {s.cur_stamina:.1f}/{s.pot_stamina:.0f} {st_g} | Grt {s.cur_grit:.1f}/{s.pot_grit:.0f} {g_g}")
                        elif upgrades.get('pro_scanner', False):
                            print(f"     Stats: Spd {s.cur_speed:.1f}/{s.pot_speed:.0f} | Sta {s.cur_stamina:.1f}/{s.pot_stamina:.0f} | Grt {s.cur_grit:.1f}/{s.pot_grit:.0f}")
                        else:
                            print(f"     Stats: Spd {s.cur_speed:.1f} | Sta {s.cur_stamina:.1f} | Grt {s.cur_grit:.1f}")
                            
                        title_str = f" | Titles: {', '.join(s.titles)}" if s.titles else ""
                        print(f"     Record: {s.wins}-{s.races_run - s.wins} | G1s: {s.championships_won}{title_str}")
                        print("-" * 64)
                        
                    print(" [S] Scan DNA")
                    print(" [Q] Back")
                    s_choice = input(f"\nBreed (1-3) or Select Option: ").upper()
                    
                    if s_choice == 'Q' or s_choice == 'C': break
                    elif s_choice == 'S':
                        if not upgrades.get('pro_scanner', False):
                            print("\n❌ You need to purchase the Pro DNA Scanner from the Store first!")
                            input("Press Enter to continue...")
                        else:
                            scan_idx = input(f"Enter {target_gender} number to Scan (1-3): ")
                            if scan_idx.isdigit() and 1 <= int(scan_idx) <= len(studs):
                                dna_scanner(studs[int(scan_idx) - 1], upgrades, stable_mgr)
                    elif s_choice.isdigit() and 1 <= int(s_choice) <= len(studs):
                        chosen_stud = studs[int(s_choice)-1]
                        fee = chosen_stud.temp_fee
                        
                        if stable_mgr.get_credits() >= fee:
                            if upgrades.get("master_scanner"):
                                sire = chosen_stud if chosen_stud.gender == "Stallion" else my_horse
                                dam = chosen_stud if chosen_stud.gender == "Mare" else my_horse
                                status = self.evaluate_bloodline(sire, dam, stable_mgr)
                                
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
                            
                            confirm = input(f"\nPay ${fee:,} to breed {my_horse.name} with {chosen_stud.name}? (Y/N): ").upper()
                            if confirm == 'Y':
                                stable_mgr.add_credits(-fee)
                                
                                inv = stable_mgr.get_inventory()
                                use_supp = False
                                if inv.get('breed_supp', 0) > 0 and input("\nUse Breeding Supplement (2x Mutation Chance)? Y/N: ").upper() == 'Y':
                                    stable_mgr.add_item('breed_supp', -1)
                                    use_supp = True
                                
                                sire = chosen_stud if chosen_stud.gender == "Stallion" else my_horse
                                dam = chosen_stud if chosen_stud.gender == "Mare" else my_horse
                                
                                chosen_stud.is_npc = True 
                                
                                if hasattr(chosen_stud, 'temp_fee'):
                                    delattr(chosen_stud, 'temp_fee')
                                
                                stable_mgr.save_horse(chosen_stud)
                                
                                new_foal = self.breed_horses(sire, dam, stable_mgr, hof_buffs, use_supp)
                                stable_mgr.save_horse(new_foal)
                                
                                input("\nPress Enter to return...")
                                return 
                        else:
                            print(f"\n❌ Insufficient funds! You need ${fee - stable_mgr.get_credits():,} more.")
                            input("Press Enter to continue...")