import os
import csv
import json

BASE_DIR = r"E:\videos\TECHNO_GAMERZ_REELS"
FINAL_REELS_DIR = os.path.join(BASE_DIR, "FINAL_REELS")
THUMBNAILS_DIR = os.path.join(BASE_DIR, "THUMBNAILS")
SUBTITLES_DIR = os.path.join(BASE_DIR, "SUBTITLES")
METADATA_DIR = os.path.join(BASE_DIR, "METADATA")
ANALYSIS_DIR = os.path.join(BASE_DIR, "ANALYSIS")

for d in [FINAL_REELS_DIR, THUMBNAILS_DIR, SUBTITLES_DIR, METADATA_DIR, ANALYSIS_DIR]:
    os.makedirs(d, exist_ok=True)

REELS_DATA = [
    {
        "id": 1,
        "name": "Techno_Reel_001",
        "start": 35,
        "duration": 26,
        "category": "Viral Reaction",
        "hook": "BOSS OF GTA IS BACK! 🔥",
        "score": 97,
        "subtitles": [
            (0.0, 4.0, "FINALLY! GTA 6 IS HERE!"),
            (4.0, 10.0, "Techno Gamerz enters Vice City!"),
            (10.0, 18.0, "The nostalgia and hype is unreal!"),
            (18.0, 26.0, "Let's begin Day 1 in Leonida!")
        ],
        "title": "Techno Gamerz Enters GTA 6 For The First Time! 🔥 Boss Of GTA Is Back #GTA6",
        "desc": "Ujjwal (Techno Gamerz) kicks off his GTA 6 series in Vice City! #GTA6 #TechnoGamerz #GTAVI #Shorts",
        "hashtags": "#GTA6 #TechnoGamerz #GTAVI #ViceCity #GamingShorts #Reels",
        "pinned": "Who else has been waiting for Techno Gamerz's GTA 6 Episode 1?! 🔥"
    },
    {
        "id": 2,
        "name": "Techno_Reel_002",
        "start": 815,
        "duration": 26,
        "category": "Funny Dialogue",
        "hook": "WAIT... DID HE JUST SAY THAT?! 💀",
        "score": 93,
        "subtitles": [
            (0.0, 5.0, "High above Vice City in the cockpit!"),
            (5.0, 12.0, "Brian: 'You know what? F*** it.'"),
            (12.0, 19.0, "Techno trying to keep it family-friendly!"),
            (19.0, 26.0, "This mission just took a wild turn!")
        ],
        "title": "Techno Gamerz Caught Off Guard In GTA 6 Cockpit Cutscene! 💀😂 #GTA6",
        "desc": "Hilarious mid-air cutscene moment during Techno Gamerz's first flight in GTA 6! #GTA6 #TechnoGamerz #Shorts",
        "hashtags": "#GTA6 #TechnoGamerz #GTA6Funny #GamingReels #Shorts",
        "pinned": "Techno's reaction when the dialogue dropped 😂💀"
    },
    {
        "id": 3,
        "name": "Techno_Reel_003",
        "start": 885,
        "duration": 25,
        "category": "Viral Reaction",
        "hook": "NEXT 2 MONTHS SORTED HAI! 🚀",
        "score": 94,
        "subtitles": [
            (0.0, 5.0, "Techno Gamerz is locked in!"),
            (5.0, 12.0, "'Agle 2 mahine toh sorted hai bhai!'"),
            (12.0, 19.0, "Non-stop GTA 6 episodes incoming!"),
            (19.0, 25.0, "Indian YouTube gaming is back!")
        ],
        "title": "Techno Gamerz: 'Agle 2 Mahine Sorted Hai!' 🔥 GTA 6 Hype Is Real #Shorts",
        "desc": "Ujjwal confirms months of epic GTA 6 content ahead! #TechnoGamerz #GTA6 #GamingShorts",
        "hashtags": "#GTA6 #TechnoGamerz #Ujjwal #GamingReels #GTA6Gameplay",
        "pinned": "How many episodes do you think this GTA 6 series will have? 👇"
    },
    {
        "id": 4,
        "name": "Techno_Reel_004",
        "start": 1695,
        "duration": 26,
        "category": "Visual Showcase",
        "hook": "GTA 6 STORM PHYSICS ARE INSANE! ⛈️",
        "score": 95,
        "subtitles": [
            (0.0, 5.0, "Flying a seaplane in a tropical storm!"),
            (5.0, 12.0, "Look at the ocean waves and rain!"),
            (12.0, 19.0, "Key Lento Marina Club in the distance!"),
            (19.0, 26.0, "Rockstar's weather engine is next-level!")
        ],
        "title": "Flying A Seaplane In A GTA 6 Tropical Storm Looks Unreal! ⛈️✈️ #GTA6",
        "desc": "Insane water physics, storm clouds, and seaplane handling in GTA 6! #GTA6 #GTA6Graphics #TechnoGamerz",
        "hashtags": "#GTA6 #GTA6Graphics #WeatherPhysics #TechnoGamerz #Shorts",
        "pinned": "Rate these storm & water graphics out of 10! ⛈️🔥"
    },
    {
        "id": 5,
        "name": "Techno_Reel_005",
        "start": 2500,
        "duration": 25,
        "category": "Funny Moments",
        "hook": "WHO JUST OPENED HIS DOOR?! 👀",
        "score": 92,
        "subtitles": [
            (0.0, 5.0, "Wait... look at Techno's webcam!"),
            (5.0, 12.0, "Someone just opened his room door!"),
            (12.0, 19.0, "He is SO locked into GTA 6..."),
            (19.0, 25.0, "He didn't even notice! 😂")
        ],
        "title": "Someone Opened Techno Gamerz's Door & He Didn't Even Notice! 👀😂 #GTA6",
        "desc": "Ujjwal was so immersed in GTA 6 that he completely missed someone opening his studio door! #TechnoGamerz #GTA6 #Shorts",
        "hashtags": "#TechnoGamerz #GTA6 #GamingMoments #FunnyReels #Shorts",
        "pinned": "Did you spot the door opening in the background?! 👀😂"
    },
    {
        "id": 6,
        "name": "Techno_Reel_006",
        "start": 2945,
        "duration": 26,
        "category": "Hidden Details",
        "hook": "GTA 6 HAS ITS OWN INSTAGRAM?! 📱",
        "score": 95,
        "subtitles": [
            (0.0, 5.0, "Checking Jason's smartphone in GTA 6!"),
            (5.0, 12.0, "Scrollable in-game social media feed!"),
            (12.0, 19.0, "With posts, likes, and full comments!"),
            (19.0, 26.0, "The attention to detail is ridiculous!")
        ],
        "title": "GTA 6 Has A Working Social Media App On Your Phone! 📱🔥 #GTA6",
        "desc": "Techno Gamerz explores the hilarious in-game social media app in GTA 6! #GTA6 #GTA6Details #TechnoGamerz",
        "hashtags": "#GTA6 #GTA6Details #EasterEggs #TechnoGamerz #Shorts",
        "pinned": "The level of detail in GTA 6 is unmatched! 📱💀"
    },
    {
        "id": 7,
        "name": "Techno_Reel_007",
        "start": 3298,
        "duration": 24,
        "category": "Funny Moments",
        "hook": "WHAT IS THIS NPC DOING?! 😂",
        "score": 91,
        "subtitles": [
            (0.0, 5.0, "Techno spots something hilarious!"),
            (5.0, 12.0, "'Abey peeche kya khujara hai?!' 😂"),
            (12.0, 18.0, "GTA 6 NPC animations are too real!"),
            (18.0, 24.0, "Rockstar programmed EVERYTHING!")
        ],
        "title": "Techno Gamerz Spots Hilarious GTA 6 NPC Behavior! 😂💀 #GTA6",
        "desc": "Ujjwal bursts out laughing at an unexpected NPC animation in Vice City! #GTA6 #TechnoGamerz #FunnyGaming",
        "hashtags": "#GTA6 #GTA6Funny #NPC #TechnoGamerz #Shorts",
        "pinned": "GTA 6 NPCs have zero chill 😂🔥"
    },
    {
        "id": 8,
        "name": "Techno_Reel_008",
        "start": 3708,
        "duration": 26,
        "category": "Gameplay Fail",
        "hook": "NPC LANDED IN HIS TRUCK BED! 💀",
        "score": 96,
        "subtitles": [
            (0.0, 5.0, "Cruising in Jason's '70 Ganado..."),
            (5.0, 12.0, "Wait... how did a whole guy get back there?!"),
            (12.0, 19.0, "NPC chilling in the pickup truck bed!"),
            (19.0, 26.0, "Techno: 'Galti toh aapki hi hai!' 😂")
        ],
        "title": "NPC Lands Straight Inside Techno Gamerz's Pickup Truck In GTA 6! 💀🚗 #GTA6",
        "desc": "Unbelievable physics moment as an NPC ends up riding in the back of Jason's pickup truck! #GTA6 #TechnoGamerz #GTA6Physics",
        "hashtags": "#GTA6 #GTA6Physics #GamingFail #TechnoGamerz #Shorts",
        "pinned": "Free Uber ride in Vice City 💀🚗"
    },
    {
        "id": 9,
        "name": "Techno_Reel_009",
        "start": 3995,
        "duration": 26,
        "category": "Story & Characters",
        "hook": "GIMME BRIAN'S RENT RIGHT NOW! 💰",
        "score": 94,
        "subtitles": [
            (0.0, 5.0, "Jason walks into the surf shop..."),
            (5.0, 12.0, "'Gimme Brian's rent or I kick your ass!'"),
            (12.0, 19.0, "Doing Brian's dirty work with a straight face!"),
            (19.0, 26.0, "Jason is an absolute menace in Vice City!")
        ],
        "title": "Jason Collecting Rent Like A Boss In GTA 6! 💰🔥 Techno Gamerz #GTA6",
        "desc": "Techno Gamerz plays the hilarious rent collection scene with Jason! #GTA6 #JasonGTA6 #TechnoGamerz #Shorts",
        "hashtags": "#GTA6 #Jason #GTA6Story #TechnoGamerz #Shorts",
        "pinned": "Jason's intimidation level: 100/100 💪🔥"
    },
    {
        "id": 10,
        "name": "Techno_Reel_010",
        "start": 4360,
        "duration": 25,
        "category": "Funny Moments",
        "hook": "GTA 6 MADE HIM FORGET EVERYTHING! 😂",
        "score": 90,
        "subtitles": [
            (0.0, 5.0, "Over 1 hour straight into GTA 6..."),
            (5.0, 12.0, "Techno refuses to take a break!"),
            (12.0, 19.0, "Pure childhood excitement on his face!"),
            (19.0, 25.0, "True OG GTA gamer energy! 🔥")
        ],
        "title": "Techno Gamerz Refuses To Pause GTA 6! 😂 Pure Gamer Energy #GTA6",
        "desc": "Nothing can pull Ujjwal away from exploring Vice City in GTA 6! #TechnoGamerz #GTA6 #GamingReels",
        "hashtags": "#TechnoGamerz #GTA6 #GamingMemes #Shorts #ViceCity",
        "pinned": "Relatable level: 1000% when playing a new GTA 😂"
    },
    {
        "id": 11,
        "name": "Techno_Reel_011",
        "start": 5092,
        "duration": 25,
        "category": "Hidden Mechanics",
        "hook": "HOLD ON... WHAT IS THIS OPTION?! 🚿",
        "score": 93,
        "subtitles": [
            (0.0, 5.0, "Exploring the safehouse bathroom..."),
            (5.0, 12.0, "Press Triangle to take a SHOWER?!"),
            (12.0, 19.0, "Techno immediately testing the mechanic!"),
            (19.0, 25.0, "Wait... why did he cut that?! 😂")
        ],
        "title": "Testing The Shower Mechanic In GTA 6! 🚿😂 Techno Gamerz #GTA6",
        "desc": "Ujjwal discovers interactive bathroom mechanics inside Jason's house in GTA 6! #GTA6 #TechnoGamerz #HiddenDetails",
        "hashtags": "#GTA6 #GTA6Details #TechnoGamerz #FunnyGaming #Shorts",
        "pinned": "Bro forgot to put a cut or did it on purpose? 😂🌚"
    },
    {
        "id": 12,
        "name": "Techno_Reel_012",
        "start": 5745,
        "duration": 25,
        "category": "Visual Showcase",
        "hook": "OFF-ROADING IN GTA 6 SWAMPS! 🚙",
        "score": 92,
        "subtitles": [
            (0.0, 5.0, "Taking Jason's '70 Ganado off-road!"),
            (5.0, 12.0, "Look at the tall grass & mud physics!"),
            (12.0, 19.0, "Tire tracks and suspension reacting live!"),
            (19.0, 25.0, "Watch out for Florida alligators! 🐊")
        ],
        "title": "GTA 6 Off-Road & Swamp Physics Are Next Level! 🚙🌿 #GTA6",
        "desc": "Testing vehicle suspension, dirt trails, and foliage physics in Leonida's swamps! #GTA6 #GTA6Graphics #TechnoGamerz",
        "hashtags": "#GTA6 #GTA6Physics #OffRoad #TechnoGamerz #Shorts",
        "pinned": "Can't wait to see what's hiding in those swamps 🐊👀"
    },
    {
        "id": 13,
        "name": "Techno_Reel_013",
        "start": 6508,
        "duration": 26,
        "category": "Hidden Details",
        "hook": "TOMMY VERCETTI COULD NEVER SWIM! 🏊",
        "score": 94,
        "subtitles": [
            (0.0, 5.0, "Down at the Vice City marina!"),
            (5.0, 12.0, "Testing swimming & water physics!"),
            (12.0, 19.0, "Remember when Tommy couldn't swim?!"),
            (19.0, 26.0, "Vice City has come a LONG way! 🔥")
        ],
        "title": "Vice City Swimming Physics Then vs Now! 🏊🔥 Techno Gamerz #GTA6",
        "desc": "From Tommy Vercetti drowning instantly to GTA 6's hyper-realistic Vice City water! #GTA6 #ViceCity #TechnoGamerz",
        "hashtags": "#GTA6 #ViceCity #TommyVercetti #TechnoGamerz #Shorts",
        "pinned": "Only OG Vice City players understand the swimming pain 😂🏊"
    },
    {
        "id": 14,
        "name": "Techno_Reel_014",
        "start": 6585,
        "duration": 25,
        "category": "Crazy Stunt",
        "hook": "HE JUMPED OUT AT FULL SPEED! 😱",
        "score": 97,
        "subtitles": [
            (0.0, 4.0, "Cruising down Vice City highway..."),
            (4.0, 10.0, "Ujjwal accidentally bails out mid-drive!"),
            (10.0, 17.0, "AND HE DIDN'T EVEN FALL?! 😂"),
            (17.0, 25.0, "Techno screaming: 'AAAAAAAA!' 😱🔥")
        ],
        "title": "Techno Gamerz Jumps Out Of A Moving Car In GTA 6 & Screams! 😱😂 #GTA6",
        "desc": "Hilarious moment when Ujjwal bails out of a moving pickup truck without falling and loses his mind! #TechnoGamerz #GTA6 #Shorts",
        "hashtags": "#GTA6 #TechnoGamerz #GTA6Funny #GamingReels #Shorts",
        "pinned": "Jason just casually stepped out of a moving car like a boss 💀🚗"
    },
    {
        "id": 15,
        "name": "Techno_Reel_015",
        "start": 6640,
        "duration": 25,
        "category": "Funny Dialogue",
        "hook": "CHACHA PULLED UP ON HIM! 💀",
        "score": 95,
        "subtitles": [
            (0.0, 5.0, "Techno messing with Vice City locals..."),
            (5.0, 12.0, "This NPC did NOT back down!"),
            (12.0, 19.0, "Full comedy chaos on the streets!"),
            (19.0, 25.0, "Classic Techno Gamerz GTA energy! 🔥")
        ],
        "title": "Techno Gamerz Messes With The Wrong NPC In GTA 6! 💀😂 #GTA6",
        "desc": "Ujjwal having the time of his life trolling NPCs in Vice City! #GTA6 #TechnoGamerz #ComedyShorts",
        "hashtags": "#GTA6 #TechnoGamerz #GTA6Memes #GamingShorts #Reels",
        "pinned": "Last 20 minutes of this video were pure comedy gold 😂🔥"
    },
    {
        "id": 16,
        "name": "Techno_Reel_016",
        "start": 6792,
        "duration": 26,
        "category": "Meme & Viral",
        "hook": "TECHNO SKIPPED THE MAIN SCENE! 😂",
        "score": 99,
        "subtitles": [
            (0.0, 5.0, "Jason fixing the kitchen sink..."),
            (5.0, 12.0, "Mandy walks in... AND TECHNO CUTS IT!"),
            (12.0, 19.0, "Bro skipped the spicy scene for YouTube!"),
            (19.0, 26.0, "50,000 comments all talking about 1:53:20! 😂")
        ],
        "title": "Why Techno Gamerz Skipped THIS GTA 6 Sink Scene! 😂🌚 #GTA6",
        "desc": "The most talked-about cut in Techno Gamerz's GTA 6 Episode 1 during the Mandy sink scene! #GTA6 #TechnoGamerz #Mandy #Shorts",
        "hashtags": "#GTA6 #TechnoGamerz #GTA6Memes #Mandy #GamingShorts",
        "pinned": "Respect to Ujjwal bhai for keeping it family-friendly 😂🌚"
    }
]

