from flask_cors import CORS
CORS(app)
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import requests

app = Flask(__name__)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def traducir(texto):
    try:
        return GoogleTranslator(source='auto', target='es').translate(texto)
    except:
        return texto


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


@app.route("/api", methods=["POST"])
def api():
    url = request.json["url"]
    return jsonify(scrape(url))


@app.route("/")
def home():
    return "API funcionando"


app.run()
