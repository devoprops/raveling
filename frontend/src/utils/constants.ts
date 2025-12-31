// Constants matching backend constants
// This ensures type safety and consistency between frontend and backend

// Item types
export const ITEM_TYPE_WEAPON = "weapon";
export const ITEM_TYPE_WEARABLE = "wearable";
export const ITEM_TYPE_CONSUMABLE = "consumable";
export const ITEM_TYPES = [ITEM_TYPE_WEAPON, ITEM_TYPE_WEARABLE, ITEM_TYPE_CONSUMABLE];

// Weapon types
export const WEAPON_TYPE_MELEE = "melee";
export const WEAPON_TYPE_RANGED = "ranged";
export const WEAPON_TYPES = [WEAPON_TYPE_MELEE, WEAPON_TYPE_RANGED];

// Melee weapon subtypes
export const MELEE_BLADED = "bladed";
export const MELEE_BLUNT = "blunt";
export const MELEE_FLAILED = "flailed";
export const MELEE_SUBTYPES = [MELEE_BLADED, MELEE_BLUNT, MELEE_FLAILED];

// Ranged weapon subtypes
export const RANGED_BOW = "bow";
export const RANGED_THROWABLE = "throwable";
export const RANGED_SUBTYPES = [RANGED_BOW, RANGED_THROWABLE];

// Skill types
export const SKILL_TYPE_ATTACK = "attack";
export const SKILL_TYPE_BUFF = "buff";
export const SKILL_TYPE_DEBUFF = "debuff";
export const SKILL_TYPE_REGENERATIVE = "regenerative";
export const SKILL_TYPE_PROCESS = "process";
export const SKILL_TYPES = [
  SKILL_TYPE_ATTACK,
  SKILL_TYPE_BUFF,
  SKILL_TYPE_DEBUFF,
  SKILL_TYPE_REGENERATIVE,
  SKILL_TYPE_PROCESS,
];

// Attack skill subtypes
export const ATTACK_PHYSICAL = "physical";
export const ATTACK_ELEMENTAL = "elemental";
export const ATTACK_SUBTYPES = [ATTACK_PHYSICAL, ATTACK_ELEMENTAL];

// Character types
export const CHARACTER_TYPE_PC = "PC";
export const CHARACTER_TYPE_NPC = "NPC";
export const CHARACTER_TYPES = [CHARACTER_TYPE_PC, CHARACTER_TYPE_NPC];

// Equipment slots (slot-based approach - generic)
export const SLOT_HEAD = "head";
export const SLOT_CHEST = "chest";
export const SLOT_LEGS = "legs";
export const SLOT_FEET = "feet";
export const SLOT_HANDS = "hands";
export const SLOT_RING = "ring";
export const SLOT_AMULET = "amulet";
export const EQUIPMENT_SLOTS = [
  SLOT_HEAD,
  SLOT_CHEST,
  SLOT_LEGS,
  SLOT_FEET,
  SLOT_HANDS,
  SLOT_RING,
  SLOT_AMULET,
];

// Elemental types - centralized definition
export const ELEMENT_EARTH = "Earth";
export const ELEMENT_WATER = "Water";
export const ELEMENT_AIR = "Air";
export const ELEMENT_FIRE = "Fire";
export const ELEMENT_LIGHTNING = "Lightning";
export const ELEMENT_ICE = "Ice";
export const ELEMENT_POISON = "Poison";
export const ELEMENT_SONIC = "Sonic";
export const ELEMENT_PSYCHIC = "Psychic";

// All elements in a single array
export const ELEMENTS = [
  ELEMENT_EARTH,
  ELEMENT_WATER,
  ELEMENT_AIR,
  ELEMENT_FIRE,
  ELEMENT_LIGHTNING,
  ELEMENT_ICE,
  ELEMENT_POISON,
  ELEMENT_SONIC,
  ELEMENT_PSYCHIC,
];

// Element display names (for UI)
export const ELEMENT_DISPLAY_NAMES: Record<string, string> = {
  [ELEMENT_EARTH]: "Earth",
  [ELEMENT_WATER]: "Water",
  [ELEMENT_AIR]: "Air",
  [ELEMENT_FIRE]: "Fire",
  [ELEMENT_LIGHTNING]: "Lightning",
  [ELEMENT_ICE]: "Ice",
  [ELEMENT_POISON]: "Poison",
  [ELEMENT_SONIC]: "Sonic",
  [ELEMENT_PSYCHIC]: "Psychic",
};

