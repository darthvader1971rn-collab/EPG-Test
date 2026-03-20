import requests
from bs4 import BeautifulSoup
import datetime
import os
import time
import re
import concurrent.futures
import gzip
import xml.etree.ElementTree as ET
import html # NOWY IMPORT: Zabezpiecza strukturę XML przed nielegalnymi znakami

start_time_pomiar = time.time()

# --- KONFIGURACJA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "epg_onet_multi.xml.gz")
EXTERNAL_EPG_URL = "https://iptv.otopay.io/guide.xml"

# TWOJA PĘTLA DNI (Zostawiam pełną, by pierwszy start nadpisał zepsuty plik od zera)
DAYS_TO_FETCH_LIST = [0, 1, 2, 3, 12] 
DEEP_SCAN = True 
MAX_WORKERS = 10 
CATCHUP_DAYS_BACK = 7 # Ile dni wstecz trzymać w pliku dla CatchUp

# --- KOSZYKI NA KANAŁY (WKLEJ SWOJE LISTY) ---
CHANNELS = {
    "TVN24": ("tvn-24-34", "TVN24.pl"),
    "Canal+ Premium": ("canal-premium-1", "CanalPlusPremium.pl"),
    "Canal+ Sport HD": ("canal-sport-120", "CanalPlusSport.pl"),
    "Eurosport 1 HD": ("eurosport-1-65", "Eurosport1.pl"),
    "Cartoon Network HD": ("cartoon-network-79", "CartoonNetwork.pl"),
    "Extreme Sports HD": ("extreme-sports-channel-135", "ExtremeSportsHD.pl")
}
EXTERNAL_CHANNELS = {
    "3_1880": "TVPKultura2HD.pl",
    "3_1671": "TVPuls2HD.pl",
    "3_1836": "iTVNHD.pl",
    "3_1837": "iTVNExtraHD.pl",
    "3_358": "TVRepublika.pl",
    "3_1871": "TVRepublikaHD.pl",
    "3_1999": "TVBiznesowa.pl",
    "3_891": "FoxNews.pl",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def load_existing_epg():
    """Wczytuje audycje z pliku .gz, usuwając stare i ignorując błędy formatowania."""
    existing_programmes = {}
    if not os.path.exists(OUTPUT_FILE):
        return existing_programmes

    print(f"[INFO] Wczytywanie istniejącej bazy EPG dla CatchUp...")
    try:
        with gzip.open(OUTPUT_FILE, 'rb') as f:
            tree = ET.parse(f)
            root = tree.get_root()
            
            now = datetime.datetime.now()
            cutoff_date = (now - datetime.timedelta(days=CATCHUP_DAYS_BACK)).strftime("%Y%m%d")

            for prog in root.findall('programme'):
                start_val = prog.get('start')
                prog_date = start_val[:8] 
                
                if prog_date >= cutoff_date:
                    ch_id = prog.get('channel')
                    key = (ch_id, start_val)
                    existing_programmes[key] = prog
        print(f"[INFO] Wczytano {len(existing_programmes)} audycji z archiwum.")
    except Exception as e:
        print(f"[OSTRZEŻENIE] Zepsuty plik XML (invalid token). Skrypt nadpisze go czystymi danymi: {e}")
    return existing_programmes

def get_deep_details(url):
    try:
        r = requests.get(f"https://programtv.onet.pl{url}", headers=HEADERS, timeout=7)
        s = BeautifulSoup(r.text, 'lxml')
        rating, actors, directors, full_desc, age_limit = "", [], [], "", ""
        desc_tag = s.find('p', class_='entryDesc')
        if desc_tag: full_desc = desc_tag.get_text(strip=True)
        return rating, actors, directors, full_desc, age_limit
    except: return "", [], [], "", ""

def process_channel_smart(name, slug, m3u_id):
    """Pobiera dane i zabezpiecza je modułem HTML Escape."""
    new_programmes = []
    for day_off in DAYS_TO_FETCH_LIST:
        date_curr = datetime.datetime.now() + datetime.timedelta(days=day_off)
        url = f"https://programtv.onet.pl/program-tv/{slug}?dzien={day_off}&pelny-dzien=1"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, 'lxml')
            items = [li for li in soup.find_all('li') if li.find('div', class_='titles')]
            last_h, shift = -1, 0
            for item in items:
                h_tag = item.find('span', class_='hour')
                if not h_tag: continue
                t_str = h_tag.get_text(strip=True)
                h, m = map(int, t_str.split(':'))
                if h < last_h and h < 5: shift += 1
                last_h = h
                start = (date_curr + datetime.timedelta(days=shift)).strftime("%Y%m%d") + f"{h:02d}{m:02d}00 +0100"
                
                title = item.find('div', class_='titles').find('a').get_text(strip=True)
                p_url = item.find('div', class_='titles').find('a').get('href')
                desc = item.find('p').get_text(strip=True) if item.find('p') else ""
                
                if DEEP_SCAN and p_url:
                    _, acts, dirs, f_desc, age = get_deep_details(p_url)
                    if f_desc: desc = f_desc
                
                # --- KLUCZOWA ZMIANA: ZABEZPIECZENIE ZNAKÓW XML ---
                safe_title = html.escape(title)
                safe_desc = html.escape(desc)
                
                prog_xml = f'  <programme start="{start}" channel="{m3u_id}">\n'
                prog_xml += f'    <title lang="pl">{safe_title}</title>\n'
                if safe_desc: prog_xml += f'    <desc lang="pl">{safe_desc}</desc>\n'
                prog_xml += f'  </programme>\n'
                new_programmes.append(((m3u_id, start), prog_xml))
            time.sleep(0.05)
        except: pass
    print(f"Onet: {name:20} -> Pobrano {len(new_programmes)} audycji")
    return new_programmes