def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def format_srt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec - int(sec)) * 100)
    return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"

for item in REELS_DATA:
    srt_file = os.path.join(SUBTITLES_DIR, f"{item['name']}.srt")
    ass_file = os.path.join(SUBTITLES_DIR, f"{item['name']}.ass")

    with open(srt_file, "w", encoding="utf-8") as sf:
        for idx, (sub_start, sub_end, text) in enumerate(item["subtitles"], 1):
            sf.write(f"{idx}\n{format_srt_time(sub_start)} --> {format_srt_time(sub_end)}\n{text}\n\n")

    ass_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Hook,Arial,64,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,8,30,30,48,1",
        "Style: Subtitle,Arial,58,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,40,40,210,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,0:00:00.00,{format_ass_time(item['duration'])},Hook,,0,0,48,,{{\\c&H00FFFF&}}{item['hook']}"
    ]

    for sub_start, sub_end, text in item["subtitles"]:
        words = text.split(" ", 1)
        if len(words) > 1:
            styled_text = f"{{\\c&H00FFFF&}}{words[0]} {{\\c&HFFFFFF&}}{words[1]}"
        else:
            styled_text = f"{{\\c&H00FFFF&}}{text}"
        ass_lines.append(f"Dialogue: 0,{format_ass_time(sub_start)},{format_ass_time(sub_end)},Subtitle,,0,0,210,,{styled_text}")

    with open(ass_file, "w", encoding="utf-8") as af:
        af.write("\n".join(ass_lines))

