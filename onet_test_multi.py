import requests
from bs4 import BeautifulSoup
import datetime
import os
import time
import re
import concurrent.futures

start_time_pomiar = time.time()

# --- KONFIGURACJA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "epg_onet_multi.xml")

DAYS_TO_FETCH = 2 
DEEP_SCAN = True 
MAX_WORKERS = 10 # Liczba jednoczesnych połączeń (10 to bezpieczne i bardzo szybkie ustawienie)

# --- LISTA KANAŁÓW ---
CHANNELS = {
    "13 Ulica": ("13-ulica-hd-509", "13Ulica.pl"),
    "2x2 HD": ("2x2-hd-613", "2x2HD.pl"),
    "360TuneBox": ("360tunebox-hd-304", "360TuneBox.pl"),
    "4Fun Dance": ("4fun-fit-dance-244", "4FunDance.pl"),
    "4Fun Kids": ("4fun-hits-283", "4FunKids.pl"),
    "4Fun TV": ("4fun-tv-269", "4FunTV.pl"),
    "AMC PL": ("mgm-hd-68", "AMCPL.pl"),
    "AXN": ("axn-hd-286", "AXN.pl"),
    "AXN Black": ("axn-black-271", "AXNBlack.pl"),
    "AXN HD": ("axn-hd-286", "AXNHD.pl"),
    "AXN Spin HD": ("axn-spin-hd-292", "AXNSpinHD.pl"),
    "AXN White": ("axn-white-272", "AXNWhite.pl"),
    "Active Family": ("active-family-hd-301", "ActiveFamily.pl"),
    "Adventure HD": ("adventure-hd-305", "AdventureHD.pl"),
    "Ale Kino+": ("ale-kino-hd-262", "AleKinoPlus.pl"),
    "Alfa TVP HD": ("alfa-tvp", "AlfaTVPHD.pl"),
    "Animal Planet HD": ("animal-planet-niem-264", "AnimalPlanetHD.pl"),
    "Antena": ("antena", "Antena.pl"),
    "Antena HD": ("antena", "AntenaHD.pl"),
    "BBC Brit": ("bbc-brit-hd-306", "BBCBrit.pl"),
    "BBC CBeebies": ("bbc-cbeebies-2", "BBCCBeebies.pl"),
    "BBC Earth": ("bbc-earth-hd-263", "BBCEarth.pl"),
    "BBC First PL": ("bbc-hd-261", "BBCFirstPL.pl"),
    "BBC Lifestyle HD": ("bbc-lifestyle-hd-542", "BBCLifestyleHD.pl"),
    "BabyTV": ("baby-tv-285", "BabyTV.pl"),
    "Biznes24": ("biznes24-hd-686", "Biznes24.pl"),
    "Bollywood HD": ("bollywood-hd-530", "BollywoodHD.pl"),
    "Canal+ 1 HD": ("canal-1-hd-299", "CanalPlus1HD.pl"),
    "Canal+ 360 HD": ("canal-family-hd-297", "CanalPlus360HD.pl"),
    "Canal+ Dokument": ("canal-discovery-hd-308", "CanalPlusDokument.pl"),
    "Canal+ Domo HD": ("domo-hd-437", "CanalPlusDomoHD.pl"),
    "Canal+ Film": ("canal-film-hd-278", "CanalPlusFilm.pl"),
    "Canal+ Kuchnia HD": ("kuchnia-hd-434", "CanalPlusKuchniaHD.pl"),
    "Canal+ Premium": ("canal-hd-288", "CanalPlusPremium.pl"),
    "Canal+ Sport 2 HD": ("canal-sport-2-hd-13", "CanalPlusSport2HD.pl"),
    "Canal+ Sport 3 HD": ("canal-sport-3-hd-676", "CanalPlusSport3HD.pl"),
    "Canal+ Sport 4 HD": ("canal-sport-4-hd-677", "CanalPlusSport4HD.pl"),
    "Canal+ Sport 5 HD": ("nsport-hd-17", "CanalPlusSport5HD.pl"),
    "Canal+ Sport HD": ("canal-sport-hd-12", "CanalPlusSportHD.pl"),
    "Cartoon Network HD": ("cartoon-network-hd-310", "CartoonNetworkHD.pl"),
    "Cartoonito HD": ("boomerang-hd-616", "CartoonitoHD.pl"),
    "Cinemax": ("cinemax-hd-57", "Cinemax.pl"),
    "Cinemax 2": ("cinemax2-hd-56", "Cinemax2.pl"),
    "Comedy Central HD": ("comedy-central-hd-60", "ComedyCentralHD.pl"),
    "DTX": ("discovery-turbo-xtra-hd-189", "DTX.pl"),
    "Da Vinci": ("da-vinci-hd-614", "DaVinci.pl"),
    "Da Vinci HD": ("da-vinci-hd-614", "DaVinciHD.pl"),
    "Disco Polo Music": ("disco-polo-music-191", "DiscoPoloMusic.pl"),
    "Discovery": ("discovery-hd-niem-450", "Discovery.pl"),
    "Discovery Historia": ("discovery-historia-54", "DiscoveryHistoria.pl"),
    "Discovery Life": ("discovery-life-hd-547", "DiscoveryLife.pl"),
    "Discovery Science": ("discovery-science-hd-52", "DiscoveryScience.pl"),
    "Disney Channel HD": ("disney-channel-hd-216", "DisneyChannelHD.pl"),
    "Disney Junior": ("disney-junior-469", "DisneyJunior.pl"),
    "Disney XD": ("disney-xd-235", "DisneyXD.pl"),
    "Dla Ciebie TV": ("dlaciebie-tv-442", "DlaCiebieTV.pl"),
    "Docubox Polska": ("docubox-hd-175", "DocuboxPolska.pl"),
    "Duck TV HD": ("ducktv-hd-151", "DuckTVHD.pl"),
    "E! Entertainment": ("e-entertainment-hd-169", "E!Entertainment.pl"),
    "Echo24": ("echo-24-687", "Echo24.pl"),
    "Eleven Sports 1 4K": ("eleven-sports-1-4k-667", "ElevenSports14K.pl"),
    "Eleven Sports 1 HD": ("eleven-hd-227", "ElevenSports1HD.pl"),
    "Eleven Sports 2 HD": ("eleven-hd-sports-228", "ElevenSports2HD.pl"),
    "Eleven Sports 3 HD": ("eleven-extra-hd-534", "ElevenSports3HD.pl"),
    "Eleven Sports 4 HD": ("eleven-sports-4-hd-611", "ElevenSports4HD.pl"),
    "English Club TV": ("english-club-tv-hd-181", "EnglishClubTV.pl"),
    "Epic Drama HD": ("epic-drama-hd-603", "EpicDramaHD.pl"),
    "Eska Rock TV": ("hip-hop-tv-511", "EskaRockTV.pl"),
    "Eska TV": ("eska-tv-hd-221", "EskaTV.pl"),
    "Eska TV Extra": ("eska-tv-extra-597", "EskaTVExtra.pl"),
    "Eurosport 1 HD": ("eurosport-niem-366", "Eurosport1HD.pl"),
    "Eurosport 2 HD": ("eurosport-2-hd-120", "Eurosport2HD.pl"),
    "FX Comedy HD": ("fox-comedy-hd-405", "FXComedyHD.pl"),
    "FX HD": ("fox-hd-128", "FXHD.pl"),
    "FashionBox HD": ("fashionbox-hd-171", "FashionBoxHD.pl"),
    "Fast FunBox": ("fast-funbox-hd-104", "FastFunBox.pl"),
    "FightBox HD": ("fightbox-hd-453", "FightBoxHD.pl"),
    "FightKlub HD": ("fightklub-hd-168", "FightKlubHD.pl"),
    "FilmBox Action": ("filmbox-action-451", "FilmBoxAction.pl"),
    "FilmBox ArtHouse": ("filmbox-arthouse-hd-190", "FilmBoxArtHouse.pl"),
    "FilmBox Extra HD": ("filmbox-extra-hd-86", "FilmBoxExtraHD.pl"),
    "FilmBox Family": ("filmbox-family-103", "FilmBoxFamily.pl"),
    "FilmBox Premium": ("filmbox-premium-85", "FilmBoxPremium.pl"),
    "Filmax HD": ("filmax", "FilmaxHD.pl"),
    "Fokus TV": ("fokus-tv-hd-47", "FokusTV.pl"),
    "Food Network HD": ("polsat-food-network-hd-209", "FoodNetworkHD.pl"),
    "Gametoon HD": ("gametoon-hd-602", "GametoonHD.pl"),
    "Golf Zone": ("golf-channel-hd-554", "GolfZone.pl"),
    "HBO": ("hbo-hd-26", "HBO.pl"),
    "HBO 2": ("hbo2-hd-27", "HBO2.pl"),
    "HBO 3": ("hbo-3-hd-28", "HBO3.pl"),
    "HGTV HD": ("hgtv-hd-558", "HGTVHD.pl"),
    "History": ("history-hd-niem-458", "History.pl"),
    "History 2": ("h2-hd-205", "History2.pl"),
    "Home TV": ("tvr-hd-170", "HomeTV.pl"),
    "Home TV HD": ("tvr-hd-170", "HomeTVHD.pl"),
    "Junior Music HD": ("top-kids-jr-hd-664", "JuniorMusicHD.pl"),
    "Kino Polska HD": ("kino-polska-hd-658", "KinoPolskaHD.pl"),
    "Kino Polska Muzyka": ("kino-polska-muzyka-426", "KinoPolskaMuzyka.pl"),
    "Kino TV HD": ("kino-tv-hd-663", "KinoTVHD.pl"),
    "MTV Polska HD": ("mtv-polska-hd-557", "MTVPolskaHD.pl"),
    "Metro HD": ("metro-hd-536", "MetroHD.pl"),
    "Mezzo": ("mezzo-234", "Mezzo.pl"),
    "MiniMini+ HD": ("minimini-hd-435", "MiniMiniPlusHD.pl"),
    "Mix tape HD": ("mixtape", "MixtapeHD.pl"),
    "Motowizja HD": ("motowizja-hd-194", "MotowizjaHD.pl"),
    "Music Box Polska": ("music-box-hd-539", "MusicBoxPolska.pl"),
    "MyZen 4K PL": ("myzen-4k", "MyZen4KPL.pl"),
    "Nat Geo People": ("nat-geo-people-hd-211", "NatGeoPeople.pl"),
    "News 24": ("news24", "News24.pl"),
    "Nick Jr.": ("nick-jr-hd-662", "NickJr..pl"),
    "Nickelodeon": ("nickelodeon-42", "Nickelodeon.pl"),
    "Nicktoons HD": ("nicktoons-hd-631", "NicktoonsHD.pl"),
    "Novela TV": ("novela-tv-hd-155", "NovelaTV.pl"),
    "Novelas+ HD": ("novelas", "NovelasPlusHD.pl"),
    "Nowa TV": ("nowa-tv-hd-529", "NowaTV.pl"),
    "Nuta Gold": ("nuta-gold", "NutaGold.pl"),
    "Nuta Gold HD": ("nuta-gold", "NutaGoldHD.pl"),
    "Nuta TV": ("nuta-tv-hd-213", "NutaTV.pl"),
    "Nuta TV HD": ("nuta-tv-hd-213", "NutaTVHD.pl"),
    "Planete+": ("planete-hd-432", "PlanetePlus.pl"),
    "Polo TV": ("polo-tv-135", "PoloTV.pl"),
    "Polonia 1": ("polonia-1-328", "Polonia1.pl"),
    "Polonia 1 HD": ("polonia-1-328", "Polonia1HD.pl"),
    "Polsat 2 HD": ("polsat-2-hd-218", "Polsat2HD.pl"),
    "Polsat Café HD": ("polsat-caf-hd-219", "PolsatCaféHD.pl"),
    "Polsat Comedy Central Extra": ("comedy-central-family-hd-612", "PolsatComedyCentralExtra.pl"),
    "Polsat Doku HD": ("polsat-doku-hd-551", "PolsatDokuHD.pl"),
    "Polsat Film HD": ("polsat-film-hd-162", "PolsatFilmHD.pl"),
    "Polsat Games HD": ("polsat-games-hd-670", "PolsatGamesHD.pl"),
    "Polsat HD": ("polsat-hd-35", "PolsatHD.pl"),
    "Polsat JimJam": ("polsat-jimjam-89", "PolsatJimJam.pl"),
    "Polsat Music HD": ("muzo-tv-200", "PolsatMusicHD.pl"),
    "Polsat News": ("polsat-news-hd-229", "PolsatNews.pl"),
    "Polsat News 2": ("polsat-news-2-hd-671", "PolsatNews2.pl"),
    "Polsat News Polityka": ("polsat-news-polityka", "PolsatNewsPolityka.pl"),
    "Polsat Play HD": ("polsat-play-hd-22", "PolsatPlayHD.pl"),
    "Polsat Rodzina": ("polsat-rodzina-hd-672", "PolsatRodzina.pl"),
    "Polsat Seriale HD": ("polsat-romans-173", "PolsatSerialeHD.pl"),
    "Polsat Sport 1": ("polsat-sport-hd-96", "PolsatSport1.pl"),
    "Polsat Sport 2": ("polsat-sport-extra-hd-144", "PolsatSport2.pl"),
    "Polsat Sport 3": ("polsat-sport-news-hd-543", "PolsatSport3.pl"),
    "Polsat Sport Extra 1": ("polsat-sport-premium-3-645", "PolsatSportExtra1.pl"),
    "Polsat Sport Extra 2": ("polsat-sport-premium-4-646", "PolsatSportExtra2.pl"),
    "Polsat Sport Extra 3": ("polsat-sport-premium-5-642", "PolsatSportExtra3.pl"),
    "Polsat Sport Extra 4": ("polsat-sport-premium-6-641", "PolsatSportExtra4.pl"),
    "Polsat Sport Fight HD": ("polsat-sport-fight-521", "PolsatSportFightHD.pl"),
    "Polsat Viasat Explore HD": ("polsat-viasat-explore-hd-82", "PolsatViasatExploreHD.pl"),
    "Polsat Viasat History HD": ("polsat-viasat-history-hd-71", "PolsatViasatHistoryHD.pl"),
    "Polsat Viasat Nature HD": ("polsat-viasat-nature-413", "PolsatViasatNatureHD.pl"),
    "Power TV": ("power-tv-hd-177", "PowerTV.pl"),
    "Power TV HD": ("power-tv-hd-177", "PowerTVHD.pl"),
    "Radio 357": ("radio-357", "Radio357.pl"),
    "Radio Nowy Świat": ("radio-nowy-swiat", "RadioNowyŚwiat.pl"),
    "Romance TV": ("romance-tv-hd-139", "RomanceTV.pl"),
    "SciFi": ("sci-fi-hd-628", "SciFi.pl"),
    "Sport Klub HD": ("sportklub-hd-620", "SportKlubHD.pl"),
    "Sportowa TV": ("sportowatv", "SportowaTV.pl"),
    "Stars TV": ("stars-tv-hd-122", "StarsTV.pl"),
    "Stingray CMusic HD": ("c-music-tv-260", "StingrayCMusicHD.pl"),
    "Stopklatka": ("stopklatka-hd-186", "Stopklatka.pl"),
    "StudioMed TV HD": ("studiomed-tv-688", "StudioMedTVHD.pl"),
    "Sundance TV HD": ("sundance-channel-hd-392", "SundanceTVHD.pl"),
    "Super Polsat HD": ("super-polsat-hd-560", "SuperPolsatHD.pl"),
    "TBN Polska": ("tbn-polska-hd-621", "TBNPolska.pl"),
    "TLC HD": ("tlc-hd-163", "TLCHD.pl"),
    "TTV HD": ("ttv-33", "TTVHD.pl"),
    "TV Okazje": ("tv-okazje-hd-633", "TVOkazje.pl"),
    "TV Puls HD": ("tv-puls-hd-197", "TVPulsHD.pl"),
    "TV Regio": ("tv-regio-679", "TVRegio.pl"),
    "TV Trwam HD": ("tv-trwam-108", "TVTrwamHD.pl"),
    "TV4 HD": ("tv-4-hd-222", "TV4HD.pl"),
    "TV6 HD": ("tv-6-hd-561", "TV6HD.pl"),
    "TVC": ("ntl-radomsko-184", "TVC.pl"),
    "TVC HD": ("ntl-radomsko-184", "TVCHD.pl"),
    "TVN 7 HD": ("tvn-7-hd-142", "TVN7HD.pl"),
    "TVN Fabuła HD": ("tvn-fabula-hd-37", "TVNFabułaHD.pl"),
    "TVN HD": ("tvn-hd-98", "TVNHD.pl"),
    "TVN Style HD": ("tvn-style-hd-141", "TVNStyleHD.pl"),
    "TVN Turbo HD": ("tvn-turbo-hd-143", "TVNTurboHD.pl"),
    "TVN24": ("tvn-24-hd-158", "TVN24.pl"),
    "TVN24 BiS": ("tvn-24-biznes-i-swiat-hd-537", "TVN24BiS.pl"),
    "TVP 1 HD": ("tvp-1-hd-380", "TVP1HD.pl"),
    "TVP 2 HD": ("tvp-2-hd-145", "TVP2HD.pl"),
    "TVP 3": ("tvp-3-172", "TVP3.pl"),
    "TVP 3 Białystok": ("tvp-3-bialystok-5", "TVP3Białystok.pl"),
    "TVP 3 HD": ("tvp-3-172", "TVP3HD.pl"),
    "TVP ABC": ("tvp-abc-182", "TVPABC.pl"),
    "TVP ABC HD": ("tvp-abc-182", "TVPABCHD.pl"),
    "TVP Dokument HD": ("tvp-dokument", "TVPDokumentHD.pl"),
    "TVP HD": ("tvp-hd-101", "TVPHD.pl"),
    "TVP Historia": ("tvp-historia-74", "TVPHistoria.pl"),
    "TVP Historia HD": ("tvp-historia-74", "TVPHistoriaHD.pl"),
    "TVP Info": ("tvp-info-hd-525", "TVPInfo.pl"),
    "TVP Kobieta": ("tvp-kobieta", "TVPKobieta.pl"),
    "TVP Kultura HD": ("tvp-kultura-hd-680", "TVPKulturaHD.pl"),
    "TVP Nauka HD": ("tvp-nauka", "TVPNaukaHD.pl"),
    "TVP Polonia": ("tvp-polonia-325", "TVPPolonia.pl"),
    "TVP Rozrywka": ("tvp-rozrywka-159", "TVPRozrywka.pl"),
    "TVP Rozrywka HD": ("tvp-rozrywka-159", "TVPRozrywkaHD.pl"),
    "TVP Seriale": ("tvp-seriale-130", "TVPSeriale.pl"),
    "TVP Sport HD": ("tvp-sport-hd-39", "TVPSportHD.pl"),
    "TVP Wilno HD": ("tvp-wilno", "TVPWilnoHD.pl"),
    "TVP World": ("tvp-world", "TVPWorld.pl"),
    "TVP World HD": ("tvp-world", "TVPWorldHD.pl"),
    "TVS": ("tvs-hd-109", "TVS.pl"),
    "TVT": ("tvt-500", "TVT.pl"),
    "TeenNick": ("teennick", "TeenNick.pl"),
    "Tele 5": ("tele-5-niem-448", "Tele5.pl"),
    "Tele 5 HD": ("tele-5-niem-448", "Tele5HD.pl"),
    "Teletoon+ HD": ("teletoon-hd-438", "TeletoonPlusHD.pl"),
    "Top Kids HD": ("top-kids-hd-224", "TopKidsHD.pl"),
    "Travel Channel HD": ("travel-channel-hd-152", "TravelChannelHD.pl"),
    "Twoja TV": ("twoja-tv-514", "TwojaTV.pl"),
    "VOX Music TV": ("vox-music-tv-193", "VOXMusicTV.pl"),
    "ViDoc TV HD": ("ctv9", "ViDocTVHD.pl"),
    "WP": ("wp-hd-533", "WP.pl"),
    "WP HD": ("wp-hd-533", "WPHD.pl"),
    "Warner TV": ("tnt-hd-220", "WarnerTV.pl"),
    "Water Planet": ("water-planet-hd-156", "WaterPlanet.pl"),
    "Wydarzenia 24": ("superstacja-hd-550", "Wydarzenia24.pl"),
    "Xtreme TV": ("super-tv-690", "XtremeTV.pl"),
    "Zoom TV": ("zoom-tv-hd-527", "ZoomTV.pl"),
    "Zoom TV HD": ("zoom-tv-hd-527", "ZoomTVHD.pl"),
    "wPolsce24": ("wpolsce-pl-hd-637", "wPolsce24.pl"),
    "wPolsce24 HD": ("wpolsce-pl-hd-637", "wPolsce24HD.pl"),
    "TVP 3 Gorzów": ("tvp-3-gorzow-wielkopolski-125", "TVP3Gorzow.pl"),
    "TVP 3 Katowice": ("tvp-3-katowice-106", "TVP3Katowice.pl"),
    "TVP 3 Kielce": ("tvp-3-kielce-126", "TVP3Kielce.pl"),
    "TVP 3 Kraków": ("tvp-3-krakow-127", "TVP3Krakow.pl"),
    "TVP 3 Lublin": ("tvp-3-lublin-123", "TVP3Lublin.pl"),
    "TVP 3 Łódź": ("tvp-3-lodz-124", "TVP3Lodz.pl"),
    "TVP 3 Olsztyn": ("tvp-3-olsztyn-129", "TVP3Olsztyn.pl"),
    "TVP 3 Opole": ("tvp-3-opole-128", "TVP3Opole.pl"),
    "TVP 3 Poznań": ("tvp-3-poznan-131", "TVP3Poznan.pl"),
    "TVP 3 Rzeszów": ("tvp-3-rzeszow-132", "TVP3Rzeszow.pl"),
    "TVP 3 Szczecin": ("tvp-3-szczecin-133", "TVP3Szczecin.pl"),
    "TVP 3 Warszawa": ("tvp-3-warszawa-134", "TVP3Warszawa.pl"),
    "TVP 3 Wrocław": ("tvp-3-wroclaw-136", "TVP3Wroclaw.pl"),
    "TVP 3 Bydgoszcz": ("tvp-3-bydgoszcz-137", "TVP3Bydgoszcz.pl"),
    "TVP 3 Gdańsk": ("tvp-3-gdansk-138", "TVP3Gdansk.pl"),
    "Red Carpet TV": ("red-carpet-tv-230", "RedCarpetTV.pl"),
    "TVS": ("tvs-hd-109", "TVS.pl"),
    "Paramount": ("paramount-network-hd-247", "Paramount.pl"),
    "Polsat CI": ("crime-investigation-polsat-92", "PolsatCI.pl"),
    "Investigation Discovery": ("id-investigation-discovery-61", "InvestigationDiscovery.pl"),
    "Nat Geo": ("national-geographic-channel-hd-83", "NatGeo.pl"),
    "Nat Geo Wild": ("nat-geo-wild-hd-84", "NatGeoWild.pl"),
    "Polsat Sport Prem 1": ("polsat-sport-premium-1-639", "PolsatSportPrem1.pl"),
    "Polsat Sport Prem 2": ("polsat-sport-premium-2-640", "PolsatSportPrem2.pl"),
    "Extreme Sports HD": ("extreme-sports-channel-62", "ExtremeSportsHD.pl"),
    "CNN International HD": ("cnn-international-70", "CNNInternationalHD.pl"),
    "BBC World News Europe HD": ("bbc-news-50", "BBCWorldNewsEuropeHD.pl"),
    "CNBC Europe HD": ("cnbc-europe-51", "CNBCEuropeHD.pl"),
    "TV Toya": ("tv-toya-202", "TVToya.pl"),
    "TVP Kultura 2 HD": ("tvp-kultura-2", "TVPKultura2HD.pl"),
    "TVP Historia 2": ("tvp-historia-2", "TVPHistoria2.pl"),
    "TVP ABC 2 HD": ("tvp-abc-2", "TVPABC2HD.pl"),
    "Stopklatka TV": ("stopklatka-hd-186", "StopklatkaTV.pl"),
    "TV Puls 2 HD": ("puls-2-214", "TVPuls2HD.pl"),
    "InUltra TV UHD PL": ("inultra", "InUltraTVUHDPL.pl"),
    "Duck TV Plus": ("ducktv-hd-151", "DuckTVPlus.pl"),
    "TV Republika": ("telewizja-republika-hd-618", "TVRepublika.pl"),
    "TV Republika HD": ("telewizja-republika-hd-618", "TVRepublikaHD.pl"),
    "Museum 4K": ("museum-4k", "Museum4K.pl"),
    "Jazz TV HD": ("jazz-hd-660", "JazzTVHD.pl"),
    "Fast FunBox 2": ("fast-funbox-hd-104", "FastFunBox2.pl"),
    "FilmBox ArtHouse 2": ("filmbox-arthouse-hd-190", "FilmBoxArtHouse2.pl"),
    "Polsat Sport Prem 1 (v2)": ("polsat-sport-premium-1-639", "PolsatSportPrem1v2.pl"),
    "Polsat Sport Prem 2 (v2)": ("polsat-sport-premium-2-640", "PolsatSportPrem2v2.pl"),
}

