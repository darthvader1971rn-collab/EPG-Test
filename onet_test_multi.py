import requests
from bs4 import BeautifulSoup
import datetime
import os
import time
import re
import concurrent.futures
import gzip
import xml.etree.ElementTree as ET
import html

start_time_pomiar = time.time()

# --- KONFIGURACJA LABORATORIUM ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "epg_onet_multi.xml.gz")

# KRÓTKA PĘTLA DLA TESTÓW (Dzisiaj i Jutro)
DAYS_TO_FETCH_LIST = [0, 1] 
DEEP_SCAN = False # Wyłączone dla maksymalnej szybkości diagnozy
MAX_WORKERS = 5
CATCHUP_DAYS_BACK = 7

# --- LISTA KONTROLNA KANAŁÓW (ZAKTUALIZOWANE LINKI ONETU) ---
CHANNELS = {
    "TVN24": ("tvn-24-hd-158", "TVN24.pl"),
    "Canal+ Premium": ("canal-hd-288", "CanalPlusPremium.pl"),
    "Canal+ Sport HD": ("canal-sport-hd-12", "CanalPlusSport.pl"),
    "Eurosport 1 HD": ("eurosport-1-hd-97", "Eurosport1.pl"),
    "Cartoon Network HD": ("cartoon-network-hd-310", "CartoonNetwork.pl"),
    "Extreme Sports HD": ("extreme-sports-channel-135", "ExtremeSportsHD.pl") # Testowy stary link
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7"
}

def clean_xml_text(text):
    """Sterylizuje tekst: usuwa niewidoczne znaki kontrolne i zabezpiecza HTML."""
    if not text:
        return ""
    # Brutalne usunięcie znaków ASCII od 0 do 31 (z wyjątkiem formatowania)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return html.escape(text)

def load_existing_epg():
    existing_programmes = {}
    if not os.path.exists(OUTPUT_FILE):
        return existing_programmes

    print(f"[INFO] Wczytywanie istniejącej bazy EPG dla CatchUp...")
    try:
        with gzip.open(OUTPUT_FILE, 'rb') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            
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
        print(f"[OSTRZEŻENIE] Zepsuty plik XML lub stary format. Tworzenie nowej bazy: {e}")
    return existing_programmes

def get_deep_details(url):
    try:
        r = requests.get(f"https://programtv.onet.pl{url}", headers=HEADERS, timeout=7)
        s = BeautifulSoup(r.text, 'lxml')
        desc_tag = s.find('p', class_='entryDesc')
        if desc_tag: return desc_tag.get_text(strip=True)
        return ""
    except: return ""

def process_channel_smart(name, slug, m3u_id):
    new_programmes = []
    for day_off in DAYS_TO_FETCH_LIST:
        date_curr = datetime.datetime.now() + datetime.timedelta(days=day_off)
        url = f"https://programtv.onet.pl/program-tv/{slug}?dzien={day_off}&pelny-dzien=1"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status() # Twardy sprawdzian - jeśli Onet odrzuci link (np. 404), wyrzuci błąd
            
            soup = BeautifulSoup(r.text, 'lxml')
            items = [li for li in soup.find_all('li') if li.find('div', class_='titles')]
            
            if not items:
                print(f"[OSTRZEŻENIE] Pusta lista audycji dla {name} - dzień {day_off}. Brak programu lub inna struktura HTML Onetu.")
            
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
                    f_desc = get_deep_details(p_url)
                    if f_desc: desc = f_desc
                
                # ZABEZPIECZENIE: Sterylizacja tekstów
                safe_title = clean_xml_text(title)
                safe_desc = clean_xml_text(desc)
                
                prog_xml = f'  <programme start="{start}" channel="{m3u_id}">\n'
                prog_xml += f'    <title lang="pl">{safe_title}</title>\n'
                if safe_desc: prog_xml += f'    <desc lang="pl">{safe_desc}</desc>\n'
                prog_xml += f'  </programme>\n'
                new_programmes.append(((m3u_id, start), prog_xml))
            time.sleep(0.05)
        except requests.exceptions.HTTPError as e:
            # Tu wyłapiemy błędne/stare linki jak 404
            print(f"[BŁĄD KRYTYCZNY] Onet zablokował dostęp (lub strona 404) dla {name} (dzień {day_off}): {e}")
        except Exception as e:
            print(f"[BŁĄD INNY] Błąd podczas pobierania {name} (dzień {day_off}): {e}")
            
    print(f"Onet: {name:20} -> Pobrano {len(new_programmes)} audycji")
    return new_programmes

def get_epg_multi():
    master_data = load_existing_epg()
    
    print(f"\n[INFO] Rozpoczynam pobieranie testowe dla dni: {DAYS_TO_FETCH_LIST}...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_channel_smart, name, slug, m3u_id): name for name, (slug, m3u_id) in CHANNELS.items()}
        for future in concurrent.futures.as_completed(futures):
            results = future.result()
            for key, xml_content in results:
                master_data[key] = xml_content 

    final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="AzmanGrabber Smart Merge v4">\n'
    
    for name, (_, m3u_id) in CHANNELS.items():
        safe_channel_name = clean_xml_text(name)
        final_xml += f'  <channel id="{m3u_id}"><display-name>{safe_channel_name}</display-name></channel>\n'

    for key in sorted(master_data.keys()):
        val = master_data[key]
        if isinstance(val, ET.Element):
            final_xml += '  ' + ET.tostring(val, encoding="unicode").strip() + '\n'
        else:
            final_xml += val

    final_xml += '</tv>'
    
    with gzip.open(OUTPUT_FILE, "wt", encoding="utf-8") as f:
        f.write(final_xml)
    
    print(f"\n[INFO] Laboratorium zakończone. Skompresowany plik EPG gotowy. Czas: {int(time.time() - start_time_pomiar)}s")

if __name__ == "__main__":
    get_epg_multi()