def get_external_epg():
    """Pobiera i filtruje dane EPG z zewnętrznego pliku XML (OtoPay)."""
    print("\n[INFO] Rozpoczynam pobieranie zewnętrznego pliku EPG (OtoPay)...")
    external_xml = ""
    try:
        r = requests.get(EXTERNAL_EPG_URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        
        dodane_kanaly = set()
        licznik_programow = 0

        # Przetwarzanie definicji kanałów
        for channel in root.findall('channel'):
            ch_id = channel.get('id')
            if ch_id in EXTERNAL_CHANNELS:
                new_id = EXTERNAL_CHANNELS[ch_id]
                display_name = channel.find('display-name')
                name_text = display_name.text if display_name is not None else new_id
                safe_name = html.escape(name_text)
                external_xml += f'  <channel id="{new_id}"><display-name>{safe_name}</display-name></channel>\n'
                dodane_kanaly.add(ch_id)

        # Przetwarzanie programów
        for programme in root.findall('programme'):
            ch_id = programme.get('channel')
            if ch_id in EXTERNAL_CHANNELS:
                new_id = EXTERNAL_CHANNELS[ch_id]
                programme.set('channel', new_id)
                prog_str = ET.tostring(programme, encoding="unicode")
                prog_str = '  ' + prog_str.replace('\n', '\n  ').strip() + '\n'
                external_xml += prog_str
                licznik_programow += 1
                
        print(f"[INFO] Sukces! Pomyślnie dodano {len(dodane_kanaly)} kanałów i {licznik_programow} audycji z zewnętrznego źródła.")
        return external_xml
    except Exception as e:
        print(f"[BŁĄD] Nie udało się pobrać lub przetworzyć zewnętrznego EPG: {e}")
        return ""

def get_epg_multi():
    # 1. Wczytaj stare dane (Merge) - jeśli zepsute, zignoruje i nadpisze
    master_data = load_existing_epg()
    
    # 2. Pobierz nowe dane z Onetu
    print(f"[INFO] Pobieranie dni z zabezpieczeniem XML: {DAYS_TO_FETCH_LIST}...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_channel_smart, name, slug, m3u_id): name for name, (slug, m3u_id) in CHANNELS.items()}
        for future in concurrent.futures.as_completed(futures):
            results = future.result()
            for key, xml_content in results:
                master_data[key] = xml_content 

    # 3. Złóż plik XML
    final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="AzmanGrabber Smart Merge v4">\n'
    
    # Kanały Onet
    for name, (_, m3u_id) in CHANNELS.items():
        safe_channel_name = html.escape(name)
        final_xml += f'  <channel id="{m3u_id}"><display-name>{safe_channel_name}</display-name></channel>\n'

    # Programy Onet
    for key in sorted(master_data.keys()):
        val = master_data[key]
        if isinstance(val, ET.Element):
            final_xml += '  ' + ET.tostring(val, encoding="unicode").strip() + '\n'
        else:
            final_xml += val

    # 4. Doklej dane z OtoPay
    final_xml += get_external_epg()

    final_xml += '</tv>'
    
    # 5. Zapis z kompresją GZIP
    with gzip.open(OUTPUT_FILE, "wt", encoding="utf-8") as f:
        f.write(final_xml)
    
    print(f"\n[INFO] Sukces! Plik {OUTPUT_FILE} gotowy. Czas: {int(time.time() - start_time_pomiar)}s")

if __name__ == "__main__":
    get_epg_multi()
