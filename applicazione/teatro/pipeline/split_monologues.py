"""Split long monologues in eurostar_act1_parsed.json into segments with fillers.

Phone calls get reactive fillers (mmm, yeah, right...) to simulate
the other person talking. Non-phone monologues get natural breath pauses.
"""
import json
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
INPUT = APP_DIR / "eurostar_act1_parsed.json"
OUTPUT = APP_DIR / "eurostar_act1_segmented.json"

PHONE_FILLERS_ARTHUR = [
    ("Mmm... yeah...", "Casual, absent-minded, listening on the phone"),
    ("Right, right...", "Quick agreement, distracted"),
    ("Heh...", "Nervous little laugh, on the phone"),
    ("Yeah... no, I know...", "Agreeing vaguely, half-listening"),
    ("Mmhmm...", "Minimal acknowledgment, bored"),
    ("Exactly, exactly...", "Quick agreement, impatient to continue"),
    ("Ha... yeah...", "Nervous chuckle, slightly uncomfortable"),
    ("Sure, sure...", "Dismissive agreement, wanting to move on"),
]

PHONE_LINE_IDS = {1, 2, 26, 28, 81, 82}

SPLIT_POINTS = {
    1: [
        ("Yes? Hello, Fred... No, I'm on the train right now...",
         "Rushed, picking up the phone, casual"),
        ("I promised my wife to take her to London for our wedding anniversary... To be honest, I hate those anniversary nonsense, and on top of that, I detest England. But you know how it is... When you're married, you have to know how to compromise!",
         "Complaining, slightly bored, resigned"),
        ("It's in London that I met Karen... I booked a room in the Bed and Breakfast where we spent our first night together... Isn't that romantic? Lucky that I didn't meet her at the Hilton in Bora-Bora... Two train tickets to London, even in business class, it's still cheaper than Polynesia...",
         "Sarcastic, dry humor, rambling"),
        ("Anyway, thank goodness we allowed for some extra time... You know I'm claustrophobic, so I'm a little anxious about taking the tunnel under the Channel... But since I'm even more afraid of flying... And then I thought it would be faster than the ferry...",
         "Anxious, slightly breathless, nervous"),
        ("But you can't imagine the boarding procedures, it's mind-boggling! It took us three quarters of an hour to go through security! I would have been better off swimming. I had forgotten that England is no longer in Europe. I feel like I'm heading to Baghdad!",
         "Exasperated, incredulous, animated"),
        ("I even got a body search. I ran into a little tough guy, like a sergeant. I thought he was going to stick a finger up my ass to see if I had any weapons of mass destruction hidden in there, before sending me straight to Guantanamo...",
         "Outraged, dramatic, storytelling with disgust"),
        ("He stressed me out so much, for a moment, I forgot to put my pants and shoes back on... Can you imagine me arriving at Waterloo barefoot and in my underwear? Luckily we're not leaving from Austerlitz, otherwise you can see the symbol... I mean, for a wedding anniversary...",
         "Self-deprecating, nervous laugh, rambling"),
        ("Oh, now it's Saint-Pancras? Anyway, now I am on board, trying to relax a little...",
         "Confused, settling down, calmer"),
        ("Karen? No, I don't know what the hell my wife is doing... I had to go to the exchange office to buy British pounds, and we agreed to meet directly on the train, but I don't see her anywhere... However, her suitcase is here. I don't understand anything...",
         "Puzzled, slightly worried, looking around"),
        ("Sorry, that's actually her calling... Okay, I'll call you back... See you soon, Fred.",
         "Quick, wrapping up the call, distracted"),
    ],
    2: [
        ("Karen? Where the hell are you?... At the kiosk?",
         "Impatient, exasperated"),
        ("Don't you realize that the train is about to leave? Yeah, well, listen, if they don't have Marie Claire, you take Vogue or Cosmopolitan. It's the same thing, right...",
         "Rushed, dismissive, impatient"),
        ("Yes, yes, I have the pounds. A thousand should be enough for a few days in London. It stresses me out a bit to carry that much cash, but... It seems worth it to exchange before we get to England...",
         "Lowering voice conspiratorially, stressed about the money"),
        ("Uh, could you get me Tennis Magazine, while you're at it? No, not Bicycling Magazine, Tennis Magazine! No, it's not the same, believe me...",
         "Annoyed, correcting her, frustrated"),
        ("Well, you'll eventually find it... Otherwise, check the newsstand next door... But hurry up, for god's sake! OK, see you later. I love you too...",
         "Impatient then softening at the end, tender"),
    ],
    26: [
        ("Karen? Where are you, damn it? Oh no, it can't be true...!",
         "Exasperated, dismayed, phone call"),
        ("But I told you to hurry up!... But I didn't care, whether it was Tennis Magazine or Tennishead! It was just to have something to read on the train...",
         "Frustrated, raising voice"),
        ("And now what do we do...? Try to catch the next train and I'll wait for you in London...? Well... What do you want me to say? Do we have another option?",
         "Resigned, deflated"),
        ("Yeah... OK, call me back...",
         "Defeated, sighing, hanging up"),
    ],
    28: [
        ("Already... Ah, it's you, Fred. No, no, it's... It's Karen. You won't believe it, but she just missed the train!",
         "Picking up phone, incredulous, disbelief"),
        ("No, I'm not joking, unfortunately... Yeah, well... If she manages to get a ticket. We booked ours three months in advance...",
         "Resigned, shaking his head"),
        ("No, but can you imagine? Here I am, off to London alone to celebrate our wedding anniversary... Well, when I say alone...",
         "Self-pitying, then perking up with a secret"),
        ("You won't believe it either, but something absolutely amazing happened to me... A crazy woman sat right in front of me on the Eurostar, in Karen's seat, actually... And she thinks I'm a film director!",
         "Excited, conspiratorial, whispering"),
        ("Which one? I don't know... Apparently, a really famous one, anyway... Well, I didn't even have time to tell her it wasn't me, you know. She didn't let me get a word in!",
         "Amused, playing innocent"),
        ("And now she's gone to get me coffee and croissants... I swear to you! She's completely ecstatic about me, I tell you!",
         "Giddy, bragging, whispering"),
        ("So now, I'm thinking of taking advantage of the situation... Three hours alone on the Eurostar is a long time... Not to mention my phobia of tunnels... At least I'll be thinking about something else...",
         "Scheming, rationalizing, playful"),
        ("Actress, yeah... Listen, not bad, but... Very motivated, in any case! I vaguely feel like I've seen her face somewhere before... In a commercial, maybe...",
         "Appreciative, thoughtful"),
        ("Stop it, I remind you that I'm married... Yeah, well, OK, but I'm sober now...",
         "Defensive, then conceding with a laugh"),
        ("And I don't know how long I'll be able to keep up the illusion, because, you know, me and the movies... I go twice a year, and that's it...",
         "Self-aware, worried, confessing"),
        ("Well, I'll let you go, she's coming back... OK, I'll tell you about it... Bye...",
         "Quick, whispering urgently, hanging up fast"),
    ],
    39: [
        ("And how do you imagine that bitch should be? Your heroine! In the script! She's quite a bitch, isn't she? Doing that to that poor guy who didn't do anything to her...",
         "Excited, opinionated, fast-talking"),
        ("But excuse me, I shouldn't have asked you that question... I promised not to be nosy... And it wouldn't be fair to the other candidates...",
         "Apologetic, catching herself, pulling back"),
        ("But I'm just so nervous... Arthur Monerot! Sitting right in front of me for three hours! I have to take advantage of this unique opportunity...",
         "Gushing, starstruck, barely containing herself"),
        ("Do you mind if I ask you something?",
         "Calming down, seeking permission, earnest"),
    ],
    81: [
        ("Yes...? Hello Karen... Yes, I'm sorry, but with the noise of the train, I didn't recognize your voice...",
         "Distracted, picking up phone, apologetic"),
        ("Sorry... It's my assistant...",
         "Quick aside to Marilyn, covering"),
        ("Yes, Karen, have you been able to solve it...? No, I'm not taking this lightly, but... we're not going to make a big deal out of it either...",
         "On phone, dismissive, trying to minimize"),
        ("No... It's not true? There's no ticket until a month from now? That can't be!",
         "Shocked, dismayed"),
    ],
    82: [
        ("Okay, I'll call you as soon as I arrive... But I can't promise anything... I don't think it's going to be easy to find a ticket to go back to Paris...",
         "Stressed, negotiating on the phone"),
        ("No, I'm not at all happy about this... Can you imagine if I had to spend the whole weekend alone in London?",
         "Annoyed, then realizing the upside"),
        ("You have some big news to tell me? You're scaring me! Well... Listen, I have to leave you because we're going into the tunnel...",
         "Worried, then finding an excuse to hang up"),
        ("Why am I talking in plural? Because I'm not alone in this train. I'm traveling in business class, not in a private compartment of the Orient Express...",
         "Defensive, quick excuse"),
        ("And it's going to be my fault again... It's still you who managed to miss this train, right...?",
         "Irritated, counterattacking"),
        ("Sorry... I just had a small problem to solve... Now, I'm all yours...",
         "Turning to Marilyn, switching to charming mode, warm smile"),
    ],
}


