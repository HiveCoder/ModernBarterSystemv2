"""
Download real product images from Unsplash CDN into static/uploads/.
Run once: python download_images.py
"""
import os
import urllib.request

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Map filename -> Unsplash photo CDN URL
IMAGES = {
    # Electronics
    "sony_headphones.jpg":   "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=450&fit=crop&auto=format",
    "ipad_pro.jpg":          "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&h=450&fit=crop&auto=format",
    "raspberry_pi.jpg":      "https://images.unsplash.com/photo-1555680202-c86f0e12f086?w=600&h=450&fit=crop&auto=format",
    "rtx_gpu.jpg":           "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=600&h=450&fit=crop&auto=format",
    "dji_drone.jpg":         "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=600&h=450&fit=crop&auto=format",
    "ipod_classic.jpg":      "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&h=450&fit=crop&auto=format",
    "mechanical_keyboard.jpg": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&h=450&fit=crop&auto=format",
    "sony_a7iii.jpg":        "https://images.unsplash.com/photo-1516724562728-afc824a36e84?w=600&h=450&fit=crop&auto=format",
    # Clothing & Fashion
    "levis_jeans.jpg":       "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&h=450&fit=crop&auto=format",
    "supreme_hoodie.jpg":    "https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=600&h=450&fit=crop&auto=format",
    "air_jordan.jpg":        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&h=450&fit=crop&auto=format",
    "patagonia_jacket.jpg":  "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&h=450&fit=crop&auto=format",
    "band_tees.jpg":         "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&h=450&fit=crop&auto=format",
    "cdg_cardigan.jpg":      "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&h=450&fit=crop&auto=format",
    # Books & Media
    "dune_book.jpg":         "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=600&h=450&fit=crop&auto=format",
    "vinyl_records.jpg":     "https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?w=600&h=450&fit=crop&auto=format",
    "wot_books.jpg":         "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?w=600&h=450&fit=crop&auto=format",
    "ps5_games.jpg":         "https://images.unsplash.com/photo-1592890288564-76628a30a657?w=600&h=450&fit=crop&auto=format",
    "gameboy.jpg":           "https://images.unsplash.com/photo-1531525645387-7f14be1bdbbd?w=600&h=450&fit=crop&auto=format",
    # Tools & Hardware
    "dewalt_drill.jpg":      "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=600&h=450&fit=crop&auto=format",
    "festool_saw.jpg":       "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=600&h=450&fit=crop&auto=format",
    "stanley_planes.jpg":    "https://images.unsplash.com/photo-1416339184264-ba87e57ef994?w=600&h=450&fit=crop&auto=format",
    "milwaukee_saw.jpg":     "https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=600&h=450&fit=crop&auto=format",
    "bambu_printer.jpg":     "https://images.unsplash.com/photo-1631557519265-3c5a1c76be65?w=600&h=450&fit=crop&auto=format",
    # Sports & Outdoors
    "trek_mtb.jpg":          "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=450&fit=crop&auto=format",
    "salomon_boots.jpg":     "https://images.unsplash.com/photo-1542219550-37153d387c27?w=600&h=450&fit=crop&auto=format",
    "climbing_gear.jpg":     "https://images.unsplash.com/photo-1522163182402-834f871fd851?w=600&h=450&fit=crop&auto=format",
    "surfboard.jpg":         "https://images.unsplash.com/photo-1504198266287-1659872e6590?w=600&h=450&fit=crop&auto=format",
    "barbell_weights.jpg":   "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600&h=450&fit=crop&auto=format",
    "garmin_watch.jpg":      "https://images.unsplash.com/photo-1557935728-e6d1eaabe558?w=600&h=450&fit=crop&auto=format",
    # Art & Collectibles
    "oil_painting.jpg":      "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=600&h=450&fit=crop&auto=format",
    "katana.jpg":            "https://images.unsplash.com/photo-1589428236953-0cf6c5dc8c22?w=600&h=450&fit=crop&auto=format",
    "banksy_print.jpg":      "https://images.unsplash.com/photo-1561101413-c73e5e99bf5b?w=600&h=450&fit=crop&auto=format",
    "leica_m3.jpg":          "https://images.unsplash.com/photo-1606041008912-f2f4f66cd8b1?w=600&h=450&fit=crop&auto=format",
    "starwars_cards.jpg":    "https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=600&h=450&fit=crop&auto=format",
    # Home & Garden
    "vitamix_blender.jpg":   "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=600&h=450&fit=crop&auto=format",
    "ember_mug.jpg":         "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=600&h=450&fit=crop&auto=format",
    "dyson_vacuum.jpg":      "https://images.unsplash.com/photo-1558618047-fcd3c6f77ce7?w=600&h=450&fit=crop&auto=format",
    "walnut_table.jpg":      "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&h=450&fit=crop&auto=format",
    "weber_grill.jpg":       "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&h=450&fit=crop&auto=format",
    "philips_hue.jpg":       "https://images.unsplash.com/photo-1558002038-1055907df827?w=600&h=450&fit=crop&auto=format",
    # Toys & Games
    "lego_technic.jpg":      "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=600&h=450&fit=crop&auto=format",
    "twilight_imp.jpg":      "https://images.unsplash.com/photo-1611371805429-8b5c1b2c34ba?w=600&h=450&fit=crop&auto=format",
    "nintendo_switch.jpg":   "https://images.unsplash.com/photo-1586182987320-4f376d39d787?w=600&h=450&fit=crop&auto=format",
    "transformers_g1.jpg":   "https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=600&h=450&fit=crop&auto=format",
    "gloomhaven.jpg":        "https://images.unsplash.com/photo-1523875194681-bedd468c58bf?w=600&h=450&fit=crop&auto=format",
    # Musical Instruments
    "fender_strat.jpg":      "https://images.unsplash.com/photo-1510915228340-29c85a43dcfe?w=600&h=450&fit=crop&auto=format",
    "roland_piano.jpg":      "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=600&h=450&fit=crop&auto=format",
    # Home / Gifts
    "sourdough_kit.jpg":     "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&h=450&fit=crop&auto=format",
    "aroids_plants.jpg":     "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=600&h=450&fit=crop&auto=format",
    "moroccan_rug.jpg":      "https://images.unsplash.com/photo-1575301658346-c9b3f3fb33c8?w=600&h=450&fit=crop&auto=format",
    "tetsubin_teapot.jpg":   "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=600&h=450&fit=crop&auto=format",
    "coffee_beans.jpg":      "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=600&h=450&fit=crop&auto=format",
    "seiko_watch.jpg":       "https://images.unsplash.com/photo-1587925358603-c2eea5305bbc?w=600&h=450&fit=crop&auto=format",
    "leather_wallet.jpg":    "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&h=450&fit=crop&auto=format",
    "alpine_tent.jpg":       "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=600&h=450&fit=crop&auto=format",
    "gravel_bike.jpg":       "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=600&h=450&fit=crop&auto=format",
    "nikon_z6.jpg":          "https://images.unsplash.com/photo-1516035069278-37df2a1df12c?w=600&h=450&fit=crop&auto=format",
    "standing_desk.jpg":     "https://images.unsplash.com/photo-1593642632323-a8a24f4fffd5?w=600&h=450&fit=crop&auto=format",
    "apple_watch_ultra.jpg": "https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=600&h=450&fit=crop&auto=format",
    "martin_guitar.jpg":     "https://images.unsplash.com/photo-1510915228340-29c85a43dcfe?w=600&h=450&fit=crop&auto=format",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SilkTrade/1.0)"
}

print(f"Downloading {len(IMAGES)} images to {UPLOAD_DIR} ...")
ok, fail = 0, 0
for fname, url in IMAGES.items():
    dest = os.path.join(UPLOAD_DIR, fname)
    if os.path.exists(dest):
        print(f"  SKIP {fname}")
        ok += 1
        continue
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        print(f"  OK   {fname}")
        ok += 1
    except Exception as e:
        print(f"  FAIL {fname}: {e}")
        fail += 1

print(f"\nDone: {ok} downloaded, {fail} failed.")
