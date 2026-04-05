from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)

headers = {
    "User-Agent": "Mozilla/5.0"
}

# 💾 cache
cache = {}

def traducir(texto):
    try:
        return GoogleTranslator(source='auto', target='es').translate(texto)
    except:
        return texto


def scrape(url):

    if url in cache:
        return cache[url]

    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    data = {
        "titulo": "",
        "imagenes": [],
        "descripcion": ""
    }

    # 🔴 F95ZONE
    if "f95zone" in url:
        titulo = soup.select_one(".p-title-value")
        contenido = soup.select_one(".message-content")

        if titulo:
            data["titulo"] = traducir(titulo.text.strip())

        if contenido:
            texto = contenido.get_text("\n")
            data["descripcion"] = texto[:3000]  # ⚡ SIN traducir

            imgs = contenido.find_all("img")[:15]
            for img in imgs:
                src = img.get("src")
                if src:
                    if src.startswith("/"):
                        src = "https://f95zone.to" + src
                    data["imagenes"].append(src)

    # 🔵 LEWD.NINJA
    elif "lewd.ninja" in url:
        titulo = soup.find("h1")
        contenido = (
            soup.select_one(".entry-content") or
            soup.select_one(".content") or
            soup.select_one("article")
        )

        if titulo:
            data["titulo"] = traducir(titulo.text.strip())

        if contenido:
            texto = contenido.get_text("\n")
            data["descripcion"] = texto[:3000]

            imgs = soup.find_all("img")[:20]
            for img in imgs:
                src = img.get("src")
                if src:
                    data["imagenes"].append(src)

    cache[url] = data
    return data


@app.route("/api", methods=["POST"])
def api():
    try:
        url = request.json.get("url")
        return jsonify(scrape(url))
    except Exception as e:
        return jsonify({"error": str(e)})


# 🔥 TRADUCCIÓN EN BACKGROUND
@app.route("/traducir", methods=["POST"])
def traducir_api():
    try:
        texto = request.json.get("texto")

        lineas = texto.split("\n")
        traducido = []

        for linea in lineas[:40]:
            if linea.strip():
                traducido.append(traducir(linea))

        return jsonify({
            "traducido": "\n".join(traducido)
        })

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/")
def home():
    return "API rápida ⚡ funcionando"


if __name__ == "__main__":
    app.run()
