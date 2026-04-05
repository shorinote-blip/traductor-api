from flask import Flask, request, jsonify
from selenium import webdriver
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import time

app = Flask(__name__)

def traducir(texto):
    try:
        return GoogleTranslator(source='auto', target='es').translate(texto)
    except:
        return texto


def scrape(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(6)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    data = {
        "titulo": "",
        "imagenes": [],
        "descripcion": "",
        "info": ""
    }

    # 🔴 F95ZONE
    if "f95zone" in url:
        titulo = soup.select_one(".p-title-value")
        contenido = soup.select_one(".message-content")

        if titulo:
            data["titulo"] = traducir(titulo.text)

        if contenido:
            data["descripcion"] = traducir(contenido.get_text("\n"))

            # imágenes
            imgs = contenido.find_all("img")
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
            data["titulo"] = traducir(titulo.text)

        if contenido:
            data["descripcion"] = traducir(contenido.get_text("\n"))

            imgs = contenido.find_all("img")
            for img in imgs:
                src = img.get("src")
                if src:
                    data["imagenes"].append(src)

    return data


@app.route("/api", methods=["POST"])
def api():
    url = request.json["url"]
    resultado = scrape(url)
    return jsonify(resultado)


app.run()
