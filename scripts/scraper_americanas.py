from urllib.parse import urljoin
import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import undetected_chromedriver as uc
import random
from tqdm import tqdm

caminho_chromedriver = 'C:\\Users\\mayka\\Downloads\\chromedriver-win64\\chromedriver.exe'
service = ChromeService(executable_path=caminho_chromedriver)
chrome_options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.114 Safari/537.36'
chrome_options.add_argument(f'--user-agent={user_agent}')
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = uc.Chrome(service=service, options=chrome_options)

link = 'https://www.reclameaqui.com.br/empresa/americanas-com-loja-online/'
reclamacoes_extraidas = []
paginas_adicionais = 99

def extrair_dados_cartao(cartao_reclamacao):
    dados = {}
    base_url_reclameaqui = 'https://www.reclameaqui.com.br'
    titulo_tag = cartao_reclamacao.find('h4', attrs={'data-testid':'compain-title-link'})
    dados['titulo'] = titulo_tag.get_text(strip=True) if titulo_tag else "Título não encontrado"
    link_review_completo = "Link não encontrado"
    if titulo_tag:
        link_tag_pai = titulo_tag.find_parent('a')
        if link_tag_pai and link_tag_pai.has_attr('href'):
            ref_relativo = link_tag_pai['href']
            link_review_completo = urljoin(base_url_reclameaqui, ref_relativo)
    dados['detalhes_link'] = link_review_completo
    descricao_tag = cartao_reclamacao.find('p', class_='sc-1pe7b5t-2 eHoNfA')
    dados['descricao_curta'] = descricao_tag.get_text(strip=True) if descricao_tag else "Descrição não encontrada"
    status_tag = cartao_reclamacao.find('span', class_='sc-1pe7b5t-4 cZrVnt')
    dados['status'] = status_tag.get_text(strip=True) if status_tag else "Status não encontrado"
    dados['data'] = "Ainda não buscada"
    dados['descricao_completa'] = "Ainda não buscada"
    return dados

#print(f"Encontrados {len(lista_cards_pagina_inicial)} cartões na página inicial.")
#for cartao in lista_cards_pagina_inicial:
    dados_cartao = extrair_dados_cartao(cartao)
    reclamacoes_extraidas.append(dados_cartao)
    print(f"Título: {dados_cartao.get('titulo', 'S/T')}")
    print(f"Descrição Curta: {dados_cartao.get('descricao_curta', 'S/DC')[:70]}...")
    print(f"Status: {dados_cartao.get('status', 'S/S')}")
    print("---")

link_base_paginacao = link.strip('/') + '/lista-reclamacoes/'

for numero_pagina in range(1, paginas_adicionais + 2):
    link_paginacao_loop = f'{link_base_paginacao}?pagina={numero_pagina}'
    print(f"\n--- Acessando Página {numero_pagina}: {link_paginacao_loop} ---")
    driver.get(link_paginacao_loop)
    time.sleep(random.randint(9, 15)) 
    html_pagina_loop = driver.page_source
    soup_loop = BeautifulSoup(html_pagina_loop, 'html.parser')
    lista_cards_pagina_atual = soup_loop.find_all('div', class_="sc-1pe7b5t-0 eJgBOc")
    print(f"Encontrados {len(lista_cards_pagina_atual)} cartões na página {numero_pagina}.")
    if not lista_cards_pagina_atual:
        print(f"Nenhuma reclamação encontrada na página {numero_pagina}. Interrompendo.")
        break
    for cartao_paginas in lista_cards_pagina_atual:
        dados_paginas = extrair_dados_cartao(cartao_paginas)
        reclamacoes_extraidas.append(dados_paginas)
    time.sleep(2)