# Zaawansowane nagłówki maskujące bota (udajemy przeglądarkę Chrome na Windowsie)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

def get_deep_details(url):
    """Pobiera opisy, aktorów, reżyserów i ograniczenia wiekowe z podstrony audycji."""
    full_url = f"https://programtv.onet.pl{url}"
    try:
        r = requests.get(full_url, headers=HEADERS, timeout=7)
        s = BeautifulSoup(r.text, 'lxml')
        rating, actors, directors, full_desc, age_limit = "", [], [], "", ""
        
        desc_tag = s.find('p', class_='entryDesc')
        if desc_tag: full_desc = desc_tag.get_text(strip=True)
        
        pegi_tag = s.find('span', class_=re.compile(r'pegi\d+'))
        if pegi_tag:
            for cls in pegi_tag.get('class', []):
                if 'pegi' in cls and cls != 'pegi':
                    age_limit = cls.replace('pegi', '')
                    break

        stars_tag = s.find('span', class_=re.compile(r'stars\d+'))
        if stars_tag:
            for cls in stars_tag.get('class', []):
                if cls.startswith('stars') and len(cls) > 5:
                    rating = f"{cls.replace('stars', '')}/5"

        cast_ul = s.find('ul', class_='cast')
        if cast_ul:
            curr = None
            for li in cast_ul.find_all('li'):
                if 'header' in li.get('class', []):
                    curr = li.get_text(strip=True).lower()
                else:
                    names = [n.strip() for n in li.get_text(separator=' ', strip=True).split(',') if n.strip()]
                    if curr and 'obsada' in curr: actors.extend(names)
                    elif curr and 'reżyseria' in curr: directors.extend(names)
        return rating, actors, directors, full_desc, age_limit
    except: return "", [], [], "", ""

