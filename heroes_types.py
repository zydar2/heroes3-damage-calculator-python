from heroes_enums import HeroSkillLevel, HeroSpecialization

class Hero:
    def __init__(self,
                 skill_offense_level: HeroSkillLevel = None,
                 skill_armorer_level: HeroSkillLevel = None,
                 skill_archery_level: HeroSkillLevel = None,
                 spec: HeroSpecialization = None,
                 level: int = 0):
        self.level = level
        self.skill_offense_level = skill_offense_level
        self.skill_armorer_level = skill_armorer_level
        self.skill_archery_level = skill_archery_level
        self.spec = spec

class Creature:
    def __init__(self, name: str, castle: str, attack: int, defense: int, damage_min: int, damage_max: int, health: int, ranged: bool, no_melee_penalty: bool):
        self.name = name
        self.castle = castle
        self.attack = attack
        self.defense = defense
        self.damage_min = damage_min
        self.damage_max = damage_max
        self.health = health
        self.ranged = ranged
        self.no_melee_penalty = no_melee_penalty

class Unit:
    def __init__(self, creature: Creature, amount: int, attack_and_defense: tuple[int, int] = ()):
        self.creature = creature
        self.amount = amount
        if attack_and_defense:
            self.attack, self.defense = attack_and_defense
        else:
            self.attack, self.defense = creature.attack, creature.defense
