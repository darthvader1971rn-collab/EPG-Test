import requests
from bs4 import BeautifulSoup
import datetime
import os
import time
import re
import concurrent.futures
import gzip
import xml.etree.ElementTree as ET

start_time_pomiar = time.time()

# --- KONFIGURACJA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "epg_onet_multi.xml.gz")
EXTERNAL_EPG_URL = "https://iptv.otopay.io/guide.xml"

# TUTAJ EDYTUJESZ PĘTLĘ DNI (np. 0, 1, 2, 12)
DAYS_TO_FETCH_LIST = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] 
DEEP_SCAN = True 
MAX_WORKERS = 10 
CATCHUP_DAYS_BACK = 7 # Ile dni wstecz trzymać w pliku dla CatchUp

# --- KOSZYKI NA KANAŁY (WKLEJ SWOJE LISTY) ---
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

EXTERNAL_CHANNELS = {
    "3_1880": "TVPKultura2HD.pl",
    "3_1671": "TVPuls2HD.pl",
    "3_1836": "iTVNHD.pl",
    "3_1837": "iTVNExtraHD.pl",
    "3_358": "TVRepublika.pl",
    "3_1871": "TVRepublikaHD.pl",
    "3_1999": "TVBiznesowa.pl",
    "3_891": "FoxNews.pl",
    "3_1979": "TVNKultoweSeriale.pl",
    "3_2003": "TVNMilionerzy.pl",
    "3_1982": "TVNKryminalnie.pl",
    "3_1985": "TVNTelenowele.pl",
    "3_2038": "TVNCzasNaSlub.pl",
    "3_1987": "TVNSerialeOKobietach.pl",
    "3_1992": "TVNPrawoIZycie.pl",
    "3_1980": "TVNRajskaMilosc.pl",
    "3_1981": "TVNTalkShow.pl",
    "3_2007": "TVNPoraNaShow.pl",
    "3_1983": "TVNMomentyPrawdy.pl",
    "3_1984": "TVNZycieJakWBajce.pl",
    "3_1986": "TVNSzpitalneHistorie.pl",
    "3_1988": "TVNSzkolaZycia.pl",
    "3_1989": "TVNWDomu.pl",
    "3_1991": "TVNUsterka.pl",
    "3_2001": "TVCSuper.pl",
    "3_1978": "TVNRewolucjeWKuchni.pl",
    "3_2039": "TVNKulinarnePodroze.pl",
    "3_2037": "TVNPatrol.pl",
    "3_1990": "TVNMoto.pl",
    "3_570": "FastFunBox2.pl",
    "3_985": "InUltraTVUHDPL.pl",
    "3_537": "RedCarpet.pl",
    "3_1834": "KapitanBombaTV.pl",
    "3_1835": "PorucznikKabura.pl",
    "3_518": "Paramount.pl",
    "3_510": "StopklatkaTV.pl",
    "3_1862": "FilmBoxArtHouse2.pl",
    "3_476": "PolsatCI.pl",
    "3_2026": "ViasatTrueCrime.pl",
    "3_344": "CBSReality.pl",
    "3_508": "InvestigationDiscovery.pl",
    "3_360": "NatGeo.pl",
    "3_449": "NatGeoWild.pl",
    "3_853": "LoveNature4KPL.pl",
    "3_1793": "TVPHistoria2.pl",
    "3_852": "Museum4K.pl",
    "3_2027": "CanalPlusExtra1HD.pl",
    "3_1878": "CanalPlusExtra1.pl",
    "3_2028": "CanalPlusExtra2HD.pl",
    "3_2029": "CanalPlusExtra3HD.pl",
    "3_2030": "CanalPlusExtra4HD.pl",
    "3_2040": "CanalPlusExtra5HD.pl",
    "3_2041": "CanalPlusExtra6HD.pl",
    "3_2042": "CanalPlusExtra7HD.pl",
    "3_452": "PolsatSportPrem1.pl",
    "3_417": "PolsatSportPrem2.pl",
    "3_1607": "PolsatSportPrem1v2.pl",
    "3_1608": "PolsatSportPrem2v2.pl",
    "3_1889": "CanalPlusSportCZ.pl",
    "3_385": "ExtremeSportsHD.pl",
    "3_1863": "PrimeFightHD.pl",
    "3_1663": "FightSportsHD.pl",
    "3_1000": "PPV1.pl",
    "3_1317": "PPV2.pl",
    "3_1718": "PPV3.pl",
    "3_2006": "PPV4.pl",
    "3_1875": "CanalPlusLive2.pl",
    "3_1876": "CanalPlusLive3.pl",
    "3_1877": "CanalPlusLive4.pl",
    "3_387": "CanalPlusNow.pl",
    "3_1774": "ViaplaySports1.pl",
    "3_1775": "ViaplaySports2.pl",
    "3_1806": "ViaplaySports3.pl",
    "3_1807": "ViaplaySports4.pl",
    "3_1828": "ViaplaySports5.pl",
    "3_1829": "ViaplaySports6.pl",
    "3_1830": "ViaplaySports7.pl",
    "3_1831": "ViaplaySports8.pl",
    "3_1881": "TVPABC2HD.pl",
    "3_409": "NickMusic.pl",
    "3_1857": "DuckTVPlus.pl",
    "3_2002": "SzlagierTV.pl",
    "3_580": "FirstMusicChannelHD.pl",
    "3_1866": "JazzTVHD.pl",
    "3_1833": "TVToya.pl",
    "3_1601": "KujawyTV.pl",
    "3_842": "CNNInternationalHD.pl",
    "3_744": "BBCWorldNewsEuropeHD.pl",
    "3_938": "CNBCEuropeHD.pl"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def load_existing_epg():
    """Wczytuje audycje z istniejącego pliku .gz, usuwając te starsze niż limit CatchUp."""
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
                prog_date = start_val[:8] # Format YYYYMMDD
                
                # Zachowaj tylko jeśli nowsze niż limit CatchUp
                if prog_date >= cutoff_date:
                    ch_id = prog.get('channel')
                    key = (ch_id, start_val)
                    existing_programmes[key] = prog
        print(f"[INFO] Wczytano {len(existing_programmes)} audycji z archiwum.")
    except Exception as e:
        print(f"[OSTRZEŻENIE] Nie udało się wczytać archiwum: {e}")
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
    """Pobiera dane tylko dla dni wybranych w DAYS_TO_FETCH_LIST."""
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
                
                prog_xml = f'  <programme start="{start}" channel="{m3u_id}">\n'
                prog_xml += f'    <title lang="pl">{title}</title>\n'
                if desc: prog_xml += f'    <desc lang="pl">{desc}</desc>\n'
                prog_xml += f'  </programme>\n'
                new_programmes.append(((m3u_id, start), prog_xml))
            time.sleep(0.05)
        except: pass
    print(f"Onet: {name:20} -> Pobrano {len(new_programmes)} audycji")
    return new_programmes

def get_epg_multi():
    # 1. Wczytaj stare dane (Merge)
    master_data = load_existing_epg()
    
    # 2. Pobierz nowe dane z Onetu (Multi-threading)
    print(f"[INFO] Pobieranie dni: {DAYS_TO_FETCH_LIST}...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_channel_smart, name, slug, m3u_id): name for name, (slug, m3u_id) in CHANNELS.items()}
        for future in concurrent.futures.as_completed(futures):
            results = future.result()
            for key, xml_content in results:
                master_data[key] = xml_content # Nadpisz/Dodaj nowe dane

    # 3. Złóż plik XML
    final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="AzmanGrabber Smart Merge">\n'
    for name, (_, m3u_id) in CHANNELS.items():
        final_xml += f'  <channel id="{m3u_id}"><display-name>{name}</display-name></channel>\n'
    
    # Sortowanie audycji chronologicznie
    for key in sorted(master_data.keys()):
        val = master_data[key]
        if isinstance(val, ET.Element):
            final_xml += '  ' + ET.tostring(val, encoding="unicode").strip() + '\n'
        else:
            final_xml += val

    final_xml += '</tv>'
    
    # 4. Zapis z kompresją
    with gzip.open(OUTPUT_FILE, "wt", encoding="utf-8") as f:
        f.write(final_xml)
    
    print(f"\n[INFO] Sukces! Plik {OUTPUT_FILE} gotowy. Czas: {int(time.time() - start_time_pomiar)}s")

if __name__ == "__main__":
    get_epg_multi()
