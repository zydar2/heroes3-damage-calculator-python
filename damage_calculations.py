from heroes_enums import HeroSkillLevel, HeroSpecialization, DamageEnum, SpecialAdditives
from heroes_types import Unit, Hero, Creature
from battle_params import BattleParams
import csv

#
# https://heroes.thelazy.net/index.php/Damage
#

_ARCHERY_SKILL_MAP: dict[HeroSkillLevel, float] = {HeroSkillLevel.BASIC: 0.1, HeroSkillLevel.ADVANCED: 0.25, HeroSkillLevel.EXPERT: 0.50}

_ARCHERY_ARTIFACT_MAP: dict[SpecialAdditives, float] = {
    SpecialAdditives.ARTIFACT___BOW_OF_ELVEN_CHERRYWOOD___5_PERCENT: 0.05,
    SpecialAdditives.ARTIFACT___BOWSTRING_OF_THE_UNICORNS_MANE___10_PERCENT: 0.10,
    SpecialAdditives.ARTIFACT___ANGEL_FEATHER_ARROWS___15_PERCENT: 0.15
}

def _is_true_in_map(_key: SpecialAdditives, _map: dict[SpecialAdditives, [bool | int]]) -> bool:
    return (_key in _map) and (_map[_key] is True)

def _handle_shield(map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}) -> float:
    if _is_true_in_map(SpecialAdditives.SHIELD_SPELL, map_of_special_additives):
        return 0.15
    elif _is_true_in_map(SpecialAdditives.SHIELD_SPELL_WITH_EARTH_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL, map_of_special_additives):
        return 0.30
    else:
        return 0

def _handle_air_shield(map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}) -> float:
    if _is_true_in_map(SpecialAdditives.AIR_SHIELD_SPELL, map_of_special_additives):
        return 0.25
    elif _is_true_in_map(SpecialAdditives.AIR_SHIELD_SPELL_WITH_AIR_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL, map_of_special_additives):
        return 0.50
    else:
        return 0

def _get_sum_of_percent(map_of_special_additives: dict[SpecialAdditives, [bool | int]]) -> float:

    set_1: set = set()

    if _is_true_in_map(SpecialAdditives.ARTIFACT___BOW_OF_ELVEN_CHERRYWOOD___5_PERCENT, map_of_special_additives):
        set_1.add(SpecialAdditives.ARTIFACT___BOW_OF_ELVEN_CHERRYWOOD___5_PERCENT)

    if _is_true_in_map(SpecialAdditives.ARTIFACT___BOWSTRING_OF_THE_UNICORNS_MANE___10_PERCENT, map_of_special_additives):
        set_1.add(SpecialAdditives.ARTIFACT___BOWSTRING_OF_THE_UNICORNS_MANE___10_PERCENT)

    if _is_true_in_map(SpecialAdditives.ARTIFACT___ANGEL_FEATHER_ARROWS___15_PERCENT, map_of_special_additives):
        set_1.add(SpecialAdditives.ARTIFACT___ANGEL_FEATHER_ARROWS___15_PERCENT)

    set_2: set = _ARCHERY_ARTIFACT_MAP.keys() | set()

    common_part_set: set = set_1.intersection(set_2)
    if common_part_set:
        sum_of_percent: float = 0
        for artifact in common_part_set:
            sum_of_percent += _ARCHERY_ARTIFACT_MAP[artifact]
        return sum_of_percent
    else:
        return 0

def _calc_I1(unit_attacker: Unit, unit_defender: Unit):

    defense: int = unit_defender.defense

    if unit_attacker.creature.name == 'Behemoth':
        a = int(0.4 * defense) + 1
        defense = int(defense - a)
    elif unit_attacker.creature.name == 'Ancient Behemoth':
        a = int(0.8 * defense) + 1
        defense = int(defense - a)

    diff: int = unit_attacker.attack - defense
    if diff <= 0:
        return 0
    else:
        value = 0.05 * diff
        return value if value < 3 else 3

def _calc_I2(hero_attacker: Hero, unit_attacker: Unit, map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}) -> float:
    ranged: bool = unit_attacker.creature.ranged
    melee: bool = (not ranged) or (ranged and (_is_true_in_map(SpecialAdditives.RANGED_UNIT_AT_MELEE_ATTACK, map_of_special_additives)))
    if (hero_attacker.skill_archery_level is not None) and (not melee):
        value_base: float = _ARCHERY_SKILL_MAP[hero_attacker.skill_archery_level]
        sum_of_percent: float = _get_sum_of_percent(map_of_special_additives)
        return value_base + sum_of_percent
    elif (hero_attacker.skill_offense_level is not None) and melee:
        match hero_attacker.skill_offense_level:
            case HeroSkillLevel.BASIC: return 0.1
            case HeroSkillLevel.ADVANCED: return 0.20
            case HeroSkillLevel.EXPERT: return 0.30
    else:
        return 0

