import random

class ArtGenerator:
    COLORS = {
        "Shadow": ("\033[38;5;236m", "\033[38;5;232m"),      
        "Ghost": ("\033[38;5;255m", "\033[38;5;255m"),      
        "Metallic": ("\033[38;5;214m", "\033[38;5;220m"),   
        "Snowburst": ("\033[38;5;123m", "\033[97m"),        
        "Bloody": ("\033[38;5;124m", "\033[38;5;88m"),      
        "Inferno": ("\033[38;5;208m", "\033[38;5;196m"),    
        "Abyss": ("\033[38;5;54m", "\033[38;5;16m"),        
        "Celestial": ("\033[38;5;226m", "\033[97m"),        
        "Cremello": ("\033[38;5;230m", "\033[97m"),         
        "Perlino": ("\033[38;5;230m", "\033[38;5;136m"),    
        "Smoky Cream": ("\033[38;5;230m", "\033[38;5;244m"),
        "Silver Dapple": ("\033[38;5;238m", "\033[38;5;145m"), 
        "Champagne": ("\033[38;5;136m", "\033[38;5;136m"),
        "Strawberry Roan": ("\033[38;5;138m", "\033[38;5;130m"),
        "Blue Roan": ("\033[38;5;66m", "\033[38;5;238m"),
        "Grullo": ("\033[38;5;244m", "\033[38;5;236m"),     
        "Red Dun": ("\033[38;5;173m", "\033[38;5;130m"),
        "Bay Dun": ("\033[38;5;178m", "\033[38;5;236m"),
        "Buckskin": ("\033[38;5;178m", "\033[38;5;236m"),   
        "Palomino": ("\033[38;5;220m", "\033[97m"),         
        "Smoky Black": ("\033[38;5;240m", "\033[38;5;234m"),
        "Dapple Grey": ("\033[38;5;246m", "\033[38;5;250m"), 
        "Fleabitten Grey": ("\033[38;5;254m", "\033[38;5;254m"),
        "Grey": ("\033[38;5;248m", "\033[38;5;244m"),            
        "Chestnut": ("\033[38;5;130m", "\033[38;5;130m"),
        "Sorrel": ("\033[38;5;166m", "\033[38;5;166m"),      
        "Bay": ("\033[38;5;94m", "\033[38;5;240m"),         
        "Black": ("\033[38;5;239m", "\033[38;5;234m"),      
        "White": ("\033[97m", "\033[97m"),
    }
    
    DEFAULT_BODY = "\033[39m"
    DEFAULT_POINT = "\033[39m"
    WHITE = "\033[97m"
    RESET = "\033[39m"

    @classmethod
    def generate(cls, horse):
        random.seed(horse.id) 
        
        pheno = horse.phenotype
        dna = horse.genotype
        
        pheno_base = pheno.split(" with ")[0]
        
        body_col = cls.DEFAULT_BODY
        point_col = cls.DEFAULT_POINT
        
        for key in sorted(cls.COLORS.keys(), key=lambda x: -len(x)):
            if key in pheno_base:
                body_col, point_col = cls.COLORS[key]
                break
                
        is_pinto = any(p in pheno for p in ["Tobiano", "Overo", "Panda", "Chimera"])
        is_appaloosa = any(p in pheno for p in ["Appaloosa", "Leopard"])
        is_brindle = "Brindle" in pheno
        is_dapple = "Dapple" in pheno
        is_fleabitten = "Fleabitten" in pheno
        is_splash = "Splash" in pheno
        is_sabino = "Sabino" in pheno
        is_rabicano = "Rabicano" in pheno
        
        face_marking = dna.get("F", ["n"])[0] != "n" if isinstance(dna, dict) else False
        leg_marking = dna.get("L", ["n"])[0] != "n" if isinstance(dna, dict) else False
        
        # --- NEW: ALL 15 MYTHIC SUB-VARIANTS ---
        front_body, front_point = body_col, point_col
        rear_body, rear_point = body_col, point_col
        
        # CHIMERA
        if "Sanguine Chimera" in pheno:
            front_body, front_point = "\033[38;5;232m", "\033[38;5;232m"
            rear_body, rear_point = "\033[38;5;124m", "\033[38;5;124m"
        elif "Eclipse Chimera" in pheno:
            front_body, front_point = "\033[38;5;232m", "\033[38;5;232m"
            rear_body, rear_point = "\033[97m", "\033[97m"
        elif "Golden Chimera" in pheno:
            front_body, front_point = "\033[97m", "\033[97m"
            rear_body, rear_point = "\033[38;5;220m", "\033[38;5;220m"
        
        # ABYSSAL PRISM
        elif "Void Abyssal Prism" in pheno:
            front_body, front_point = "\033[38;5;201m", "\033[38;5;201m" 
            rear_body, rear_point = "\033[38;5;57m", "\033[38;5;57m"     
        elif "Oceanic Abyssal Prism" in pheno:
            front_body, front_point = "\033[38;5;51m", "\033[38;5;51m"
            rear_body, rear_point = "\033[38;5;18m", "\033[38;5;18m"
        elif "Cosmic Abyssal Prism" in pheno:
            front_body, front_point = "\033[38;5;213m", "\033[38;5;213m"
            rear_body, rear_point = "\033[38;5;17m", "\033[38;5;17m"
            
        # GHOST WALKER
        elif "Spectral Ghost Walker" in pheno:
            front_body, front_point = "\033[38;5;51m", "\033[38;5;51m"   
            rear_body, rear_point = "\033[38;5;153m", "\033[38;5;153m"   
        elif "Banshee Ghost Walker" in pheno:
            front_body, front_point = "\033[38;5;46m", "\033[38;5;46m"
            rear_body, rear_point = "\033[38;5;250m", "\033[38;5;250m"
        elif "Wraith Ghost Walker" in pheno:
            front_body, front_point = "\033[38;5;183m", "\033[38;5;183m"
            rear_body, rear_point = "\033[38;5;240m", "\033[38;5;240m"
            
        # SOLAR FLARE
        elif "Nova Solar Flare" in pheno:
            front_body, front_point = "\033[38;5;226m", "\033[38;5;196m" 
            rear_body, rear_point = front_body, front_point
        elif "Corona Solar Flare" in pheno:
            front_body, front_point = "\033[38;5;208m", "\033[97m"
            rear_body, rear_point = front_body, front_point
        elif "Plasma Solar Flare" in pheno:
            front_body, front_point = "\033[38;5;205m", "\033[38;5;39m"
            rear_body, rear_point = front_body, front_point
            
        # GOLD-DIPPED
        elif "Aureate Gold-Dipped" in pheno:
            front_body, front_point = "\033[38;5;220m", "\033[38;5;214m" 
            rear_body, rear_point = front_body, front_point
        elif "Rose Gold-Dipped" in pheno:
            front_body, front_point = "\033[38;5;217m", "\033[38;5;211m"
            rear_body, rear_point = front_body, front_point
        elif "Platinum Gold-Dipped" in pheno:
            front_body, front_point = "\033[38;5;230m", "\033[38;5;255m"
            rear_body, rear_point = front_body, front_point
            
        # Fallbacks for older save data
        elif "Chimera" in pheno:
            front_body, front_point = "\033[38;5;232m", "\033[38;5;232m"
            rear_body, rear_point = "\033[38;5;124m", "\033[38;5;124m"
        elif "Abyssal Prism" in pheno:
            front_body, front_point = "\033[38;5;201m", "\033[38;5;201m" 
            rear_body, rear_point = "\033[38;5;57m", "\033[38;5;57m"     
        elif "Ghost Walker" in pheno:
            front_body, front_point = "\033[38;5;51m", "\033[38;5;51m"   
            rear_body, rear_point = "\033[38;5;153m", "\033[38;5;153m"   
        elif "Solar Flare" in pheno:
            front_body, front_point = "\033[38;5;226m", "\033[38;5;196m" 
            rear_body, rear_point = front_body, front_point
        elif "Gold-Dipped" in pheno:
            front_body, front_point = "\033[38;5;220m", "\033[38;5;214m" 
            rear_body, rear_point = front_body, front_point

        raw_lines = [
            "      ,~_       __,~  ",
            "    //  _\\     /  \\\\  ",
            "    \\ \\/ \\/    \\/ \\/  ",
            "     FRONT      REAR  "
        ]
        
        painted_lines = [""] 
        
        for r_idx, line in enumerate(raw_lines):
            painted_line = ""
            for c_idx, char in enumerate(line):
                if char in [' ', '\n']:
                    painted_line += char
                    continue
                    
                is_front = c_idx < 13 
                current_body = front_body if is_front else rear_body
                current_point = front_point if is_front else rear_point
                
                current_char_color = current_body
                
                if r_idx == 3:
                    current_char_color = "\033[38;5;240m" 
                    painted_line += f"{current_char_color}{char}{cls.RESET}"
                    continue
                
                if r_idx == 0:
                    if is_front: 
                        if char in [',', '~']: 
                            current_char_color = current_point
                        elif char == '_': 
                            current_char_color = cls.WHITE if face_marking or is_sabino else current_body
                    else: 
                        if char == '~': 
                            current_char_color = cls.WHITE if is_rabicano else current_point
                        else:
                            current_char_color = current_body
                
                elif r_idx == 2:
                    if char in ['\\', '/']:
                        current_char_color = current_point
                        if is_splash and random.random() < 0.90: current_char_color = cls.WHITE
                        elif is_sabino and random.random() < 0.85: current_char_color = cls.WHITE
                        elif leg_marking and random.random() < 0.70: current_char_color = cls.WHITE
                        
                if current_char_color == current_body:
                    if is_pinto and random.random() < 0.45:
                        current_char_color = cls.WHITE
                    elif is_appaloosa and random.random() < 0.25:
                        current_char_color = cls.WHITE
                    elif is_brindle and random.random() < 0.35:
                        if current_body in ["\033[38;5;239m", "\033[38;5;240m", "\033[38;5;236m"]:
                            current_char_color = "\033[38;5;130m" 
                        else:
                            current_char_color = "\033[38;5;234m" 
                    elif is_dapple and random.random() < 0.25:
                        current_char_color = "\033[38;5;252m"
                    elif is_fleabitten and random.random() < 0.15:
                        current_char_color = random.choice(["\033[38;5;130m", "\033[38;5;240m"])
                    elif is_splash and r_idx == 2 and random.random() < 0.60:
                        current_char_color = cls.WHITE
                    elif is_sabino and random.random() < 0.15:
                        current_char_color = cls.WHITE
                    elif is_rabicano and not is_front and random.random() < 0.20:
                        current_char_color = cls.WHITE

                painted_line += f"{current_char_color}{char}{cls.RESET}"
            painted_lines.append(painted_line)
            
        painted_lines.append("") 
        
        random.seed() 
        return "\n".join(painted_lines)