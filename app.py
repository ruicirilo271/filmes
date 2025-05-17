from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get_filmes(search_term=None):
    base_url = "https://megafilmeshdz.space"
    filmes = []

    url = base_url
    if search_term:
        url = f"{base_url}/?s={search_term.replace(' ', '+')}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        for article in soup.select("article"):
            link_tag = article.find("a", href=True)
            titulo_tag = article.find("h2")
            capa_tag = article.find("img")
            desc_tag = article.find("div", class_="tmdb-overview")

            if link_tag and titulo_tag:
                filme_url = link_tag["href"]
                titulo = titulo_tag.get_text(strip=True)
                capa = capa_tag["src"] if capa_tag else None
                descricao = desc_tag.get_text(strip=True) if desc_tag else ""

                filme_page = requests.get(filme_url, headers=HEADERS, timeout=10)
                filme_soup = BeautifulSoup(filme_page.text, 'html.parser')
                iframe = filme_soup.find("iframe")
                video_link = iframe["src"] if iframe else None

                # Link direto para download (se termina com mp4 ou mkv)
                link_baixar = None
                if video_link and (video_link.endswith(".mp4") or video_link.endswith(".mkv")):
                    link_baixar = video_link

                filmes.append({
                    "titulo": titulo,
                    "url": video_link,
                    "capa": capa,
                    "descricao": descricao,
                    "download": link_baixar
                })

    except Exception as e:
        filmes.append({
            "titulo": "Erro ao buscar filmes",
            "url": None,
            "capa": None,
            "descricao": str(e),
            "download": None
        })

    return filmes


@app.route('/', methods=["GET"])
def index():
    search = request.args.get("search", None)
    filmes = get_filmes(search_term=search)
    return render_template("index.html", filmes=filmes, search=search)


if __name__ == '__main__':
    app.run(debug=True)