print(f"\n--- INICIANDO BUSCA POR DETALHES (DESCRIÇÃO E DATA) PARA {len(reclamacoes_extraidas)} RECLAMAÇÕES ---")
for i, uma_reclamacao_data in enumerate(tqdm(reclamacoes_extraidas, desc="Processando detalhes", unit="reclamacao")):
    link_para_visitar = uma_reclamacao_data.get('detalhes_link')
    if link_para_visitar and link_para_visitar != "Link não encontrado":
        try:
            driver.get(link_para_visitar)
            time.sleep(4)
            html_pagina_detalhe = driver.page_source
            soup_pagina_detalhe = BeautifulSoup(html_pagina_detalhe, 'html.parser')
            elemento_descricao_completa = soup_pagina_detalhe.find('p', attrs={'data-testid': 'complaint-description'})
            if elemento_descricao_completa:
                texto_completo = elemento_descricao_completa.get_text(strip=True)
                uma_reclamacao_data['descricao_completa'] = texto_completo
            else:
                uma_reclamacao_data['descricao_completa'] = "Descrição completa não encontrada (detalhe)"
            elemento_data_absoluta = soup_pagina_detalhe.find('span', attrs={'data-testid': 'complaint-creation-date'})
            if elemento_data_absoluta:
                texto_data_final = ""
                if elemento_data_absoluta.name == 'time' and elemento_data_absoluta.has_attr('datetime'):
                    texto_data_final = elemento_data_absoluta['datetime']
                elif elemento_data_absoluta.has_attr('title') and len(elemento_data_absoluta['title']) > 8:
                    texto_data_final = elemento_data_absoluta['title']
                else:
                    texto_data_final = elemento_data_absoluta.get_text(strip=True)
                uma_reclamacao_data['data'] = texto_data_final
            else:
                uma_reclamacao_data['data'] = "Data absoluta não encontrada (detalhe)"
        except Exception as e_detalhe:
            if 'descricao_completa' not in uma_reclamacao_data or uma_reclamacao_data['descricao_completa'] == "Ainda não buscada":
                uma_reclamacao_data['descricao_completa'] = "Erro ao buscar descrição"
            if 'data' not in uma_reclamacao_data or uma_reclamacao_data['data'] == "Ainda não buscada":
                uma_reclamacao_data['data'] = "Erro ao buscar data"
        time.sleep(1)
    else:
        uma_reclamacao_data['descricao_completa'] = "Link para detalhe não disponível (desc)"
        uma_reclamacao_data['data'] = "Link para detalhe não disponível (data)"

    if (i + 1) % 50 == 0:
        nome_do_arquivo_csv = 'reclamacoes_parcial.csv'
        nomes_das_colunas = ['titulo', 'status', 'descricao_curta', 'detalhes_link', 'descricao_completa', 'data']
        with open(nome_do_arquivo_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=nomes_das_colunas)
            writer.writeheader()
            writer.writerows(reclamacoes_extraidas)
        print(f"--- Progresso salvo com {i+1} registros. ---")

print("--- Busca por detalhes finalizada! ---")

if reclamacoes_extraidas:
    print(f"\n--- COLETA FINALIZADA ---")
    print(f"Total de {len(reclamacoes_extraidas)} reclamações foram processadas.")
    nome_do_arquivo_csv = 'reclamacoes_americanas_final.csv'
    print(f"\n--- Salvando dados em '{nome_do_arquivo_csv}' ---")
    nomes_das_colunas = ['titulo', 'status', 'descricao_curta', 'detalhes_link', 'descricao_completa', 'data']
    try:
        with open(nome_do_arquivo_csv, 'w', newline='', encoding='utf-8-sig') as arquivo_csv_saida:
            escritor_csv = csv.DictWriter(arquivo_csv_saida, fieldnames=nomes_das_colunas, extrasaction='ignore')
            escritor_csv.writeheader()
            for uma_reclamacao_final in reclamacoes_extraidas:
                escritor_csv.writerow(uma_reclamacao_final)
        print(f"Dados salvos com sucesso em '{nome_do_arquivo_csv}'!")
    except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo CSV: {e}")
else:
    print('\nNenhuma reclamação foi extraída no total.')

driver.quit()
print("Script finalizado.")
