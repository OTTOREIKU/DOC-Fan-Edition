import random
import textwrap
import os

# --- IMPORT OUR NEW CONFIG SYSTEM ---
from config import EVENT_CHANCE_TRAINING, EVENT_CHANCE_RACING, EVENT_CHANCE_BREEDING

class EventManager:
    def __init__(self):
        # --- TRAINING & REST EVENTS ---
        self.training_events = [
            {"name": "The Stable Cat", "text": "A stray orange tabby cat decided to take a nap on {name}'s back. They seem incredibly relaxed and happy to have a friend.", "eff": {"mood": 20, "trust": 15}, "items": {}, "is_bad": False},
            {"name": "Training Breakthrough", "text": "Something just clicked! {name} suddenly understood the training perfectly and pushed past their normal limits!", "eff": {"speed": 0.3, "stamina": 0.3, "grit": 0.3}, "items": {}, "is_bad": False},
            {"name": "Spooked!", "text": "A loud truck drove by the farm and completely spooked {name}! They spent the afternoon pacing nervously.", "eff": {"fatigue": 10, "mood": -15}, "items": {}, "is_bad": True},
            {"name": "Found a Coin", "text": "While walking the paddock, you noticed something shiny in the dirt. It's a dropped wallet containing some cash!", "eff": {}, "items": {"credits": 2500}, "is_bad": False},
            {"name": "Extra Zoomies", "text": "{name} was feeling incredibly energetic today and did extra laps around the paddock! They are tired, but gained some speed.", "eff": {"fatigue": 15, "speed": 0.2}, "items": {}, "is_bad": False},
            {"name": "Sponsorship Sample", "text": "A sales rep stopped by the farm and offered you a free sample of their new racing paste!", "eff": {}, "items": {"paste": 1}, "is_bad": False},
            {"name": "Bad Hay", "text": "A bad batch of hay gave {name} a slight stomach ache. They are feeling a bit sluggish today.", "eff": {"fatigue": 10, "mood": -10}, "items": {}, "is_bad": True},
            {"name": "Fan Mail", "text": "A package arrived at the stable from a devoted fan! It contained some premium horse treats.", "eff": {}, "items": {"mints": 1}, "is_bad": False},
            {"name": "Abandoned Supply Shed", "text": "While cleaning out an old barn on the property, you found a sealed crate of perfectly good premium oats!", "eff": {}, "items": {"oats": 2}, "is_bad": False},
            {"name": "Stubborn Streak", "text": "{name} decided they simply did not want to cooperate today. They ignored your commands and got frustrated.", "eff": {"trust": -10, "mood": -15}, "items": {}, "is_bad": True}
        ]

        # --- GENERAL POST-RACE EVENTS ---
        self.race_events = [
            {"name": "Muddy Puddles", "text": "After the race, {name} found a mud puddle and gleefully rolled in it. They are filthy, but very happy.", "eff": {"mood": 15}, "items": {}, "is_bad": False},
            {"name": "Paparazzi", "text": "Aggressive sports photographers flashed bright cameras in {name}'s face while walking back to the stables. They are highly agitated.", "eff": {"mood": -20}, "items": {}, "is_bad": True},
            {"name": "Sore Muscle", "text": "{name} tweaked a muscle slightly while cooling down. It's not a full injury, but they are extra fatigued.", "eff": {"fatigue": 20}, "items": {}, "is_bad": True},
            {"name": "A Generous Fan", "text": "A wealthy spectator was incredibly impressed with {name}'s running style and handed you a tip!", "eff": {}, "items": {"credits": 5000}, "is_bad": False},
            {"name": "Dietary Gift", "text": "A local farm owner loved the race and gifted your stable a bag of their highest quality oats.", "eff": {}, "items": {"oats": 1}, "is_bad": False},
            {"name": "Jockey's Praise", "text": "The jockey couldn't stop talking about how well-behaved {name} was in the gates. The horse fed off the positive energy!", "eff": {"trust": 15, "mood": 10}, "items": {}, "is_bad": False},
            {"name": "Post-Race Jitters", "text": "The roar of the crowd got to {name}. They are sweating profusely and having a hard time calming down.", "eff": {"fatigue": 15, "trust": -5}, "items": {}, "is_bad": True},
            {"name": "Track Side Snack", "text": "You let {name} graze on some incredibly lush, sweet grass near the track exit. They feel great.", "eff": {"fatigue": -10, "mood": 10}, "items": {}, "is_bad": False}
        ]

        # --- WINNER'S CIRCLE EVENTS (1st Place Only) ---
        self.win_events = [
            {"name": "The Winner's Bouquet", "text": "Officials draped a beautiful, fragrant wreath of flowers over {name}'s neck! They look incredibly majestic and proud.", "eff": {"mood": 35, "trust": 25}, "items": {}, "is_bad": False},
            {"name": "Sponsorship Deal", "text": "A representative from a luxury saddle company wants to sponsor {name}! They handed you a massive signing bonus.", "eff": {}, "items": {"credits": 25000}, "is_bad": False},
            {"name": "Adoring Fans", "text": "The entire grandstand chanted {name}'s name as you paraded them in front of the rails. The horse feels invincible!", "eff": {"mood": 25, "grit": 0.3}, "items": {}, "is_bad": False},
            {"name": "Champion's Vigor", "text": "Winning this race unlocked something deep inside {name}. They realize they are a champion, permanently boosting their potential.", "eff": {"p_speed": 0.2, "p_stam": 0.2, "p_grit": 0.2}, "items": {}, "is_bad": False},
            {"name": "Miracle Delivery", "text": "To celebrate the victory, an anonymous fan mailed a rare medical salve to your stable!", "eff": {}, "items": {"salve": 1}, "is_bad": False},
            {"name": "Cover of the Magazine", "text": "{name} made the front cover of 'Derby Digest' magazine! The prestige brings in bonus stable funds.", "eff": {"mood": 15}, "items": {"credits": 10000}, "is_bad": False}
        ]

        # --- BREEDING EVENTS (Birth Events) ---
        self.breeding_events = [
            {"name": "The Miracle Foal", "text": "Against all odds, the foal was born bursting with an unnatural vigor. They seem destined for greatness!", "eff": {"p_speed": 5.0, "p_stam": 5.0, "p_grit": 5.0}},
            {"name": "Love at First Sight", "text": "The moment the foal stood up, it walked directly over to you and nuzzled your coat. A bond was instantly formed.", "eff": {"trust": 100, "mood": 100}},
            {"name": "Media Bidding War", "text": "Because of the parents' legendary status, racing magazines paid a fortune for the exclusive first photos of the foal!", "items": {"credits": 25000}},
            {"name": "The Reincarnation", "text": "The stablehands are whispering... this foal looks and acts EXACTLY like a champion from 50 years ago. It already knows how to run.", "eff": {"reincarnation": True}},
            {"name": "The Runt of the Litter", "text": "The foal is incredibly small and weak, but the vet says it has the heart of a lion. It will take a lot of work to train.", "eff": {"runt": True}},
            {"name": "Wild & Untamed", "text": "This foal is an absolute terror! It kicked a hole in the stall on day one! It's incredibly fast, but completely unmanageable.", "eff": {"wild": True}},
            {"name": "Difficult Foaling", "text": "It was a rough night in the barn. The foal survived, but needs extra care and rest immediately.", "eff": {"fatigue": 50}, "items": {"salve": 1}}
        ]

    def trigger_event(self, horse, stable_mgr, event_type="training", did_win=False):
        roll = random.random()

        # --- TRIGGERS PULLED FROM CONFIG ---
        if event_type == "training":
            trigger_chance = EVENT_CHANCE_TRAINING 
            bad_threshold = 0.10  
        else: 
            trigger_chance = EVENT_CHANCE_RACING 
            bad_threshold = 0.15  

        if roll > trigger_chance:
            return False

        is_bad_roll = roll > bad_threshold

        if event_type == "race" and did_win and random.random() < 0.50:
            pool = self.win_events
            icon = "🏆"
            is_bad_roll = False 
        elif event_type == "race":
            pool = self.race_events
            icon = "🎫"
        else:
            pool = self.training_events
            icon = "🎲"

        valid_events = [e for e in pool if e.get("is_bad", False) == is_bad_roll]
        
        if not valid_events:
            valid_events = pool

        event = random.choice(valid_events)
        self._apply_and_display(horse, stable_mgr, event, icon)
        return True

    def trigger_breeding_event(self, horse, stable_mgr):
        # --- TRIGGER PULLED FROM CONFIG ---
        if random.random() > EVENT_CHANCE_BREEDING: 
            return False
            
        event = random.choice(self.breeding_events)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*64)
        print(f"🌟 RARE BIRTH EVENT: {event['name'].upper()} 🌟".center(64))
        print("="*64)
        
        wrapped_text = textwrap.fill(event["text"], width=60)
        for line in wrapped_text.split('\n'):
            print(f"  {line}")
            
        print("-" * 64)
        print(" [EFFECTS]".center(64))
        
        eff = event.get("eff", {})
        if "p_speed" in eff:
            horse.pot_speed += eff["p_speed"]
            horse.pot_stamina += eff["p_stam"]
            horse.pot_grit += eff["p_grit"]
            print("  ✨ +5.0 to ALL Potential Stats!")
            
        if "trust" in eff:
            horse.trust = eff["trust"]
            horse.condition = eff.get("mood", 100)
            print("  💖 Trust and Mood maximized instantly!")
            
        if "reincarnation" in eff:
            horse.cur_speed = horse.pot_speed * 0.50
            horse.cur_stamina = horse.pot_stamina * 0.50
            horse.cur_grit = horse.pot_grit * 0.50
            print("  🏇 Foal starts with 50% of its training already complete!")
            
        if "runt" in eff:
            horse.cur_speed = horse.pot_speed * 0.05
            horse.cur_stamina = horse.pot_stamina * 0.05
            horse.cur_grit = horse.pot_grit * 0.05
            horse.pot_grit *= 1.20
            print("  📉 Starts with terrible current stats.")
            print("  🔥 Maximum Grit Potential increased by 20%!")
            
        if "wild" in eff:
            horse.personality = "Alpha"
            horse.trust = 0.0
            horse.condition = 0.0
            horse.pot_speed *= 1.15
            print("  💢 Personality set to 'Alpha' with 0 Trust and 0 Mood.")
            print("  ⚡ Maximum Speed Potential increased by 15%!")
            
        if "fatigue" in eff:
            horse.fatigue = eff["fatigue"]
            print(f"  🔴 Foal starts with {eff['fatigue']}% Fatigue.")
            
        items = event.get("items", {})
        if "credits" in items:
            stable_mgr.add_credits(items["credits"])
            print(f"  💰 Earned ${items['credits']:,}!")
            
        if "salve" in items:
            stable_mgr.add_item("salve", items["salve"])
            print(f"  ⚕️ Received x{items['salve']} Miracle Salve from the Vet!")
            
        print("=" * 64)
        input("\nPress Enter to continue...")
        return True

    def _apply_and_display(self, horse, stable_mgr, event, icon):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*64)
        print(f"{icon} RANDOM EVENT OCCURRED! {icon}".center(64))
        print("="*64)
        
        formatted_text = event["text"].format(name=horse.name)
        wrapped_text = textwrap.fill(formatted_text, width=60)
        for line in wrapped_text.split('\n'):
            print(f"  {line}")
            
        print("-" * 64)
        print(" [EFFECTS]".center(64))
        
        eff = event.get("eff", {})
        if "mood" in eff:
            horse.condition = max(0.0, min(100.0, getattr(horse, 'condition', 50.0) + eff["mood"]))
            symbol = "📈" if eff["mood"] > 0 else "📉"
            print(f"  {symbol} Mood changed by {eff['mood']}")
            
        if "fatigue" in eff:
            horse.fatigue = max(0.0, min(100.0, horse.fatigue + eff["fatigue"]))
            symbol = "🟢" if eff["fatigue"] < 0 else "🔴"
            print(f"  {symbol} Fatigue changed by {eff['fatigue']}")
            
        if "trust" in eff:
            horse.trust = max(0.0, min(100.0, getattr(horse, 'trust', 50.0) + eff["trust"]))
            symbol = "💖" if eff["trust"] > 0 else "💔"
            print(f"  {symbol} Trust changed by {eff['trust']}")
            
        if "speed" in eff:
            horse.cur_speed = min(horse.pot_speed, horse.cur_speed + eff["speed"])
            print(f"  ⚡ Speed increased slightly!")
            
        if "stamina" in eff:
            horse.cur_stamina = min(horse.pot_stamina, horse.cur_stamina + eff["stamina"])
            print(f"  🛡️ Stamina increased slightly!")
            
        if "grit" in eff:
            horse.cur_grit = min(horse.pot_grit, horse.cur_grit + eff["grit"])
            print(f"  🔥 Grit increased slightly!")
            
        if "p_speed" in eff:
            horse.pot_speed += eff["p_speed"]
            horse.pot_stamina += eff["p_stam"]
            horse.pot_grit += eff["p_grit"]
            print(f"  ✨ Maximum Genetic Potential increased!")

        items = event.get("items", {})
        if "credits" in items:
            stable_mgr.add_credits(items["credits"])
            print(f"  💰 Earned ${items['credits']:,}!")
            
        if "mints" in items:
            stable_mgr.add_item("mints", items["mints"])
            print(f"  🍬 Received x{items['mints']} Peppermint Treats!")
            
        if "oats" in items:
            stable_mgr.add_item("oats", items["oats"])
            print(f"  🍎 Received x{items['oats']} Premium Oats!")
            
        if "salve" in items:
            stable_mgr.add_item("salve", items["salve"])
            print(f"  ⚕️ Received x{items['salve']} Miracle Salve!")
            
        if "paste" in items:
            stable_mgr.add_item("paste", items["paste"])
            print(f"  ⚡ Received x{items['paste']} Electrolyte Paste!")

        print("=" * 64)
        input("\nPress Enter to continue...")