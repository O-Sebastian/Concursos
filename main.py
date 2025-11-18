import os
import json
import re
from datetime import datetime
from urllib.parse import urlparse
#from concursos.concursos import concursos_bp
from flask import Flask
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
#from requests_html import HTMLSession

from flask import Blueprint, render_template, abort, jsonify, request


# =====================================================
# 🔹 CONFIGURAÇÕES
# =====================================================

app = Flask(__name__)
load_dotenv()
api_key = os.environ.get("API_KEY")
debug_mode = os.environ.get("DEBUG", "False") == "True"
port = int(os.environ.get("PORT", 5000))  # Porta padrão local 5000

# registra o blueprint
#app.register_blueprint(concursos_bp)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "usuarios.json")

#concursos_bp = Blueprint(
#     'concursos',
#     __name__,
#     url_prefix='/concursos',
#     template_folder='templates',
#     static_folder='static'
# )


# =====================================================
# 🔹 FUNÇÕES DE USUÁRIO
# =====================================================

def carregar_usuarios():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        dados = json.load(f)
        return dados.get("usuarios", [])


def usuario_existe(subpath):
    return subpath in carregar_usuarios()


def caminho_json(subpath):
    return os.path.join(DATA_DIR, f"{subpath}.json")


# =====================================================
# 🔹 FUNÇÕES DE ARQUIVO JSON (USUÁRIO)
# =====================================================