def _calc_I3(hero_attacker: Hero, I2: float) -> float:
    if (hero_attacker.spec == HeroSpecialization.ARCHERY) or (hero_attacker.spec == HeroSpecialization.OFFENSE):
        return 0.05 * hero_attacker.level * I2
    return 0

def _calc_R1(unit_attacker: Unit, unit_defender: Unit):

    defense: int = unit_defender.defense

    if unit_attacker.creature.name == 'Behemoth':
        defense = int(defense - (0.4 * defense))
    elif unit_attacker.creature.name == 'Ancient Behemoth':
        defense = int(defense - (0.8 * defense))

    diff: int = unit_attacker.attack - defense
    if diff >= 0:
        return 0
    else:
        value = 0.025 * abs(diff)
        return value if value < 0.7 else 0.7

def _calc_R2(hero_defender: Hero) -> float:
    if hero_defender.skill_armorer_level is not None:
        match hero_defender.skill_armorer_level:
            case HeroSkillLevel.BASIC: return 0.05
            case HeroSkillLevel.ADVANCED: return 0.10
            case HeroSkillLevel.EXPERT: return 0.15
    else:
        return 0

def _calc_R3(hero_defender: Hero, R2: float) -> float:
    if hero_defender.spec == HeroSpecialization.ARMORER:
        return 0.05 * hero_defender.level * R2
    return 0

def _calc_R4(unit_attacker: Unit, map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}) -> float:

    if unit_attacker.creature.ranged:
        if _is_true_in_map(SpecialAdditives.RANGED_UNIT_AT_MELEE_ATTACK, map_of_special_additives):
            return _handle_shield(map_of_special_additives)
        else:
            return _handle_air_shield(map_of_special_additives)
    else:
        return _handle_shield(map_of_special_additives)

# Range and Melee penalty
def _calc_R5(unit_attacker: Unit, map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}) -> float:
    if not unit_attacker.creature.ranged:
        return 0
    if _is_true_in_map(SpecialAdditives.SHOT_WITH_A_BROKEN_ARROW, map_of_special_additives):
        return 0.5
    elif _is_true_in_map(SpecialAdditives.RANGED_UNIT_AT_MELEE_ATTACK, map_of_special_additives):
        if unit_attacker.creature.no_melee_penalty:
            return 0
        else:
            return 0.5
    return 0

def _get_damage_base(unit: Unit, map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}):

    if _is_true_in_map(SpecialAdditives.BLESS_SPELL, map_of_special_additives):
        return unit.creature.damage_max
    elif _is_true_in_map(SpecialAdditives.BLESS_SPELL_WITH_WATER_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL, map_of_special_additives):
        return unit.creature.damage_max + 1
    elif _is_true_in_map(SpecialAdditives.CURSE_SPELL, map_of_special_additives):
        return unit.creature.damage_min
    elif _is_true_in_map(SpecialAdditives.CURSE_SPELL_WITH_FIRE_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL, map_of_special_additives):
        return unit.creature.damage_min if unit.creature.damage_min == 1 else unit.creature.damage_min - 1

def _calc_damage_base(unit: Unit, map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}) -> int:
    return _get_damage_base(unit, map_of_special_additives)

def _calc_I5_case_jousting(unit_defender: Unit, map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}):
    if map_of_special_additives[SpecialAdditives.CAVALIER_AND_CHAMPION_HEX] == -1:
        return 0
    if unit_defender.creature.name in ['Pikeman', 'Halberdier']:
        return 0
    hex_amount: int = map_of_special_additives[SpecialAdditives.CAVALIER_AND_CHAMPION_HEX]
    return 0.05 * hex_amount

def _calc_I5_case_hate(unit_attacker: Unit, unit_defender: Unit):
    attacker_name, defender_name = unit_attacker.creature.name, unit_defender.creature.name

    angels, devils = ['Angel', 'Archangel'], ['Devil', 'Arch Devil']
    titans, black_dragons = ['Giant', 'Titan'], ['Red Dragon', 'Black Dragon']
    genies, efreets = ['Genie', 'Master Genie'], ['Efreet', 'Efreet Sultan']

    case_1: bool = attacker_name in angels and defender_name in devils
    case_2: bool = attacker_name in devils and defender_name in angels
    case_3: bool = attacker_name in titans and defender_name in black_dragons
    case_4: bool = attacker_name in black_dragons and defender_name in titans
    case_5: bool = attacker_name in genies and defender_name in efreets
    case_6: bool = attacker_name in efreets and defender_name in genies

    return 0.5 if (case_1 or case_2 or case_3 or case_4 or case_5 or case_6) else 0

