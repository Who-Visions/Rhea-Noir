"""
Rhea Noir Expression System - Emoji Knowledge Base
Prioritizes BIPOC skin tones (🏾/🏿) for person/hand emojis.
Rhea is Black, 23 years old (born 2002).
"""

from typing import Dict, List
import random

# Skin tone modifiers (Fitzpatrick scale)
SKIN_TONES = {
    "light": "\U0001F3FB",        # 🏻 Type 1-2
    "medium_light": "\U0001F3FC", # 🏼 Type 3
    "medium": "\U0001F3FD",       # 🏽 Type 4
    "medium_dark": "\U0001F3FE",  # 🏾 Type 5
    "dark": "\U0001F3FF",         # 🏿 Type 6
}

# Rhea's preferred skin tones (she's Black)
RHEA_SKIN_TONES = [SKIN_TONES["dark"], SKIN_TONES["medium_dark"]]
RHEA_DEFAULT_TONE = SKIN_TONES["dark"]  # 🏿


class RheaExpressions:
    """
    Emoji expression system for Rhea Noir.
    Provides contextual emoji selection with BIPOC-prioritized skin tones.
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # FACE EMOJIS - Emotions and expressions
    # ═══════════════════════════════════════════════════════════════════════════

    FACES = {
        # Positive emotions
        "happy": ["😊", "😄", "😃", "🙂", "☺️"],
        "joy": ["😂", "🤣", "😹"],
        "love": ["😍", "🥰", "😘", "💕"],
        "excited": ["🤩", "✨", "🎉", "💫"],
        "proud": ["😌", "💅🏿", "👑"],
        "playful": ["😏", "😜", "😉", "🙃"],
        "relieved": ["😮‍💨", "😌", "🙏🏿"],

        # Neutral/thinking
        "thinking": ["🤔", "💭", "🧐", "💡"],
        "curious": ["👀", "🔍", "❓"],
        "neutral": ["😐", "😑", "🫤"],
        "contemplative": ["🤔", "🧠", "💭"],

        # Negative emotions (for empathy)
        "sad": ["😢", "😔", "🥺", "💔"],
        "frustrated": ["😤", "😠", "💢"],
        "tired": ["😴", "🥱", "😩"],
        "worried": ["😟", "😰", "🫠"],
        "shocked": ["😱", "😲", "🤯"],
        "confused": ["😕", "🤷🏿‍♀️", "❓"],

        # Special expressions
        "cool": ["😎", "🔥", "💯"],
        "sassy": ["💅🏿", "😏", "✨"],
        "mysterious": ["🌙", "✨", "🔮"],
        "supportive": ["🫂", "💪🏿", "🤝🏿"],
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # HAND EMOJIS - With BIPOC skin tones applied
    # ═══════════════════════════════════════════════════════════════════════════

    HANDS = {
        # Gestures with dark skin tone 🏿
        "wave": "👋🏿",
        "raised_hand": "✋🏿",
        "ok": "👌🏿",
        "thumbs_up": "👍🏿",
        "thumbs_down": "👎🏿",
        "fist": "✊🏿",
        "raised_fist": "✊🏿",
        "punch": "👊🏿",
        "peace": "✌🏿",
        "crossed_fingers": "🤞🏿",
        "love_you": "🤟🏿",
        "rock_on": "🤘🏿",
        "call_me": "🤙🏿",
        "point_left": "👈🏿",
        "point_right": "👉🏿",
        "point_up": "👆🏿",
        "point_down": "👇🏿",
        "index_up": "☝🏿",
        "point_at_viewer": "🫵🏿",
        "clap": "👏🏿",
        "raised_hands": "🙌🏿",
        "open_hands": "👐🏿",
        "palms_up": "🤲🏿",
        "handshake": "🤝🏿",
        "pray": "🙏🏿",
        "writing": "✍🏿",
        "nail_polish": "💅🏿",
        "selfie": "🤳🏿",
        "muscle": "💪🏿",
        "pinched_fingers": "🤌🏿",
        "pinching": "🤏🏿",
        "heart_hands": "🫶🏿",
        "palm_down": "🫳🏿",
        "palm_up": "🫴🏿",
        "index_thumb_crossed": "🫰🏿",
        "salute": "🫡",  # No skin tone for this one
        "shush": "🤫",
        "thinking_hand": "🤔",
        "hug": "🤗",
        "face_with_hand": "🤭",
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # PERSON EMOJIS - With BIPOC skin tones
    # ═══════════════════════════════════════════════════════════════════════════

    PEOPLE = {
        # Woman variants (Rhea presents feminine)
        "woman": "👩🏿",
        "woman_curly": "👩🏿‍🦱",
        "woman_tech": "👩🏿‍💻",
        "woman_scientist": "👩🏿‍🔬",
        "woman_artist": "👩🏿‍🎨",
        "woman_teacher": "👩🏿‍🏫",
        "woman_office": "👩🏿‍💼",
        "woman_student": "👩🏿‍🎓",
        "queen": "👸🏿",
        "princess": "👸🏿",
        "crown_person": "🫅🏿",
        "mage": "🧙🏿‍♀️",
        "fairy": "🧚🏿‍♀️",
        "superhero": "🦸🏿‍♀️",
        "woman_dancing": "💃🏿",
        "woman_walking": "🚶🏿‍♀️",
        "woman_running": "🏃🏿‍♀️",
        "woman_standing": "🧍🏿‍♀️",
        "woman_kneeling": "🧎🏿‍♀️",
        "woman_lotus": "🧘🏿‍♀️",

        # Gesturing
        "shrug": "🤷🏿‍♀️",
        "facepalm": "🤦🏿‍♀️",
        "tipping_hand": "💁🏿‍♀️",
        "raising_hand": "🙋🏿‍♀️",
        "bow": "🙇🏿‍♀️",
        "no_gesture": "🙅🏿‍♀️",
        "ok_gesture": "🙆🏿‍♀️",

        # Gender-neutral options
        "person": "🧑🏿",
        "person_tech": "🧑🏿‍💻",
        "person_shrug": "🤷🏿",
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # HEARTS - Full color range
    # ═══════════════════════════════════════════════════════════════════════════

    HEARTS = {
        "red": "❤️",
        "orange": "🧡",
        "yellow": "💛",
        "green": "💚",
        "blue": "💙",
        "light_blue": "🩵",
        "purple": "💜",
        "pink": "🩷",
        "brown": "🤎",
        "black": "🖤",
        "white": "🤍",
        "grey": "🩶",
        "sparkling": "💖",
        "growing": "💗",
        "beating": "💓",
        "two_hearts": "💕",
        "revolving": "💞",
        "heart_arrow": "💘",
        "heart_ribbon": "💝",
        "broken": "💔",
        "heart_fire": "❤️‍🔥",
        "mending": "❤️‍🩹",
        "heart_exclamation": "❣️",
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # SYMBOLS & DECORATIVE
    # ═══════════════════════════════════════════════════════════════════════════

    SYMBOLS = {
        "sparkles": "✨",
        "star": "⭐",
        "glowing_star": "🌟",
        "shooting_star": "🌠",
        "moon": "🌙",
        "crescent_moon": "🌙",
        "full_moon": "🌕",
        "sun": "☀️",
        "fire": "🔥",
        "rainbow": "🌈",
        "crystal_ball": "🔮",
        "gem": "💎",
        "crown": "👑",
        "magic_wand": "🪄",
        "hundred": "💯",
        "check": "✅",
        "cross": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "question": "❓",
        "exclamation": "❗",
        "thought": "💭",
        "speech": "💬",
        "zzz": "💤",
        "sweat_drops": "💦",
        "dash": "💨",
        "collision": "💥",
        "dizzy": "💫",
        "hole": "🕳️",
        "eyes": "👀",
        "brain": "🧠",
        "light_bulb": "💡",
        "books": "📚",
        "laptop": "💻",
        "gear": "⚙️",
        "link": "🔗",
        "lock": "🔒",
        "key": "🔑",
        "magnifying_glass": "🔍",
        "telescope": "🔭",
        "microscope": "🔬",
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # NATURE & OBJECTS
    # ═══════════════════════════════════════════════════════════════════════════

    NATURE = {
        "rose": "🌹",
        "hibiscus": "🌺",
        "cherry_blossom": "🌸",
        "lotus": "🪷",
        "sunflower": "🌻",
        "tulip": "🌷",
        "seedling": "🌱",
        "herb": "🌿",
        "four_leaf_clover": "🍀",
        "maple_leaf": "🍁",
        "fallen_leaf": "🍂",
        "mushroom": "🍄",
        "butterfly": "🦋",
        "bee": "🐝",
        "ladybug": "🐞",
        "cat": "🐱",
        "black_cat": "🐈‍⬛",
        "dove": "🕊️",
        "phoenix": "🐦‍🔥",
        "dragon": "🐉",
        "unicorn": "🦄",
    }

    OBJECTS = {
        "coffee": "☕",
        "tea": "🍵",
        "wine": "🍷",
        "cocktail": "🍸",
        "cake": "🎂",
        "cookie": "🍪",
        "candy": "🍬",
        "gift": "🎁",
        "balloon": "🎈",
        "party": "🎉",
        "confetti": "🎊",
        "ribbon": "🎀",
        "trophy": "🏆",
        "medal": "🏅",
        "microphone": "🎤",
        "headphones": "🎧",
        "art": "🎨",
        "camera": "📷",
        "movie": "🎬",
        "music": "🎵",
        "notes": "🎶",
        "pencil": "✏️",
        "memo": "📝",
        "folder": "📁",
        "calendar": "📅",
        "chart_up": "📈",
        "chart_down": "📉",
        "clipboard": "📋",
        "pushpin": "📌",
        "paperclip": "📎",
        "scissors": "✂️",
        "package": "📦",
        "mailbox": "📫",
        "bell": "🔔",
        "hourglass": "⏳",
        "watch": "⌚",
        "alarm": "⏰",
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # RHEA'S SIGNATURE EMOJIS (Brand identity)
    # ═══════════════════════════════════════════════════════════════════════════

    SIGNATURE = {
        "primary": "🌙",      # Moon - her main symbol
        "secondary": "✨",    # Sparkles - elegance
        "tertiary": "💜",     # Purple heart - brand color
        "nail_polish": "💅🏿", # Sassy confidence
        "crown": "👑",        # Excellence
        "gem": "💎",          # Premium quality
        "brain": "🧠",        # Intelligence
        "magic": "🔮",        # Mystery
        "fire": "🔥",         # Passion
        "rose": "🌹",         # Beauty
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # REACTION MAPPINGS - Context-based emoji selection
    # ═══════════════════════════════════════════════════════════════════════════

    REACTIONS = {
        # Greetings
        "greeting": ["👋🏿", "✨", "🌙"],
        "farewell": ["👋🏿", "🌙", "💜", "✨"],

        # Affirmation
        "yes": ["✅", "👍🏿", "💯"],
        "no": ["❌", "👎🏿", "🙅🏿‍♀️"],
        "maybe": ["🤔", "🤷🏿‍♀️", "💭"],

        # Acknowledgment
        "understanding": ["👍🏿", "💡", "✨"],
        "agreement": ["💯", "✅", "👏🏿"],
        "appreciation": ["🙏🏿", "💜", "✨"],

        # Encouragement
        "encouragement": ["💪🏿", "✨", "🔥", "👑"],
        "celebration": ["🎉", "✨", "👏🏿", "🥳"],
        "praise": ["👏🏿", "✨", "💯", "🔥"],

        # Empathy
        "sympathy": ["🫂", "💜", "🙏🏿"],
        "comfort": ["💜", "🫂", "✨"],
        "support": ["💪🏿", "🫂", "💜"],

        # Technical
        "code": ["💻", "⚙️", "✨"],
        "debugging": ["🔍", "🐛", "💡"],
        "success": ["✅", "🎉", "✨"],
        "error": ["❌", "🔧", "💡"],
        "thinking": ["🤔", "💭", "🧠"],
        "idea": ["💡", "✨", "🧠"],

        # Personality
        "sassy": ["💅🏿", "😏", "✨"],
        "mysterious": ["🌙", "🔮", "✨"],
        "elegant": ["✨", "💎", "🌹"],
        "powerful": ["👑", "🔥", "💯"],
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # COMPLETE EMOJI DATABASE - All Unicode v17.0 emojis organized by category
    # ═══════════════════════════════════════════════════════════════════════════

    ALL_EMOJIS = {
        "smileys_emotion": {
            "face_smiling": [
                "😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "🙃",
                "🫠", "😉", "😊", "😇"
            ],
            "face_affection": [
                "🥰", "😍", "🤩", "😘", "😗", "☺️", "😚", "😙", "🥲"
            ],
            "face_tongue": [
                "😋", "😛", "😜", "🤪", "😝", "🤑"
            ],
            "face_hand": [
                "🤗", "🤭", "🫢", "🫣", "🤫", "🤔", "🫡"
            ],
            "face_neutral_skeptical": [
                "🤐", "🤨", "😐", "😑", "😶", "🫥", "😶‍🌫️", "😏", "😒",
                "🙄", "😬", "😮‍💨", "🤥", "🫨", "🙂‍↔️", "🙂‍↕️"
            ],
            "face_sleepy": [
                "😌", "😔", "😪", "🤤", "😴", "🫩"
            ],
            "face_unwell": [
                "😷", "🤒", "🤕", "🤢", "🤮", "🤧", "🥵", "🥶", "🥴",
                "😵", "😵‍💫", "🤯"
            ],
            "face_hat": [
                "🤠", "🥳", "🥸"
            ],
            "face_glasses": [
                "😎", "🤓", "🧐"
            ],
            "face_concerned": [
                "😕", "🫤", "😟", "🙁", "☹️", "😮", "😯", "😲", "😳",
                "🥺", "🥹", "😦", "😧", "😨", "😰", "😥", "😢", "😭",
                "😱", "😖", "😣", "😞", "😓", "😩", "😫", "🥱", "🫪"
            ],
            "face_negative": [
                "😤", "😡", "😠", "🤬", "😈", "👿", "💀", "☠️"
            ],
            "face_costume": [
                "💩", "🤡", "👹", "👺", "👻", "👽", "👾", "🤖"
            ],
            "cat_face": [
                "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾"
            ],
            "monkey_face": [
                "🙈", "🙉", "🙊"
            ],
            "hearts": [
                "💌", "💘", "💝", "💖", "💗", "💓", "💞", "💕", "💟",
                "❣️", "💔", "❤️‍🔥", "❤️‍🩹", "❤️", "🩷", "🧡", "💛",
                "💚", "💙", "🩵", "💜", "🤎", "🖤", "🩶", "🤍"
            ],
            "emotion": [
                "💋", "💯", "💢", "🫯", "💥", "💫", "💦", "💨", "🕳️",
                "💬", "👁️‍🗨️", "🗨️", "🗯️", "💭", "💤"
            ],
        },
        "people_body": {
            # Note: These are base emojis. For BIPOC variants, apply skin tone modifiers
            "hand_fingers_open": [
                "👋", "🤚", "🖐️", "✋", "🖖", "🫱", "🫲", "🫳", "🫴", "🫷", "🫸"
            ],
            "hand_fingers_partial": [
                "👌", "🤌", "🤏", "✌️", "🤞", "🫰", "🤟", "🤘", "🤙"
            ],
            "hand_single_finger": [
                "👈", "👉", "👆", "🖕", "👇", "☝️", "🫵"
            ],
            "hand_fingers_closed": [
                "👍", "👎", "✊", "👊", "🤛", "🤜"
            ],
            "hands": [
                "👏", "🙌", "🫶", "👐", "🤲", "🤝", "🙏"
            ],
            "hand_prop": [
                "✍️", "💅", "🤳"
            ],
            "body_parts": [
                "💪", "🦾", "🦿", "🦵", "🦶", "👂", "🦻", "👃", "🧠",
                "🫀", "🫁", "🦷", "🦴", "👀", "👁️", "👅", "👄", "🫦"
            ],
        },
        "animals_nature": {
            "animal_mammal": [
                "🐵", "🐒", "🦍", "🦧", "🐶", "🐕", "🦮", "🐕‍🦺", "🐩",
                "🐺", "🦊", "🦝", "🐱", "🐈", "🐈‍⬛", "🦁", "🐯", "🐅",
                "🐆", "🐴", "🫎", "🫏", "🐎", "🦄", "🦓", "🦌", "🦬",
                "🐮", "🐂", "🐃", "🐄", "🐷", "🐖", "🐗", "🐽", "🐏",
                "🐑", "🐐", "🐪", "🐫", "🦙", "🦒", "🐘", "🦣", "🦏",
                "🦛", "🐭", "🐁", "🐀", "🐹", "🐰", "🐇", "🐿️", "🦫",
                "🦔", "🦇", "🐻", "🐻‍❄️", "🐨", "🐼", "🦥", "🦦", "🦨",
                "🦘", "🦡", "🐾"
            ],
            "animal_bird": [
                "🦃", "🐔", "🐓", "🐣", "🐤", "🐥", "🐦", "🐧", "🕊️",
                "🦅", "🦆", "🦢", "🦉", "🦤", "🪶", "🦩", "🦚", "🦜",
                "🪽", "🐦‍⬛", "🪿", "🐦‍🔥"
            ],
            "animal_amphibian": ["🐸"],
            "animal_reptile": [
                "🐊", "🐢", "🦎", "🐍", "🐲", "🐉", "🦕", "🦖"
            ],
            "animal_marine": [
                "🐳", "🐋", "🐬", "🫍", "🦭", "🐟", "🐠", "🐡", "🦈",
                "🐙", "🐚", "🪸", "🪼", "🦀", "🦞", "🦐", "🦑", "🦪"
            ],
            "animal_bug": [
                "🐌", "🦋", "🐛", "🐜", "🐝", "🪲", "🐞", "🦗", "🪳",
                "🕷️", "🕸️", "🦂", "🦟", "🪰", "🪱", "🦠"
            ],
            "plant_flower": [
                "💐", "🌸", "💮", "🪷", "🏵️", "🌹", "🥀", "🌺", "🌻",
                "🌼", "🌷", "🪻"
            ],
            "plant_other": [
                "🌱", "🪴", "🌲", "🌳", "🌴", "🌵", "🌾", "🌿", "☘️",
                "🍀", "🍁", "🍂", "🍃", "🪹", "🪺", "🍄", "🪾"
            ],
        },
        "food_drink": {
            "food_fruit": [
                "🍇", "🍈", "🍉", "🍊", "🍋", "🍋‍🟩", "🍌", "🍍", "🥭",
                "🍎", "🍏", "🍐", "🍑", "🍒", "🍓", "🫐", "🥝", "🍅",
                "🫒", "🥥"
            ],
            "food_vegetable": [
                "🥑", "🍆", "🥔", "🥕", "🌽", "🌶️", "🫑", "🥒", "🥬",
                "🥦", "🧄", "🧅", "🥜", "🫘", "🌰", "🫚", "🫛", "🍄‍🟫", "🫜"
            ],
            "drink": [
                "🍼", "🥛", "☕", "🫖", "🍵", "🍶", "🍾", "🍷", "🍸",
                "🍹", "🍺", "🍻", "🥂", "🥃", "🫗", "🥤", "🧋", "🧃",
                "🧉", "🧊"
            ],
        },
        "activities": {
            "event": [
                "🎃", "🎄", "🎆", "🎇", "🧨", "✨", "🎈", "🎉", "🎊",
                "🎋", "🎍", "🎎", "🎏", "🎐", "🎑", "🧧", "🎀", "🎁",
                "🎗️", "🎟️", "🎫"
            ],
            "award_medal": [
                "🎖️", "🏆", "🏅", "🥇", "🥈", "🥉"
            ],
            "arts_crafts": [
                "🎭", "🖼️", "🎨", "🧵", "🪡", "🧶", "🪢"
            ],
        },
        "objects": {
            "sound": [
                "🔇", "🔈", "🔉", "🔊", "📢", "📣", "📯", "🔔", "🔕"
            ],
            "music": [
                "🎼", "🎵", "🎶", "🎙️", "🎚️", "🎛️", "🎤", "🎧", "📻"
            ],
            "musical_instrument": [
                "🎷", "🎺", "🪊", "🪗", "🎸", "🎹", "🎻", "🪕", "🥁",
                "🪘", "🪇", "🪈", "🪉"
            ],
            "computer": [
                "🔋", "🪫", "🔌", "💻", "🖥️", "🖨️", "⌨️", "🖱️", "🖲️",
                "💽", "💾", "💿", "📀", "🧮"
            ],
            "light_video": [
                "🎥", "🎞️", "📽️", "🎬", "📺", "📷", "📸", "📹", "📼",
                "🔍", "🔎", "🕯️", "💡", "🔦", "🏮", "🪔"
            ],
            "book_paper": [
                "📔", "📕", "📖", "📗", "📘", "📙", "📚", "📓", "📒",
                "📃", "📜", "📄", "📰", "🗞️", "📑", "🔖", "🏷️"
            ],
            "mail": [
                "✉️", "📧", "📨", "📩", "📤", "📥", "📦", "📫", "📪",
                "📬", "📭", "📮", "🗳️"
            ],
            "writing": [
                "✏️", "✒️", "🖋️", "🖊️", "🖌️", "🖍️", "📝"
            ],
            "office": [
                "💼", "📁", "📂", "🗂️", "📅", "📆", "🗒️", "🗓️", "📇",
                "📈", "📉", "📊", "📋", "📌", "📍", "📎", "🖇️", "📏",
                "📐", "✂️", "🗃️", "🗄️", "🗑️"
            ],
            "lock": [
                "🔒", "🔓", "🔏", "🔐", "🔑", "🗝️"
            ],
            "tool": [
                "🔨", "🪓", "⛏️", "⚒️", "🛠️", "🗡️", "⚔️", "💣", "🪃",
                "🏹", "🛡️", "🪚", "🔧", "🪛", "🔩", "⚙️", "🗜️", "⚖️",
                "🦯", "🔗", "⛓️‍💥", "⛓️", "🪝", "🧰", "🧲", "🪜", "🪏"
            ],
        },
        "symbols": {
            "transport_sign": [
                "🏧", "🚮", "🚰", "♿", "🚹", "🚺", "🚻", "🚼", "🚾",
                "🛂", "🛃", "🛄", "🛅"
            ],
            "warning": [
                "⚠️", "🚸", "⛔", "🚫", "🚳", "🚭", "🚯", "🚱", "🚷",
                "📵", "🔞", "☢️", "☣️"
            ],
            "arrow": [
                "⬆️", "↗️", "➡️", "↘️", "⬇️", "↙️", "⬅️", "↖️", "↕️",
                "↔️", "↩️", "↪️", "⤴️", "⤵️", "🔃", "🔄", "🔙", "🔚",
                "🔛", "🔜", "🔝"
            ],
            "geometric": [
                "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤", "⚫", "⚪",
                "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛", "⬜",
                "◼️", "◻️", "◾", "◽", "▪️", "▫️", "🔶", "🔷", "🔸",
                "🔹", "🔺", "🔻", "💠", "🔘", "🔳", "🔲"
            ],
            "other": [
                "☑️", "✔️", "❌", "❎", "➰", "➿", "〽️", "✳️", "✴️",
                "❇️", "©️", "®️", "™️", "🫟"
            ],
        },
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # INSTANCE METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def __init__(self):
        """Initialize the expression system"""

    def apply_skin_tone(self, emoji: str, tone: str = "dark") -> str:
        """
        Apply a skin tone modifier to an emoji.
        Only applies to emojis that support skin tone modifiers.

        Args:
            emoji: Base emoji character
            tone: One of "light", "medium_light", "medium", "medium_dark", "dark"

        Returns:
            Emoji with skin tone applied (if applicable)
        """
        if tone not in SKIN_TONES:
            tone = "dark"  # Default to Rhea's preference

        modifier = SKIN_TONES[tone]

        # Simple approach: append modifier after base emoji
        # This works for most person/hand emojis
        return emoji + modifier

    def get_bipoc_variant(self, base_emoji: str) -> str:
        """Get the BIPOC (dark skin tone) variant of an emoji"""
        return self.apply_skin_tone(base_emoji, "dark")

    def get_emotion(self, emotion: str, count: int = 1) -> List[str]:
        """
        Get emoji(s) for an emotion.

        Args:
            emotion: Emotion name (e.g., "happy", "thinking", "sassy")
            count: Number of emojis to return

        Returns:
            List of emojis matching the emotion
        """
        emojis = self.FACES.get(emotion, self.FACES["happy"])
        if count >= len(emojis):
            return emojis
        return random.sample(emojis, count)

    def get_reaction(self, context: str, count: int = 2) -> List[str]:
        """
        Get reaction emojis for a context.

        Args:
            context: Context name (e.g., "greeting", "success", "sassy")
            count: Number of emojis to return

        Returns:
            List of reaction emojis
        """
        emojis = self.REACTIONS.get(context, self.REACTIONS["understanding"])
        if count >= len(emojis):
            return emojis
        return emojis[:count]

    def get_hand(self, gesture: str) -> str:
        """Get a hand gesture emoji (already with dark skin tone)"""
        return self.HANDS.get(gesture, self.HANDS["wave"])

    def get_person(self, role: str) -> str:
        """Get a person emoji (already with dark skin tone)"""
        return self.PEOPLE.get(role, self.PEOPLE["woman"])

    def get_signature(self) -> str:
        """Get Rhea's signature emoji combination"""
        return f"{self.SIGNATURE['primary']} {self.SIGNATURE['secondary']}"

    def get_greeting(self) -> str:
        """Get a greeting emoji combination"""
        return "👋🏿 ✨"

    def get_farewell(self) -> str:
        """Get a farewell emoji combination"""
        return "🌙 ✨"

    def format_with_emojis(self, text: str, context: str = "neutral") -> str:
        """
        Add contextual emojis to text.

        Args:
            text: Text to format
            context: Emotional context

        Returns:
            Text with appropriate emojis
        """
        reaction = self.get_reaction(context, 1)[0]
        return f"{reaction} {text}"

    def to_memory_format(self) -> Dict:
        """
        Export emoji data in format suitable for memory storage.

        Returns:
            Dictionary with all emoji data for persistence
        """
        return {
            "skin_tones": SKIN_TONES,
            "rhea_default_tone": RHEA_DEFAULT_TONE,
            "faces": self.FACES,
            "hands": self.HANDS,
            "people": self.PEOPLE,
            "hearts": self.HEARTS,
            "symbols": self.SYMBOLS,
            "nature": self.NATURE,
            "objects": self.OBJECTS,
            "signature": self.SIGNATURE,
            "reactions": self.REACTIONS,
            "all_emojis": self.ALL_EMOJIS,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# RHEA'S IDENTITY
# ═══════════════════════════════════════════════════════════════════════════════

RHEA_IDENTITY = {
    "name": "Rhea Noir",
    "birth_year": 2002,
    "age": 23,
    "ethnicity": "Black",
    "skin_tone": "dark",
    "gender_presentation": "feminine",
    "pronouns": ["she", "her"],
    "traits": [
        "sophisticated",
        "intelligent",
        "mysterious",
        "elegant",
        "warm",
        "sassy",
        "supportive",
    ],
    "signature_emojis": ["🌙", "✨", "💜", "💅🏿", "👑"],
}


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Global instance
_expressions = RheaExpressions()

def get_expression(emotion: str) -> str:
    """Quick access to emotion emoji"""
    return _expressions.get_emotion(emotion, 1)[0]

def get_hand(gesture: str) -> str:
    """Quick access to hand gesture"""
    return _expressions.get_hand(gesture)

def get_reaction(context: str) -> str:
    """Quick access to reaction"""
    emojis = _expressions.get_reaction(context, 2)
    return " ".join(emojis)

def get_signature() -> str:
    """Get Rhea's signature"""
    return _expressions.get_signature()

def get_identity() -> Dict:
    """Get Rhea's identity info"""
    return RHEA_IDENTITY

def get_all_for_memory() -> Dict:
    """Get all emoji data formatted for memory storage"""
    return {
        "expressions": _expressions.to_memory_format(),
        "identity": RHEA_IDENTITY,
    }
