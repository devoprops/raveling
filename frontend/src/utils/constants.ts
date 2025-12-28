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

// Elemental types
export const ELEMENT_METAL = "metal";
export const ELEMENT_WATER = "water";
export const ELEMENT_WOOD = "wood";
export const ELEMENT_FIRE = "fire";
export const ELEMENT_EARTH = "earth";
export const ELEMENTS = [ELEMENT_METAL, ELEMENT_WATER, ELEMENT_WOOD, ELEMENT_FIRE, ELEMENT_EARTH];

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