def _calc_I5_case_elementals(unit_attacker: Unit, unit_defender: Unit):
    attacker_name, defender_name = unit_attacker.creature.name, unit_defender.creature.name

    waters, fires = ['Water Elemental', 'Ice Elemental'], ['Fire Elemental', 'Energy Elemental']
    earths, aires = ['Earth Elemental', 'Magma Elemental'], ['Air Elemental', 'Storm Elemental']

    case_1: bool = attacker_name in waters and defender_name in fires
    case_2: bool = attacker_name in fires and defender_name in waters
    case_3: bool = attacker_name in earths and defender_name in aires
    case_4: bool = attacker_name in aires and defender_name in earths

    return 1 if (case_1 or case_2 or case_3 or case_4) else 0

def _calc_I5_dread_knight(map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}):
    return 1 if _is_true_in_map(SpecialAdditives.DEATHBLOW_OF_THE_DREAD_KNIGHT, map_of_special_additives) else 0

def _calc_I5(unit_attacker: Unit, unit_defender: Unit, map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}):
    case_1 = _calc_I5_case_jousting(unit_defender, map_of_special_additives)
    case_2 = _calc_I5_case_hate(unit_attacker, unit_defender)
    case_3 = _calc_I5_case_elementals(unit_attacker, unit_defender)
    case_4 = _calc_I5_dread_knight(map_of_special_additives)
    return case_1 + case_2 + case_3 + case_4

def _calculate_damage(unit_attacker: Unit,
                      unit_defender: Unit,
                      hero_attacker: Hero = Hero(),
                      hero_defender: Hero = Hero(),
                      map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}) -> int:

    damage_base: int = _calc_damage_base(unit_attacker, map_of_special_additives)

    I1 = _calc_I1(unit_attacker, unit_defender)
    I2 = _calc_I2(hero_attacker, unit_attacker, map_of_special_additives)
    I3 = _calc_I3(hero_attacker, I2)
    I4 = 1 if _is_true_in_map(SpecialAdditives.FORTUNE, map_of_special_additives) else 0
    I5 = _calc_I5(unit_attacker, unit_defender, map_of_special_additives)
    I_all = (1 + I1 + I2 + I3 + I4 + I5)
    R1 = _calc_R1(unit_attacker, unit_defender)
    R2 = _calc_R2(hero_defender)
    R3 = _calc_R3(hero_defender, R2)
    R4 = _calc_R4(unit_attacker, map_of_special_additives)
    R5 = _calc_R5(unit_attacker, map_of_special_additives)
    R6, R7, R8, R9 = 0, 0, 0, 0
    r1, r2and3, r4, r5, r6, r7, r8, r9 = (1 - R1), (1 - R2 - R3), (1 - R4), (1 - R5), (1 - R6), (1 - R7), (1 - R8), (1 - R9)
    damage: float = (unit_attacker.amount * damage_base) * (I_all * r1 * r2and3 * r4 * r5 * r6 * r7 * r8 * r9)
    damage_int: int = 1 if int(damage) == 0 else int(damage)
    return damage_int

def _create_hero_specialization(offense: bool, armorer: bool, archery: bool) -> HeroSpecialization | None:
    if offense:
        return HeroSpecialization.OFFENSE
    elif armorer:
        return HeroSpecialization.ARMORER
    elif archery:
        return HeroSpecialization.ARCHERY
    else:
        return None

def _load_creatures() -> dict[str, Creature]:
    creature_map: dict[str, Creature] = {}
    with open('creatures.csv', 'r') as f:
        csv_reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for row in csv_reader:
            ranged: bool = 'Ranged' in row['Special_abilities']
            no_melee_penalty: bool = 'Nomeleepenalty' in row['Special_abilities']
            creature = Creature(
                row['Unit_name'], row['Castle'],
                int(row['Attack']), int(row['Defence']),
                int(row['Minimum Damage']), int(row['Maximum Damage']),
                int(row['Health']),
                ranged, no_melee_penalty
            )
            creature_map[creature.name] = creature
    return creature_map

_creature_map: dict[str, Creature] = _load_creatures()


