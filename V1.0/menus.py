import os
from art_generator import ArtGenerator
from calendar_events import CalendarEvents

# --- IMPORT CONFIG VARIABLES ---
from config import MAX_POTENTIAL_BASE, MAX_POTENTIAL_PER_GEN, FACILITY_BONUS_PER_LVL

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time(seconds):
    m = int(seconds // 60)
    s = seconds - (m * 60)
    return f"{m}:{s:05.2f}"

def show_race_history(horse):
    clear_screen()
    print("\n" + "📜"*32)
    print(f"PAST PERFORMANCES: {horse.name.upper()}".center(64))
    print("📜"*32)
    
    history = getattr(horse, 'race_history', [])
    if not history:
        print("\nThis horse has not run any races yet.")
    else:
        for race in reversed(history): 
            suffix = "th"
            if race['placement'] == 1: suffix = "st"
            elif race['placement'] == 2: suffix = "nd"
            elif race['placement'] == 3: suffix = "rd"
            
            print(f"\n[{race['age']}yo | M{race['month']} W{race['week']}] {race['race_name']} (${race.get('purse', 0):,})")
            print(f" Details : {race['distance']}m {race['surface']} | Track: {race['condition']}")
            print(f" Finish  : {race['placement']}{suffix} Place")
            print(f" Field   : {' | '.join(race['field'])}")
            print("-" * 64)
            
    input("\nPress Enter to return...")

def _highlight_dna(gene_list, is_base=False):
    if not gene_list: return "['n', 'n']"
    if is_base: return f"['{gene_list[0]}', '{gene_list[1]}']"
    c1 = f"\033[93m'{gene_list[0]}'\033[0m" if gene_list[0] != 'n' else f"'{gene_list[0]}'"
    c2 = f"\033[93m'{gene_list[1]}'\033[0m" if gene_list[1] != 'n' else f"'{gene_list[1]}'"
    return f"[{c1}, {c2}]"

def _print_parent_block(parent, title):
    print(f"--- {title} ".ljust(64, "-"))
    if parent:
        print(ArtGenerator.generate(parent))
        print(f" Name  : {parent.name} (Gen {parent.generation})")
        print(f" Coat  : \033[93m{parent.phenotype}\033[0m")
        print(f" Stats : Spd {parent.cur_speed:.1f} | Sta {parent.cur_stamina:.1f} | Grt {parent.cur_grit:.1f}")
        print(f" Record: {parent.wins}-{parent.races_run - parent.wins} | G1s: {parent.championships_won}")
        
        dna = parent.genotype
        if dna:
            print("\n [Genetic Profile]")
            print(f" Base : E {_highlight_dna(dna.get('E',['e','e']), True)} | A {_highlight_dna(dna.get('A',['a','a']), True)} | G {_highlight_dna(dna.get('G',['n','n']))}")
            print(f" Dil  : Cr {_highlight_dna(dna.get('Cr',['n','n']))} | D {_highlight_dna(dna.get('D',['n','n']))} | Ch {_highlight_dna(dna.get('Ch',['n','n']))} | Z {_highlight_dna(dna.get('Z',['n','n']))}")
            print(f" Patt : Rn {_highlight_dna(dna.get('Rn',['n','n']))} | To {_highlight_dna(dna.get('To',['n','n']))} | O {_highlight_dna(dna.get('O',['n','n']))} | Spl {_highlight_dna(dna.get('Spl',['n','n']))}")
    else:
        print("\n[Record Lost or Horse Sold to Market]")

def show_lineage(horse, stable_mgr):
    clear_screen()
    print("\n" + "🧬"*32)
    print(f"BLOODLINE & PEDIGREE: {horse.name.upper()}".center(64))
    print("🧬"*32 + "\n")

    if horse.generation == 0 or (not horse.sire_id and not horse.dam_id):
        print("This is a Foundation Horse (Generation 0).")
        print("They have no recorded lineage in the stable database.")
    else:
        sire = stable_mgr.get_horse_by_id(horse.sire_id)
        dam = stable_mgr.get_horse_by_id(horse.dam_id)

        _print_parent_block(sire, "SIRE (FATHER)")
        print("")
        _print_parent_block(dam, "DAM (MOTHER)")

    print("\n" + "🧬"*32)
    input("Press Enter to return...")

def get_letter_grade(pot_stat, gen):
    max_pot = MAX_POTENTIAL_BASE + (gen * MAX_POTENTIAL_PER_GEN)
    ratio = pot_stat / max_pot
    
    if ratio >= 0.95: return "[SS]"
    if ratio >= 0.85: return "[S]"
    if ratio >= 0.70: return "[A]"
    if ratio >= 0.50: return "[B]"
    if ratio >= 0.30: return "[C]"
    return "[D]"

def dna_scanner(horse, upgrades, stable_mgr=None):
    clear_screen()
    has_pro = upgrades.get('pro_scanner', False)
    has_master = upgrades.get('master_scanner', False)
    
    print("\n" + "🧬"*32)
    print(f"GENETIC SCANNER: {horse.name.upper()}".center(64))
    print("🧬"*32)
    
    print(ArtGenerator.generate(horse))
    
    print(f"PHENOTYPE : \033[93m{horse.phenotype}\033[0m")
    print(f"RACE STYLE: \033[96m{horse.running_style}\033[0m")
    print("-" * 64)
    
    print("📊 CURRENT STATS:")
    print(f" Speed  : {horse.cur_speed:.1f}")
    print(f" Stamina: {horse.cur_stamina:.1f}")
    print(f" Grit   : {horse.cur_grit:.1f}")
    print("-" * 64)
    
    if has_master:
        print("📈 [MASTER] MAXIMUM GENETIC POTENTIAL:")
        spd_g = get_letter_grade(horse.pot_speed, horse.generation)
        sta_g = get_letter_grade(horse.pot_stamina, horse.generation)
        grt_g = get_letter_grade(horse.pot_grit, horse.generation)
        print(f" Speed  : {horse.pot_speed:.1f} {spd_g}")
        print(f" Stamina: {horse.pot_stamina:.1f} {sta_g}")
        print(f" Grit   : {horse.pot_grit:.1f} {grt_g}")
        print("-" * 64)
    elif has_pro:
        print("📈 [PRO] MAXIMUM GENETIC POTENTIAL:")
        print(f" Speed  : {horse.pot_speed:.1f}")
        print(f" Stamina: {horse.pot_stamina:.1f}")
        print(f" Grit   : {horse.pot_grit:.1f}")
        print("-" * 64)
        
    print("GENOTYPE (Hidden DNA):")
    dna = horse.genotype

    print(f"Base Colors : E {_highlight_dna(dna.get('E', ['e','e']), True)} | A {_highlight_dna(dna.get('A', ['a','a']), True)} | G {_highlight_dna(dna.get('G', ['n','n']))}")
    print(f"Dilutions   : Cr {_highlight_dna(dna.get('Cr', ['n','n']))} | D {_highlight_dna(dna.get('D', ['n','n']))} | Ch {_highlight_dna(dna.get('Ch', ['n','n']))} | Z {_highlight_dna(dna.get('Z', ['n','n']))}")
    print(f"Patterns 1  : Rn {_highlight_dna(dna.get('Rn', ['n','n']))} | To {_highlight_dna(dna.get('To', ['n','n']))} | O {_highlight_dna(dna.get('O', ['n','n']))} | Lp {_highlight_dna(dna.get('Lp', ['n','n']))}")
    print(f"Patterns 2  : Br {_highlight_dna(dna.get('Br', ['n','n']))} | Spl {_highlight_dna(dna.get('Spl', ['n','n']))} | Sb {_highlight_dna(dna.get('Sb', ['n','n']))} | Rb {_highlight_dna(dna.get('Rb', ['n','n']))}")
    print(f"Markings    : F {_highlight_dna(dna.get('F', ['n','n']))} | L {_highlight_dna(dna.get('L', ['n','n']))}")
    
    mut1, mut2 = dna.get("Mut", ['n', 'n'])
    if mut1 == "n" and mut2 == "n": 
        print(f"Legendary   : ['n', 'n'] (Normal)")
    elif mut1 != "n" and mut2 != "n": 
        print(f"Legendary   : {_highlight_dna([mut1, mut2])} (⭐ EXPRESSED! ⭐)")
    else:
        hidden = mut1 if mut1 != "n" else mut2
        print(f"Legendary   : {_highlight_dna([mut1, mut2])} (⚠️ CARRIER: \033[93m{hidden.upper()}\033[0m ⚠️)")
        
    if has_master:
        print("-" * 64)
        radar = []
        if dna.get('Cr') == ['Cr', 'Cr']: radar.append("Gold-Dipped")
        if 'E' in dna.get('E', []) and 'e' in dna.get('E', []): radar.append("Chimera")
        if dna.get('Ch') == ['Ch', 'Ch'] and dna.get('E') == ['e', 'e']: radar.append("Solar Flare")
        if dna.get('Z') == ['Z', 'Z']: radar.append("Abyssal Prism")
        if dna.get('Rn') == ['Rn', 'Rn'] and dna.get('G') == ['G', 'G']: radar.append("Ghost Walker")

        if radar:
            if stable_mgr: 
                for r in radar:
                    stable_mgr.add_seen_mutation(r)
            print("📡 MUTATION RADAR: Carrier of \033[93m" + ", ".join(radar) + "\033[0m")
        else:
            print("📡 MUTATION RADAR: No Rare Coat Combinations Detected")

    print("-" * 64)
    print("🏅 EARNED TITLES & TRAITS:")
    title_descs = {
        "Shadow Slayer": "+10% Speed burst in the final 400m.",
        "Storm Chaser": "Grit is twice as effective when exhausted.",
        "Iron Breaker": "Halves stamina penalty from Heavy/Yielding tracks.",
        "Dream Weaver": "Halves the chance of suffering post-race injuries.",
        "Sun God": "Reduces stamina drain by 15% on Firm/Fast tracks.",
        "Void Walker": "Massive Speed burst in the final 400m.",
        "Phantom Terror": "Tension fills twice as fast when Holding.",
        "Golden Emperor": "Multiplies all race winnings by 1.5x!",
        "Iron Horse": "Retire with 20+ races and 0 lifetime injuries.",
        "Invincible": "Retire with 10+ races and a 100% win rate.",
        "Workhorse": "Retire with 30+ lifetime races.",
        "Globetrotter": "Retire with 3+ wins on Turf and 3+ wins on Dirt.",
        "Triple Crown": "Win 3+ G1 races during Juvenile (Age 2) or Age 3 years.",
        "High Roller": "Retire with over $1,000,000 in career earnings.",
        "Sprint Specialist": "Retire with 5+ wins at 1000m or 1200m distances.",
        "Marathon Legend": "Retire with 5+ wins at 2400m or 3000m distances.",
        "Late Bloomer": "Win 2+ G1 races at Age 6 or older.",
        "Nightmare Weaver": "Fuse [Shadow Slayer] and [Dream Weaver].",
        "Thunderous Iron": "Fuse [Storm Chaser] and [Iron Breaker].",
        "Track Sovereign": "Fuse [Nightmare Weaver] and [Thunderous Iron]."
    }
    
    if horse.titles:
        for t in horse.titles:
            if t in title_descs:
                desc = title_descs[t]
                print(f" [{t}] : \033[36m{desc}\033[0m")
            else:
                print(f" [{t}]")
    else:
        print(" No titles earned yet.")

    print("="*64 + "\n")
    input("Press Enter to return...")

def _preview_coats_menu(stable_mgr):
    from spawner import Horse 
    while True:
        clear_screen()
        print("\n" + "🎨"*32)
        print("RARE COAT PREVIEW".center(64))
        print("🎨"*32)
        
        seen = stable_mgr.get_seen_mutations()
        
        variants = {
            "Gold-Dipped": ["Aureate Gold-Dipped", "Rose Gold-Dipped", "Platinum Gold-Dipped"],
            "Chimera": ["Sanguine Chimera", "Eclipse Chimera", "Golden Chimera"],
            "Solar Flare": ["Nova Solar Flare", "Corona Solar Flare", "Plasma Solar Flare"],
            "Abyssal Prism": ["Void Abyssal Prism", "Oceanic Abyssal Prism", "Cosmic Abyssal Prism"],
            "Ghost Walker": ["Spectral Ghost Walker", "Banshee Ghost Walker", "Wraith Ghost Walker"]
        }
        
        unlocked_variants = []
        for base in ["Gold-Dipped", "Chimera", "Solar Flare", "Abyssal Prism", "Ghost Walker"]:
            if base in seen:
                unlocked_variants.extend(variants[base])
        
        if not unlocked_variants:
            print("\nYou haven't discovered any rare mutation genes yet!")
            print("Use the Master DNA Scanner or breed rare coats to unlock them.")
            input("\nPress Enter to return...")
            return
            
        for i, coat in enumerate(unlocked_variants):
            print(f" [{i+1}] Preview {coat}")
            
        print("-" * 64)
        print(" [Q] Back")
        
        choice = input("\nSelect variant to preview: ").upper()
        if choice == 'Q' or choice == 'C': break
        
        if choice.isdigit() and 1 <= int(choice) <= len(unlocked_variants):
            selected_coat = unlocked_variants[int(choice)-1]
            
            exact_pheno = selected_coat
            if any(m in selected_coat for m in ["Ghost Walker", "Abyssal Prism"]):
                exact_pheno += " (MYTHIC COAT)"
            elif any(l in selected_coat for l in ["Solar Flare", "Chimera", "Gold-Dipped"]):
                exact_pheno += " (LEGENDARY COAT)"
                
            dummy = Horse(name=f"Example {selected_coat}", phenotype=exact_pheno)
            
            clear_screen()
            print("\n" + "="*64)
            print(f"PREVIEW: {selected_coat.upper()}".center(64))
            print("="*64)
            print(ArtGenerator.generate(dummy))
            print(f" Coat Type: \033[93m{exact_pheno}\033[0m".center(73)) 
            print("="*64)
            input("\nPress Enter to return...")

def _show_jockey_compendium(stable_mgr):
    while True:
        clear_screen()
        print("\n" + "🏇"*32)
        print("JOCKEY GUILD COMPENDIUM".center(64))
        print("🏇"*32)
        print("\n [1] Affinity Level Progression")
        print(" [2] Jockey Archetypes & Signatures")
        print("-" * 64)
        print(" [Q] Back")
        
        c = input("\nSelect option: ").upper()
        if c == 'Q' or c == 'C': break
        elif c == '1':
            clear_screen()
            print("\n" + "📈"*32)
            print("AFFINITY LEVEL PROGRESSION".center(64))
            print("📈"*32)
            print("\n Win Special Event races (⭐) to gain XP and level up Jockeys.\n")
            print(" Lv  1 (Hired Gun)     : Base Stat Boost (+1.0), 10% Purse Cut")
            print(" Lv  2 (Acquaintance)  : Booking fee permanently waived ($0)")
            print(" Lv  3 (Specialist)    : 🔓 Unlocks Archetype Synergy")
            print(" Lv  4 (Regular)       : -5% Post-race Fatigue")
            print(" Lv  5 (Trusted Rider) : Base Stat Boost increases to +2.0")
            print(" Lv  6 (Companion)     : Prevents post-race Trust loss")
            print(" Lv  7 (Master)        : 🔓 Unlocks Signature Move")
            print(" Lv  8 (Stable Fav.)   : Purse Cut drops to 7%")
            print(" Lv  9 (Elite)         : Base Stat Boost increases to +3.0")
            print(" Lv 10 (Soulmate)      : Purse Cut 5%, +3% to All Stats")
            print("\n" + "-" * 64)
            input("Press Enter to return...")
        elif c == '2':
            clear_screen()
            print("\n" + "🏇"*32)
            print("JOCKEY ARCHETYPES & SIGNATURES".center(64))
            print("🏇"*32)
            print("\n THE AGGRESSOR  | Focus: Speed")
            print("  Synergy (Lv3) : +5% Spd for Front-runner/Start Dash.")
            print("  Signature(Lv7): Whips drain 25% less Stamina in first half.")
            
            print("\n THE TACTICIAN  | Focus: Stamina")
            print("  Synergy (Lv3) : +5% Sta for Last Spurt/Stretch-runner.")
            print("  Signature(Lv7): Tension fills 30% faster when Holding.")
            
            print("\n THE IRON RIDER | Focus: Grit")
            print("  Synergy (Lv3) : +5% Grt for Almighty style.")
            print("  Signature(Lv7): Grit +50% effective when exhausted in final 400m.")
            
            print("\n THE MUDLARK    | Focus: Stamina")
            print("  Synergy (Lv3) : +5% All Stats on Yielding/Heavy tracks.")
            print("  Signature(Lv7): Nullifies heavy stamina-drain track penalties.")
            
            print("\n THE TURF GLIDER| Focus: Speed")
            print("  Synergy (Lv3) : +5% Spd on Turf tracks.")
            print("  Signature(Lv7): Turf races generate 25% less Fatigue.")
            
            print("\n THE DIRT GRINDER| Focus: Grit")
            print("  Synergy (Lv3) : +5% Grt on Dirt tracks.")
            print("  Signature(Lv7): Whips are 15% more effective on Dirt.")
            
            print("\n THE CARETAKER  | Focus: Mood (+15 on saddle, or +5% Stats if Peak)")
            print("  Synergy (Lv3) : Extra 10% post-race fatigue reduction.")
            print("  Signature(Lv7): 75% less chance of post-race injury.")
            
            print("\n THE WHISPERER  | Focus: Trust (+15 on saddle, or +5% Stats if Max)")
            print("  Synergy (Lv3) : Using the Whip doesn't cause resentment.")
            print("  Signature(Lv7): Horses with Poor/Terrible Mood race as Normal.")
            
            print("\n THE SHOWMAN    | Focus: Balanced (+All Stats)")
            print("  Synergy (Lv3) : +10% All Stats in G1 Championship races.")
            print("  Signature(Lv7): 50% chance to drop Premium Item on Win.")
            
            print("\n THE MERCENARY  | Focus: Greed (Starts at 15% Purse Cut)")
            print("  Synergy (Lv3) : +25% Purse Winnings.")
            print("  Signature(Lv7): Doubles wealthy fan item drops (Alfalfa/Beer/Basket).")
            print("\n" + "-" * 64)
            input("Press Enter to return...")

def show_compendium(stable_mgr):
    while True:
        clear_screen()
        all_horses = stable_mgr.get_saved_horses()
        unlocked_titles = set()
        seen_mutations = stable_mgr.get_seen_mutations()
        
        for h in all_horses:
            for t in h.titles: unlocked_titles.add(t)
            
            for chase in ["Ghost Walker", "Abyssal Prism", "Solar Flare", "Chimera", "Gold-Dipped"]:
                if chase in h.phenotype and chase not in seen_mutations:
                    stable_mgr.add_seen_mutation(chase)
                    seen_mutations.append(chase)
                
        boss_data = {
            "EMPEROR'S SHADOW": {"pheno": "Shadow", "title": "Shadow Slayer", "desc": "+10% Speed burst in the final 400m."},
            "CRIMSON LIGHTNING": {"pheno": "Bloody", "title": "Storm Chaser", "desc": "Grit is twice as effective when exhausted."},
            "IRON JUGGERNAUT": {"pheno": "Silver Dapple", "title": "Iron Breaker", "desc": "Halves stamina penalty from Heavy/Yielding tracks."},
            "CELESTIAL DREAM": {"pheno": "Celestial", "title": "Dream Weaver", "desc": "Halves the chance of suffering post-race injuries."},
            "SUPERNOVA": {"pheno": "Solar Flare", "title": "Sun God", "desc": "Reduces stamina drain by 15% on Firm/Fast tracks."},
            "ABYSSAL KING": {"pheno": "Abyssal Prism", "title": "Void Walker", "desc": "Massive Speed burst in the final 400m."},
            "GHOST LORD": {"pheno": "Ghost Walker", "title": "Phantom Terror", "desc": "Tension fills twice as fast when Holding."},
            "AUREATE LEGEND": {"pheno": "Gold-Dipped", "title": "Golden Emperor", "desc": "Multiplies all race winnings by 1.5x!"}
        }
        
        career_titles = {
            "Iron Horse": "Retire with 20+ races and 0 lifetime injuries.",
            "Invincible": "Retire with 10+ races and a 100% win rate.",
            "Workhorse": "Retire with 30+ lifetime races.",
            "Globetrotter": "Retire with 3+ wins on Turf and 3+ wins on Dirt.",
            "Triple Crown": "Win 3+ G1 races during Juvenile (Age 2) or Age 3 years.",
            "High Roller": "Retire with over $1,000,000 in career earnings.",
            "Sprint Specialist": "Retire with 5+ wins at 1000m or 1200m distances.",
            "Marathon Legend": "Retire with 5+ wins at 2400m or 3000m distances.",
            "Late Bloomer": "Win 2+ G1 races at Age 6 or older."
        }

        mythic_titles = {
            "Nightmare Weaver": "Fuse [Shadow Slayer] and [Dream Weaver].",
            "Thunderous Iron": "Fuse [Storm Chaser] and [Iron Breaker].",
            "Track Sovereign": "Fuse [Nightmare Weaver] and [Thunderous Iron]."
        }

        chase_coats_info = {
            "Gold-Dipped": {"desc": "Gen 3+ | Double Cream (Cr, Cr) genes.", "tier": "LEGENDARY"},
            "Chimera": {"desc": "Gen 5+ | Heterozygous Extension (E, e) genes.", "tier": "LEGENDARY"},
            "Solar Flare": {"desc": "Gen 6+ | Double Champagne (Ch, Ch) + Chestnut (e, e).", "tier": "LEGENDARY"},
            "Abyssal Prism": {"desc": "Gen 7+ | Double Silver (Z, Z) genes.", "tier": "MYTHIC"},
            "Ghost Walker": {"desc": "Gen 8+ | Double Roan (Rn, Rn) + Double Grey (G, G).", "tier": "MYTHIC"}
        }
        
        seen_bosses = stable_mgr.get_seen_bosses()
        active_buffs = get_active_hof_buffs(stable_mgr)
        
        print("\n" + "📖"*32)
        print("THE OWNER'S COMPENDIUM".center(64))
        print("📖"*32)
        
        print("\n" + "--- 1. RACING STRATEGY ".ljust(64, "-"))
        print("🐎 Front-runner   : Whip in first 35%-45% of race.")
        print("🐎 Start Dash     : Whip in first 55%-65% of race.")
        print("🐎 Stretch-runner : Whip in last 45%-35% of race.")
        print("🐎 Last Spurt     : Whip in last 65%-55% of race.")
        print("🐎 Almighty       : Whip is slightly effective anywhere.")
        
        print("\n" + "--- 2. STABLE MANAGEMENT ".ljust(64, "-"))
        print("🍎 Favorite Foods : Matching flavor profile grants 2x stat gains!")
        print("💖 Trust (Hearts) : Higher trust = better push in the final 400m.")
        print("🚑 Injuries       : Fatigue over 60% rapidly increases risk.")
        
        print("\n" + "--- 3. GENETICS & BREEDING ".ljust(64, "-"))
        print("🧬 Potentials     : Foals inherit average of parents' potentials.")
        print("🧬 Inheritance    : Boss Titles have a 15% chance to be inherited.")

        print("\n" + "--- 4. TRACK CONDITIONS ".ljust(64, "-"))
        print("☀️ Firm/Fast : Standard. Normal speed, stamina, and purse.")
        print("⛅ Good      : Slight moisture. 10% extra drain. +15% Purse.")
        print("🌧️ Yielding  : Muddy track. 25% extra drain. +35% Purse.")
        print("⛈️ Heavy     : Deep mud! 50% extra drain. +60% Purse.")
        
        print("\n" + "--- 5. HORSE MOOD ".ljust(64, "-"))
        print("↑ Peak (80-100) : +10% to all stats during a race.")
        print("↗ Good (60-79)  : +5% to all stats.")
        print("→ Normal (40-59): Baseline performance.")
        print("↘ Poor (20-39)  : -5% penalty to all stats.")
        print("↓ Terrible (0-19): -10% penalty to all stats.")
        
        print("\n" + "--- 6. LEGENDARY RIVALS ".ljust(64, "-"))
        for name, data in boss_data.items():
            if name in seen_bosses: print(f"🔥 {name} ({data['pheno']}) -> [{data['title']}]\n   Buff: {data['desc']}")
            else: print(f"❓ ??? (Encounter in G2/G1 to unlock)")

        print("\n" + "--- 7. CAREER ACHIEVEMENTS ".ljust(64, "-"))
        for title, desc in career_titles.items():
            if title in unlocked_titles: print(f"🏅 [{title}] : {desc}")
            else: print(f"🔒 ??? (Hidden Career Achievement)")

        print("\n" + "--- 8. MYTHIC BLOODLINES ".ljust(64, "-"))
        for title, desc in mythic_titles.items():
            if title in unlocked_titles: print(f"🌟 [{title}] : {desc}")
            else: print(f"🔒 ??? (Hidden Title Fusion)")

        print("\n" + "--- 9. CHASE MUTATIONS ".ljust(64, "-"))
        for coat, data in chase_coats_info.items():
            if coat in seen_mutations: print(f"✨ {coat} ({data['tier']}) : {data['desc']}")
            else: print(f"🔒 ??? (Undiscovered {data['tier']} Coat)")
                
        print("\n" + "--- 10. EVENT PASSIVES ".ljust(64, "-"))
        events_list = CalendarEvents().events
        event_buffs = {}
        for e in events_list:
            b_name = e.get("buff_name")
            if b_name: event_buffs[b_name] = e.get("buff_desc", "A permanent passive reward.")
                
        if not event_buffs: print("No event passives available in the current calendar.")
        else:
            for b_name, desc in event_buffs.items():
                if b_name in active_buffs: print(f"✨ [{b_name}] : {desc}")
                else: print(f"🔒 ??? (Hidden Event Passive)")

        print("="*64)
        
        settings = stable_mgr.get_settings()
        jockey_on = settings.get("jockey_system", True)
        
        # --- UI CHANGE: Q ALWAYS ON THE LEFT ---
        if jockey_on:
            print(" [Q] Back | [P] Preview Discovered Coats | [J] Jockey Guild Info")
        else:
            print(" [Q] Back | [P] Preview Discovered Coats")
        
        c = input("\nSelect option: ").upper()
        if c == 'Q' or c == 'C': break
        elif c == 'P': _preview_coats_menu(stable_mgr)
        elif c == 'J' and jockey_on: _show_jockey_compendium(stable_mgr)

def get_active_hof_buffs(stable_mgr):
    buffs = set()
    events = CalendarEvents().events
    for h in stable_mgr.get_saved_horses():
        if h.is_retired:
            for title in h.titles:
                for e in events:
                    if e["title"] == title: buffs.add(e["buff_name"])
                # --- UPDATED TO INCLUDE THE FUSED MYTHIC TITLES ---
                boss_titles = ["Shadow Slayer", "Storm Chaser", "Iron Breaker", "Dream Weaver", "Sun God", "Void Walker", "Phantom Terror", "Golden Emperor", "Nightmare Weaver", "Thunderous Iron", "Track Sovereign"]
                if title in boss_titles:
                    buffs.add(title)
    return list(buffs)

# --- NEW DETAILED ACTIVE BUFFS MENU ---
def show_active_buffs_menu(stable_mgr):
    while True:
        clear_screen()
        upgrades = stable_mgr.get_upgrades()
        print("\n" + "🌟"*32)
        print("ACTIVE STABLE BUFFS".center(64))
        print("🌟"*32 + "\n")
        
        print("--- 🏗️  FACILITY UPGRADES ".ljust(64, "-"))
        turf_lvl = upgrades.get('turf_track_lvl', 1)
        dirt_lvl = upgrades.get('dirt_track_lvl', 1)
        pool_lvl = upgrades.get('pool_lvl', 1)
        at_lvl = upgrades.get('assistant_trainer_lvl', 0)
        
        fac_count = 0
        if turf_lvl > 1:
            print(f" Turf Track (Lv.{turf_lvl}) : +{int((turf_lvl-1)*FACILITY_BONUS_PER_LVL*100)}% Speed training gains")
            fac_count += 1
        if dirt_lvl > 1:
            print(f" Dirt Track (Lv.{dirt_lvl}) : +{int((dirt_lvl-1)*FACILITY_BONUS_PER_LVL*100)}% Grit training gains")
            fac_count += 1
        if pool_lvl > 1:
            print(f" Swim Pool (Lv.{pool_lvl})  : +{int((pool_lvl-1)*FACILITY_BONUS_PER_LVL*100)}% Stamina training gains")
            fac_count += 1
        if at_lvl > 0:
            print(f" Asst. Trainer (Lv.{at_lvl}): Passively trains benched horses (+{at_lvl*0.1:.1f}/mo)")
            fac_count += 1
        if fac_count == 0: print(" (No facility buffs active)")

        print("\n--- 🛠️  TECH & GEAR ".ljust(64, "-"))
        tech_count = 0
        if upgrades.get('premium_saddles'):
            print(" Premium Saddles : Slight stat boost during races")
            tech_count += 1
        if upgrades.get('advanced_walker'):
            print(" Advanced Walker : Extra weekly recovery & less training fatigue")
            tech_count += 1
        elif upgrades.get('auto_walker'):
            print(" Auto-Walker     : Passively reduces fatigue each week")
            tech_count += 1
        if upgrades.get('vet_clinic'):
            print(" Vet Clinic      : Halves injury duration")
            tech_count += 1
        if upgrades.get('luxury_spa'):
            print(" Luxury Spa      : Rest recovers massive energy")
            tech_count += 1
        if tech_count == 0: print(" (No tech/gear buffs active)")

        print("\n--- ✨ LEGACY TITLES (HALL OF FAME) ".ljust(64, "-"))
        active_hof = get_active_hof_buffs(stable_mgr)
        if not active_hof:
            print(" (No legacy titles active)")
        else:
            events = CalendarEvents().events
            boss_desc = {
                "Shadow Slayer": "+10% Speed burst in the final 400m.",
                "Storm Chaser": "Grit is twice as effective when exhausted.",
                "Iron Breaker": "Halves stamina penalty from Heavy/Yielding tracks.",
                "Dream Weaver": "Halves the chance of suffering post-race injuries.",
                "Sun God": "Reduces stamina drain by 15% on Firm/Fast tracks.",
                "Void Walker": "Massive Speed burst in the final 400m.",
                "Phantom Terror": "Tension fills twice as fast when Holding.",
                "Golden Emperor": "Multiplies all race winnings by 1.5x!",
                "Nightmare Weaver": "Fuse [Shadow Slayer] and [Dream Weaver].",
                "Thunderous Iron": "Fuse [Storm Chaser] and [Iron Breaker].",
                "Track Sovereign": "Fuse [Nightmare Weaver] and [Thunderous Iron]."
            }
            
            for b in active_hof:
                desc = "A permanent passive reward."
                for e in events:
                    if e.get("buff_name") == b:
                        desc = e.get("buff_desc")
                        break
                if b in boss_desc:
                    desc = boss_desc[b]
                    
                print(f" [{b}] : {desc}")
        
        print("-" * 64)
        print(" [Q] Back")
        if input("\nSelect option: ").upper() in ['Q', 'C']:
            break

def show_national_records(stable_mgr):
    clear_screen()
    print("\n" + "⏱️"*32)
    print("NATIONAL TRACK RECORDS".center(64))
    print("⏱️"*32 + "\n")
    
    records = stable_mgr.load_data().get("national_records", {})
    distances = [1000, 1200, 1600, 2000, 2400, 3000]
    surfaces = ["Turf", "Dirt"]
    
    for dist in distances:
        for surf in surfaces:
            key = f"{dist}_{surf}"
            if key in records:
                rec = records[key]
                t_str = format_time(rec['time'])
                holder = rec['holder']
                print(f" 🚩 {dist}m {surf.ljust(4)} : {t_str} by {holder}")
            else:
                print(f" 🚩 {dist}m {surf.ljust(4)} : --:--.-- (No Record)")
    
    print("\n" + "⏱️"*32)
    input("Press Enter to return...")

def show_hall_of_fame(stable_mgr):
    while True:
        clear_screen()
        saved_horses = stable_mgr.get_saved_horses()
        retired_horses = [h for h in saved_horses if h.is_retired and not getattr(h, 'is_npc', False)]
        hof_horses = sorted(retired_horses, key=lambda h: (h.championships_won, h.earnings), reverse=True)
        
        print("\n" + "🏆"*32)
        print("HALL OF FAME".center(64))
        print("🏆"*32)
        
        buffs = get_active_hof_buffs(stable_mgr)
        if buffs:
            print("\n✨ ACTIVE PASSIVE BUFFS UNLOCKED ✨")
            for b in buffs: print(f" - {b}")
            print("-" * 64)
            
        if not hof_horses: print("\nNo legends have been retired yet.")
        else:
            for i, h in enumerate(hof_horses):
                print(f"\n#{i+1} {h.name.upper()} | {h.phenotype}")
                title_str = f" | Titles: {', '.join(h.titles)}" if h.titles else ""
                print(f" Record: {h.wins}-{h.races_run - h.wins} | G1s: {h.championships_won}{title_str}")
                print(f" Earnings: ${h.earnings:,}")
                
        print("\n" + "🏆"*32)
        print(" [1] View National Track Records") 
        print(" [2] View Owner's Compendium") 
        print(" [Q] Back to Main Menu")
        
        c = input("\nSelect option: ").upper()
        if c == '1':
            show_national_records(stable_mgr)
        elif c == '2':
            show_compendium(stable_mgr)
        elif c == 'Q' or c == 'C':
            break

def farm_menu(stable_mgr):
    while True:
        clear_screen()
        saved_horses = stable_mgr.get_saved_horses()
        retired_horses = [h for h in saved_horses if h.is_retired and not getattr(h, 'is_npc', False) and not getattr(h, 'is_archived', False)]
        
        farm_horses = [h for h in retired_horses if not getattr(h, 'is_in_academy', False)]
        academy_horses = [h for h in retired_horses if getattr(h, 'is_in_academy', False)]
        
        upgrades = stable_mgr.get_upgrades()
        
        print("\n" + "🌾"*32)
        print("THE FARM & RIDING ACADEMY".center(64))
        print("🌾"*32)
        
        print("\n--- AT THE FARM (Available to Breed) ---".ljust(64, "-"))
        if not farm_horses: print(" No horses currently resting at the farm.")
        for i, h in enumerate(farm_horses):
            title_str = f" | ⭐ {len(h.titles)} Titles" if h.titles else ""
            print(f" [{i+1}] {h.name} ({h.gender}){title_str} | G1s: {h.championships_won}")
            
        print("\n--- AT THE ACADEMY (Generating Income) ---".ljust(64, "-"))
        if not academy_horses: print(" No horses currently working in the Academy.")
        for i, h in enumerate(academy_horses):
            idx = len(farm_horses) + i + 1
            est_payout = int(5000 + ((h.trust + getattr(h, 'condition', 50.0)) * 100) + (h.generation * 2500))
            print(f" [{idx}] {h.name} ({h.gender}) -> Earns ~${est_payout:,}/mo")
            
        print("-" * 64)
        print("[Q] Back")
        
        c = input("\nSelect horse to view: ").upper()
        if c == 'Q': return
        if c.isdigit():
            idx = int(c) - 1
            if 0 <= idx < len(farm_horses):
                selected = farm_horses[idx]
            elif len(farm_horses) <= idx < len(farm_horses) + len(academy_horses):
                selected = academy_horses[idx - len(farm_horses)]
            else:
                continue

            while True:
                clear_screen()
                print("\n" + "🌾"*32)
                print(f"FARM RECORDS: {selected.name.upper()}".center(64))
                print("🌾"*32)
                
                print(ArtGenerator.generate(selected)) 
                print(f" Gender : {selected.gender}")
                print(f" Gen    : {selected.generation}")
                print(f" Coat   : \033[93m{selected.phenotype}\033[0m")
                print(f" Style  : {selected.running_style} | Pref: {selected.preferred_surface}")
                print("-" * 64)
                print(f" Record : {selected.wins} Wins / {selected.races_run} Races")
                print(f" G1s    : {selected.championships_won}")
                if selected.titles: print(f" Titles : {', '.join(selected.titles)}")
                print(f" Earned : ${selected.earnings:,}")
                print("-" * 64)
                
                print(" [1] Run DNA Scanner")
                print(" [2] View Race History")
                print(" [3] View Lineage (Parents)") 
                
                if getattr(selected, 'is_in_academy', False):
                    print(" [4] Recall to Farm (Enables Breeding)")
                else:
                    print(" [4] Send to Riding Academy (Generates Income)")
                    
                print(" [5] Archive Horse (Hide from Farm lists)")
                print("-" * 64)
                print(" [Q] Back")
                
                sub = input("\nSelect option: ").upper()
                if sub == 'Q': break
                elif sub == '1': dna_scanner(selected, upgrades, stable_mgr) 
                elif sub == '2': show_race_history(selected)
                elif sub == '3': show_lineage(selected, stable_mgr) 
                elif sub == '4':
                    if getattr(selected, 'is_in_academy', False):
                        selected.is_in_academy = False
                        stable_mgr.save_horse(selected)
                        print(f"\n🌾 {selected.name} has returned to the Farm and can now breed!")
                    else:
                        selected.is_in_academy = True
                        stable_mgr.save_horse(selected)
                        print(f"\n🎓 {selected.name} is now working at the Academy!")
                    input("Press Enter to continue...")
                    break 
                elif sub == '5':
                    confirm = input(f"\nArchive {selected.name}? They will be hidden from the Farm and Breeding lists, but their Titles will remain in the Hall of Fame. (Y/N): ").upper()
                    if confirm == 'Y':
                        selected.is_archived = True
                        stable_mgr.save_horse(selected)
                        print(f"\n📦 {selected.name} has been safely archived.")
                        input("Press Enter to continue...")
                        break