with open(os.path.join(METADATA_DIR, "youtube_upload_details.csv"), "w", newline="", encoding="utf-8") as mf:
    writer = csv.writer(mf)
    writer.writerow([
        "Clip Number", "Filename", "Original Timestamp", "Duration (s)",
        "Title", "Description", "Hashtags", "Suggested Pinned Comment", "Viral Score", "Category"
    ])
    for item in REELS_DATA:
        writer.writerow([
            item["id"], f"{item['name']}.mp4", format_timestamp(item["start"]),
            item["duration"], item["title"], item["desc"], item["hashtags"],
            item["pinned"], item["score"], item["category"]
        ])

with open(os.path.join(ANALYSIS_DIR, "complete_clip_timestamps.csv"), "w", newline="", encoding="utf-8") as af:
    writer = csv.writer(af)
    writer.writerow([
        "Clip Number", "Original Start (s)", "Original Start Time",
        "Original End (s)", "Original End Time", "Clip Duration",
        "Viral Score", "Clip Category", "Generated Title", "Description", "Hashtags"
    ])
    for item in REELS_DATA:
        writer.writerow([
            item["id"], item["start"], format_timestamp(item["start"]),
            item["start"] + item["duration"], format_timestamp(item["start"] + item["duration"]),
            f"{item['duration']}s", item["score"], item["category"],
            item["title"], item["desc"], item["hashtags"]
        ])

print(f"Prepared metadata & subtitles for {len(REELS_DATA)} 1080p60 Techno Gamerz Reels.")
