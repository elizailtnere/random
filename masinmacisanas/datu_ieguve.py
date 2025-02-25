import requests
import os
from bs4 import BeautifulSoup as bs
import csv
import time
import re

URL = "https://www.ss.lv/lv/transport/cars/today-5/sell/"
DATI = "masinmacisanas/datii/"
LAPAS = "masinmacisanas/lapas/"


def saglaba_lapu(url, nosaukums):
    iegutais = requests.get(url)
    print(iegutais.status_code)
    if iegutais.status_code == 200:
        with open(nosaukums, "w", encoding="utf-8") as f:
            f.write(iegutais.text)
    return


def saglaba_visas_lapas(skaits):
    for i in range(1, skaits+1):
        saglaba_lapu(f"{URL}page{i}.html", f"{LAPAS}lapa{i}.html")
        time.sleep(0.5)
    return


def dabut_info(lapa):
    dati = []
    with open(lapa, "r", encoding="utf-8") as f:
        html = f.read()
    zupa = bs(html, "html.parser")
    galvenais = zupa.find(id="page_main")
    tabulas = galvenais.find_all('table')
    rindas = tabulas[2].find_all('tr')
    
    for rinda in rindas[1:]:
        lauki = rinda.find_all('td')
        if len(lauki) < 8:
            print("Dīvaina rinda")
            continue
        auto = {}
        auto['sludinajuma_saite'] = lauki[1].find('a')['href']
        auto['bilde'] = lauki[1].find('img')['src']

       
        sludinajums_url = auto['sludinajuma_saite']
        auto['marka'] = ''
        auto['gads'] = ''
        auto['dzinēja_tilpums'] = ''
        auto['dzinēja_tips'] = ''
        auto['nobraukums'] = ''
        auto['cena'] = ''

        
        iegutais = requests.get(sludinajums_url)
        if iegutais.status_code == 200:
            sludinajuma_zupa = bs(iegutais.text, "html.parser")
            info_sadaļa = sludinajuma_zupa.find_all('td', class_="fleft")

           
            for item in info_sadaļa:
                teksts = item.get_text(strip=True)

                
                if 'Marka' in teksts:
                    auto['marka'] = teksts.split(':')[-1].strip()
                if 'Gads' in teksts:
                    auto['gads'] = re.search(r'\d{4}', teksts).group() if re.search(r'\d{4}', teksts) else ''

                
                if 'Dzinējs' in teksts:
                    dzinēja_informācija = teksts.split(':')[-1].strip()
                    dzinēja_informācija_sadalīta = dzinēja_informācija.split('/')
                    if len(dzinēja_informācija_sadalīta) > 1:
                        auto['dzinēja_tilpums'] = dzinēja_informācija_sadalīta[0].strip()
                        auto['dzinēja_tips'] = dzinēja_informācija_sadalīta[1].strip()

                if 'Nobraukums' in teksts:
                    auto['nobraukums'] = re.sub(r'\D', '', teksts)  
                if 'Cena' in teksts:
                    auto['cena'] = re.sub(r'\D', '', teksts)  

        dati.append(auto)
    return dati


def saglaba_datus(dati):
    with open(DATI + "sslv.csv", "w", encoding="utf-8") as f:
        lauku_nosaukumi = ['sludinajuma_saite', 'bilde', 'marka', 'gads', 'dzinēja_tilpums', 'dzinēja_tips', 'nobraukums', 'cena']
        w = csv.DictWriter(f, fieldnames=lauku_nosaukumi)
        w.writeheader()
        for auto in dati:
            w.writerow(auto)
    return

def dabut_info_daudz(skaits):
    visi_dati = []
    for i in range(1, skaits+1):
        dati = dabut_info(f"{LAPAS}lapa{i}.html")
        visi_dati += dati
    return visi_dati

saglaba_visas_lapas(20)
info = dabut_info_daudz(20)
saglaba_datus(info)

    