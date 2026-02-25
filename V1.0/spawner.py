import random
import uuid
from dataclasses import dataclass, field
from typing import Optional
from genetics import CoatGenetics

from config import AI_DIFFICULTY_SCALING, BOSS_DIFFICULTY_SCALING, MARKET_PRICE_BASE, GEN_PRICE_MULTIPLIER, MAX_POTENTIAL_BASE, MAX_POTENTIAL_PER_GEN, SCOUTING_NETWORK_TIERS

@dataclass
class Horse:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8]) 
    name: str = "Unnamed"
    gender: str = "Colt"
    age: int = 2
    month: int = 1 
    week: int = 1  
    is_retired: bool = False
    
    genotype: dict = field(default_factory=dict)
    phenotype: str = "Bay"
    
    pot_speed: float = 0.0
    pot_stamina: float = 0.0
    pot_grit: float = 0.0
    cur_speed: float = 0.0
    cur_stamina: float = 0.0
    cur_grit: float = 0.0
    fatigue: float = 0.0
    condition: float = 50.0 
    
    personality: str = "Honest"
    trust: float = 50.0
    bad_interaction_streak: int = 0
    is_locked: bool = False 
    
    running_style: str = "Almighty"
    style_points: dict = field(default_factory=dict) 
    preferred_surface: str = "Turf"
    
    race_class: str = "Maiden" 
    wins: int = 0
    races_run: int = 0
    championships_won: int = 0
    earnings: int = 0 
    price: int = 0    
    injury_weeks: int = 0 
    lifetime_injuries: int = 0 
    titles: list = field(default_factory=list) 
    current_race_card: list = field(default_factory=list) 
    race_history: list = field(default_factory=list) 
    
    sire_id: Optional[str] = None
    dam_id: Optional[str] = None
    generation: int = 0
    
    favorite_food: str = "1" 
    boss_title: Optional[str] = None
    
    is_npc: bool = False 
    npc_parents_data: list = field(default_factory=list) 
    is_archived: bool = False
    is_in_academy: bool = False
    draft_beer_buff: bool = False 
    assistant_stats_gained: float = 0.0 # NEW

