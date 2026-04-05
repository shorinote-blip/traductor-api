from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

# 🔥 crear app
app = Flask(__name__)
CORS(app)

# headers para evitar bloqueos
headers = {
    "User-Agent": "Mozilla/5.0"
}

# 🌐 traducir texto
def traducir(texto):
    try:
        return GoogleTranslator(source='auto', target='es').translate(texto)
    except:
        return texto

# 🧠 scraper
def scrape(url):
    res = requests.get(url, headers=headers)
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
            data["descripcion"] = traducir(contenido.get_text("\n"))

            for img in contenido.find_all("img"):
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
            data["descripcion"] = traducir(contenido.get_text("\n"))

            for img in contenido.find_all("img"):
                src = img.get("src")
                if src:
                    data["imagenes"].append(src)

    return data

# 🚀 API
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

# 🧪 ruta principal
@app.route("/")
def home():
    return "API funcionando 🚀"

# 🔥 IMPORTANTE para Render
if __name__ == "__main__":
    app.run()
