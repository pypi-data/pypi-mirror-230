class Weapon:
    def __init__(self, item_popup_element, tier) -> None:
        self.name = ""
        self.rarity = ""
        self.tier = tier
        self.type = "weapon"
        self.level_req = 0
        self.stats = []
        self.min_damage = 0
        self.max_damage = 0
        self.parse_item(item_popup_element)
    def __repr__(self) -> str:
        return f"<Weapon {self.name}>"
    def __eq__(self, obj):
        if isinstance(obj, Weapon) and all([
            self.name == obj.name,
            self.rarity == obj.rarity,
            self.tier == obj.tier,
            self.type == obj.type,
            self.level_req == obj.level_req,
            self.stats == obj.stats
        ]):
            return True
        else:
            return False
    def parse_item(self, item_popup_element) -> list:
        if isinstance(item_popup_element, str):
            item_stats = [stat.strip() for stat in item_popup_element.split('\n')]
        else:
            item_stats = [stat.strip() for stat in item_popup_element.text.split('\n')]
        self.name = item_stats[0].lower()
        rarities = ["magical","rare","mystical","angelic","mythical","arcane","legendary","godly","epic","relic","artifact","unique"]
        rarity = self.name.split()[0].lower()
        if rarity in rarities:
            self.rarity = rarity
        else:
            self.rarity = 'plain'
        for stat in item_stats[1:]:
            if "level req:" in stat.lower():
                self.level_req = int(stat.split(' ')[-1])
            if "damage:" in stat.lower():
                self.min_damage, self.max_damage = [int(num) for num in stat.split(' ') if num.isdigit()]
            if "+" in stat.lower():
                self.stats.append(stat.lower())
#-----------------------------------------------
class Armor:
    def __init__(self, item_popup_element, tier) -> None:
        self.name = ""
        self.rarity = ""
        self.tier = tier
        self.type = "armor"
        self.level_req = 0
        self.stats = []
        self.min_phys_defense = 0
        self.max_phys_defense = 0
        self.min_mag_defense = 0
        self.max_mag_defense = 0
        self.parse_item(item_popup_element)
    def __repr__(self) -> str:
        return f"<Armor {self.name}>"
    def __eq__(self, obj):
        if isinstance(obj, Armor) and all([
            self.name == obj.name,
            self.rarity == obj.rarity,
            self.tier == obj.tier,
            self.type == obj.type,
            self.level_req == obj.level_req,
            self.stats == obj.stats
        ]):
            return True
        else:
            return False
    def parse_item(self, item_popup_element) -> list:
        if isinstance(item_popup_element, str):
            item_stats = [stat.strip() for stat in item_popup_element.split('\n')]
        else:
            item_stats = [stat.strip() for stat in item_popup_element.text.split('\n')]
        self.name = item_stats[0].lower()
        rarities = ["plain","magical","rare","mystical","angelic","mythical","arcane","legendary","godly","epic","relic","artifact","unique"]
        rarity = self.name.split()[0].lower()
        if rarity in rarities:
            self.rarity = rarity
        else:
            self.rarity = 'plain'
        for stat in item_stats[1:]:
            if "level req" in stat.lower():
                self.level_req = int(stat.split(' ')[-1])
            if "physical defense" in stat.lower():
                self.min_phys_defense, self.max_phys_defense = [int(num) for num in stat.split(' ') if num.isdigit()]
            if "magic defense" in stat.lower():
                self.min_mag_defense, self.max_mag_defense = [int(num) for num in stat.split(' ') if num.isdigit()]
            if "+" in stat:
                self.stats.append(stat)
#-----------------------------------------------
class Charm:
    def __init__(self, item_popup_element, tier) -> None:
        self.name = ""
        self.rarity = ""
        self.tier = tier
        self.type = "charm"
        self.level_req = 0
        self.stats = []
        self.min_spell_effect = 0
        self.max_spell_effect = 0
        self.mana_cost = 0
        self.parse_item(item_popup_element)
    def __repr__(self) -> str:
        return f"<Charm {self.name}>"
    def __eq__(self, obj):
        if isinstance(obj, Charm) and all([
            self.name == obj.name,
            self.rarity == obj.rarity,
            self.tier == obj.tier,
            self.type == obj.type,
            self.level_req == obj.level_req,
            self.stats == obj.stats
        ]):
            return True
        else:
            return False
    def parse_item(self, item_popup_element) -> list:
        if isinstance(item_popup_element, str):
            item_stats = [stat.strip() for stat in item_popup_element.split('\n')]
        else:
            item_stats = [stat.strip() for stat in item_popup_element.text.split('\n')]
        self.name = item_stats[0].lower()
        rarities = ["magical","rare","mystical","angelic","mythical","arcane","legendary","godly","epic","relic","artifact","unique"]
        rarity = self.name.split()[0].lower()
        if rarity in rarities:
            self.rarity = rarity
        else:
            self.rarity = 'plain'
        for stat in item_stats[1:]:
            if "level req" in stat.lower():
                self.level_req = int(stat.split(' ')[-1])
            if "spell damage" in stat.lower() or "heals" in stat.lower():
                self.min_spell_effect, self.max_spell_effect = [int(num) for num in stat.split(' ') if num.isdigit()]
            if "mana cost" in stat.lower():
                self.mana_cost = int(stat.split(':')[-1].strip())
            if "+" in stat.lower():
                self.stats.append(stat.lower())
#-----------------------------------------------