// Helper function to create default elemental affinities (all set to 1.0)
export function createDefaultElementAffinities(): Record<string, number> {
  const affinities: Record<string, number> = {};
  ELEMENTS.forEach(element => {
    affinities[element] = 1.0;
  });
  return affinities;
}

// Helper function to create default elemental detriments (all set to 1.0)
export function createDefaultElementDetriments(): Record<string, number> {
  const detriments: Record<string, number> = {};
  ELEMENTS.forEach(element => {
    detriments[element] = 1.0;
  });
  return detriments;
}

// Helper function to create default affinities object (elemental + race)
export function createDefaultAffinities() {
  return {
    elemental: createDefaultElementAffinities(),
    race: {} as Record<string, number>,
  };
}

// Helper function to create default detriments object (elemental + race)
export function createDefaultDetriments() {
  return {
    elemental: createDefaultElementDetriments(),
    race: {} as Record<string, number>,
  };
}

// Designer navigation structure
export interface DesignerNavItem {
  id: string;
  label: string;
  path: string;
  icon?: string;
  subgroups?: DesignerNavItem[];
}

export const DESIGNER_NAVIGATION: DesignerNavItem[] = [
  {
    id: "skills",
    label: "Skills",
    path: "/designer/skills",
    icon: "⚔️",
    subgroups: [
      { id: "attack-physical", label: "Physical Attack", path: "/designer/skills/attack/physical" },
      { id: "attack-elemental", label: "Elemental Attack", path: "/designer/skills/attack/elemental" },
      { id: "buff", label: "Buff", path: "/designer/skills/buff" },
      { id: "debuff", label: "Debuff", path: "/designer/skills/debuff" },
      { id: "regenerative", label: "Regenerative", path: "/designer/skills/regenerative" },
      { id: "process", label: "Process", path: "/designer/skills/process" },
    ],
  },
  {
    id: "spells",
    label: "Spells",
    path: "/designer/spells",
    icon: "✨",
    subgroups: [
      { id: "spell-attack-physical", label: "Physical Attack", path: "/designer/spells/attack/physical" },
      { id: "spell-attack-elemental", label: "Elemental Attack", path: "/designer/spells/attack/elemental" },
      { id: "spell-buff", label: "Buff", path: "/designer/spells/buff" },
      { id: "spell-debuff", label: "Debuff", path: "/designer/spells/debuff" },
    ],
  },
  {
    id: "effect-styles",
    label: "Effect Styles",
    path: "/designer/effect-styles",
    icon: "🎨",
  },
  {
    id: "zones",
    label: "Zones",
    path: "/designer/zones",
    icon: "🗺️",
  },
  {
    id: "characters",
    label: "Characters",
    path: "/designer/characters",
    icon: "👤",
    subgroups: [
      { id: "pc", label: "PC", path: "/designer/characters/PC" },
      { id: "npc", label: "NPC", path: "/designer/characters/NPC" },
      { id: "other", label: "Other", path: "/designer/characters/other" },
    ],
  },
  {
    id: "wearables",
    label: "Wearables",
    path: "/designer/wearables",
    icon: "🛡️",
    subgroups: [
      { id: "head", label: "Head", path: "/designer/wearables/head" },
      { id: "chest", label: "Chest", path: "/designer/wearables/chest" },
      { id: "legs", label: "Legs", path: "/designer/wearables/legs" },
      { id: "feet", label: "Feet", path: "/designer/wearables/feet" },
      { id: "hands", label: "Hands", path: "/designer/wearables/hands" },
      { id: "ring", label: "Ring", path: "/designer/wearables/ring" },
      { id: "amulet", label: "Amulet", path: "/designer/wearables/amulet" },
    ],
  },
  {
    id: "weapons",
    label: "Weapons",
    path: "/designer/weapons",
    icon: "⚔️",
    subgroups: [
      { id: "melee-bladed", label: "Bladed", path: "/designer/weapons/melee/bladed" },
      { id: "melee-blunt", label: "Blunt", path: "/designer/weapons/melee/blunt" },
      { id: "melee-flailed", label: "Flailed", path: "/designer/weapons/melee/flailed" },
      { id: "ranged-bow", label: "Bow", path: "/designer/weapons/ranged/bow" },
      { id: "ranged-throwable", label: "Throwable", path: "/designer/weapons/ranged/throwable" },
    ],
  },
  {
    id: "consumables",
    label: "Consumables",
    path: "/designer/consumables",
    icon: "🧪",
  },
];