def carregar_dados_usuario(subpath):
    path = caminho_json(subpath)

    if not os.path.exists(path):
        dados = {
            "novos": {
                "CONSULTA MANUAL": {
                    "https://www.concursosfcc.com.br/concursoInscricaoAberta.html": {
                        "titulo": "Fundação Carlos Chagas",
                        "data_texto": ""
                    },
                    "https://inscricoes.unesp.br/concurso/inscricao-aberta": {
                        "titulo": "Unesp - Universidade Estadual Paulista Júlio de Mesquita Filho",
                        "data_texto": ""
                    },
                    "https://www.fuvest.br/concursos/": {
                        "titulo": "FUVEST - Universidade de São Paulo (USP)",
                        "data_texto": ""
                    },
                    "https://www.vunesp.com.br/busca/concurso/inscricoes%20abertas": {
                        "titulo": "Fundação VUNESP",
                        "data_texto": ""
                    }
                }
            },
            "acompanhar": {},
            "dispensados": {},
            "ultima_atualizacao": None
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return dados

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_dados_usuario(subpath, dados):
    path = caminho_json(subpath)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def limpar_ufs_vazias(dados):
    for categoria in ["novos", "acompanhar", "dispensados"]:
        ufs_para_remover = [uf for uf, concursos_uf in dados[categoria].items() if not concursos_uf]
        for uf in ufs_para_remover:
            del dados[categoria][uf]


def contar_por_estado(dados):
    resultado = {"novos": {}, "acompanhar": {}, "dispensados": {}}
    for categoria in resultado.keys():
        for estado, concursos in dados[categoria].items():
            resultado[categoria][estado] = len(concursos)
    return resultado


# =====================================================
# 🔹 FUNÇÃO DE SCRAPING COMPLETA (TODOS OS SITES)
# =====================================================

def obter_concursos():
    ufs = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT",
           "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
           "RO", "RR", "SC", "SP", "SE", "TO"]

    estados = ['ACRE', 'ALAGOAS', 'AMAPÁ', 'AMAZONAS', 'BAHIA', 'CEARÁ',
               'DISTRITO FEDERAL', 'ESPÍRITO SANTO', 'GOIÁS', 'MARANHÃO',
               'MATO GROSSO', 'MATO GROSSO DO SUL', 'MINAS GERAIS', 'PARÁ',
               'PARAÍBA', 'PARANÁ', 'PERNAMBUCO', 'PIAUÍ', 'RIO DE JANEIRO',
               'RIO GRANDE DO NORTE', 'RIO GRANDE DO SUL', 'RONDÔNIA',
               'RORAIMA', 'SANTA CATARINA', 'SÃO PAULO', 'SERGIPE', 'TOCANTINS']

    concursos = {}

    # =============================================================
    # 1️⃣ PCI Concursos
    # =============================================================
    url = "https://www.pciconcursos.com.br/concursos/"
    resposta = requests.get(url)
    resposta.encoding = "utf-8"

    soup = BeautifulSoup(resposta.text, 'html.parser')
    corpo = soup.find('div', id='concursos')

    uf_atual = ''

    if corpo:
        for da in corpo.find_all("div", class_=["da", "na", "ea", "ua"]):

            classes = da.get('class', [])

            if 'ua' in classes:
                uf_div = da.find("div", class_="uf")
                uf_atual = uf_div.get_text(strip=True) if uf_div else "NACIONAL"

                if uf_atual not in concursos:
                    concursos[uf_atual] = {}

            else:
                for ca in da.find_all("div", class_="ca"):
                    link = ca.find("a")
                    titulo = link.get("title")
                    data_url = da.get("data-url")
                    ce = da.find("div", class_="ce")

                    data_texto = ce.get_text(strip=True) if ce else ""

                    concursos.setdefault(uf_atual, {})[data_url] = {
                        "titulo": titulo,
                        "data_texto": data_texto
                    }

    # =============================================================
    # 2️⃣ Imperio + MMC
    # =============================================================
    urls = [
        "https://portal.imperioconcursos.com.br/edital/index/abertos",
        "https://portal.cmmconcursos.com.br/edital/index/abertos"
    ]

    for url in urls:
        resposta = requests.get(url)
        resposta.encoding = "utf-8"

        soup = BeautifulSoup(resposta.text, 'html.parser')
        corpo = soup.find('div', id='abertos')

        uf_atual = "NÃO CLASSIFICADOS"

        if uf_atual not in concursos:
            concursos[uf_atual] = {}

        if corpo:
            for da in corpo.select('.row.align-items-center'):
                tit = da.select_one('p.text-500.text-18.mb-0')
                titulo = tit.get_text(strip=True) if tit else ""
                link = da.find("a")
                data_url = link.get("href") if link else ""

                data_raw = da.select_one('.text-500.text-12.mb-2').get_text(strip=True)
                m = re.search(r'(\d{2}/\d{2}/\d{4})', data_raw)
                data_texto = m.group(1) if m else ""

                concursos[uf_atual][data_url] = {
                    "titulo": titulo,
                    "data_texto": data_texto
                }

    # =============================================================
    # 3️⃣ Sites ISO-8859-1
    # =============================================================
    urls_iso = [
        "https://www.ibamsp-concursos.org.br/index/abertos/",
        "https://abcp.selecao.net.br/index/abertos/",
        "https://aplicativa.selecao.net.br/index/abertos/",
        "https://www.avancasp.org.br/index/abertos/",
        "https://funcamp.selecao.net.br/index/abertos/"
    ]

    for url in urls_iso:
        resposta = requests.get(url)
        resposta.encoding = "iso-8859-1"

        soup = BeautifulSoup(resposta.text, 'html.parser')
        corpo = soup.find('div', class_='row') or soup.find('ul', class_='lista')

        if not corpo:
            continue

        for da in corpo.find_all(["div", "td"], class_=['col-6', 'col-2']):

            link = da.find('h3').find("a") if da.find('h3') else da.find('a')
            if not link:
                continue

            titulo = link.get_text(strip=True)
            titulo_upper = titulo.upper()

            uf_atual = "NÃO CLASSIFICADOS"

            for uf in ufs:
                padrao = rf"(?<![A-Z])[/\-\(\s]*{uf}[/\-\)\s]*(?![A-Z])"
                if re.search(padrao, titulo_upper):
                    uf_atual = estados[ufs.index(uf)]
                    break

            if uf_atual not in concursos:
                concursos[uf_atual] = {}

            dominio = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
            href = link.get("href")
            data_url = f"{dominio}{href}" if href else ""

            datas = da.select("p.inscricoes-info-mobile-only b")
            data_texto = datas[1].get_text(strip=True) if len(datas) > 1 else ""

            concursos[uf_atual][data_url] = {
                "titulo": titulo,
                "data_texto": data_texto
            }

    # =============================================================
    # 4️⃣ Publiconsult
    # =============================================================
    url_pub = "http://www.publiconsult.com.br"

    resposta = requests.get(url_pub)
    resposta.encoding = "iso-8859-1"

    soup = BeautifulSoup(resposta.text, 'html.parser')
    corpo = soup.find('div', id='tabs-1')

    if corpo:
        uf_atual = "NÃO CLASSIFICADOS"

        if uf_atual not in concursos:
            concursos[uf_atual] = {}

        for da in corpo.find_all("div", class_='panel panel-default'):

            link = da.find('a')
            titulo = da.find("div", class_="panel-heading").find('p').get_text(strip=True)

            dominio = f'{urlparse(url_pub).scheme}://{urlparse(url_pub).netloc}'
            href = link.get("href") if link else ""
            data_url = f"{dominio}{href}" if href else ""

            txt = da.find("div", class_="col-sm-10 col-xs-12").get_text(" ", strip=True)
            m = re.search(r"Fim:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})", txt)
            data_texto = m.group(1) if m else ""

            concursos[uf_atual][data_url] = {
                "titulo": titulo,
                "data_texto": data_texto
            }

    return concursos