def raise_if_validation_error(map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {}):
    bless: bool = _is_true_in_map(SpecialAdditives.BLESS_SPELL, map_of_special_additives)
    bless_with_water: bool = _is_true_in_map(SpecialAdditives.BLESS_SPELL_WITH_WATER_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL, map_of_special_additives)
    curse: bool = _is_true_in_map(SpecialAdditives.CURSE_SPELL, map_of_special_additives)
    curse_with_fire: bool = _is_true_in_map(SpecialAdditives.CURSE_SPELL_WITH_FIRE_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL, map_of_special_additives)
    if not (bless or bless_with_water or curse or curse_with_fire):
        raise ValueError('Exactly one of these four flags must be set to true: BLESS_SPELL, BLESS_SPELL_WITH_WATER_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL, CURSE_SPELL lub CURSE_SPELL_WITH_FIRE_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL')


def calculate_damage(params: BattleParams) -> int:

    hero_attacker_specialization: HeroSpecialization = _create_hero_specialization(params.hero_attacker_specialization_offence, False, params.hero_attacker_specialization_archery)
    hero_defender_specialization: HeroSpecialization = _create_hero_specialization(False, params.hero_defender_specialization_armorer, False)

    unit_attacker: Unit = Unit(_creature_map[params.unit_attacker_name], params.unit_attacker_amount, (params.unit_attacker_attack, -1))
    unit_defender: Unit = Unit(_creature_map[params.unit_defender_name], -1, (-1, params.unit_defender_defence))

    hero_attacker: Hero = Hero(skill_armorer_level=None, skill_offense_level=params.hero_attacker_skill_offense_level, skill_archery_level=params.hero_attacker_skill_archery_level, spec=hero_attacker_specialization, level=params.hero_attacker_level)
    hero_defender: Hero = Hero(skill_armorer_level=params.hero_defender_skill_armorer_level, skill_offense_level=None, skill_archery_level=None, spec=hero_defender_specialization, level=params.hero_defender_level)

    map_of_special_additives: dict[SpecialAdditives, [bool | int]] = {
        SpecialAdditives.CAVALIER_AND_CHAMPION_HEX: params.cavalier_and_champion_hex,
        SpecialAdditives.FORTUNE: params.fortune,
        SpecialAdditives.BLESS_SPELL: params.bless_spell,
        SpecialAdditives.BLESS_SPELL_WITH_WATER_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL: params.bless_spell_with_water_magic_at_least_at_advanced_level,
        SpecialAdditives.DEATHBLOW_OF_THE_DREAD_KNIGHT: params.deathblow_of_the_dread_knight,
        SpecialAdditives.CURSE_SPELL: params.curse_spell,
        SpecialAdditives.CURSE_SPELL_WITH_FIRE_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL: params.curse_spell_with_fire_magic_at_least_at_advanced_level,
        SpecialAdditives.SHOT_WITH_A_BROKEN_ARROW: params.shot_with_a_broken_arrow,
        SpecialAdditives.RANGED_UNIT_AT_MELEE_ATTACK: params.ranged_unit_at_melee_attack,
        SpecialAdditives.ARTIFACT___BOW_OF_ELVEN_CHERRYWOOD___5_PERCENT: params.artifact___bow_of_elven_cherrywood___5_percent,
        SpecialAdditives.ARTIFACT___BOWSTRING_OF_THE_UNICORNS_MANE___10_PERCENT: params.artifact___bowstring_of_the_unicorns_mane___10_percent,
        SpecialAdditives.ARTIFACT___ANGEL_FEATHER_ARROWS___15_PERCENT: params.artifact___angel_feather_arrows___15_percent,
        SpecialAdditives.SHIELD_SPELL: params.shield_spell,
        SpecialAdditives.SHIELD_SPELL_WITH_EARTH_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL: params.shield_spell_with_earth_magic_at_least_at_advanced_level,
        SpecialAdditives.AIR_SHIELD_SPELL: params.air_shield_spell,
        SpecialAdditives.AIR_SHIELD_SPELL_WITH_AIR_MAGIC_AT_LEAST_AT_ADVANCED_LEVEL: params.air_shield_spell_with_air_magic_at_least_at_advanced_level
    }

    raise_if_validation_error(map_of_special_additives)

    damage: int = _calculate_damage(unit_attacker=unit_attacker,
                                    unit_defender=unit_defender,
                                    hero_attacker=hero_attacker,
                                    hero_defender=hero_defender,
                                    map_of_special_additives=map_of_special_additives)
    return damage

