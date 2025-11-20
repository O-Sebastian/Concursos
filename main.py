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
                    },
                    "https://www.institutounivida.org.br/concursos/": {
                        "titulo": "Instituto Univida",
                        "data_texto": ""
                    },
                    "https://www.institutomais.org.br/Concursos/ConcursosAbertos": {
                        "titulo": "Instituto Mais",
                        "data_texto": ""
                    },
                    "https://www.seprev.sp.gov.br/transparencia/concurso": {
                        "titulo": "SEPREV - Indaiatuba",
                        "data_texto": ""
                    },
                    "https://www.avalia.org.br/concursos/status/inscricoes-abertas": {
                        "titulo": "Instituto Avalia",
                        "data_texto": ""
                    },
                    "https://www.cebraspe.org.br/concursos/inscricoes-abertas/": {
                        "titulo": "Centro CEBRASPE",
                        "data_texto": ""
                    },
                    "https://concursos.unioeste.br/?action=abertas": {
                        "titulo": "Universidade UNOESTE",
                        "data_texto": ""
                    },
                    "https://www.avalia.org.br/concursos/status/inscricoes-abertas": {
                        "titulo": "Instituto Avalia",
                        "data_texto": ""
                    },
                    "https://conhecimento.fgv.br/concursos": {
                        "titulo": "Fundação Getúlio Vargas - FGV",
                        "data_texto": ""
                    },
                    "https://sis.consesp.com.br/site/index.php?pg=concursos/c&t=C&c=A": {
                        "titulo": "CONSESP – Consultoria em Concursos Públicos e Pesquisas Sociais",
                        "data_texto": ""
                    },
                    "http://www.institutoindec.org.br/": {
                        "titulo": "Instituto INDEC",
                        "data_texto": ""
                    },
                    "https://novo.ibgpconcursos.com.br/inscricoes_abertas.jsp": {
                        "titulo": "IBGP - Instituto Brasileiro de Gestão e Pesquisa",
                        "data_texto": ""
                    },
                    "https://processoseletivo.igesdf.org.br/vagas": {
                        "titulo": "IGESDF - Instituto de Gestão Estratégica",
                        "data_texto": ""
                    },
                    "https://site.quadrix.org.br/": {
                        "titulo": "Instituto Quadrix",
                        "data_texto": ""
                    },
                    "https://www.shdias.com.br/concursos/": {
                        "titulo": "SHDias - Consultoria e Assessoria",
                        "data_texto": ""
                    },
                    "https://sigmaassessoria.com.br/sigma/": {
                        "titulo": "Sigma - Assessoria Administrativa",
                        "data_texto": ""
                    },
                    "https://folha.qconcursos.com/e/concursos-abertos": {
                        "titulo": "Q Concursos - Folha Dirigida",
                        "data_texto": ""
                    },
                    "https://abertos.proximosconcursos.com/": {
                        "titulo": "Próximos Concursos",
                        "data_texto": ""
                    },
                    "https://concursosnobrasil.com/concursos/": {
                        "titulo": "Concursos no Brasil",
                        "data_texto": ""
                    },
                    "https://www.institutoaocp.org.br/concursos/status/inscricoes-abertas": {
                        "titulo": "Instituto AOCP",
                        "data_texto": ""
                    },
                    "https://www.cesgranrio.org.br/concursos?id=index-205112&ucat=27": {
                        "titulo": "Instituto AOCP",
                        "data_texto": ""
                    },
                    "https://megaconcursos.com/concursos/": {
                        "titulo": "Mega Concursos",
                        "data_texto": ""
                    }
                } # 
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
                    data_texto = formatadata(ce.get_text(strip=True)) if ce else ""
                    try:
                        datetime.strptime(data_texto, "%d/%m/%Y")
                        data_valida = True
                    except:
                        data_valida = False                        
                    if uf_atual != "" and titulo != '' and data_valida and data_url !='':
                        concursos.setdefault(uf_atual, {})[data_url] = {
                            "titulo": titulo,
                            "data_texto": data_texto
                        }
                    # else:
                    #     print(f'[INFO] Não é completo: uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')

    urls = [
        "https://portal.imperioconcursos.com.br/edital/index/abertos",
        "https://portal.cmmconcursos.com.br/edital/index/abertos",
        "https://portal.fenix.selecao.site/edital/index/abertos",
        "https://portal.glconsultoria.com.br/edital/index/abertos",
        "https://portal.institutoibepp.com.br/edital/index/abertos",
        "https://portal.recrutamentobrasil.com.br/edital"
    ]
    for url in urls:
        resposta = requests.get(url)
        resposta.encoding = "utf-8"
        soup = BeautifulSoup(resposta.text, 'html.parser')
        corpo = soup.find('div', id='abertos')
        if not corpo:
            print('não tem corpo')
            continue
        for da in corpo.select('.row.align-items-center'):
            tit = da.select_one('p.text-500.text-18.mb-0')
            titulo = tit.get_text(strip=True) if tit else ""
            link = da.find("a")
            titulo_upper = titulo.upper()
            uf_atual = "NÃO CLASSIFICADOS"
            for uf in ufs:
                padrao = rf"(?<![A-Z])[/\-\(\s]*{uf}[/\-\)\s]*(?![A-Z])"
                if re.search(padrao, titulo_upper):
                    uf_atual = estados[ufs.index(uf)]
                    break
            if uf_atual not in concursos:
                concursos[uf_atual] = {}
            data_url = link.get("href") if link else ""
            data_raw = da.select_one('.text-500.text-12.mb-2').get_text(strip=True)
            m = re.findall(r'(\d{2}/\d{2}/\d{4})', data_raw)
            data_texto = formatadata(m[-1]) if m else ""
