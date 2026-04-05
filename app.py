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

# 💾 CACHE (memoria)
cache = {}

# 🌐 traducir (rápido)
def traducir(texto):
    try:
        return GoogleTranslator(source='auto', target='es').translate(texto)
    except:
        return texto

# 🧠 traducir SOLO lo necesario
def traducir_ligero(texto):
    lineas = texto.split("\n")
    resultado = []

    for linea in lineas[:40]:  # 🔥 LIMITE CLAVE
        if linea.strip():
            resultado.append(traducir(linea.strip()))

    return "\n".join(resultado)

# 🚀 SCRAPER OPTIMIZADO
def scrape(url):

    # 🔥 CACHE (si ya existe, regresa rápido)
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
            data["descripcion"] = traducir_ligero(texto)

            imgs = contenido.find_all("img")[:15]  # 🔥 límite imágenes
            for img in imgs:
                src = img.get("src")
                if src:
                    if src.startswith("/"):
                        src = "https://f95zone.to" + src
                    data["imagenes"].append(src)

    # 🔵 LEWD.NINJA
    elif "lewd.ninja" in url:
        titulo = soup.find("h1")
        contenido = soup.select_one(".entry-content")

        if titulo:
            data["titulo"] = traducir(titulo.text.strip())

        if contenido:
            texto = contenido.get_text("\n")
            data["descripcion"] = traducir_ligero(texto)

            imgs = contenido.find_all("img")[:15]
            for img in imgs:
                src = img.get("src")
                if src:
                    data["imagenes"].append(src)

    # 💾 guardar en cache
    cache[url] = data

    return data


@app.route("/api", methods=["POST"])
def api():
    try:
        url = request.json.get("url")

        if not url:
            return jsonify({"error": "No URL enviada"})

        resultado = scrape(url)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/")
def home():
    return "API rápida ⚡ funcionando"


if __name__ == "__main__":
    app.run()
