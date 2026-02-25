import json
import zlib
import base64
import os
import re
import uuid
import math
import textwrap 
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo
from art_generator import ArtGenerator

class CardGenerator:
    def __init__(self):
        self.coat_gradients = {
            "Bay": ("#5c3a21", "#1a0f08"),
            "Chestnut": ("#8b4513", "#3a1904"),
            "Black": ("#2b2b2b", "#050505"),
            "Grey": ("#808080", "#262626"),
            "White": ("#e6e6e6", "#888888"),
            "Roan": ("#7a6363", "#2e2121"),
            "Palomino": ("#cda434", "#59430b"),
            "Buckskin": ("#dfc16d", "#4a3c18"),
            "Gold-Dipped": ("#ffd700", "#665500"),
            "Chimera": ("#800000", "#1a1a1a"), 
            "Solar Flare": ("#ff4500", "#ffaa00"), 
            "Abyssal Prism": ("#000033", "#4b0082"), 
            "Ghost Walker": ("#b3b3cc", "#404040"),
            "Shadow": ("#1a1a1a", "#000000"),
            "Bloody": ("#8b0000", "#220000"),
            "Silver Dapple": ("#a9a9a9", "#404040"),
            "Celestial": ("#f0f8ff", "#6ba5c2") 
        }

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _create_gradient_bg(self, width, height, color1, color2):
        base = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(base)
        r1, g1, b1 = self._hex_to_rgb(color1)
        r2, g2, b2 = self._hex_to_rgb(color2)
        for y in range(height):
            ratio = y / height
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        return base

    def get_marking_accents(self, phenotype):
        accents = []
        p_lower = phenotype.lower()
        if "white socks" in p_lower or "sock" in p_lower: accents.append("#FFFFFF")
        if "blaze" in p_lower: accents.append("#F8F8F8")
        if "star" in p_lower: accents.append("#E8E8E8")
        if "appaloosa" in p_lower: accents.extend(["#FFFFFF", "#1A1A1A"])
        if "tobiano" in p_lower or "overo" in p_lower or "splash" in p_lower: accents.append("#FFFFFF")
        if "roan" in p_lower: accents.append("#D8C8C8")
        if "dapple" in p_lower: accents.append("#CCCCCC")
        if "champagne" in p_lower: accents.append("#FAD6A5")
        if "dun" in p_lower: accents.append("#C3B091")
        if "cream" in p_lower or "cremello" in p_lower or "perlino" in p_lower: accents.append("#FFFDD0")
        if "pearl" in p_lower: accents.append("#EAE0C8")
        if "chimera" in p_lower: accents.append("#800000")
        if "solar flare" in p_lower: accents.append("#FF4500")
        if "abyssal" in p_lower: accents.append("#000033")
        if "ghost" in p_lower: accents.append("#B3B3CC")
        return accents

    def compress_horse(self, horse):
        packed_data = {
            "id": horse.id, 
            "n": horse.name, "g": horse.gender, "c": horse.phenotype,
            "dna": horse.genotype, "gen": horse.generation,
            "ps": round(horse.pot_speed, 2), "pt": round(horse.pot_stamina, 2), "pg": round(horse.pot_grit, 2),
            "cs": round(horse.cur_speed, 2), "ct": round(horse.cur_stamina, 2), "cg": round(horse.cur_grit, 2),
            "rs": horse.running_style, "psurf": horse.preferred_surface,
            "w": horse.wins, "rr": horse.races_run, "cw": horse.championships_won,
            "e": horse.earnings,
            "t": horse.titles, "p": horse.personality, "f": getattr(horse, 'favorite_food', "1"),
            "a": horse.age, "mo": horse.month, "wk": horse.week,
            "fat": round(horse.fatigue, 1), "cond": round(getattr(horse, 'condition', 50.0), 1),
            "ret": horse.is_retired
        }
        
        json_str = json.dumps(packed_data, separators=(',', ':'))
        compressed = zlib.compress(json_str.encode('utf-8'))
        encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')
        return encoded

    def decompress_horse(self, code_str):
        from spawner import Horse
        try:
            compressed = base64.urlsafe_b64decode(code_str.encode('utf-8'))
            json_str = zlib.decompress(compressed).decode('utf-8')
            data = json.loads(json_str)
            
            return Horse(
                id=data.get("id", str(uuid.uuid4())[:8]), 
                name=data["n"], gender=data["g"], phenotype=data["c"], genotype=data["dna"],
                generation=data["gen"], pot_speed=data["ps"], pot_stamina=data["pt"], pot_grit=data["pg"],
                cur_speed=data["cs"], cur_stamina=data["ct"], cur_grit=data["cg"],
                running_style=data["rs"], preferred_surface=data["psurf"],
                wins=data["w"], races_run=data["rr"], championships_won=data["cw"],
                earnings=data.get("e", 0),
                titles=data.get("t", []), personality=data.get("p", "Willing"), favorite_food=data.get("f", "1"),
                age=data.get("a", 3), month=data.get("mo", 1), week=data.get("wk", 1),
                fatigue=data.get("fat", 0.0), condition=data.get("cond", 50.0),
                is_retired=data.get("ret", True), is_npc=False
            )
        except Exception as e:
            return None

    # --- RESTORED COLOR MEMORY FIX + VIBRANT MATH ---
    def _draw_ansi_text(self, draw, x_start, y, text, font, char_width, start_color="#ffffff"):
        current_color = start_color
        parts = re.split(r'\x1b\[([0-9;]*)m', text)
        x = x_start
        
        for i, part in enumerate(parts):
            if i % 2 == 1: 
                code = part
                if code in ('0', '', '39'): current_color = "#ffffff"
                elif code in ('93', '33'): current_color = "#ffd700"
                elif code == '90': current_color = "#aaaaaa" 
                elif code.startswith('38;5;'): 
                    try:
                        cidx = int(code.split(';')[-1])
                        if 16 <= cidx <= 231:
                            val = cidx - 16
                            steps = [0, 95, 135, 175, 215, 255]
                            r = steps[(val // 36)]
                            g = steps[(val % 36) // 6]
                            b = steps[(val % 6)]
                            
                            r = min(255, int(r * 1.35))
                            g = min(255, int(g * 1.35))
                            b = min(255, int(b * 1.35))
                            
                            current_color = f"#{r:02x}{g:02x}{b:02x}"
                        elif 232 <= cidx <= 255: 
                            v = (cidx - 232) * 10 + 8
                            v = min(255, int(v * 1.4)) 
                            current_color = f"#{v:02x}{v:02x}{v:02x}"
                        
                        if cidx == 130: current_color = "#ff8c00" 
                        if cidx == 94: current_color = "#e65c00"  
                        if cidx == 52: current_color = "#ff4d4d"  
                        if cidx == 237: current_color = "#888888" 
                    except: pass
            else: 
                if part:
                    draw.text((x, y), part, fill=current_color, font=font)
                    x += len(part) * char_width
        
        return current_color # Passes the active color back out so the next line remembers it!

    def _draw_star(self, draw, cx, cy, radius, fill):
        points = []
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
            inner_angle = math.radians(i * 72 + 36 - 90)
            inner_radius = radius * 0.4
            points.append((cx + inner_radius * math.cos(inner_angle), cy + inner_radius * math.sin(inner_angle)))
        draw.polygon(points, fill=fill)

    def generate_card(self, horse, include_code=True):
        trade_code = self.compress_horse(horse) if include_code else None
        
        width, height = 400, 860
        
        c1, c2 = self.coat_gradients.get(next((c for c in self.coat_gradients if c in horse.phenotype), "Bay"), ("#5c3a21", "#1a0f08"))
        
        outer_border_color = "#A0A0A0" 
        text_color = "#ffffff"

        img = Image.new('RGB', (width, height), color="#000000")
        
        grad_bg = self._create_gradient_bg(width, height, c1, c2)
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([10, 10, width-10, height-10], radius=20, fill=255)
        img.paste(grad_bg, (0,0), mask)

        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([10, 10, width-10, height-10], radius=20, outline=outer_border_color, width=4)

        try:
            header_font = ImageFont.truetype("arial.ttf", 15)
            text_font = ImageFont.truetype("arial.ttf", 13)
            bold_font = ImageFont.truetype("arialbd.ttf", 13)
            small_font = ImageFont.truetype("arial.ttf", 11)
            small_bold = ImageFont.truetype("arialbd.ttf", 11)
            code_font = ImageFont.truetype("arial.ttf", 10) 
        except IOError:
            header_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            bold_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            small_bold = ImageFont.load_default()
            code_font = ImageFont.load_default()
        
        # --- UPSCALED FONT FOR LARGER HORSE ---
        try:
            art_font = ImageFont.truetype("consola.ttf", 24) 
        except IOError:
            try:
                art_font = ImageFont.truetype("Menlo.ttc", 24) 
            except IOError:
                try:
                    art_font = ImageFont.truetype("cour.ttf", 24) 
                except IOError:
                    art_font = ImageFont.load_default() 

        name_text = horse.name.upper()
        name_font_size = 28
        max_name_width = width - 40 
        
        try:
            name_font = ImageFont.truetype("arial.ttf", name_font_size)
            try: text_w = draw.textlength(name_text, font=name_font)
            except AttributeError: text_w = name_font.getsize(name_text)[0]
            
            while text_w > max_name_width and name_font_size > 12:
                name_font_size -= 1
                name_font = ImageFont.truetype("arial.ttf", name_font_size)
                try: text_w = draw.textlength(name_text, font=name_font)
                except AttributeError: text_w = name_font.getsize(name_text)[0]
            
            while text_w > max_name_width and len(name_text) > 5:
                name_text = name_text[:-4] + "..."
                try: text_w = draw.textlength(name_text, font=name_font)
                except AttributeError: text_w = name_font.getsize(name_text)[0]
                
        except IOError:
            name_font = ImageFont.load_default()

        draw.text((width/2, 35), name_text, fill=text_color, font=name_font, anchor="mm")

        def draw_lbl(x, y, lbl, val, val_color=text_color):
            draw.text((x, y), lbl, fill=text_color, font=bold_font)
            try: offset = draw.textlength(lbl, font=bold_font)
            except AttributeError: offset = bold_font.getsize(lbl)[0]
            
            draw.text((x + offset, y), val, fill=val_color, font=text_font)
            
            try: return x + offset + draw.textlength(val, font=text_font)
            except AttributeError: return x + offset + text_font.getsize(val)[0]

        art_box_top = 65
        art_box_height = 160
        draw.rectangle([25, art_box_top, width-25, art_box_top + art_box_height], fill="#000000", outline="#ffffff")
        
        horse_art = ArtGenerator.generate(horse)
        art_lines = horse_art.split('\n')
        
        try: char_width = draw.textlength("M", font=art_font)
        except AttributeError: char_width = art_font.getsize("M")[0]
            
        max_chars = max([len(re.sub(r'\x1b\[[0-9;]*m', '', l.replace('\r', ''))) for l in art_lines] + [0])
        max_width = max_chars * char_width

        global_x_start = (width / 2) - (max_width / 2)

        art_y = art_box_top + 25 
        current_art_color = "#ffffff"
        
        for line in art_lines:
            line = line.replace('\r', '')
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            if clean_line.strip() == '': continue
            
            # Draw text and save the color state for the next line!
            current_art_color = self._draw_ansi_text(draw, global_x_start, art_y, line, art_font, char_width, current_art_color)
            
            # --- FONT IS 24, LINE HEIGHT IS 20 (Perfect Squish Ratio) ---
            art_y += 20 

        info_y = art_box_top + art_box_height + 15
        
        nx = draw_lbl(30, info_y, "GEN: ", f"{horse.generation} | ")
        draw_lbl(nx, info_y, "SEX: ", horse.gender.upper())
        
        coat_lines = textwrap.wrap(horse.phenotype, width=32)
        draw_lbl(30, info_y + 20, "COAT: ", coat_lines[0])
        
        coat_shift = 0
        if len(coat_lines) > 1:
            try: indent = draw.textlength("COAT: ", font=bold_font)
            except AttributeError: indent = bold_font.getsize("COAT: ")[0]
            
            for i, line in enumerate(coat_lines[1:]):
                coat_shift += 16
                draw.text((30 + indent, info_y + 20 + coat_shift), line, fill=text_color, font=text_font)
        
        nx = draw_lbl(30, info_y + 40 + coat_shift, "STYLE: ", f"{horse.running_style} | ")
        draw_lbl(nx, info_y + 40 + coat_shift, "PREF: ", horse.preferred_surface)
        nx = draw_lbl(30, info_y + 60 + coat_shift, "RECORD: ", f"{horse.wins}W - {horse.races_run-horse.wins}L | ")
        draw_lbl(nx, info_y + 60 + coat_shift, "G1 Wins: ", str(horse.championships_won))
        draw_lbl(30, info_y + 80 + coat_shift, "CAREER EARNINGS: ", f"${horse.earnings:,}")
        
        if not horse.is_retired:
            nx = draw_lbl(30, info_y + 100 + coat_shift, "AGE: ", f"{horse.age}yo | ")
            nx = draw_lbl(nx, info_y + 100 + coat_shift, "FATIGUE: ", f"{horse.fatigue:.1f}% | ")
            draw_lbl(nx, info_y + 100 + coat_shift, "MOOD: ", f"{getattr(horse, 'condition', 50.0):.1f}%")
        else:
            nx = draw_lbl(30, info_y + 100 + coat_shift, "TRUST: ", f"{horse.trust:.1f}% | ")
            draw_lbl(nx, info_y + 100 + coat_shift, "MOOD: ", f"{getattr(horse, 'condition', 50.0):.1f}%")
        
        stat_box_top = info_y + 140 + coat_shift 
        draw.rounded_rectangle([25, stat_box_top, width-25, stat_box_top + 90], radius=10, fill="#1a1a1a", outline="#ffffff")
        draw.text((width/2, stat_box_top + 20), "--- FINAL PERFORMANCE STATS ---", fill=text_color, font=header_font, anchor="mm")
        
        col1_x, col2_x, col3_x = 50, 160, 270
        stat_y = stat_box_top + 45
        
        draw.text((col1_x, stat_y), "SPEED", fill="#888888", font=small_bold)
        draw.text((col1_x, stat_y + 15), f"{horse.cur_speed:.1f}/{horse.pot_speed:.0f}", fill=text_color, font=text_font)
        draw.text((col2_x, stat_y), "STAMINA", fill="#888888", font=small_bold)
        draw.text((col2_x, stat_y + 15), f"{horse.cur_stamina:.1f}/{horse.pot_stamina:.0f}", fill=text_color, font=text_font)
        draw.text((col3_x, stat_y), "GRIT", fill="#888888", font=small_bold)
        draw.text((col3_x, stat_y + 15), f"{horse.cur_grit:.1f}/{horse.pot_grit:.0f}", fill=text_color, font=text_font)

        title_y_start = stat_box_top + 105
        draw.text((30, title_y_start), "EARNED TITLES & HONORS:", fill=text_color, font=bold_font)
        
        if not horse.titles:
            draw.text((40, title_y_start + 25), "No legendary titles earned.", fill="#888888", font=text_font)
        else:
            if len(horse.titles) <= 12: 
                t_font = text_font
                line_spacing = 18
                max_per_col = 6
            elif len(horse.titles) <= 16:
                t_font = small_font
                line_spacing = 14
                max_per_col = 8
            else: 
                try: t_font = ImageFont.truetype("arial.ttf", 9)
                except: t_font = ImageFont.load_default()
                line_spacing = 11
                max_per_col = 10

            col1_x = 40
            col2_x = 210

            for i, title in enumerate(horse.titles[:max_per_col*2]): 
                col = i // max_per_col
                row = i % max_per_col
                x = col1_x if col == 0 else col2_x
                y = title_y_start + 22 + (row * line_spacing)
                
                display_text = f"• {title}"[:25] 
                draw.text((x, y), display_text, fill=text_color, font=t_font)

        footer_top = height - 170 
        bar_height = 6 
        gap_height = 6
        
        base_colors = [c1, c2]
        segment_width_top = (width - 30) / len(base_colors)
        top_bar_bottom = footer_top - bar_height - gap_height
        top_bar_top = top_bar_bottom - bar_height
        
        for i, color in enumerate(base_colors):
            x_start = 15 + (i * segment_width_top)
            x_end = x_start + segment_width_top
            draw.rectangle([x_start, top_bar_top, x_end, top_bar_bottom], fill=color)

        accents = self.get_marking_accents(horse.phenotype)
        if not accents: accents = [c2, c1] 
        
        segment_width_bot = (width - 30) / len(accents)
        for i, color in enumerate(accents):
            x_start = 15 + (i * segment_width_bot)
            x_end = x_start + segment_width_bot
            draw.rectangle([x_start, footer_top - bar_height, x_end, footer_top], fill=color)

        draw.rounded_rectangle([15, footer_top, width-15, height-15], radius=15, fill="#000000", outline="#ffffff", corners=(False, False, True, True))
        
        star_y = footer_top + 15
        num_stars = min(horse.generation, 10) 
        if num_stars > 0:
            star_radius = 5
            star_spacing = 18
            total_star_width = (num_stars - 1) * star_spacing
            start_x = (width / 2) - (total_star_width / 2)
            
            for i in range(num_stars):
                cx = start_x + (i * star_spacing)
                self._draw_star(draw, cx, star_y, star_radius, "#ffffff")
        
        metadata = PngInfo()

        if include_code:
            draw.text((width/2, footer_top + 35), "--- OFFICIAL TRANSFER CODE ---", fill=text_color, font=header_font, anchor="mm")
            
            chunk_size = 44 
            code_chunks = [trade_code[i:i+chunk_size] for i in range(0, len(trade_code), chunk_size)]
            
            code_y = footer_top + 55
            line_height = 12
            
            if len(code_chunks) * line_height > (height - 20 - code_y):
                line_height = (height - 20 - code_y) / len(code_chunks)
                
            for chunk in code_chunks:
                draw.text((width/2, code_y), chunk, fill="#00ff00", font=code_font, anchor="mt") 
                code_y += line_height
                
            metadata.add_text("DOC_TRADE_CODE", trade_code)
        else:
            draw.text((width/2, footer_top + 60), "--- OFFICIAL STABLE COLLECTION ---", fill=text_color, font=header_font, anchor="mm")
            draw.text((width/2, footer_top + 90), "NOT VALID FOR TRADE", fill="#ff3333", font=name_font, anchor="mm")

        draw.rounded_rectangle([15, 15, width-15, height-15], radius=15, outline="#ffffff", width=1)

        if not os.path.exists("cards"):
            os.makedirs("cards")
            
        safe_name = "".join(x for x in horse.name if x.isalnum() or x in " -_").strip()
        suffix = "Trade" if include_code else "Collection"
        filepath = f"cards/{safe_name}_Gen{horse.generation}_{suffix}.png"
        
        img.save(filepath, pnginfo=metadata)
        
        return filepath, trade_code