#            print(f'uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')
            try:
                datetime.strptime(data_texto, "%d/%m/%Y")
                data_valida = True
            except:
                data_valida = False                        
            if uf_atual != "" and titulo != '' and data_valida and data_url !='':
                concursos.setdefault(uf_atual, {})[data_url] = {
                    "titulo": titulo,
                    "data_texto": data_texto
                }
            # else:
            #     print(f'[INFO] Não é completo: uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')

    urls_iso = [
        "https://www.ibamsp-concursos.org.br/index/abertos/",
        "https://abcp.selecao.net.br/index/abertos/",
        "https://aplicativa.selecao.net.br/index/abertos/",
        "https://www.avancasp.org.br/index/abertos/",
        "https://funcamp.selecao.net.br/index/abertos/",
        "https://concursos.ipefae.org.br/index/abertos/",
        "https://indepac.selecao.net.br/index/abertos/"
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
            data_texto = formatadata(datas[1].get_text(strip=True)) if len(datas) > 1 else ""
#            print(f'uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')
            try:
                datetime.strptime(data_texto, "%d/%m/%Y")
                data_valida = True
            except:
                data_valida = False                        
            if uf_atual != "" and titulo != '' and data_valida and data_url !='':
                concursos.setdefault(uf_atual, {})[data_url] = {
                    "titulo": titulo,
                    "data_texto": data_texto
                }
            # else:
            #     print(f'[INFO] Não é completo: uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')

    urls_iso = [
        "https://www.concursosfau.com.br/novo/concursos/"
    ]

    for url in urls_iso:
        resposta = requests.get(url)
        resposta.encoding = "utf-8"
        soup = BeautifulSoup(resposta.text, 'html.parser')
        corpo = soup.find('div', class_='row') or soup.find('ul', class_='lista')
        if not corpo:
            print('sem corpo')
            continue
        for da in corpo.find_all(["div", "td"], class_=['col-6', 'col-2', 'box-concursos']):
            # print('tem for')
            link = da.find('h3').find("a") if da.find('h3') else da.find('a')
            if not link:
                continue
            titulo = da.get('title')
            dominio = ''
            data_texto = formatadata(da.select('div.Light')[0].get_text(strip=True)) if da.select('div.Light') else ""
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
#            print(f'uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')
            try:
                datetime.strptime(data_texto, "%d/%m/%Y")
                data_valida = True
            except:
                data_valida = False                        
            if uf_atual != "" and titulo != '' and data_valida and data_url !='':
                concursos.setdefault(uf_atual, {})[data_url] = {
                    "titulo": titulo,
                    "data_texto": data_texto
                }
            # else:
            #     print(f'[INFO] Não é completo: uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')


    urls_iso = [
         "https://www.consulpam.com.br/index.php"
    ]
    for url in urls_iso:
        resposta = requests.get(url)
        resposta.encoding = "utf-8" #"iso-8859-1"
        soup = BeautifulSoup(resposta.text, 'html.parser')
        corpo = soup.select_one('div.bloco')
        if not corpo:
            print('sem corpo')
            continue
        for da in corpo.find_all("td"):
            if not da.find('h3'):
                continue
            link = da.find('h3').find("a")
            titulo = link.get_text(strip= True)
            dominio = ''
            datas = da.select_one('div.resumoDesc').get_text(strip=True)
            m = re.findall(r"(\d{2}/\d{2}/\d{4})", datas)
            data_texto = formatadata(m[-1]) if m else ""
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
#            print(f'uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')
            try:
                datetime.strptime(data_texto, "%d/%m/%Y")
                data_valida = True
            except:
                data_valida = False                        
            if uf_atual != "" and titulo != '' and data_valida and data_url !='':
                concursos.setdefault(uf_atual, {})[data_url] = {
                    "titulo": titulo,
                    "data_texto": data_texto
                }
            # else:
            #     print(f'[INFO] Não é completo: uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')

    urls_iso = [
        "https://www.institutounicampo.com.br/"
    ]
    for url in urls_iso:
        resposta = requests.get(url)
        resposta.encoding = "utf-8" #"iso-8859-1" #
        soup = BeautifulSoup(resposta.text, 'html.parser')
        corpo = soup.find_all("div", class_="container")[2]
        if not corpo:
            continue
        for da in corpo.select("div.concurso-card"):
            if not da.find('h3'):
                continue
            link = da.find('h3').find('a')
            titulo = link.get_text(strip= True)
            dominio = ''
            titulo_upper = titulo.upper()
            uf_atual = "NÃO CLASSIFICADOS"
            for uf in ufs:
                padrao = rf"(?<![A-Z])[/\-\(\s]*{uf}[/\-\)\s]*(?![A-Z])"
                if re.search(padrao, titulo_upper):
                    uf_atual = estados[ufs.index(uf)]
                    break
            if uf_atual not in concursos:
                concursos[uf_atual] = {}
            href = link['href']
            data_url = f"{dominio}{href}" if href else ""
            datas = da.find_all("p")
            data_texto = ""
            for p in datas:
                if "Inscrições" in p.get_text():
                    datas = p.get_text(strip=True)
                    m = re.findall(r"(\d{2}/\d{2}/\d{4})", datas)
                    data_texto = formatadata(m[-1]) if m else ""
                    break
#            print(f'uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')
            try:
                datetime.strptime(data_texto, "%d/%m/%Y")
                data_valida = True
            except:
                data_valida = False                        
            if uf_atual != "" and titulo != '' and data_valida and data_url !='':
                concursos.setdefault(uf_atual, {})[data_url] = {
                    "titulo": titulo,
                    "data_texto": data_texto
                }

    urls_iso = [
        "https://www.publiconsult.com.br/"
    ]
    for url in urls_iso:
        resposta = requests.get(url)
        resposta.encoding = "utf-8" #"iso-8859-1" #
        soup = BeautifulSoup(resposta.text, 'html.parser')
        corpo = soup.find("div", id="tabs-1")
        if not corpo:
            continue
        for da in corpo.find_all("div", class_="panel panel-default"):
            link = da.find('a')
            titulo = da.find('p').get_text(strip= True)
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
            href = link['href']
            data_url = f"{dominio}{href}" if href else ""
            datas = da.find("div", class_="col-sm-10").get_text(strip=True, separator=" ")
            m = re.findall(r"(\d{2}/\d{2}/\d{4})", datas)
            data_texto = formatadata(m[-1]) if m else ""
#            print(f'uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')
            try:
                datetime.strptime(data_texto, "%d/%m/%Y")
                data_valida = True
            except:
                data_valida = False                        
            if uf_atual != "" and titulo != '' and data_valida and data_url !='':
                concursos.setdefault(uf_atual, {})[data_url] = {
                    "titulo": titulo,
                    "data_texto": data_texto
                }
            # else:
            #     print(f'[INFO] Não é completo: uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')

    urls_iso = [
        "https://www.estrategiaconcursos.com.br/blog/concursos-abertos/",
        "https://blog.grancursosonline.com.br/concursos-abertos/"
    ]
    for url in urls_iso:
        resposta = requests.get(url)
        resposta.encoding = "utf-8"
        soup = BeautifulSoup(resposta.text, 'html.parser')
        corpo = soup.find("div", class_=["content-inner", "col-12 col-3-5-l"])
        if not corpo:
            continue
        for h3 in corpo.select("h3.wp-block-heading a"):
            titulo = h3.get_text(strip=True)
            data_url = h3['href']
            uf_atual = "NÃO CLASSIFICADOS"
            titulo_upper = titulo.upper()
            for uf in ufs:
                padrao = rf"(?<![A-Z])[/\-\(\s]*{uf}[/\-\)\s]*(?![A-Z])"
                if re.search(padrao, titulo_upper):
                    uf_atual = estados[ufs.index(uf)]
                    break
            if uf_atual not in concursos:
                concursos[uf_atual] = {}
            ul = h3.find_next("ul")
            data_texto = ""
            if ul:
                for li in ul.find_all("li"):
                    texto_li = li.get_text(separator=" ", strip=True)
                    if "inscrições".upper() in texto_li.upper():
                        datas = datas = re.findall(r"(\d{1,2}/\d{1,2}(?:/\d{4})?)", texto_li)
                        if datas:
                            ultima_data = datas[-1]  # última data do período
                            if re.match(r"\d{1,2}/\d{1,2}/\d{4}", ultima_data):
                                data_texto = formatadata(ultima_data)
                            else:
                                dia, mes = map(int, ultima_data.split("/"))
                                hoje = datetime.today()
                                ano = hoje.year if mes >= hoje.month else hoje.year + 1
                                data_texto = formatadata(f"{dia:02d}/{mes:02d}/{ano}") 
                        break  # achou a data, não precisa continuar
#            print(f'uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}.')
            try:
                datetime.strptime(data_texto, "%d/%m/%Y")
                data_valida = True
            except:
                data_valida = False                        
            if uf_atual != "" and titulo != '' and data_valida and data_url !='':
                concursos.setdefault(uf_atual, {})[data_url] = {
                    "titulo": titulo,
                    "data_texto": data_texto
                }
            # else:
            #     print(f'[INFO] Não é completo: uf={uf_atual}. titulo={titulo}. link={data_url}. data={data_texto}. ultima_data={ultima_data}.')

    return concursos


def formatadata(texto):
    if not texto:
        return ""

    texto = texto.strip()

    # 1) Se já for dd/mm/aaaa → retornar direto
    if re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", texto):
        return texto

    # 2) Se for apenas dd/mm → completar o ano
    if re.match(r"^\d{2}/\d{2}$", texto):
        dia, mes = map(int, texto.split("/"))
        hoje = datetime.today()
        ano = hoje.year if mes >= hoje.month else hoje.year + 1
        return f"{dia:02d}/{mes:02d}/{ano}"

    # 3) Se for algo como "24/11 a 08/12/2025"
    datas = re.findall(r"\d{2}/\d{2}(?:/\d{4})?", texto)
    if datas:
        ultima = datas[-1]
        # Se tem ano → retorna
        if re.match(r"\d{2}/\d{2}/\d{4}", ultima):
            return ultima
        else:
            # completar o ano
            dia, mes = map(int, ultima.split("/"))
            hoje = datetime.today()
            ano = hoje.year if mes >= hoje.month else hoje.year + 1
            return f"{dia:02d}/{mes:02d}/{ano}"

    # 4) Novos padrões que forem surgindo podem ser adicionados aqui
    # exemplo: "até 14/12", "inscrições até 07/01"
    m = re.search(r"(\d{2}/\d{2})", texto)
    if m:
        ddmm = m.group(1)
        dia, mes = map(int, ddmm.split("/"))
        hoje = datetime.today()
        ano = hoje.year if mes >= hoje.month else hoje.year + 1
        return f"{dia:02d}/{mes:02d}/{ano}"

    # Nada deu certo
    return ""


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

##############
# DESCOMENTAR ESTE TRECHO - INÍCIO
    if atualizado != hoje:
        concursos_site = obter_concursos()
# DESCOMENTAR ESTE TRECHO - FIM
##############
#    concursos_site = obter_concursos() # RETIRAR ESTA LINHA


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
                        print(f"🗑️ Removendo vencido: {info['titulo']} ({uf}) da categoria {categoria}")
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