# =====================================================
# 🔹 ROTAS (Apenas 2 rotas)
# =====================================================


# MOVER ENTRE CATEGORIAS
@app.route("/<usuario>/api/mover", methods=["POST"])
def api_mover(usuario):
    dados = carregar_dados_usuario(usuario)
    payload = request.get_json()

    url = payload.get("url")
    nova_categoria = payload.get("categoria")
    uf = payload.get("uf")

    if not url or not nova_categoria or not uf:
        return jsonify({"status": "erro", "msg": "Parâmetros inválidos"}), 400

    categorias = ["novos", "acompanhar", "dispensados"]
    if nova_categoria not in categorias:
        return jsonify({"status": "erro", "msg": "Categoria inválida"}), 400

    concurso = None
    uf_antiga = None

    # Procurar e remover o concurso da categoria atual
    for cat in categorias:
        for uf_atual, concursos_uf in dados[cat].items():
            if url in concursos_uf:
                concurso = concursos_uf.pop(url)
                uf_antiga = uf_atual
                # Se a UF ficou vazia, remover
                if not concursos_uf:
                    del dados[cat][uf_atual]
                break
        if concurso:
            break

    if not concurso:
        # Se não encontrar, cria um genérico (não deveria ocorrer normalmente)
        concurso = {"titulo": "Título desconhecido", "data_texto": datetime.now().strftime("%d/%m/%Y")}

    # Adicionar à nova categoria
    dados[nova_categoria].setdefault(uf, {})[url] = concurso

    # Atualizar última atualização
    dados["ultima_atualizacao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Salvar
    salvar_dados_usuario(usuario, dados)

    return jsonify({
        "status": "ok",
        "msg": f"Concurso movido para {nova_categoria}",
        "concurso": concurso,
        "uf": uf,
        "categoria": nova_categoria
    })



# ROTA PRINCIPAL
@app.route('/<subpath>')
def concursos_usuario(subpath):

    if not usuario_existe(subpath):
        abort(404)

    dados = carregar_dados_usuario(subpath)

    hoje = datetime.now().date()

    ultima = dados.get("ultima_atualizacao")
    atualizado = None

    if ultima:
        try:
            atualizado = datetime.strptime(ultima, "%d/%m/%Y %H:%M:%S").date()
        except:
            pass

    concursos_site = None

    if atualizado != hoje:
        concursos_site = obter_concursos()

    if concursos_site:
        for uf, concursos_uf in concursos_site.items():
            for url, info in concursos_uf.items():

                if (
                    uf not in dados["novos"] or url not in dados["novos"][uf]
                ) and (
                    uf not in dados["acompanhar"] or url not in dados["acompanhar"][uf]
                ) and (
                    uf not in dados["dispensados"] or url not in dados["dispensados"][uf]
                ):
                    dados["novos"].setdefault(uf, {})[url] = info

            for categoria in ["novos", "dispensados"]:
                ufs_para_remover = []

                for uf, concursos_uf in dados[categoria].items():
                    urls_para_remover = []

                    for url, info in concursos_uf.items():

                        try:
                            data = datetime.strptime(info["data_texto"], "%d/%m/%Y").date()
                            if data < hoje:
                                urls_para_remover.append(url)
                        except:
                            pass

                    for url in urls_para_remover:
                        del concursos_uf[url]

                    if not concursos_uf:
                        ufs_para_remover.append(uf)

                for uf in ufs_para_remover:
                    del dados[categoria][uf]

        dados["ultima_atualizacao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        limpar_ufs_vazias(dados)
        salvar_dados_usuario(subpath, dados)

    totais = contar_por_estado(dados)

    return render_template(
        "concursos.jinja",
        novos=dados["novos"],
        acompanhar=dados["acompanhar"],
        dispensados=dados["dispensados"],
        ultima_atualizacao=dados["ultima_atualizacao"],
        totais_novos=totais["novos"],
        totais_acompanhar=totais["acompanhar"],
        totais_dispensados=totais["dispensados"],
        base_url = f"/{subpath}",
    )

@app.route("/health")
def health():
    return "OK", 200

if __name__ == '__main__':
    # Porta para desenvolvimento local
    port = int(os.environ.get("PORT", 5000))  # 5000 é padrão local
    # Host 0.0.0.0 permite acesso externo
    app.run(host="0.0.0.0", port=port, debug=debug_mode)