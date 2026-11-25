import os
import json
import subprocess
import yt_dlp

# Candidate moments from across the entire 9h 45m stream:
CANDIDATES = [
    # Format: (name, start_sec, duration_sec, category, description)
    ("GTA6_Unlock_Reaction", 245, 40, "Epic Reaction", "GTA 6 officially unlocks on PS5, Carry goes crazy cheering and screaming"),
    ("First_Cinematic_Scout", 390, 45, "Cinematic Intro", "Scout leaves, opening cutscene of Vice City with credits and Jason"),
    ("Maa_Chudaye_Paisa", 850, 35, "Funny Dialogue", "First robbery dialogue: Carry screaming about music over money"),
    ("First_Police_Busted", 1490, 35, "Gameplay Fail", "First high speed chase ending in getting busted by Vice City police"),
    ("Physics_Glitch_Ragdoll", 2370, 30, "Glitches & Physics", "Hilarious ragdoll glitch where character model twists through wall/hand"),
    ("Vice_City_Neon_Night", 3670, 45, "Visual Graphics", "Cruising Vice City coastline at night under ultra-realistic neon reflections"),
    ("Pole_Crash_Details", 5035, 35, "Hidden Details", "Insane crash physics into lamppost showing vehicle deformation & audio"),
    ("Highspeed_Stunt_Jump", 8060, 35, "Crazy Stunt", "Supercar jump across freeway ramp over police barricade"),
    ("Bat_Attack_Encounter", 9495, 35, "Funny NPC", "Crazy Florida NPC with baseball bat ambushes Carry in alleyway"),
    ("Freeway_Pileup_Explosion", 10315, 35, "Action & Explosion", "Freeway multi-car pileup chain explosion with five star wanted level"),
    ("Deadpool_Song_Drive", 11635, 40, "Soundtrack Moment", "Deadpool 2 song playing on radio while dodging SWAT vehicles"),
    ("Lucia_Character_Switch", 11855, 40, "Story & Gameplay", "First time unlocking and switching to Lucia in Vice City"),
    ("Instant_Karma_Death", 12015, 35, "Funny Death", "Carry mocking NPC before immediately getting hit by a speeding ambulance"),
    ("Mandy_Club_Infiltration", 13650, 45, "Story Mission", "Sneaking into Mandy's club in downtown Vice City"),
    ("Rockstar_Troll_Cutscene", 13675, 40, "Meme & Viral", "Carry getting trolled by Rockstar camera cutaway in the club"),
    ("Mini_Games_Arcade", 19695, 35, "Secret Mechanics", "Discovering playable mini-games inside GTA 6 retro arcade"),
    ("Five_Star_Swat_Shootout", 26030, 40, "Epic Action", "Massive SWAT shootout on Vice Beach hotel strip"),
    ("NPC_Limping_Troll", 28255, 35, "Funny NPC Interaction", "Carry making hilarious commentary about a limp NPC in Vice Beach"),
    ("Broke_300_Dollars", 29330, 35, "Funny Reaction", "Carry realizing he doesn't even have $300 in Vice City economy"),
    ("Swamp_Alligator_Chase", 30070, 40, "Unexpected Event", "Getting chased by Florida swamp alligators while on the run from cops"),
    ("Strip_Club_600_Dollars", 31310, 45, "Most Viral Moment", "Carry spending $600 to enter VIP room and frantic camera blurring"),
    ("Eyes_Wide_Open_Reaction", 31560, 35, "Meme Reaction", "Carry's shock face and wide eyes as Mandy cutscene unfolds"),
    ("Lean_On_Club_Vibes", 31665, 40, "Music & Atmosphere", "Club dance floor with Lean On beat and hyper-detailed NPC crowds")
]

print(f"Total candidate moments across 9h45m: {len(CANDIDATES)}")
os.makedirs("candidates_preview", exist_ok=True)

with open("stream_url_360p.txt", "r") as f:
    stream_url = f.read().strip()

print("Extracting preview frames...")
for name, start, dur, cat, desc in CANDIDATES:
    frame_path = f"candidates_preview/{name}.jpg"
    if not os.path.exists(frame_path):
        cmd = [
            "ffmpeg", "-y", "-ss", str(start + 5), "-i", stream_url,
            "-vframes", "1", "-update", "1", frame_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Captured frame for {name} at {start}s")
    else:
        print(f"Frame exists for {name}")

print("Done extracting preview frames!")