def process_channel(name, slug, m3u_id):
    """Funkcja robocza dla jednego wątku - pobiera wszystkie dni dla zadanego kanału."""
    channel_xml = ""
    added = 0
    
    for day_off in range(DAYS_TO_FETCH):
        date_curr = datetime.datetime.now() + datetime.timedelta(days=day_off)
        url = f"https://programtv.onet.pl/program-tv/{slug}?dzien={day_off}&pelny-dzien=1"
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, 'lxml')
            
            # Wyszukujemy elementy listy zawierające tytuły (bardziej uniwersalne)
            items = [li for li in soup.find_all('li') if li.find('div', class_='titles')]

            last_h, shift = -1, 0
            for item in items:
                h_tag = item.find('span', class_='hour')
                if not h_tag: continue
                t_str = h_tag.get_text(strip=True)
                if not re.match(r'^\d{2}:\d{2}$', t_str): continue
                
                h, m = map(int, t_str.split(':'))
                if h < last_h and h < 5: shift += 1
                last_h = h
                
                start = (date_curr + datetime.timedelta(days=shift)).strftime("%Y%m%d") + f"{h:02d}{m:02d}00 +0100"
                
                titles_div = item.find('div', class_='titles')
                title_a = titles_div.find('a')
                if not title_a: continue
                title = title_a.get_text(strip=True)
                p_url = title_a.get('href')
                
                cat_tag = item.find('span', class_='type')
                cat = cat_tag.get_text(strip=True) if cat_tag else ""
                desc = item.find('p').get_text(strip=True) if item.find('p') else ""
                
                rate, acts, dirs, f_desc, age = "", [], [], "", ""
                if DEEP_SCAN and p_url:
                    rate, acts, dirs, f_desc, age = get_deep_details(p_url)
                    if f_desc: desc = f_desc

                channel_xml += f'  <programme start="{start}" channel="{m3u_id}">\n'
                channel_xml += f'    <title lang="pl">{title}</title>\n'
                if desc: channel_xml += f'    <desc lang="pl">{desc}</desc>\n'
                if cat: channel_xml += f'    <category lang="pl">{cat}</category>\n'
                if age: channel_xml += f'    <rating system="advisory"><value>{age}</value></rating>\n'
                if acts or dirs:
                    channel_xml += '    <credits>\n'
                    for d in dirs: channel_xml += f'      <director>{d}</director>\n'
                    for a in acts: channel_xml += f'      <actor>{a}</actor>\n'
                    channel_xml += '    </credits>\n'
                if rate: channel_xml += f'    <star-rating><value>{rate}</value></star-rating>\n'
                channel_xml += f'  </programme>\n'
                added += 1

            time.sleep(0.05) # Delikatne opóźnienie dla stabilności
        except Exception as e:
            print(f"BŁĄD dla {name} (dzień {day_off}): {e}")
            
    print(f"Zakończono: {name:20} -> Pobrano audycji: {added}")
    return channel_xml

