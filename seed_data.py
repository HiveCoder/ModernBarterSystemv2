"""
Seed script: populates the database (Supabase or SQLite) with
realistic sample users, items, tags, trade offers and reviews.

Run from project root:
    python seed_data.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

from extensions import db
from models import User, Category, Item, ItemImage, ItemTag, TradeOffer, Review
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

USERS = [
    dict(username="marco_polo",  email="marco@silktrade.com",  display_name="Marco Polo",
         bio="Globe-trotter & master trader. I swap rare finds from my travels.",
         location="New York, NY", is_verified=True, trade_credits=320),
    dict(username="jade_chen",   email="jade@silktrade.com",   display_name="Jade Chen",
         bio="Vintage fashion curator. Always hunting for 70s & 80s gems.",
         location="San Francisco, CA", is_verified=True, trade_credits=215),
    dict(username="rupert_k",    email="rupert@silktrade.com", display_name="Rupert King",
         bio="DIY enthusiast. My garage is a treasure chest of tools.",
         location="Austin, TX", is_verified=False, trade_credits=88),
    dict(username="sofia_m",     email="sofia@silktrade.com",  display_name="Sofia Mendez",
         bio="Bookworm and board-game addict. Trade me anything nerdy!",
         location="Chicago, IL", is_verified=True, trade_credits=175),
    dict(username="dev_rajesh",  email="rajesh@silktrade.com", display_name="Rajesh Patel",
         bio="Tech collector & gadget hoarder since 2005.",
         location="Seattle, WA", is_verified=False, trade_credits=60),
    dict(username="anna_b",      email="anna@silktrade.com",   display_name="Anna Brünn",
         bio="Artist and gallery owner. Swapping original prints and crafts.",
         location="Portland, OR", is_verified=True, trade_credits=290),
]

# (title, description, category_name, condition, value, trade_type, looking_for, tags, featured)
ITEMS = [
    # --- Electronics ---
    ("Sony WH-1000XM5 Headphones",
     "Flagship ANC headphones, barely used. Comes with original case, cable, and adapters. Sound is incredible — deep bass, crystal highs.",
     "Electronics", "like_new", 320.0, "trade",
     "Looking for a mirrorless camera or high-end mechanical keyboard.",
     ["sony", "headphones", "anc", "wireless", "audio"], True),

    ("Apple iPad Pro 11\" (2022)",
     "256GB Wi-Fi + Cellular, Space Gray. Apple Pencil 2 included. Screen protector applied, no scratches.",
     "Electronics", "good", 750.0, "trade",
     "MacBook Air M2 or equivalent laptop.",
     ["ipad", "apple", "tablet", "pencil", "ios"], True),

    ("Raspberry Pi 4 Starter Kit",
     "4GB RAM model with official case, 32GB SD card preloaded with Raspberry Pi OS, power supply included.",
     "Electronics", "new", 95.0, "sell",
     None, ["raspberry-pi", "linux", "diy", "programming", "sbc"], False),

    ("NVIDIA RTX 3070 GPU",
     "Pulled from a gaming rig upgrade. 8GB GDDR6, runs cool and quiet. No box but includes all original accessories.",
     "Electronics", "good", 380.0, "trade",
     "RTX 4060 Ti or gaming laptop with RTX 40 series.",
     ["gpu", "nvidia", "gaming", "rtx", "graphics"], True),

    ("DJI Mini 3 Pro Drone",
     "Fly More Combo with 3 batteries. Under 50 flight hours. Includes RC-N1 controller and carrying bag.",
     "Electronics", "like_new", 680.0, "trade",
     "Camera gear, lenses, or studio lighting.",
     ["drone", "dji", "photography", "aerial", "camera"], True),

    ("Vintage iPod Classic 160GB",
     "Black, 7th gen. Flash-modded with 256GB SSD — no spinning drive. Works perfectly, custom leather case.",
     "Electronics", "good", 220.0, "sell",
     None, ["ipod", "apple", "music", "vintage", "mp3"], False),

    ("Mechanical Keyboard – Keychron Q1",
     "Full aluminum body, Gateron G Pro Brown switches. Custom keycaps (GMK Nord). Hot-swappable PCB.",
     "Electronics", "like_new", 180.0, "trade",
     "Anything interesting — surprise me!",
     ["keyboard", "mechanical", "keychron", "typing", "gaming"], False),

    ("Sony A7III Mirrorless Camera",
     "24MP full-frame. ~15k shutter count. Comes with 28-70mm kit lens, two batteries, charger, and camera bag.",
     "Electronics", "good", 1200.0, "trade",
     "Medium format camera or high-end audio equipment.",
     ["sony", "camera", "mirrorless", "photography", "fullframe"], True),

    # --- Clothing & Fashion ---
    ("Vintage Levi's 501 Jeans – W32 L32",
     "Authentic 1990s Levi's with great fading and character. Minor wear at knees but structurally perfect.",
     "Clothing & Fashion", "good", 85.0, "trade",
     "Other vintage denim or 90s streetwear.",
     ["levis", "vintage", "denim", "jeans", "90s"], False),

    ("Supreme Box Logo Hoodie – Size L",
     "FW20 Black/White. Authentic — receipt available. Worn twice, flawless.",
     "Clothing & Fashion", "like_new", 450.0, "trade",
     "Arc'teryx jacket, Patagonia, or designer sneakers.",
     ["supreme", "hoodie", "streetwear", "hype", "fw20"], True),

    ("Nike Air Jordan 1 Retro High OG – Size 10",
     "Bred Toe colourway. Worn 3 times. Original box and laces included.",
     "Clothing & Fashion", "like_new", 280.0, "trade",
     "Yeezy 350s, New Balance 992/993, or trade value.",
     ["jordan", "nike", "sneakers", "bred", "basketball"], True),

    ("Patagonia Down Sweater Jacket – M",
     "Classic navy. Excellent insulation, no tears. Stuff sack included.",
     "Clothing & Fashion", "good", 140.0, "trade",
     "Outdoor gear, hiking boots, or climbing equipment.",
     ["patagonia", "jacket", "down", "outdoor", "warm"], False),

    ("Vintage Band Tees Bundle (5 shirts)",
     "Mix of 80s/90s originals: Metallica, Nirvana, Pink Floyd, Radiohead, RHCP. All XL or L.",
     "Clothing & Fashion", "fair", 200.0, "trade",
     "Other vintage tees or vinyl records.",
     ["vintage", "band-tee", "music", "90s", "tshirt"], False),

    ("Comme des Garçons PLAY Cardigan",
     "Heart logo, black, size M. Purchased at CDG store Tokyo. Barely worn.",
     "Clothing & Fashion", "like_new", 320.0, "sell",
     None, ["cdg", "comme-des-garcons", "designer", "cardigan", "japanese"], False),

    # --- Books & Media ---
    ("First Edition 'Dune' by Frank Herbert",
     "1965 Chilton Books first edition, first printing. Spine intact, boards solid. Minor foxing on interior pages.",
     "Books & Media", "fair", 800.0, "trade",
     "Other rare sci-fi first editions or vintage vinyl.",
     ["dune", "frankherbert", "scifi", "firstedition", "rare"], True),

    ("Vinyl Record Collection (50+ albums)",
     "Curated mix: jazz, rock, soul, classic. Artists include Miles Davis, Led Zeppelin, Marvin Gaye, Fleetwood Mac.",
     "Books & Media", "good", 350.0, "trade",
     "High-end turntable, camera equipment, or watches.",
     ["vinyl", "records", "music", "jazz", "rock"], True),

    ("Complete 'Wheel of Time' Hardcover Set",
     "All 14 volumes plus prequel. Minor shelf wear. Brandon Sanderson finale volumes are signed.",
     "Books & Media", "good", 180.0, "trade",
     "Other fantasy/sci-fi hardcovers or board games.",
     ["fantasy", "books", "wheeloftime", "hardcover", "signed"], False),

    ("PlayStation 5 Game Bundle (12 games)",
     "All physical discs: God of War Ragnarök, Spider-Man 2, Elden Ring, FF XVI, and more. All in cases.",
     "Books & Media", "good", 280.0, "trade",
     "Xbox Series X games or Switch titles.",
     ["ps5", "games", "playstation", "gaming", "bundle"], False),

    ("Original Nintendo Game Boy + 20 Games",
     "DMG-01 fully recapped and new screen lens. Games include Tetris, Link's Awakening, Pokémon Red/Blue.",
     "Books & Media", "good", 160.0, "trade",
     "Other retro consoles or vintage electronics.",
     ["gameboy", "nintendo", "retro", "gaming", "portable"], False),

    # --- Tools & Hardware ---
    ("DeWalt 20V MAX Drill + Impact Combo",
     "DCK240C2 kit. Both tools, 2 batteries (2Ah), charger, and contractor bag. Less than 10 hours use.",
     "Tools & Hardware", "like_new", 220.0, "trade",
     "Other power tools or workshop equipment.",
     ["dewalt", "drill", "impact", "cordless", "powertools"], True),

    ("Festool TS 55 Track Saw",
     "Professional track saw with 1.4m guide rail and parallel guides. Dust extractor fitting included.",
     "Tools & Hardware", "good", 480.0, "trade",
     "Festool router, sander, or domino joiner.",
     ["festool", "tracksaw", "woodworking", "professional", "saw"], False),

    ("Vintage Stanley Plane Collection",
     "5 hand planes: #4, #5, #6, #7, #78 rabbet. All restored, tuned, and sharp. Ready to use.",
     "Tools & Hardware", "good", 240.0, "trade",
     "Other vintage hand tools or woodworking books.",
     ["stanley", "planes", "handtools", "woodworking", "vintage"], False),

    ("Milwaukee M18 FUEL Circular Saw",
     "M18 FCSS-0 (bare tool). Used on 2 projects, blade included. Compatible with all M18 batteries.",
     "Tools & Hardware", "like_new", 180.0, "trade",
     "Milwaukee M18 grinder, router, or jigsaw.",
     ["milwaukee", "circular-saw", "m18", "cordless", "woodworking"], False),

    ("3D Printer – Bambu Lab P1P",
     "250mm/s print speed. 0.2mm nozzle, textured PEI plate. ~40 hours print time. Great condition.",
     "Tools & Hardware", "good", 560.0, "trade",
     "Laser cutter, CNC router, or resin printer.",
     ["3dprinter", "bambu", "maker", "printing", "fablab"], True),

    # --- Sports & Outdoors ---
    ("Trek Marlin 7 Mountain Bike – 29\" L",
     "2022 model, RockShox fork, hydraulic disc brakes. Tubeless setup done. Minor trail scratches.",
     "Sports & Outdoors", "good", 650.0, "trade",
     "Road bike, gravel bike, or e-bike.",
     ["trek", "mtb", "bicycle", "bike", "trail"], True),

    ("Salomon X Ultra 4 GTX Hiking Boots – M11",
     "Goretex waterproof, 2 seasons old. Excellent grip remaining. No tears or sole separation.",
     "Sports & Outdoors", "good", 135.0, "trade",
     "Trail running shoes or camping gear.",
     ["salomon", "hiking", "boots", "goretex", "outdoor"], False),

    ("Climbing Harness & Shoe Bundle",
     "Black Diamond Momentum harness (M) + La Sportiva Tarantulace shoes (EU42). Both <15 days use.",
     "Sports & Outdoors", "like_new", 140.0, "trade",
     "Cams, nuts, or other climbing hardware.",
     ["climbing", "harness", "shoes", "bouldering", "gear"], False),

    ("Surfboard – 6'2 Shortboard",
     "Channel Islands Twin Pin, 6'2 x 19.5 x 2.5. Minor dings repaired. 3-fin setup (fins included).",
     "Sports & Outdoors", "good", 380.0, "trade",
     "Longboard, wetsuit, or kayak.",
     ["surfboard", "surfing", "shortboard", "fins", "ocean"], False),

    ("Gym Equipment Bundle – Barbell + Plates",
     "7ft Olympic barbell (20kg) + 140kg bumper plate set (pairs: 5/10/15/20/25kg). Power rack NOT included.",
     "Sports & Outdoors", "good", 520.0, "trade",
     "Home gym equipment, squat rack, or adjustable dumbbells.",
     ["barbell", "gym", "weights", "lifting", "fitness"], True),

    ("Garmin Fenix 7X Sapphire Solar",
     "Titanium, Solar charging, Sapphire lens. 14 months old. Multi-sport GPS. Extra silicone band included.",
     "Sports & Outdoors", "like_new", 750.0, "trade",
     "Garmin Edge cycling computer or other premium GPS watch.",
     ["garmin", "watch", "gps", "fitness", "outdoor"], True),

    # --- Art & Collectibles ---
    ("Original Oil Painting – Abstract Cityscape",
     "24x36\" oil on canvas by Portland artist Anna Brünn. Certificate of authenticity included.",
     "Art & Collectibles", "new", 600.0, "trade",
     "Other original artwork or photography prints.",
     ["painting", "oil", "abstract", "original", "art"], True),

    ("Japanese Katana – Edo Period Reproduction",
     "High-carbon steel, hand-forged by Mino Tanren studio. Full tang, ray skin handle. Display stand included.",
     "Art & Collectibles", "new", 340.0, "sell",
     None, ["katana", "japanese", "sword", "handforged", "collector"], False),

    ("Signed Banksy 'Balloon Girl' Print",
     "Numbered 42/150. Certified by Pest Control. Framed in conservation glass. Authentication docs included.",
     "Art & Collectibles", "new", 2800.0, "trade",
     "Other authenticated street art or investment-grade collectibles.",
     ["banksy", "streetart", "print", "signed", "investment"], True),

    ("Vintage Leica M3 Film Camera",
     "1956 double stroke. CLA'd by DAG Camera in 2024. Comes with 50mm Summicron f/2 lens.",
     "Art & Collectibles", "good", 1800.0, "trade",
     "Digital Leica M or other rangefinder with lens.",
     ["leica", "film", "camera", "rangefinder", "vintage"], True),

    ("Star Wars Original Trilogy Lobby Card Set",
     "Complete set of 8 lobby cards for A New Hope (1977), Empire Strikes Back (1980), Return of the Jedi (1983).",
     "Art & Collectibles", "good", 420.0, "trade",
     "Other movie memorabilia or sci-fi collectibles.",
     ["starwars", "lobbycard", "movie", "memorabilia", "vintage"], False),

    # --- Home & Garden ---
    ("Vitamix 5200 Professional Blender",
     "Classic series, 64oz container. Refurbished by Vitamix with full 5-year warranty. Like new.",
     "Home & Garden", "like_new", 280.0, "trade",
     "Kitchen appliances, espresso machine, or instant pot.",
     ["vitamix", "blender", "kitchen", "cooking", "appliance"], False),

    ("Ember Mug² 14oz – Stainless Steel",
     "Temperature-controlled smart mug. Charging coaster included. 80-min battery. Bought last year.",
     "Home & Garden", "like_new", 110.0, "sell",
     None, ["ember", "mug", "smart", "coffee", "kitchen"], False),

    ("Dyson V15 Detect Cordless Vacuum",
     "With all attachments and wall dock. 1.5 years old. Filter cleaned, battery holds 45+ min.",
     "Home & Garden", "good", 350.0, "trade",
     "Roomba j7+ or other robot vacuum.",
     ["dyson", "vacuum", "cordless", "cleaning", "home"], True),

    ("Handmade Walnut Dining Table (6-seat)",
     "Custom crafted from solid black walnut, natural edge. 84x40\". Made by local Portland craftsman.",
     "Home & Garden", "new", 1800.0, "trade",
     "Other quality furniture or workshop tools.",
     ["table", "walnut", "handmade", "furniture", "dining"], True),

    ("Weber Genesis E-325s Gas Grill",
     "3-burner, 513 sq in cooking area. Iridescent pearl enamel. Used 2 summers, cover included.",
     "Home & Garden", "good", 480.0, "trade",
     "Pellet smoker, kamado grill, or outdoor furniture.",
     ["weber", "grill", "bbq", "outdoor", "cooking"], False),

    ("Philips Hue Smart Lighting Starter Kit",
     "Bridge + 4 A19 color bulbs + motion sensor. Works with Alexa, Google, HomeKit. Box and all accessories.",
     "Home & Garden", "like_new", 130.0, "trade",
     "Other smart home devices.",
     ["philips-hue", "smart-home", "lighting", "iot", "alexa"], False),

    # --- Toys & Games ---
    ("LEGO Technic Bugatti Chiron – 42083",
     "Complete set, fully built once and carefully stored. All 3,599 pieces present. Instructions and box.",
     "Toys & Games", "like_new", 320.0, "trade",
     "Other large LEGO Technic or Creator sets.",
     ["lego", "technic", "bugatti", "collector", "complete"], True),

    ("Twilight Imperium 4th Edition + Prophecy of Kings",
     "Both expansions included. Everything sleeved and organized. Only played 4 times.",
     "Toys & Games", "like_new", 160.0, "trade",
     "Other heavy strategy games: Gloomhaven, Arkham Horror, Dune Imperium.",
     ["boardgame", "ti4", "strategy", "4x", "scifi"], False),

    ("Nintendo Switch OLED + 15 Games",
     "White model, 64GB. Comes with: Zelda TotK/BotW, Mario Odyssey, Splatoon 3, and 11 more. Joy-Con grips.",
     "Toys & Games", "good", 430.0, "trade",
     "PlayStation 5 or Xbox Series X bundle.",
     ["nintendo", "switch", "oled", "gaming", "zelda"], True),

    ("Vintage Transformers G1 Collection",
     "13 original 1984-1987 Autobots. Complete: Optimus Prime, Jazz, Ironhide, Ratchet + 9 others. Some boxes.",
     "Toys & Games", "fair", 380.0, "trade",
     "Other vintage G1 Transformers or 80s action figures.",
     ["transformers", "g1", "vintage", "hasbro", "collectible"], False),

    ("Gloomhaven: Jaws of the Lion",
     "Standalone game, fully punched and sleeved. Played through entire campaign. All content available.",
     "Toys & Games", "good", 45.0, "trade",
     "Frosthaven, Pandemic Legacy, or Arkham Horror LCG.",
     ["gloomhaven", "boardgame", "rpg", "coop", "dungeon"], False),

    # --- Musical Instruments ---
    ("Fender American Professional II Stratocaster",
     "Ocean Turquoise, rosewood fretboard. 2021 model, OHSC. Set up professionally, plays beautifully.",
     "Art & Collectibles", "like_new", 1450.0, "trade",
     "Les Paul Standard, acoustic guitar, or studio monitors.",
     ["fender", "stratocaster", "guitar", "electric", "american"], True),

    ("Roland FP-90X Digital Piano",
     "88-key weighted PHA-50 action. Bluetooth MIDI. Comes with matching stand, pedal unit, and cover.",
     "Art & Collectibles", "like_new", 1800.0, "trade",
     "Upright acoustic piano or high-end synthesizer.",
     ["roland", "piano", "digital", "keyboard", "88key"], True),

    # --- Gifts ---
    ("Homemade Sourdough Starter Kit",
     "6-month-old live culture, premium flour blend, recipe booklet, and fermentation jar. Ready to bake!",
     "Home & Garden", "new", 0.0, "gift",
     None, ["sourdough", "bread", "baking", "fermentation", "homemade"], False),

    ("Indoor Plant Collection (5 rare aroids)",
     "Monstera deliciosa variegata, Philodendron gloriosum, Anthurium warocqueanum + 2 more. All healthy.",
     "Home & Garden", "good", 180.0, "trade",
     "Other rare aroids, orchids, or succulents.",
     ["plants", "aroids", "monstera", "philodendron", "tropical"], False),

    # --- Regions ---
    ("Handwoven Moroccan Berber Rug – 5x8",
     "Authentic azilal style from Marrakech medina. Wool on wool, hand-knotted. Age: ~15 years. Unique pattern.",
     "Home & Garden", "good", 280.0, "trade",
     "Other handmade textiles or antiques.",
     ["rug", "moroccan", "berber", "handwoven", "wool"], False),

    ("Japanese Tetsubin Cast Iron Teapot",
     "Nanbu tekki style, 1.2L capacity. Includes bamboo strainer. Pristine enamel interior, never rusted.",
     "Home & Garden", "like_new", 85.0, "sell",
     None, ["teapot", "japanese", "cast-iron", "tetsubin", "tea"], False),

    ("Colombian Coffee Sampler Box (2kg)",
     "8 x 250g micro-lot single-origin beans from Huila, Nariño, and Antioquia. All specialty grade 87+.",
     "Home & Garden", "new", 60.0, "sell",
     None, ["coffee", "specialty", "colombian", "beans", "singleorigin"], False),

    ("Swiss Made Seiko 5 Sports SRPD71 Watch",
     "Box and papers. Blue dial, stainless bracelet. Worn 10 times. Automatic movement, 100m WR.",
     "Art & Collectibles", "like_new", 250.0, "trade",
     "Other automatic watches, Citizen, Orient, or Tissot.",
     ["seiko", "watch", "automatic", "sports", "japanese"], False),

    ("Handmade Leather Bifold Wallet",
     "Full-grain vegetable-tanned leather. Made in Portland. Natural tan that will patina beautifully.",
     "Clothing & Fashion", "new", 65.0, "sell",
     None, ["leather", "wallet", "handmade", "bifold", "accessories"], False),

    ("Mountain Hardwear Trango Tent (2-person)",
     "4-season alpine tent. Used on 2 expeditions. All poles intact, seams sealed. Footprint included.",
     "Sports & Outdoors", "good", 450.0, "trade",
     "Sleeping bags, backpacks, or other expedition gear.",
     ["tent", "camping", "4season", "alpine", "outdoor"], False),

    ("Specialized Diverge Gravel Bike – 54cm",
     "2021, carbon frame, GRX 800 drivetrain. 35mm tires. Flared bars. ~2,000km. No damage.",
     "Sports & Outdoors", "good", 2400.0, "trade",
     "Mountain bike, road bike, or e-bike (partial trade ok).",
     ["specialized", "gravel", "bike", "carbon", "cycling"], True),

    ("Nikon Z6 II Mirrorless + 24-70 f/4 Lens",
     "24.5MP, dual card slots, IBIS. Shutter count: ~8,000. Includes lens hood, extra battery, and camera bag.",
     "Electronics", "good", 1650.0, "trade",
     "Sony A7 series, Fujifilm GFX, or quality glass.",
     ["nikon", "z6", "mirrorless", "camera", "photography"], True),

    ("Standing Desk – Flexispot E7 Pro (72x30)",
     "Dual motor, sits/stands 60-127cm. Bamboo top, 3-preset memory. Minor surface scratches.",
     "Home & Garden", "good", 420.0, "trade",
     "Other office furniture or monitor arms.",
     ["standing-desk", "ergonomic", "office", "flexispot", "furniture"], False),

    ("Apple Watch Ultra 2 – 49mm Titanium",
     "Midnight Ocean Band included. Less than 4 months old. AppleCare+ transferable.",
     "Electronics", "like_new", 780.0, "trade",
     "Garmin Fenix 7X or other premium sports watch.",
     ["apple-watch", "ultra", "titanium", "smartwatch", "fitness"], True),

    ("Acoustic Guitar – Martin 000-15M",
     "All-mahogany satin finish. 2020 model, OHSC. Plays in tune, excellent action. No cracks.",
     "Art & Collectibles", "good", 650.0, "trade",
     "Electric guitar, bass, or studio recording gear.",
     ["martin", "acoustic", "guitar", "000-15", "mahogany"], False),
]

def run():
    # Skip if we already have a lot of items
    from models import Item
    if Item.query.count() > 20:
        print(f"Database already has {Item.query.count()} items. Skipping seed.")
        return

    print("Creating users...")
    users = []
    pw_hash = generate_password_hash("Password123!")
    for u in USERS:
        existing = User.query.filter_by(username=u["username"]).first()
        if existing:
            users.append(existing)
            continue
        user = User(
            username=u["username"],
            email=u["email"],
            password_hash=pw_hash,
            display_name=u["display_name"],
            bio=u["bio"],
            location=u["location"],
            avatar="default_avatar.png",
            is_verified=u["is_verified"],
            trade_credits=u["trade_credits"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
        )
        db.session.add(user)
        users.append(user)
    db.session.commit()
    print(f"  {len(users)} users ready.")

    # Build category lookup
    cats = {c.name: c for c in Category.query.all()}

    print(f"Creating {len(ITEMS)} items...")
    created_items = []
    for i, (title, desc, cat_name, cond, val, ttype, lf, tags, featured) in enumerate(ITEMS):
        # Round-robin assign owners
        owner = users[i % len(users)]
        cat = cats.get(cat_name)
        created_at = datetime.utcnow() - timedelta(days=random.randint(1, 180))

        item = Item(
            title=title,
            description=desc,
            condition=cond,
            estimated_value=val,
            location=owner.location,
            is_available=True,
            is_featured=featured,
            view_count=random.randint(5, 800),
            trade_type=ttype,
            looking_for=lf,
            owner_id=owner.id,
            category_id=cat.id if cat else None,
            created_at=created_at,
        )
        db.session.add(item)
        db.session.flush()  # get item.id

        # Primary image placeholder
        img = ItemImage(item_id=item.id, filename="no_image.png", is_primary=True)
        db.session.add(img)

        # Tags
        for tag in tags:
            db.session.add(ItemTag(item_id=item.id, tag=tag))

        created_items.append(item)

    db.session.commit()
    print(f"  {len(created_items)} items created.")

    # Add a few trade offers
    print("Adding sample trade offers...")
    if len(created_items) >= 4:
        offers = [
            (users[0], users[1], created_items[0], created_items[8]),
            (users[1], users[2], created_items[9], created_items[19]),
            (users[2], users[3], created_items[19], created_items[24]),
            (users[3], users[4], created_items[28], created_items[33]),
        ]
        for sender, receiver, off_item, req_item in offers:
            if sender.id != receiver.id and off_item.owner_id == sender.id:
                offer = TradeOffer(
                    sender_id=sender.id,
                    receiver_id=receiver.id,
                    offered_item_id=off_item.id,
                    requested_item_id=req_item.id,
                    message="Hey! I'd love to trade. Let me know if you're interested.",
                    status="pending",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 14)),
                )
                db.session.add(offer)
        db.session.commit()
        print("  Sample trade offers added.")

    # Add a few reviews
    print("Adding sample reviews...")
    review_pairs = [
        (users[1], users[0], 5, "Marco is a fantastic trader — item exactly as described. Highly recommend!"),
        (users[0], users[1], 5, "Jade packaged everything perfectly. Super fast response. A+ trader."),
        (users[2], users[3], 4, "Good experience overall. Item was in great condition."),
        (users[3], users[2], 5, "Rupert is a gem. Tools were immaculate. Would trade again."),
        (users[4], users[5], 5, "Anna's artwork is stunning and she's wonderful to deal with."),
    ]
    for reviewer, reviewed, rating, comment in review_pairs:
        existing = Review.query.filter_by(reviewer_id=reviewer.id, reviewed_id=reviewed.id).first()
        if not existing:
            db.session.add(Review(
                reviewer_id=reviewer.id,
                reviewed_id=reviewed.id,
                rating=rating,
                comment=comment,
                created_at=datetime.utcnow() - timedelta(days=random.randint(3, 60)),
            ))
    db.session.commit()
    print("  Sample reviews added.")

    total_items = Item.query.count()
    total_users = User.query.count()
    print(f"\nDone! Database now has {total_users} users and {total_items} items.")


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        run()
