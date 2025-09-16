from heroes_enums import HeroSkillLevel, DamageEnum

class BattleParams:
    def __init__(self, json_params: str):
        self.unit_attacker_name: str = json_params['unit_attacker_name']
        self.unit_defender_name: str = json_params['unit_defender_name']
        self.unit_attacker_amount: int = json_params['unit_attacker_amount']
        self.unit_attacker_attack: int = json_params['unit_attacker_attack']
        self.unit_defender_defence: int = json_params['unit_defender_defence']
        self.hero_attacker_skill_offense_level: HeroSkillLevel = HeroSkillLevel[json_params['hero_attacker_skill_offense_level']] if json_params['hero_attacker_skill_offense_level'] is not None else None
        self.hero_attacker_skill_archery_level: HeroSkillLevel = HeroSkillLevel[json_params['hero_attacker_skill_archery_level']] if json_params['hero_attacker_skill_archery_level'] is not None else None
        self.hero_attacker_specialization_offence: bool = json_params['hero_attacker_specialization_offence']
        self.hero_attacker_specialization_archery: bool = json_params['hero_attacker_specialization_archery']
        self.hero_attacker_level: int = json_params['hero_attacker_level']
        self.hero_defender_skill_armorer_level: HeroSkillLevel = HeroSkillLevel[json_params['hero_defender_skill_armorer_level']] if json_params['hero_defender_skill_armorer_level'] is not None else None
        self.hero_defender_specialization_armorer: bool = json_params['hero_defender_specialization_armorer']
        self.hero_defender_level: int = json_params['hero_defender_level']
        self.fortune: bool = json_params['fortune']
        self.bless_spell: bool = json_params['bless_spell']
        self.bless_spell_with_water_magic_at_least_at_advanced_level: bool = json_params['bless_spell_with_water_magic_at_least_at_advanced_level']
        self.curse_spell: bool = json_params['curse_spell']
        self.curse_spell_with_fire_magic_at_least_at_advanced_level: bool = json_params['curse_spell_with_fire_magic_at_least_at_advanced_level']
        self.shot_with_a_broken_arrow: bool = json_params['shot_with_a_broken_arrow']
        self.ranged_unit_at_melee_attack: bool = json_params['ranged_unit_at_melee_attack']
        self.artifact___bow_of_elven_cherrywood___5_percent: bool = json_params['artifact___bow_of_elven_cherrywood___5_percent']
        self.artifact___bowstring_of_the_unicorns_mane___10_percent: bool = json_params['artifact___bowstring_of_the_unicorns_mane___10_percent']
        self.artifact___angel_feather_arrows___15_percent: bool = json_params['artifact___angel_feather_arrows___15_percent']
        self.shield_spell: bool = json_params['shield_spell']
        self.shield_spell_with_earth_magic_at_least_at_advanced_level: bool = json_params['shield_spell_with_earth_magic_at_least_at_advanced_level']
        self.air_shield_spell: bool = json_params['air_shield_spell']
        self.air_shield_spell_with_air_magic_at_least_at_advanced_level: bool = json_params['air_shield_spell_with_air_magic_at_least_at_advanced_level']
        self.deathblow_of_the_dread_knight: bool = json_params['deathblow_of_the_dread_knight']
        self.cavalier_and_champion_hex: int = json_params['cavalier_and_champion_hex']