def split_script():
    with open(INPUT, "r", encoding="utf-8") as f:
        script = json.load(f)

    original_count = len(script["lines"])
    new_lines = []
    filler_idx = 0

    for line in script["lines"]:
        line_id = line["id"]

        if line_id not in SPLIT_POINTS:
            new_lines.append(line)
            continue

        segments = SPLIT_POINTS[line_id]
        is_phone = line_id in PHONE_LINE_IDS
        character = line["character"]

        for i, (text, instruct) in enumerate(segments):
            sub_id = f"{line_id}.{i + 1}"
            new_lines.append({
                "id": sub_id,
                "character": character,
                "text": text,
                "instruct": instruct,
                "original_line": line_id,
            })

            if is_phone and i < len(segments) - 1:
                filler_text, filler_instruct = PHONE_FILLERS_ARTHUR[filler_idx % len(PHONE_FILLERS_ARTHUR)]
                filler_idx += 1
                new_lines.append({
                    "id": f"{line_id}.{i + 1}f",
                    "character": character,
                    "text": filler_text,
                    "instruct": filler_instruct,
                    "original_line": line_id,
                    "is_filler": True,
                })

    script["lines"] = new_lines
    script["segmented"] = True
    script["total_segments"] = len(new_lines)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    phone_fillers = sum(1 for l in new_lines if l.get("is_filler"))
    segments = sum(1 for l in new_lines if "original_line" in l and not l.get("is_filler"))
    unchanged = sum(1 for l in new_lines if "original_line" not in l)
    print(f"Original: {original_count} lines")
    print(f"Segmented: {segments} segments from {len(SPLIT_POINTS)} monologues")
    print(f"Fillers added: {phone_fillers}")
    print(f"Unchanged lines: {unchanged}")
    print(f"Total: {len(new_lines)} items")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    split_script()
