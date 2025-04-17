from flask import Flask, request, send_file, abort
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app)  # 允许所有跨域

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CARD_DIR = os.path.join(BASE_DIR, "卡牌图片")

def get_all_races():
    return [d for d in os.listdir(CARD_DIR) if os.path.isdir(os.path.join(CARD_DIR, d))]

def get_stars(race_name):
    race_path = os.path.join(CARD_DIR, race_name)
    if not os.path.exists(race_path):
        return []
    star_dirs = [d for d in os.listdir(race_path) if os.path.isdir(os.path.join(race_path, d))]
    return [f"{race_name}{star}" for star in sorted(star_dirs)] if star_dirs else None

def get_cards(race_star):
    match = re.match(r"^(.*?)(\d星)$", race_star)
    if not match:
        return []
    race, star = match.group(1), match.group(2)
    path = os.path.join(CARD_DIR, race, star)
    if not os.path.exists(path):
        return []
    return [f.split("_")[0] for f in os.listdir(path) if f.endswith(".jpg") and "_" in f]

def find_card_image(card_name):
    for race in os.listdir(CARD_DIR):
        race_path = os.path.join(CARD_DIR, race)
        if not os.path.isdir(race_path):
            continue
        for file in os.listdir(race_path):
            if file.startswith(card_name + "_") and file.endswith(".jpg"):
                return os.path.join(race_path, file)
        for star in os.listdir(race_path):
            star_path = os.path.join(race_path, star)
            if not os.path.isdir(star_path):
                continue
            for file in os.listdir(star_path):
                if file.startswith(card_name + "_") and file.endswith(".jpg"):
                    return os.path.join(star_path, file)
    return None

@app.route("/api", methods=["GET"])
def card_api():
    race_param = request.args.get("race")
    card_param = request.args.get("card")

    if card_param:
        img_path = find_card_image(card_param)
        if img_path:
            return send_file(img_path, mimetype="image/jpeg")
        return "❌ 未找到该卡牌图片", 404, {'Content-Type': 'text/plain; charset=utf-8'}

    if race_param:
        races = get_all_races()
        if race_param in races:
            stars = get_stars(race_param)
            if stars:
                return "\n".join(stars), 200, {'Content-Type': 'text/plain; charset=utf-8'}
            path = os.path.join(CARD_DIR, race_param)
            files = [f.split("_")[0] for f in os.listdir(path) if f.endswith(".jpg")]
            return "\n".join(files), 200, {'Content-Type': 'text/plain; charset=utf-8'}
        cards = get_cards(race_param)
        if cards:
            return "\n".join(cards), 200, {'Content-Type': 'text/plain; charset=utf-8'}
        return "❌ 未找到该种族或星级", 404, {'Content-Type': 'text/plain; charset=utf-8'}

    races = get_all_races()
    ordered = []
    if '龙' in races: ordered.append('龙')
    middle = sorted([r for r in races if r not in ('龙','装备','角色','咒术牌')])
    ordered += middle
    for special in ('装备','角色','咒术牌'):
        if special in races:
            ordered.append(special)
    return "\n".join(ordered), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    # 用 Render 提供的 PORT 环境变量，如果不存在则退回 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