class HorseSpawner:
    def __init__(self):
        self.prefixes = ["Admiral", "Azure", "Bold", "Brave", "Captain", "Chief", "Crimson", "Dark", "Desert", "Diamond", "Duke", "Electric", "Flying", "Frost", "Golden", "Grand", "Hidden", "Iron", "King", "Lady", "Little", "Lord", "Lucky", "Magic", "Midnight", "Mighty", "Mystic", "Noble", "Phantom", "Quantum", "Rebel", "Royal", "Secret", "Silent", "Silver", "Sir", "Solar", "Steel", "Swift", "Velvet", "Wild", "Winter"]
        self.suffixes = ["Ace", "Arrow", "Biscuit", "Blaze", "Bolt", "Charm", "Cloud", "Comet", "Dancer", "Dash", "Dawn", "Dream", "Echo", "Express", "Fire", "Flame", "Flash", "Ghost", "Glory", "Gold", "Heart", "Hoof", "Jewel", "Knight", "Legend", "Light", "Majesty", "Moon", "Pearl", "Prince", "Princess", "Queen", "Rose", "Runner", "Shadow", "Spark", "Spirit", "Star", "Storm", "Strike", "Sun", "Thunder"]
        self.genetics = CoatGenetics()
        self.leg_types = ["Front-runner", "Start Dash", "Last Spurt", "Stretch-runner", "Almighty"]
        
        self.ai_cycle = [0, 0, 1, 1, 2]
        random.shuffle(self.ai_cycle)
        self.ai_index = 0

    def _generate_horse_name(self) -> str:
        roll = random.random()
        if roll < 0.10: return random.choice(self.prefixes + self.suffixes)
        elif roll < 0.20:
            return random.choice([
                f"The {random.choice(self.prefixes)} {random.choice(self.suffixes)}",
                f"{random.choice(self.prefixes)} Of {random.choice(self.suffixes)}"
            ])
        else: return f"{random.choice(self.prefixes)} {random.choice(self.suffixes)}"

    def generate_market_horse(self, max_gen=0, scouting_lvl=0) -> Horse:
        gender = random.choice(["Colt", "Filly"])
        name = self._generate_horse_name()
        surface = random.choice(["Turf", "Dirt"])
        
        parent_gen = max(0, max_gen - 1)
        p_mean = 50.0 + (parent_gen * 10.0)
        
        sire_dna = self.genetics.generate_gen0_genotype()
        dam_dna = self.genetics.generate_gen0_genotype()
        
        s_spd, s_sta, s_grt = random.uniform(p_mean, p_mean+15), random.uniform(p_mean, p_mean+15), random.uniform(p_mean, p_mean+15)
        d_spd, d_sta, d_grt = random.uniform(p_mean, p_mean+15), random.uniform(p_mean, p_mean+15), random.uniform(p_mean, p_mean+15)
        
        sire = Horse(
            name=self._generate_horse_name(), gender="Stallion", genotype=sire_dna, 
            phenotype=self.genetics.get_phenotype(sire_dna), generation=parent_gen, 
            is_npc=True, is_retired=True, 
            pot_speed=s_spd, pot_stamina=s_sta, pot_grit=s_grt,
            cur_speed=s_spd, cur_stamina=s_sta, cur_grit=s_grt, 
            wins=random.randint(0, 6), races_run=random.randint(6, 25)
        )
        dam = Horse(
            name=self._generate_horse_name(), gender="Mare", genotype=dam_dna, 
            phenotype=self.genetics.get_phenotype(dam_dna), generation=parent_gen, 
            is_npc=True, is_retired=True, 
            pot_speed=d_spd, pot_stamina=d_sta, pot_grit=d_grt,
            cur_speed=d_spd, cur_stamina=d_sta, cur_grit=d_grt, 
            wins=random.randint(0, 6), races_run=random.randint(6, 25)
        )
        
        foal_dna = self.genetics.cross_dna(sire_dna, dam_dna)
        coat_name = self.genetics.get_phenotype(foal_dna)
        
        tier_data = SCOUTING_NETWORK_TIERS.get(scouting_lvl, SCOUTING_NETWORK_TIERS[0])
        pot_mult = 1.0 + tier_data["pot_bonus"]
        cur_mult = 1.0 + tier_data["cur_bonus"]
        
        mean_pot = 50.0 + (max_gen * 10.0)
        max_pot = (MAX_POTENTIAL_BASE + (max_gen * MAX_POTENTIAL_PER_GEN)) * pot_mult
        min_pot = 30.0 + (max_gen * 5.0)
        
        p_speed = min(max_pot, max(min_pot, random.gauss(mean_pot, 10.0))) * pot_mult
        p_stamina = min(max_pot, max(min_pot, random.gauss(mean_pot, 10.0))) * pot_mult
        p_grit = min(max_pot, max(min_pot, random.gauss(mean_pot, 10.0))) * pot_mult
        
        c_speed = min(p_speed, (p_speed * random.uniform(0.15, 0.25)) * cur_mult)
        c_stamina = min(p_stamina, (p_stamina * random.uniform(0.15, 0.25)) * cur_mult)
        c_grit = min(p_grit, (p_grit * random.uniform(0.15, 0.25)) * cur_mult)
        
        base_value = (c_speed + c_stamina + c_grit) * MARKET_PRICE_BASE
        market_value = int(base_value * (GEN_PRICE_MULTIPLIER ** max_gen))
        start_style = random.choice(self.leg_types)
        
        return Horse(
            name=name, gender=gender, genotype=foal_dna, phenotype=coat_name,
            pot_speed=p_speed, pot_stamina=p_stamina, pot_grit=p_grit,
            cur_speed=c_speed, cur_stamina=c_stamina, cur_grit=c_grit,
            preferred_surface=surface, running_style=start_style,
            generation=max_gen, price=market_value, 
            sire_id=sire.id, dam_id=dam.id, npc_parents_data=[sire.__dict__, dam.__dict__],
            favorite_food=random.choice(["1", "2", "3"]),
            condition=random.uniform(40.0, 60.0),
            personality=random.choice(["Willing", "Hot-Blooded", "Anxious", "Stoic", "Alpha"]),
            trust=random.uniform(40.0, 60.0) 
        )

    def generate_stud_horse(self, max_gen=0, forced_gender="Colt") -> Horse:
        name = self._generate_horse_name()
        surface = random.choice(["Turf", "Dirt"])
        
        parent_gen = max(0, max_gen - 1)
        p_mean = 50.0 + (parent_gen * 10.0)
        
        sire_dna = self.genetics.generate_gen0_genotype()
        dam_dna = self.genetics.generate_gen0_genotype()
        
        s_spd, s_sta, s_grt = random.uniform(p_mean, p_mean+15), random.uniform(p_mean, p_mean+15), random.uniform(p_mean, p_mean+15)
        d_spd, d_sta, d_grt = random.uniform(p_mean, p_mean+15), random.uniform(p_mean, p_mean+15), random.uniform(p_mean, p_mean+15)
        
        sire = Horse(
            name=self._generate_horse_name(), gender="Stallion", genotype=sire_dna, 
            phenotype=self.genetics.get_phenotype(sire_dna), generation=parent_gen, 
            is_npc=True, is_retired=True, 
            pot_speed=s_spd, pot_stamina=s_sta, pot_grit=s_grt,
            cur_speed=s_spd, cur_stamina=s_sta, cur_grit=s_grt, 
            wins=random.randint(0, 6), races_run=random.randint(6, 25)
        )
        dam = Horse(
            name=self._generate_horse_name(), gender="Mare", genotype=dam_dna, 
            phenotype=self.genetics.get_phenotype(dam_dna), generation=parent_gen, 
            is_npc=True, is_retired=True, 
            pot_speed=d_spd, pot_stamina=d_sta, pot_grit=d_grt,
            cur_speed=d_spd, cur_stamina=d_sta, cur_grit=d_grt, 
            wins=random.randint(0, 6), races_run=random.randint(6, 25)
        )
        
        foal_dna = self.genetics.cross_dna(sire_dna, dam_dna)
        
        if random.random() < 0.15: foal_dna['Z'] = ['Z', 'Z']
        if random.random() < 0.15: foal_dna['Cr'] = ['Cr', 'Cr']
        if random.random() < 0.15: foal_dna['G'] = ['G', 'G']
        
        coat_name = self.genetics.get_phenotype(foal_dna)
        
        mean_pot = 50.0 + (max_gen * 10.0)
        max_pot = MAX_POTENTIAL_BASE + (max_gen * MAX_POTENTIAL_PER_GEN)
        min_pot = 30.0 + (max_gen * 5.0)
        
        p_speed = min(max_pot, max(min_pot, random.gauss(mean_pot, 15.0)))
        p_stamina = min(max_pot, max(min_pot, random.gauss(mean_pot, 15.0)))
        p_grit = min(max_pot, max(min_pot, random.gauss(mean_pot, 15.0)))
        
        c_speed = p_speed * random.uniform(0.75, 1.0)
        c_stamina = p_stamina * random.uniform(0.75, 1.0)
        c_grit = p_grit * random.uniform(0.75, 1.0)
        
        start_style = random.choice(self.leg_types)
        
        titles = []
        bosses = ["Shadow Slayer", "Storm Chaser", "Iron Breaker", "Dream Weaver"]
        if random.random() < 0.10: titles.append(random.choice(bosses))
        
        return Horse(
            name=f"Champion {name}", gender=forced_gender, genotype=foal_dna, phenotype=coat_name,
            pot_speed=p_speed, pot_stamina=p_stamina, pot_grit=p_grit,
            cur_speed=c_speed, cur_stamina=c_stamina, cur_grit=c_grit,
            preferred_surface=surface, running_style=start_style,
            generation=max_gen, is_npc=True, is_retired=True, 
            sire_id=sire.id, dam_id=dam.id, npc_parents_data=[sire.__dict__, dam.__dict__],
            wins=random.randint(10, 20), races_run=random.randint(20, 30),
            championships_won=random.randint(1, 5), titles=titles
        )

    def generate_ai_opponent(self, player_horse) -> Horse:
        name = self._generate_horse_name()
        surface = random.choice(["Turf", "Dirt"])
        dna = self.genetics.generate_gen0_genotype()
        coat_name = self.genetics.get_phenotype(dna)
        target_class = player_horse.race_class
        
        player_max_pot = MAX_POTENTIAL_BASE + (player_horse.generation * MAX_POTENTIAL_PER_GEN)
        
        difficulty_range = AI_DIFFICULTY_SCALING.get(target_class, (0.15, 0.25))
        base_stat = player_max_pot * random.uniform(difficulty_range[0], difficulty_range[1])
        
        tier = self.ai_cycle[self.ai_index]
        self.ai_index = (self.ai_index + 1) % len(self.ai_cycle)
        if self.ai_index == 0: 
            random.shuffle(self.ai_cycle)
            
        if tier == 0: 
            tier_mult = random.uniform(0.60, 0.75)
            cond = random.uniform(30.0, 50.0)
        elif tier == 1: 
            tier_mult = random.uniform(0.85, 0.95)
            cond = random.uniform(50.0, 80.0)
        else: 
            tier_mult = random.uniform(1.0, 1.05)
            cond = random.uniform(80.0, 100.0)
            
        final_stat = base_stat * tier_mult
        
        if player_horse.age == 2:
            final_stat *= 0.85 
        
        return Horse(
            name=name, gender="Colt", genotype=dna, phenotype=coat_name, 
            cur_speed=final_stat * random.uniform(0.95, 1.05),
            cur_stamina=final_stat * random.uniform(0.95, 1.05),
            cur_grit=final_stat * random.uniform(0.95, 1.05),
            preferred_surface=surface, race_class=target_class,
            running_style=random.choice(self.leg_types),
            condition=cond 
        )

    def generate_boss_opponent(self, player_horse) -> Horse:
        gen = player_horse.generation
        
        if gen < 6:
            bosses = [
                {"name": "EMPEROR'S SHADOW", "pheno": "Shadow", "style": "Front-runner", "title": "Shadow Slayer", "pref": "Turf"},
                {"name": "CRIMSON LIGHTNING", "pheno": "Bloody", "style": "Start Dash", "title": "Storm Chaser", "pref": "Dirt"},
                {"name": "IRON JUGGERNAUT", "pheno": "Silver Dapple", "style": "Almighty", "title": "Iron Breaker", "pref": "Dirt"},
                {"name": "CELESTIAL DREAM", "pheno": "Celestial", "style": "Last Spurt", "title": "Dream Weaver", "pref": "Turf"}
            ]
            b_data = random.choice(bosses)
            effective_gen = min(5, gen)
            player_max_pot = MAX_POTENTIAL_BASE + (effective_gen * MAX_POTENTIAL_PER_GEN)
            final_stat = player_max_pot * BOSS_DIFFICULTY_SCALING.get("Tier1", 1.10) 
            
        else:
            bosses = [
                {"name": "SUPERNOVA", "pheno": "Solar Flare", "style": "Start Dash", "title": "Sun God", "pref": "Dirt"},
                {"name": "ABYSSAL KING", "pheno": "Oceanic Abyssal Prism", "style": "Last Spurt", "title": "Void Walker", "pref": "Turf"},
                {"name": "GHOST LORD", "pheno": "Wraith Ghost Walker", "style": "Stretch-runner", "title": "Phantom Terror", "pref": "Dirt"},
                {"name": "AUREATE LEGEND", "pheno": "Rose Gold-Dipped", "style": "Almighty", "title": "Golden Emperor", "pref": "Turf"}
            ]
            b_data = random.choice(bosses)
            effective_gen = min(10, gen)
            player_max_pot = MAX_POTENTIAL_BASE + (effective_gen * MAX_POTENTIAL_PER_GEN)
            final_stat = player_max_pot * BOSS_DIFFICULTY_SCALING.get("Tier2", 1.15)

        if player_horse.age == 2:
            final_stat *= 0.85
            
        return Horse(
            name=b_data["name"], gender="Colt", phenotype=b_data["pheno"], 
            cur_speed=final_stat * random.uniform(0.95, 1.1),
            cur_stamina=final_stat * random.uniform(0.95, 1.1),
            cur_grit=final_stat * random.uniform(0.95, 1.1),
            preferred_surface=b_data["pref"], race_class=player_horse.race_class,
            running_style=b_data["style"], boss_title=b_data["title"],
            condition=100.0 
        )