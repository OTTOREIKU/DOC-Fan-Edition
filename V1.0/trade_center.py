import os
from PIL import Image
from menus import clear_screen
from card_generator import CardGenerator
from art_generator import ArtGenerator

class TradeCenter:
    def __init__(self, stable_mgr):
        self.stable_mgr = stable_mgr
        self.card_gen = CardGenerator()

    def enter(self, capacity, current_active_param): # the passed parameter is now ignored and recalculated
        while True:
            clear_screen()
            print("\n" + "🌐"*32)
            print("THE TRADING HUB (MULTIPLAYER)".center(64))
            print("🌐"*32 + "\n")
            
            print("Welcome to the Syndicate Trading Hub.")
            print("Here you can generate Digital Trading Cards for your horses")
            print("to share with other players, or import a friend's")
            print("legendary horse into your own breeding program!\n")
            
            print(" [1] Generate Collection Card (Keep Horse in Stable)")
            print(" [2] Generate Trading Card (Remove Horse from Stable)")
            print(" [3] Import Horse (Scan Card or Paste Code)")
            print("-" * 64)
            print(" [Q] Back to Main Menu")
            
            c = input("\nSelect option: ").upper()
            
            if c == 'Q': break
            elif c == '1':
                self._export_horse(is_trade=False)
            elif c == '2':
                self._export_horse(is_trade=True)
            elif c == '3':
                self._import_horse(capacity)

    def _export_horse(self, is_trade):
        while True:
            clear_screen()
            saved_horses = self.stable_mgr.get_saved_horses()
            
            if is_trade:
                tradable = [h for h in saved_horses if not getattr(h, 'is_npc', False) and not getattr(h, 'is_in_academy', False)]
                title_text = "EXPORT TRADING CARD"
                icon = "📤"
            else:
                tradable = [h for h in saved_horses if not getattr(h, 'is_npc', False)]
                title_text = "GENERATE COLLECTION CARD"
                icon = "🎴"
            
            print("\n" + icon*32)
            print(title_text.center(64))
            print(icon*32)
            
            if not tradable:
                print("\nYou have no eligible horses.")
                input("\nPress Enter to return...")
                return
                
            print("\nSelect a horse to generate a physical Card for:")
            for i, h in enumerate(tradable):
                status_str = "[Farm]" if h.is_retired else f"[Active - {h.age}yo]"
                title_str = f" | {len(h.titles)} Titles" if h.titles else ""
                print(f" [{i+1}] {h.name} {status_str} (Gen {h.generation}){title_str}")
                
            print("-" * 64)
            
            if not is_trade:
                print(" [A] Generate All (Collection Only)")
            print(" [Q] Cancel")
            
            sel = input("\nSelect option: ").upper()
            if sel == 'Q' or sel == 'C': return
            
            if not is_trade and sel == 'A':
                print("\n⚙️ Generating collection cards for ALL eligible horses. Please wait...")
                for h in tradable:
                    self.card_gen.generate_card(h, include_code=False)
                print("\n" + "="*64)
                print(f"✅ {len(tradable)} COLLECTION CARDS GENERATED!".center(64))
                print("="*64)
                print("\n 📸 Check the 'cards' folder in your game directory.")
                input("\nPress Enter to return...")
                return
            
            if sel.isdigit() and 1 <= int(sel) <= len(tradable):
                horse = tradable[int(sel)-1]
                
                if is_trade:
                    print(f"\n⚠️ WARNING: Generating a Trade Card for {horse.name} will PERMANENTLY remove them from your game!")
                    confirm = input("Are you sure you want to trade them away? (Y/N): ").upper()
                    if confirm != 'Y': continue
                    
                    print("\n⚙️ Generating physical card and injecting secret DNA metadata...")
                    filepath, small_code = self.card_gen.generate_card(horse, include_code=True)
                    
                    self.stable_mgr.delete_horse(horse.id)
                    
                    print("\n" + "="*64)
                    print("✅ TRADE CARD GENERATED SUCCESSFULLY!".center(64))
                    print("="*64)
                    print(f"\n 📸 A digital Trading Card has been saved to your game folder at:")
                    print(f"    -> {filepath}")
                    print("\n You can send this image file directly to a friend!")
                    print(" They can drop it in their 'cards' folder to scan it.")
                    print("\n Alternatively, they can manually type in this code:")
                    print("\n" + "-"*64)
                    print(small_code)
                    print("-" * 64 + "\n")
                    input("Press Enter to return...")
                    return
                else:
                    print("\n⚙️ Generating digital collection card...")
                    filepath, _ = self.card_gen.generate_card(horse, include_code=False)
                    
                    print("\n" + "="*64)
                    print("✅ COLLECTION CARD GENERATED!".center(64))
                    print("="*64)
                    print(f"\n 📸 A digital Collection Card has been saved to your game folder at:")
                    print(f"    -> {filepath}")
                    print("\n Your horse remains safely in your stable.")
                    input("\nPress Enter to return...")
                    return

    def _import_horse(self, capacity):
        clear_screen()
        print("\n" + "📥"*32)
        print("IMPORT FRIEND'S HORSE".center(64))
        print("📥"*32)
        
        # --- DYNAMIC CAPACITY CALCULATION FIX ---
        # Recalculates exact slots the second you open the import menu!
        saved_horses = self.stable_mgr.get_saved_horses()
        current_active = len([h for h in saved_horses if not h.is_retired and not getattr(h, 'is_npc', False)])
        
        print(f"\n[Active Stable: {current_active}/{capacity} Stalls Filled]")
        print(" [1] Paste Text Code Manually")
        print(" [2] Scan Trading Card Image (.png from cards folder)")
        print("-" * 64)
        print(" [Q] Cancel")
        
        c = input("\nSelect import method: ").upper()
        if c == 'Q' or c == 'C': return
        
        code_str = None
        
        if c == '1':
            code_str = input("\nTrade Code: ").strip()
            if not code_str or code_str.upper() == 'Q': return
            
        elif c == '2':
            if not os.path.exists("cards"):
                print("\n❌ The 'cards' folder does not exist! Generate a card or create the folder first.")
                input("Press Enter to continue...")
                return
                
            png_files = [f for f in os.listdir("cards") if f.endswith(".png")]
            if not png_files:
                print("\n❌ No .png files found in the 'cards' folder!")
                input("Press Enter to continue...")
                return
                
            print("\nAvailable Cards to Scan:")
            for i, f in enumerate(png_files):
                print(f" [{i+1}] {f}")
                
            sel = input("\nSelect card to scan (or Q to cancel): ").upper()
            if sel == 'Q' or sel == 'C': return
            
            if sel.isdigit() and 1 <= int(sel) <= len(png_files):
                target_file = os.path.join("cards", png_files[int(sel)-1])
                try:
                    with Image.open(target_file) as img:
                        code_str = img.info.get("DOC_TRADE_CODE")
                        
                    if not code_str:
                        print("\n❌ Error: No hidden Trade Code found in this image's metadata.")
                        print("Are you sure this is a Trading Card and not a Collection Card?")
                        input("Press Enter to continue...")
                        return
                except Exception as e:
                    print(f"\n❌ Error reading image: {e}")
                    input("Press Enter to continue...")
                    return
            else:
                return
        else:
            return
        
        imported_horse = self.card_gen.decompress_horse(code_str)
        
        if not imported_horse:
            print("\n❌ Error: Invalid or corrupted Trade Code data.")
            input("Press Enter to continue...")
            return
            
        player_max_gen = self.stable_mgr.get_highest_generation()
        if imported_horse.generation > player_max_gen:
            print(f"\n❌ TRADE BLOCKED: Generation {imported_horse.generation} is locked for you.")
            print(f"You must breed at least one Gen {imported_horse.generation} horse in your own stable first!")
            input("\nPress Enter to continue...")
            return

        existing_horse = self.stable_mgr.get_horse_by_id(imported_horse.id)
        if existing_horse:
            print(f"\n❌ Security Alert: Duplicate DNA Detected!")
            print(f"The genetic ID of this card perfectly matches '{existing_horse.name}', which is currently in your stable.")
            print("You cannot import two of the exact same horse!")
            input("\nPress Enter to continue...")
            return
            
        if not imported_horse.is_retired and current_active >= capacity:
            print("\n❌ Your Active Stable is full! You must make room before importing an unretired horse.")
            input("Press Enter to continue...")
            return
            
        print("\n" + "="*64)
        print("🐴 INCOMING TRANSFER DETECTED 🐴".center(64))
        print("="*64)
        print(ArtGenerator.generate(imported_horse))
        print(f" Name   : {imported_horse.name} (Gen {imported_horse.generation})")
        print(f" Status : {'Retired (Farm / Breeding Stock)' if imported_horse.is_retired else f'Active Racer (Age {imported_horse.age})'}")
        print(f" Coat   : \033[93m{imported_horse.phenotype}\033[0m")
        print(f" Stats  : Spd {imported_horse.cur_speed:.1f} | Sta {imported_horse.cur_stamina:.1f} | Grt {imported_horse.cur_grit:.1f}")
        print(f" Record : {imported_horse.wins}-{imported_horse.races_run - imported_horse.wins} | G1s: {imported_horse.championships_won}")
        
        dest = "The Farm" if imported_horse.is_retired else "your Active Stable"
        confirm = input(f"\nAccept this transfer into {dest}? (Y/N): ").upper()
        if confirm == 'Y':
            self.stable_mgr.save_horse(imported_horse)
            print(f"\n🎉 Welcome to your new home, {imported_horse.name}!")
            input("Press Enter to continue...")