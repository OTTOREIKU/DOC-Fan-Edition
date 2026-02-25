import random

class CoatGenetics:
    def __init__(self):
        self.mutations = ["Shadow", "Ghost", "Metallic", "Snowburst", "Bloody", "Inferno", "Abyss", "Celestial"]

    def generate_gen0_genotype(self):
        def roll(alleles, weights): 
            return [random.choices(alleles, weights)[0], random.choices(alleles, weights)[0]]
        
        return {
            "E": roll(['E', 'e'], [0.5, 0.5]),
            "A": roll(['A', 'a'], [0.5, 0.5]),
            "G": roll(['G', 'g'], [0.1, 0.9]),     # NEW: Grey Gene
            "Cr": roll(['Cr', 'n'], [0.1, 0.9]),
            "D": roll(['D', 'n'], [0.1, 0.9]),
            "Ch": roll(['Ch', 'n'], [0.05, 0.95]),
            "Z": roll(['Z', 'n'], [0.05, 0.95]),
            "Rn": roll(['Rn', 'n'], [0.1, 0.9]),
            "To": roll(['To', 'n'], [0.1, 0.9]),
            "O": roll(['O', 'n'], [0.1, 0.9]),
            "Lp": roll(['Lp', 'n'], [0.05, 0.95]),
            "Br": roll(['Br', 'n'], [0.05, 0.95]), 
            "Spl": roll(['Spl', 'n'], [0.05, 0.95]), # NEW: Splash Pattern
            "Sb": roll(['Sb', 'n'], [0.05, 0.95]),   # NEW: Sabino Pattern
            "Rb": roll(['Rb', 'n'], [0.05, 0.95]),   # NEW: Rabicano Pattern
            "F": roll(['Star', 'Blaze', 'n'], [0.2, 0.1, 0.7]),
            "L": roll(['Sock', 'Stocking', 'n'], [0.2, 0.1, 0.7]),
            "Mut": ['n', 'n'] 
        }

    def breed_genotypes(self, sire, dam):
        dna = {}
        for key in sire.keys():
            sire_gene = sire.get(key, ['n', 'n'])
            dam_gene = dam.get(key, ['n', 'n'])
            dna[key] = [random.choice(sire_gene), random.choice(dam_gene)]
            
        # Safe-loads for the new genes in case you breed old horses!
        for new_gene in ["G", "Spl", "Sb", "Rb"]:
            if new_gene not in dna:
                dna[new_gene] = [random.choice(sire.get(new_gene, ['n', 'n'])), random.choice(dam.get(new_gene, ['n', 'n']))]
            
        return dna

    def get_phenotype(self, dna):
        mut1, mut2 = dna.get("Mut", ['n', 'n'])
        if mut1 != 'n' and mut2 != 'n':
            return mut1 

        e_gene = 'E' in dna.get('E', ['e', 'e'])
        a_gene = 'A' in dna.get('A', ['a', 'a'])
        
        if e_gene and a_gene: base = "Bay"
        elif e_gene and not a_gene: base = "Black"
        else: base = random.choice(["Chestnut", "Sorrel"]) 

        # NEW: The Grey modifier overrides the visual base coat
        g_gene = 'G' in dna.get('G', ['g', 'g'])
        if g_gene:
            base = random.choice(["Grey", "Dapple Grey", "Fleabitten Grey"])

        cr_count = dna.get('Cr', ['n', 'n']).count('Cr')
        if cr_count == 1 and not g_gene:
            if base in ["Chestnut", "Sorrel"]: base = "Palomino"
            elif base == "Bay": base = "Buckskin"
            elif base == "Black": base = "Smoky Black"
        elif cr_count == 2 and not g_gene:
            if base in ["Chestnut", "Sorrel"]: base = "Cremello"
            elif base == "Bay": base = "Perlino"
            elif base == "Black": base = "Smoky Cream"

        d_gene = 'D' in dna.get('D', ['n', 'n'])
        if d_gene and not g_gene:
            if base in ["Chestnut", "Sorrel"]: base = "Red Dun"
            elif base == "Bay": base = "Bay Dun"
            elif base == "Black": base = "Grullo"
            else: base = f"{base} Dun"

        ch_gene = 'Ch' in dna.get('Ch', ['n', 'n'])
        if ch_gene and not g_gene: base = f"Champagne {base}" if base not in ["Chestnut", "Sorrel", "Bay", "Black"] else "Champagne"

        z_gene = 'Z' in dna.get('Z', ['n', 'n'])
        if z_gene and 'E' in dna.get('E', ['e', 'e']) and not g_gene: 
            if base == "Black": base = "Silver Dapple"
            else: base = f"Silver {base}"

        rn_gene = 'Rn' in dna.get('Rn', ['n', 'n'])
        if rn_gene and not g_gene:
            if base in ["Chestnut", "Sorrel"]: base = "Strawberry Roan"
            elif base == "Black": base = "Blue Roan"
            elif base == "Bay": base = "Bay Roan"
            else: base = f"{base} Roan"
            
        if not cr_count and not d_gene and not ch_gene and not g_gene and random.random() < 0.05:
            base = "Dapple Grey"

        patterns = []
        if 'To' in dna.get('To', ['n', 'n']): patterns.append("Tobiano")
        if 'O' in dna.get('O', ['n', 'n']): patterns.append("Overo")
        if 'Lp' in dna.get('Lp', ['n', 'n']): patterns.append("Appaloosa")
        if 'Br' in dna.get('Br', ['n', 'n']): patterns.append("Brindle") 
        if 'Spl' in dna.get('Spl', ['n', 'n']): patterns.append("Splash") # NEW
        if 'Sb' in dna.get('Sb', ['n', 'n']): patterns.append("Sabino")   # NEW
        if 'Rb' in dna.get('Rb', ['n', 'n']): patterns.append("Rabicano") # NEW

        if patterns:
            base = f"{base} {'-'.join(patterns)}"

        f_mark = dna.get('F', ['n', 'n'])[0] if dna.get('F', ['n', 'n'])[0] != 'n' else (dna.get('F', ['n', 'n'])[1] if dna.get('F', ['n', 'n'])[1] != 'n' else None)
        l_mark = dna.get('L', ['n', 'n'])[0] if dna.get('L', ['n', 'n'])[0] != 'n' else (dna.get('L', ['n', 'n'])[1] if dna.get('L', ['n', 'n'])[1] != 'n' else None)
        
        markings = []
        if f_mark: markings.append(f"a {f_mark}")
        if l_mark: markings.append(f"White {l_mark}s")
        
        if markings:
            base = f"{base} with {' and '.join(markings)}"
            
        return base
    
    def cross_dna(self, sire_dna, dam_dna):
        import random
        foal_dna = {}
        
        # Loop through every genetic trait (Extension, Agouti, Roan, etc.)
        for gene in sire_dna.keys():
            # The foal gets exactly ONE random allele from the dad, and ONE from the mom!
            sire_allele = random.choice(sire_dna.get(gene, ['n', 'n']))
            dam_allele = random.choice(dam_dna.get(gene, ['n', 'n']))
            
            # Combine them for the baby! (Sorting puts Capital/Dominant letters first nicely)
            foal_dna[gene] = sorted([sire_allele, dam_allele])
            
        return foal_dna