def get_epg_multi():
    """Główna funkcja orkiestrująca wielowątkowość."""
    if not os.path.exists(os.path.dirname(OUTPUT_FILE)) and os.path.dirname(OUTPUT_FILE) != "": 
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="AzmanGrabber Onet Multi v2.0">\n'
    
    # Tworzenie nagłówków kanałów
    for name, (_, m3u_id) in CHANNELS.items():
        xml += f'  <channel id="{m3u_id}"><display-name>{name}</display-name></channel>\n'

    print(f"[INFO] Rozpoczynam pobieranie na {MAX_WORKERS} wątkach jednocześnie...")
    
    # Odpalamy silnik wielowątkowy
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_channel, name, slug, m3u_id): name for name, (slug, m3u_id) in CHANNELS.items()}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result_xml = future.result()
                xml += result_xml
            except Exception as e:
                print(f"Wystąpił krytyczny błąd w jednym z wątków: {e}")

    xml += '</tv>'
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f: 
        f.write(xml)
        
    # Podsumowanie czasu pracy
    end_time_pomiar = time.time()
    czas_trwania = end_time_pomiar - start_time_pomiar
    minuty = int(czas_trwania // 60)
    sekundy = int(czas_trwania % 60)
    print(f"\n[INFO] Zakończono sukcesem! Plik EPG: {OUTPUT_FILE}")
    print(f"[INFO] Całkowity czas pobierania wielowątkowego wyniósł: {minuty} minut i {sekundy} sekund.")

if __name__ == "__main__":
    get_epg_multi()
