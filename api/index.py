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

            if link_tag and titulo_tag:
                filme_url = link_tag["href"]
                titulo = titulo_tag.get_text(strip=True)
                capa = capa_tag["src"] if capa_tag else None

                filme_page = requests.get(filme_url, headers=HEADERS, timeout=10)
                filme_soup = BeautifulSoup(filme_page.text, 'html.parser')
                iframe = filme_soup.find("iframe")
                video_link = iframe["src"] if iframe else None

                filmes.append({
                    "titulo": titulo,
                    "url": video_link,
                    "capa": capa,
                    "tmdb_link": f"https://www.themoviedb.org/search?query={titulo.replace(' ', '+')}"
                })

    except Exception as e:
        filmes.append({
            "titulo": "Erro ao buscar filmes",
            "url": None,
            "capa": None,
            "tmdb_link": "#"
        })

    return filmes

@app.route('/', methods=["GET"])
def index():
    search = request.args.get("search", None)
    filmes = get_filmes(search_term=search)
    return render_template("index.html", filmes=filmes, search=search)

@app.route('/favoritos')
def favoritos():
    # Essa página não carrega dados do servidor, só mostra a UI para gerenciar favoritos no localStorage.
    return render_template("favoritos.html")

if __name__ == '__main__':
    app.run(debug=True)





