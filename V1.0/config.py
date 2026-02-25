# config.py
# ==========================================
# ⚙️ DERBY OWNERS CLUB - MASTER CONFIG ⚙️
# ==========================================

# --- RACE ENGINE SETTINGS ---
# "multiplicative" = Buffs cascade and multiply each other (Exponential/Original)
# "additive" = Buffs are summed into one total pool before multiplying (Linear)
BUFF_MATH_MODE = "additive" 

# Hidden stat penalties for early generations during races to encourage breeding.
# Gen 5+ defaults to 1.0 (no penalty).
GENERATION_MULTIPLIERS = {
    0: 0.95, # -5% to all stats
    1: 0.96, # -4% to all stats
    2: 0.97, # -3% to all stats
    3: 0.98, # -2% to all stats
    4: 0.99  # -1% to all stats
}

# --- MARKETPLACE & SCOUTING ---
BRIBE_COST_MULTIPLIERS = [0.50, 0.75, 1.00]
MAX_BRIBES_PER_CYCLE = 3
BRIBE_RESET_MONTHS = 12

SCOUTING_NETWORK_TIERS = {
    0: {"size": 3, "cur_bonus": 0.0, "pot_bonus": 0.0},
    1: {"size": 4, "cur_bonus": 0.0, "pot_bonus": 0.0},
    2: {"size": 4, "cur_bonus": 0.05, "pot_bonus": 0.0},
    3: {"size": 5, "cur_bonus": 0.05, "pot_bonus": 0.0},
    4: {"size": 5, "cur_bonus": 0.10, "pot_bonus": 0.0},
    5: {"size": 5, "cur_bonus": 0.10, "pot_bonus": 0.10},
}

# --- ECONOMY & REWARDS ---
BASE_PURSES = {
    "Maiden": 2000, 
    "G3": 8000, 
    "G2": 25000, 
    "G1": 100000
}

MARKET_PRICE_BASE = 150       # Base multiplier for buying Market horses
STUD_FEE_BASE = 200           # Base multiplier for Syndicate breeding fees
GEN_PRICE_MULTIPLIER = 1.5    # How much prices scale up per generation

ACADEMY_BASE_PAYOUT = 5000    # Flat monthly income per horse in Academy
ACADEMY_GEN_BONUS = 2500      # Extra monthly income per generation level

# --- AI DIFFICULTY SCALING ---
AI_DIFFICULTY_SCALING = {
    "Maiden": (0.15, 0.25), 
    "G3": (0.40, 0.55),      
    "G2": (0.70, 0.85),      
    "G1": (0.90, 1.00)       
}

BOSS_DIFFICULTY_SCALING = {
    "Tier1": 1.10, # Bosses for Gen 0-5
    "Tier2": 1.15  # Mythic Bosses for Gen 6+
}

# --- BREEDING & GENETICS ---
MAX_POTENTIAL_BASE = 75.0     # Gen 0 maximum potential cap
MAX_POTENTIAL_PER_GEN = 15.0  # How much the cap increases each generation

MUTATION_CHANCE = 0.05        # 5% chance to roll a Mythic/Legendary coat 
TITLE_INHERIT_CHANCE = 0.15   # 15% base chance to pass down a career title

LINEBREEDING_BONUS = 1.15     # +15% potential stat boost for linebreeding
INBREEDING_STAM_PENALTY = 0.75 # -25% max stamina penalty for inbreeding

# --- TRAINING & REST ---
RACE_FATIGUE_RANGE = (30.0, 45.0) 

ASSISTANT_TRAINER_MAX_STATS = 20.0  # Max total stat points a horse can gain passively

STD_REST_FATG = 35.0          # Fatigue removed by resting in a normal stable
STD_REST_MOOD = 20.0          # Mood gained by resting in a normal stable
SPA_REST_FATG = 60.0          # Fatigue removed by resting with a Luxury Spa
SPA_REST_MOOD = 40.0          # Mood gained by resting with a Luxury Spa

FACILITY_BONUS_PER_LVL = 0.05 # 5% stat gain increase per Track/Pool upgrade level

# --- RANDOM EVENTS ---
EVENT_CHANCE_TRAINING = 0.15  # 15% chance for a random event during training weeks
EVENT_CHANCE_RACING = 0.20    # 20% chance for a random event post-race
EVENT_CHANCE_BREEDING = 0.10  # 10% chance for a rare birth event