import requests
from bs4 import BeautifulSoup
import datetime
import os
import time
import re
import concurrent.futures 
import html
import gzip
import io

start_time_pomiar = time.time()

# --- KONFIGURACJA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Zmieniamy rozszerzenie na .gz
OUTPUT_FILE_GZ = os.path.join(BASE_DIR, "Output", "onet_test_full.xml.gz")

# DNI DO POBRANIA (Twoja strategia: Dziś, jutro, pojutrze + dzień 12)
DAYS_TO_REFRESH = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
CATCHUP_DAYS = 7 # Jak głęboko w tył trzymamy historię

DEEP_SCAN = True 
MAX_WORKERS = 15 # Twój Hardcore Mode

CHANNELS = {
    "13 Ulica": ("13-ulica-316", "13Ulica.pl"), [cite: 35]
    "13 Ulica HD": ("13-ulica-hd-509", "13UlicaHD.pl"), [cite: 35]
    "13th Street": ("13th-street-250", "13thStreet.pl"), [cite: 35]
    "2x2": ("2x2-604", "2x2.pl"), [cite: 35]
    "2x2 HD": ("2x2-hd-613", "2x2HD.pl"), [cite: 35]
    "360TuneBox": ("360tunebox-302", "360TuneBox.pl"), [cite: 35]
    "360TuneBox HD": ("360tunebox-hd-304", "360TuneBoxHD.pl"), [cite: 35]
    "4FUN DANCE": ("4fun-fit-dance-244", "4FUNDANCE.pl"), [cite: 35]
    "4FUN KIDS": ("4fun-hits-283", "4FUNKIDS.pl"), [cite: 35]
    "4FUN.TV": ("4fun-tv-269", "4FUN.TV.pl"), [cite: 35]
    "Active Family": ("active-family-300", "ActiveFamily.pl"), [cite: 36]
    "Active Family HD": ("active-family-hd-301", "ActiveFamilyHD.pl"), [cite: 36]
    "Adventure": ("adventure-303", "Adventure.pl"), [cite: 36]
    "Adventure HD": ("adventure-hd-305", "AdventureHD.pl"), [cite: 36]
    "Ale kino+": ("ale-kino-319", "AlekinoPlus.pl"), [cite: 36]
    "Ale kino+ HD": ("ale-kino-hd-262", "AlekinoPlusHD.pl"), [cite: 36]
    "Alfa TVP": ("alfa-tvp", "AlfaTVP.pl"), [cite: 36]
    "AMC": ("mgm-333", "AMC.pl"), [cite: 36]
    "AMC HD": ("mgm-hd-68", "AMCHD.pl"), [cite: 36]
    "Animal Planet HD": ("animal-planet-hd-284", "AnimalPlanetHD.pl"), [cite: 36]
    "Animal Planet (niem.)": ("animal-planet-niem-264", "AnimalPlanet(niem.).pl"), [cite: 36]
    "Antena": ("antena", "Antena.pl"), [cite: 36]
    "AXN": ("axn-249", "AXN.pl"), [cite: 36]
    "AXN Black": ("axn-black-271", "AXNBlack.pl"), [cite: 36]
    "AXN HD": ("axn-hd-286", "AXNHD.pl"), [cite: 37]
    "AXN Spin": ("axn-spin-294", "AXNSpin.pl"), [cite: 37]
    "AXN Spin HD": ("axn-spin-hd-292", "AXNSpinHD.pl"), [cite: 37]
    "AXN White": ("axn-white-272", "AXNWhite.pl"), [cite: 37]
    "Baby TV": ("baby-tv-285", "BabyTV.pl"), [cite: 37]
    "BBC Brit": ("bbc-brit-275", "BBCBrit.pl"), [cite: 37]
    "BBC Brit HD": ("bbc-brit-hd-306", "BBCBritHD.pl"), [cite: 37]
    "BBC CBeebies": ("bbc-cbeebies-2", "BBCCBeebies.pl"), [cite: 37]
    "BBC Earth": ("bbc-earth-274", "BBCEarth.pl"), [cite: 37]
    "BBC Earth HD": ("bbc-earth-hd-263", "BBCEarthHD.pl"), [cite: 37]
    "BBC First": ("bbc-hd-261", "BBCFirst.pl"), [cite: 37]
    "BBC Lifestyle": ("bbc-lifestyle-277", "BBCLifestyle.pl"), [cite: 37]
    "BBC Lifestyle HD": ("bbc-lifestyle-hd-542", "BBCLifestyleHD.pl"), [cite: 37]
    "BBC News": ("bbc-world-news-254", "BBCNews.pl"), [cite: 37]
    "Biznes24 HD": ("biznes24-hd-686", "Biznes24HD.pl"), [cite: 38]
    "Bollywood HD": ("bollywood-hd-530", "BollywoodHD.pl"), [cite: 38]
    "CANAL+ 1": ("canal-1-295", "CANALPlus1.pl"), [cite: 38]
    "CANAL+ 1 HD": ("canal-1-hd-299", "CANALPlus1HD.pl"), [cite: 38]
    "CANAL+ 360": ("canal-family-296", "CANALPlus360.pl"), [cite: 38]
    "CANAL+ 360 HD": ("canal-family-hd-297", "CANALPlus360HD.pl"), [cite: 38]
    "CANAL+ DOKUMENT": ("canal-discovery-307", "CANALPlusDOKUMENT.pl"), [cite: 38]
    "CANAL+ DOKUMENT HD": ("canal-discovery-hd-308", "CANALPlusDOKUMENTHD.pl"), [cite: 39]
    "CANAL+ DOMO": ("domo-106", "CANALPlusDOMO.pl"), [cite: 39]
    "CANAL+ DOMO HD": ("domo-hd-437", "CANALPlusDOMOHD.pl"), [cite: 39]
    "CANAL+ Film": ("canal-film-320", "CANALPlusFilm.pl"), [cite: 39]
    "CANAL+ Film HD": ("canal-film-hd-278", "CANALPlusFilmHD.pl"), [cite: 39]
    "CANAL+ KUCHNIA": ("kuchnia-489", "CANALPlusKUCHNIA.pl"), [cite: 39]
    "CANAL+ KUCHNIA HD": ("kuchnia-hd-434", "CANALPlusKUCHNIAHD.pl"), [cite: 39]
    "CANAL+ PREMIUM": ("canal-246", "CANALPlusPREMIUM.pl"), [cite: 39]
    "CANAL+ PREMIUM HD": ("canal-hd-288", "CANALPlusPREMIUMHD.pl"), [cite: 39]
    "CANAL+ Seriale": ("canal-seriale-293", "CANALPlusSeriale.pl"), [cite: 39]
    "CANAL+ Seriale HD": ("canal-seriale-hd-298", "CANALPlusSerialeHD.pl"), [cite: 39]
    "CANAL+ Sport": ("canal-sport-14", "CANALPlusSport.pl"), [cite: 39]
    "CANAL+ Sport 2": ("canal-sport-2-15", "CANALPlusSport2.pl"), [cite: 39]
    "CANAL+ Sport 2 HD": ("canal-sport-2-hd-13", "CANALPlusSport2HD.pl"), [cite: 39]
    "CANAL+ Sport 3": ("canal-sport-3-674", "CANALPlusSport3.pl"), [cite: 40]
    "CANAL+ Sport 3 HD": ("canal-sport-3-hd-676", "CANALPlusSport3HD.pl"), [cite: 40]
    "CANAL+ Sport 4": ("canal-sport-4-675", "CANALPlusSport4.pl"), [cite: 40]
    "CANAL+ Sport 4 HD": ("canal-sport-4-hd-677", "CANALPlusSport4HD.pl"), [cite: 40]
    "CANAL+ Sport 5": ("nsport-19", "CANALPlusSport5.pl"), [cite: 40]
    "CANAL+ Sport 5 HD": ("nsport-hd-17", "CANALPlusSport5HD.pl"), [cite: 40]
    "CANAL+ Sport HD": ("canal-sport-hd-12", "CANALPlusSportHD.pl"), [cite: 40]
    "Cartoon Network": ("cartoon-network-273", "CartoonNetwork.pl"), [cite: 40]
    "Cartoon Network HD": ("cartoon-network-hd-310", "CartoonNetworkHD.pl"), [cite: 40]
    "Cartoonito": ("boomerang-270", "Cartoonito.pl"), [cite: 40]
    "Cartoonito HD": ("boomerang-hd-616", "CartoonitoHD.pl"), [cite: 40]
    "CI Polsat": ("ci-polsat-257", "CIPolsat.pl"), [cite: 41]
    "CI Polsat HD": ("ci-polsat-hd-640", "CIPolsatHD.pl"), [cite: 41]
    "Cinemax": ("cinemax-59", "Cinemax.pl"), [cite: 41]
    "Cinemax HD": ("cinemax-hd-57", "CinemaxHD.pl"), [cite: 41]
    "Cinemax 2": ("cinemax2-58", "Cinemax2.pl"), [cite: 41]
    "Cinemax 2 HD": ("cinemax2-hd-56", "Cinemax2HD.pl"), [cite: 41]
    "Comedy Central": ("comedy-central-63", "ComedyCentral.pl"), [cite: 41]
    "Comedy Central HD": ("comedy-central-hd-60", "ComedyCentralHD.pl"), [cite: 41]
    "Da Vinci": ("da-vinci-learning-83", "DaVinci.pl"), [cite: 42]
    "Da Vinci HD": ("da-vinci-hd-614", "DaVinciHD.pl"), [cite: 42]
    "Disco Polo Music": ("disco-polo-music-191", "DiscoPoloMusic.pl"), [cite: 42]
    "Discovery Channel": ("discovery-channel-202", "DiscoveryChannel.pl"), [cite: 42]
    "Discovery Channel HD": ("discovery-channel-hd-67", "DiscoveryChannelHD.pl"), [cite: 42]
    "Discovery Historia": ("discovery-historia-54", "DiscoveryHistoria.pl"), [cite: 42]
    "Discovery Life": ("discovery-life-187", "DiscoveryLife.pl"), [cite: 42]
    "Discovery Life HD": ("discovery-life-hd-547", "DiscoveryLifeHD.pl"), [cite: 43]
    "Discovery Science": ("discovery-science-53", "DiscoveryScience.pl"), [cite: 43]
    "Discovery Science HD": ("discovery-science-hd-52", "DiscoveryScienceHD.pl"), [cite: 43]
    "Disney Channel": ("disney-channel-478", "DisneyChannel.pl"), [cite: 43]
    "Disney Channel HD": ("disney-channel-hd-216", "DisneyChannelHD.pl"), [cite: 43]
    "Disney Junior": ("disney-junior-469", "DisneyJunior.pl"), [cite: 43]
    "Disney XD": ("disney-xd-235", "DisneyXD.pl"), [cite: 43]
    "Docubox HD": ("docubox-hd-175", "DocuboxHD.pl"), [cite: 43]
    "DTX": ("discovery-turbo-xtra-239", "DTX.pl"), [cite: 44]
    "DTX HD": ("discovery-turbo-xtra-hd-189", "DTXHD.pl"), [cite: 44]
    "ducktv": ("ducktv-94", "ducktv.pl"), [cite: 44]
    "ducktv HD": ("ducktv-hd-151", "ducktvHD.pl"), [cite: 44]
    "E! Entertainment": ("e-entertainment-73", "E!Entertainment.pl"), [cite: 44]
    "E! Entertainment HD": ("e-entertainment-hd-169", "E!EntertainmentHD.pl"), [cite: 45]
    "Echo 24": ("echo-24-687", "Echo24.pl"), [cite: 45]
    "Eleven Sports 1": ("eleven-208", "ElevenSports1.pl"), [cite: 45]
    "Eleven Sports 1 4K": ("eleven-sports-1-4k-667", "ElevenSports14K.pl"), [cite: 45]
    "Eleven Sports 1 HD": ("eleven-hd-227", "ElevenSports1HD.pl"), [cite: 45]
    "Eleven Sports 2": ("eleven-sports-212", "ElevenSports2.pl"), [cite: 45]
    "Eleven Sports 2 HD": ("eleven-hd-sports-228", "ElevenSports2HD.pl"), [cite: 45]
    "Eleven Sports 3": ("eleven-extra-531", "ElevenSports3.pl"), [cite: 45]
    "Eleven Sports 3 HD": ("eleven-extra-hd-534", "ElevenSports3HD.pl"), [cite: 45]
    "Eleven Sports 4": ("eleven-sports-4-607", "ElevenSports4.pl"), [cite: 45]
    "Eleven Sports 4 HD": ("eleven-sports-4-hd-611", "ElevenSports4HD.pl"), [cite: 45]
    "Epic Drama": ("epic-drama-610", "EpicDrama.pl"), [cite: 46]
    "Epic Drama HD": ("epic-drama-hd-603", "EpicDramaHD.pl"), [cite: 46]
    "Eska Rock TV": ("hip-hop-tv-511", "EskaRockTV.pl"), [cite: 46]
    "Eska TV": ("eska-tv-114", "EskaTV.pl"), [cite: 46]
    "Eska TV Extra": ("eska-tv-extra-597", "EskaTVExtra.pl"), [cite: 46]
    "Eska TV HD": ("eska-tv-hd-221", "EskaTVHD.pl"), [cite: 46]
    "Eurosport 1": ("eurosport-1-93", "Eurosport1.pl"), [cite: 47]
    "Eurosport 1 HD": ("eurosport-1-hd-97", "Eurosport1HD.pl"), [cite: 47]
    "Eurosport 2": ("eurosport-2-76", "Eurosport2.pl"), [cite: 47]
    "Eurosport 2 HD": ("eurosport-2-hd-120", "Eurosport2HD.pl"), [cite: 47]
    "Extreme Channel": ("extreme-sports-channel-231", "ExtremeChannel.pl"), [cite: 47]
    "Extreme Channel HD": ("extreme-sports-channel-hd-217", "ExtremeChannelHD.pl"), [cite: 47]
    "FashionBox HD": ("fashionbox-hd-171", "FashionBoxHD.pl"), [cite: 47]
    "Fast&FunBox HD": ("fast-funbox-hd-104", "Fast&FunBoxHD.pl"), [cite: 47]
    "FightBox": ("fightbox-436", "FightBox.pl"), [cite: 47]
    "FightBox HD": ("fightbox-hd-453", "FightBoxHD.pl"), [cite: 47]
    "Fightklub": ("fightklub-78", "Fightklub.pl"), [cite: 48]
    "Fightklub HD": ("fightklub-hd-168", "FightklubHD.pl"), [cite: 48]
    "FILMAX": ("filmax", "FILMAX.pl"), [cite: 48]
    "FilmBox Action": ("filmbox-action-451", "FilmBoxAction.pl"), [cite: 48]
    "FilmBox Arthouse": ("filmbox-arthouse-183", "FilmBoxArthouse.pl"), [cite: 48]
    "FilmBox Arthouse HD": ("filmbox-arthouse-hd-190", "FilmBoxArthouseHD.pl"), [cite: 48]
    "FilmBox Extra HD": ("filmbox-extra-hd-86", "FilmBoxExtraHD.pl"), [cite: 48]
    "FilmBox Family": ("filmbox-family-103", "FilmBoxFamily.pl"), [cite: 48]
    "FilmBox Premium HD": ("filmbox-premium-85", "FilmBoxPremiumHD.pl"), [cite: 48]
    "Fokus TV": ("fokus-tv-46", "FokusTV.pl"), [cite: 48]
    "Fokus TV HD": ("fokus-tv-hd-47", "FokusTVHD.pl"), [cite: 48]
    "Food Network": ("polsat-food-157", "FoodNetwork.pl"), [cite: 48]
    "Food Network HD": ("polsat-food-network-hd-209", "FoodNetworkHD.pl"), [cite: 48]
    "FX": ("fox-127", "FX.pl"), [cite: 49]
    "FX Comedy": ("fox-comedy-75", "FXComedy.pl"), [cite: 49]
    "FX Comedy HD": ("fox-comedy-hd-405", "FXComedyHD.pl"), [cite: 49]
    "FX HD": ("fox-hd-128", "FXHD.pl"), [cite: 49]
    "Gametoon HD": ("gametoon-hd-602", "GametoonHD.pl"), [cite: 49]
    "Golf Zone": ("golf-channel-553", "GolfZone.pl"), [cite: 50]
    "Golf Zone HD": ("golf-channel-hd-554", "GolfZoneHD.pl"), [cite: 50]
    "HBO": ("hbo-hd-26", "HBO.pl"), [cite: 50]
    "HBO2": ("hbo2-hd-27", "HBO2.pl"), [cite: 50]
    "HBO3": ("hbo-3-hd-28", "HBO3.pl"), [cite: 50]
    "HGTV": ("tvn-meteo-active-79", "HGTV.pl"), [cite: 50]
    "HGTV HD": ("hgtv-hd-558", "HGTVHD.pl"), [cite: 50]
    "HISTORY": ("history-hd-92", "HISTORY.pl"), [cite: 50]
    "HISTORY HD": ("history-hd-92", "HISTORYHD.pl"), [cite: 50]
    "HISTORY2": ("h2-203", "HISTORY2.pl"), [cite: 51]
    "HISTORY2 HD": ("h2-hd-205", "HISTORY2HD.pl"), [cite: 51]
    "HOME TV": ("tvr-132", "HOMETV.pl"), [cite: 51]
    "HOME TV HD": ("tvr-hd-170", "HOMETVHD.pl"), [cite: 51]
    "INULTRA": ("insight-tv-uhd-682", "INULTRA.pl"), [cite: 51]
    "JAZZ HD": ("jazz-650", "JAZZHD.pl"), [cite: 51]
    "Junior Music": ("top-kids-jr-685", "JuniorMusic.pl"), [cite: 51]
    "Junior Music HD": ("top-kids-jr-hd-664", "JuniorMusicHD.pl"), [cite: 51]
    "Kino Polska": ("kino-polska-324", "KinoPolska.pl"), [cite: 52]
    "Kino Polska HD": ("kino-polska-hd-658", "KinoPolskaHD.pl"), [cite: 52]
    "Kino Polska Muzyka": ("kino-polska-muzyka-426", "KinoPolskaMuzyka.pl"), [cite: 52]
    "Kino TV": ("filmbox-84", "KinoTV.pl"), [cite: 52]
    "Kino TV HD": ("kino-tv-hd-663", "KinoTVHD.pl"), [cite: 52]
    "METRO": ("metro-535", "METRO.pl"), [cite: 52]
    "METRO HD": ("metro-hd-536", "METROHD.pl"), [cite: 52]
    "Mezzo": ("mezzo-234", "Mezzo.pl"), [cite: 53]
    "MiniMini+": ("minimini-236", "MiniMiniPlus.pl"), [cite: 53]
    "MiniMini+ HD": ("minimini-hd-435", "MiniMiniPlusHD.pl"), [cite: 53]
    "MIXTAPE": ("mixtape", "MIXTAPE.pl"), [cite: 53]
    "Motowizja": ("motowizja-178", "Motowizja.pl"), [cite: 53]
    "Motowizja HD": ("motowizja-hd-194", "MotowizjaHD.pl"), [cite: 53]
    "MTV Polska": ("mtv-polska-7", "MTVPolska.pl"), [cite: 53]
    "MTV Polska HD": ("mtv-polska-hd-557", "MTVPolskaHD.pl"), [cite: 53]
    "Museum TV 4K": ("museum-tv-4k", "MuseumTV4K.pl"), [cite: 53]
    "Music Box": ("music-box-538", "MusicBox.pl"), [cite: 53]
    "Music Box HD": ("music-box-hd-539", "MusicBoxHD.pl"), [cite: 53]
    "MyZen 4K": ("myzen-4k", "MyZen4K.pl"), [cite: 53]
    "Nat Geo People": ("nat-geo-people-625", "NatGeoPeople.pl"), [cite: 54]
    "Nat Geo People HD": ("nat-geo-people-hd-211", "NatGeoPeopleHD.pl"), [cite: 54]
    "National Geographic": ("national-geographic-channel-32", "NationalGeographic.pl"), [cite: 54]
    "National Geographic HD": ("national-geographic-channel-hd-34", "NationalGeographicHD.pl"), [cite: 54]
    "National Geographic Wild": ("nat-geo-wild-77", "NationalGeographicWild.pl"), [cite: 54]
    "National Geographic Wild HD": ("nat-geo-wild-hd-121", "NationalGeographicWildHD.pl"), [cite: 54]
    "News24": ("news24", "News24.pl"), [cite: 54]
    "NICK": ("nick-488", "NICK.pl"), [cite: 54]
    "Nick Jr.": ("nick-jr-45", "NickJr.pl"), [cite: 54]
    "Nick Jr. HD": ("nick-jr-hd-662", "NickJr.HD.pl"), [cite: 55]
    "Nickelodeon": ("nickelodeon-42", "Nickelodeon.pl"), [cite: 55]
    "Nicktoons": ("nickelodeon-hd-44", "Nicktoons.pl"), [cite: 55]
    "Nicktoons HD": ("nicktoons-hd-631", "NicktoonsHD.pl"), [cite: 55]
    "Novela tv": ("novela-tv-461", "Novelatv.pl"), [cite: 55]
    "Novela tv HD": ("novela-tv-hd-155", "NovelatvHD.pl"), [cite: 55]
    "Novelas+": ("novelas", "NovelasPlus.pl"), [cite: 55]
    "Nowa TV": ("nowa-tv-528", "NowaTV.pl"), [cite: 55]
    "Nowa TV HD": ("nowa-tv-hd-529", "NowaTVHD.pl"), [cite: 55]
    "Nuta Gold": ("nuta-gold", "NutaGold.pl"), [cite: 55]
    "Nuta.TV": ("nuta-tv-214", "Nuta.TV.pl"), [cite: 55]
    "Nuta.TV HD": ("nuta-tv-hd-213", "Nuta.TVHD.pl"), [cite: 56]
    "Planete+": ("planete-349", "PlanetePlus.pl"), [cite: 56]
    "Planete+ HD": ("planete-hd-432", "PlanetePlusHD.pl"), [cite: 56]
    "Polo TV": ("polo-tv-135", "PoloTV.pl"), [cite: 56]
    "Polonia 1": ("polonia-1-328", "Polonia1.pl"), [cite: 56]
    "Polsat": ("polsat-38", "Polsat.pl"), [cite: 56]
    "Polsat 2": ("polsat-2-327", "Polsat2.pl"), [cite: 56]
    "Polsat 2 HD": ("polsat-2-hd-218", "Polsat2HD.pl"), [cite: 56]
    "Polsat Café": ("polsat-caf-110", "PolsatCafé.pl"), [cite: 57]
    "Polsat Café HD": ("polsat-caf-hd-219", "PolsatCaféHD.pl"), [cite: 57]
    "Polsat Comedy Central Extra": ("comedy-central-family-61", "PolsatComedyCentralExtra.pl"), [cite: 57]
    "Polsat Comedy Central Extra HD": ("comedy-central-family-hd-612", "PolsatComedyCentralExtraHD.pl"), [cite: 57]
    "Polsat Doku": ("polsat-doku-548", "PolsatDoku.pl"), [cite: 57]
    "Polsat Doku HD": ("polsat-doku-hd-551", "PolsatDokuHD.pl"), [cite: 57]
    "Polsat Film": ("polsat-film-123", "PolsatFilm.pl"), [cite: 57]
    "Polsat Film HD": ("polsat-film-hd-162", "PolsatFilmHD.pl"), [cite: 57]
    "Polsat Games": ("polsat-games-653", "PolsatGames.pl"), [cite: 57]
    "Polsat Games HD": ("polsat-games-hd-670", "PolsatGamesHD.pl"), [cite: 57]
    "Polsat HD": ("polsat-hd-35", "PolsatHD.pl"), [cite: 57]
    "Polsat JimJam": ("polsat-jimjam-89", "PolsatJimJam.pl"), [cite: 57]
    "Polsat Music": ("polsat-music-564", "PolsatMusic.pl"), [cite: 57]
    "Polsat Music HD": ("muzo-tv-200", "PolsatMusicHD.pl"), [cite: 57]
    "Polsat News": ("polsat-news-100", "PolsatNews.pl"), [cite: 58]
    "Polsat News 2": ("polsat-news-2-471", "PolsatNews2.pl"), [cite: 58]
    "Polsat News 2 HD": ("polsat-news-2-hd-671", "PolsatNews2HD.pl"), [cite: 58]
    "Polsat News HD": ("polsat-news-hd-229", "PolsatNewsHD.pl"), [cite: 58]
    "Polsat News Polityka": ("polsat-news-polityka", "PolsatNewsPolityka.pl"), [cite: 58]
    "Polsat Play": ("polsat-play-21", "PolsatPlay.pl"), [cite: 58]
    "Polsat Play HD": ("polsat-play-hd-22", "PolsatPlayHD.pl"), [cite: 58]
    "Polsat Rodzina": ("polsat-rodzina-651", "PolsatRodzina.pl"), [cite: 58]
    "Polsat Rodzina HD": ("polsat-rodzina-hd-672", "PolsatRodzinaHD.pl"), [cite: 58]
    "Polsat Seriale": ("polsat-romans-173", "PolsatSeriale.pl"), [cite: 58]
    "Polsat Sport 1": ("polsat-sport-334", "PolsatSport1.pl"), [cite: 58]
    "Polsat Sport 1 HD": ("polsat-sport-hd-96", "PolsatSport1HD.pl"), [cite: 58]
    "Polsat Sport 2": ("polsat-sport-extra-485", "PolsatSport2.pl"), [cite: 58]
    "Polsat Sport 2 HD": ("polsat-sport-extra-hd-144", "PolsatSport2HD.pl"), [cite: 59]
    "Polsat Sport 3": ("polsat-sport-news-431", "PolsatSport3.pl"), [cite: 59]
    "Polsat Sport 3 HD": ("polsat-sport-news-hd-543", "PolsatSport3HD.pl"), [cite: 59]
    "Polsat Sport Extra 1": ("polsat-sport-premium-3-645", "PolsatSportExtra1.pl"), [cite: 59]
    "Polsat Sport Extra 2": ("polsat-sport-premium-4-646", "PolsatSportExtra2.pl"), [cite: 59]
    "Polsat Sport Extra 3": ("polsat-sport-premium-5-642", "PolsatSportExtra3.pl"), [cite: 59]
    "Polsat Sport Extra 4": ("polsat-sport-premium-6-641", "PolsatSportExtra4.pl"), [cite: 59]
    "Polsat Sport Fight": ("polsat-sport-fight-546", "PolsatSportFight.pl"), [cite: 59]
    "Polsat Sport Fight HD": ("polsat-sport-fight-521", "PolsatSportFightHD.pl"), [cite: 59]
    "Polsat Sport Premium 1": ("polsat-sport-premium-1-643", "PolsatSportPremium1.pl"), [cite: 59]
    "Polsat Sport Premium 2": ("polsat-sport-premium-2-644", "PolsatSportPremium2.pl"), [cite: 60]
    "Polsat Viasat Explore HD": ("polsat-viasat-explore-hd-82", "PolsatViasatExploreHD.pl"), [cite: 60]
    "Polsat Viasat History HD": ("polsat-viasat-history-hd-71", "PolsatViasatHistoryHD.pl"), [cite: 60]
    "Polsat Viasat Nature HD": ("polsat-viasat-nature-413", "PolsatViasatNatureHD.pl"), [cite: 60]
    "Power TV": ("power-tv-176", "PowerTV.pl"), [cite: 60]
    "Power TV HD": ("power-tv-hd-177", "PowerTVHD.pl"), [cite: 60]
    "PULS 2": ("puls-2-439", "PULS2.pl"), [cite: 60]
    "PULS 2 HD": ("puls-2-hd-199", "PULS2HD.pl"), [cite: 61]
    "Radio 357": ("radio-357", "Radio357.pl"), [cite: 61]
    "Radio Nowy Świat": ("radio-nowy-swiat", "RadioNowyŚwiat.pl"), [cite: 61]
    "Republika": ("tv-republika-18", "Republika.pl"), [cite: 61]
    "Republika HD": ("tv-republika-hd-16", "RepublikaHD.pl"), [cite: 61]
    "Romance TV": ("romance-tv-129", "RomanceTV.pl"), [cite: 62]
    "Romance TV HD": ("romance-tv-hd-139", "RomanceTVHD.pl"), [cite: 62]
    "SCI FI": ("scifi-universal-20", "SCIFI.pl"), [cite: 62]
    "SCI FI HD": ("sci-fi-hd-628", "SCIFIHD.pl"), [cite: 62]
    "Sportklub": ("sportklub-29", "Sportklub.pl"), [cite: 63]
    "Sportklub HD": ("sportklub-hd-620", "SportklubHD.pl"), [cite: 63]
    "Sportowa.TV": ("sportowatv", "Sportowa.TV.pl"), [cite: 63]
    "STARS.TV": ("stars-tv-149", "STARS.TV.pl"), [cite: 63]
    "STARS.TV HD": ("stars-tv-hd-122", "STARS.TVHD.pl"), [cite: 64]
    "STOPKLATKA": ("stopklatka-tv-185", "STOPKLATKA.pl"), [cite: 64]
    "STOPKLATKA HD": ("stopklatka-hd-186", "STOPKLATKAHD.pl"), [cite: 64]
    "StudioMED TV": ("studiomed-tv-688", "StudioMEDTV.pl"), [cite: 64]
    "Sundance TV": ("sundance-channel-237", "SundanceTV.pl"), [cite: 65]
    "Sundance TV HD": ("sundance-channel-hd-392", "SundanceTVHD.pl"), [cite: 65]
    "Super Polsat": ("super-polsat-541", "SuperPolsat.pl"), [cite: 65]
    "Super Polsat HD": ("super-polsat-hd-560", "SuperPolsatHD.pl"), [cite: 65]
    "TBN Polska": ("tbn-polska-598", "TBNPolska.pl"), [cite: 65]
    "TBN Polska HD": ("tbn-polska-hd-621", "TBNPolskaHD.pl"), [cite: 65]
    "TeenNick": ("teennick", "TeenNick.pl"), [cite: 65]
    "Tele 5": ("tele-5-352", "Tele5.pl"), [cite: 65]
    "Tele 5 HD": ("tele-5-hd-147", "Tele5HD.pl"), [cite: 65]
    "teleTOON+": ("teletoon-232", "teleTOONPlus.pl"), [cite: 65]
    "teleTOON+ HD": ("teletoon-hd-438", "teleTOONPlusHD.pl"), [cite: 65]
    "TLC": ("tlc-238", "TLC.pl"), [cite: 66]
    "TLC HD": ("tlc-hd-163", "TLCHD.pl"), [cite: 66]
    "Top Kids": ("top-kids-225", "TopKids.pl"), [cite: 66]
    "Top Kids HD": ("top-kids-hd-224", "TopKidsHD.pl"), [cite: 66]
    "Travel Channel": ("travel-channel-201", "TravelChannel.pl"), [cite: 66]
    "Travel Channel HD": ("travel-channel-hd-152", "TravelChannelHD.pl"), [cite: 66]
    "TTV": ("ttv-624", "TTV.pl"), [cite: 66]
    "TTV HD": ("ttv-33", "TTVHD.pl"), [cite: 66]
    "TV 4": ("tv-4-360", "TV4.pl"), [cite: 66]
    "TV 4 HD": ("tv-4-hd-222", "TV4HD.pl"), [cite: 66]
    "TV 6": ("tv-6-429", "TV6.pl"), [cite: 66]
    "TV 6 HD": ("tv-6-hd-561", "TV6HD.pl"), [cite: 67]
    "TV Okazje HD": ("tv-okazje-hd-633", "TVOkazjeHD.pl"), [cite: 67]
    "TV Puls": ("tv-puls-332", "TVPuls.pl"), [cite: 67]
    "TV Puls HD": ("tv-puls-hd-197", "TVPulsHD.pl"), [cite: 67]
    "TV Regio": ("tv-regio-679", "TVRegio.pl"), [cite: 67]
    "TV Trwam": ("tv-trwam-108", "TVTrwam.pl"), [cite: 67]
    "TVC": ("ntl-radomsko-184", "TVC.pl"), [cite: 67]
    "TVN": ("tvn-357", "TVN.pl"), [cite: 67]
    "TVN 24": ("tvn-24-347", "TVN24.pl"), [cite: 67]
    "TVN 24 HD": ("tvn-24-hd-158", "TVN24HD.pl"), [cite: 68]
    "TVN 7": ("tvn-7-326", "TVN7.pl"), [cite: 68]
    "TVN 7 HD": ("tvn-7-hd-142", "TVN7HD.pl"), [cite: 68]
    "TVN Fabuła": ("tvn-fabula-4", "TVNFabuła.pl"), [cite: 68]
    "TVN Fabuła HD": ("tvn-fabula-hd-37", "TVNFabułaHD.pl"), [cite: 68]
    "TVN HD": ("tvn-hd-98", "TVNHD.pl"), [cite: 68]
    "TVN Style": ("tvn-style-472", "TVNStyle.pl"), [cite: 68]
    "TVN Style HD": ("tvn-style-hd-141", "TVNStyleHD.pl"), [cite: 68]
    "TVN Turbo": ("tvn-turbo-346", "TVNTurbo.pl"), [cite: 68]
    "TVN Turbo HD": ("tvn-turbo-hd-143", "TVNTurboHD.pl"), [cite: 68]
    "TVN24 BiS": ("tvn-24-biznes-i-swiat-6", "TVN24BiS.pl"), [cite: 68]
    "TVN24 BiS HD": ("tvn-24-biznes-i-swiat-hd-537", "TVN24BiSHD.pl"), [cite: 68]
    "TVP 1": ("tvp-1-321", "TVP1.pl"), [cite: 68]
    "TVP 1 HD": ("tvp-1-hd-380", "TVP1HD.pl"), [cite: 68]
    "TVP 2": ("tvp-2-323", "TVP2.pl"), [cite: 68]
    "TVP 2 HD": ("tvp-2-hd-145", "TVP2HD.pl"), [cite: 69]
    "TVP 3": ("tvp-3-172", "TVP3.pl"), [cite: 69]
    "TVP 3 Białystok": ("tvp-3-bialystok-5", "TVP3Białystok.pl"), [cite: 69]
    "TVP 3 Bydgoszcz": ("tvp-3-bydgoszcz-378", "TVP3Bydgoszcz.pl"), [cite: 69]
    "TVP 3 Gdańsk": ("tvp-3-gdansk-386", "TVP3Gdańsk.pl"), [cite: 69]
    "TVP 3 Gorzów Wielkopolski": ("tvp-3-gorzow-wielkopolski-342", "TVP3GorzówWielkopolski.pl"), [cite: 69]
    "TVP 3 Katowice": ("tvp-3-katowice-394", "TVP3Katowice.pl"), [cite: 69]
    "TVP 3 Kielce": ("tvp-3-kielce-475", "TVP3Kielce.pl"), [cite: 69]
    "TVP 3 Kraków": ("tvp-3-krakow-403", "TVP3Kraków.pl"), [cite: 69]
    "TVP 3 Lublin": ("tvp-3-lublin-409", "TVP3Lublin.pl"), [cite: 69]
    "TVP 3 Łódź": ("tvp-3-lodz-416", "TVP3Łódź.pl"), [cite: 69]
    "TVP 3 Olsztyn": ("tvp-3-olsztyn-339", "TVP3Olsztyn.pl"), [cite: 69]
    "TVP 3 Opole": ("tvp-3-opole-335", "TVP3Opole.pl"), [cite: 70]
    "TVP 3 Poznań": ("tvp-3-poznan-425", "TVP3Poznań.pl"), [cite: 70]
    "TVP 3 Rzeszów": ("tvp-3-rzeszow-433", "TVP3Rzeszów.pl"), [cite: 70]
    "TVP 3 Szczecin": ("tvp-3-szczecin-440", "TVP3Szczecin.pl"), [cite: 70]
    "TVP 3 Warszawa": ("tvp-3-warszawa-446", "TVP3Warszawa.pl"), [cite: 70]
    "TVP 3 Wrocław": ("tvp-3-wroclaw-454", "TVP3Wrocław.pl"), [cite: 70]
    "TVP ABC": ("tvp-abc-182", "TVPABC.pl"), [cite: 70]
    "TVP Dokument": ("tvp-dokument", "TVPDokument.pl"), [cite: 70]
    "TVP HD": ("tvp-hd-101", "TVPHD.pl"), [cite: 70]
    "TVP Historia": ("tvp-historia-74", "TVPHistoria.pl"), [cite: 70]
    "TVP Info": ("tvp-info-462", "TVPInfo.pl"), [cite: 70]
    "TVP Info HD": ("tvp-info-hd-525", "TVPInfoHD.pl"), [cite: 70]
    "TVP Kobieta": ("tvp-kobieta", "TVPKobieta.pl"), [cite: 70]
    "TVP Kultura": ("tvp-kultura-477", "TVPKultura.pl"), [cite: 70]
    "TVP Kultura HD": ("tvp-kultura-hd-680", "TVPKulturaHD.pl"), [cite: 70]
    "TVP Nauka": ("tvp-nauka", "TVPNauka.pl"), [cite: 71]
    "TVP Polonia": ("tvp-polonia-325", "TVPPolonia.pl"), [cite: 71]
    "TVP Rozrywka": ("tvp-rozrywka-159", "TVPRozrywka.pl"), [cite: 71]
    "TVP Seriale": ("tvp-seriale-130", "TVPSeriale.pl"), [cite: 71]
    "TVP Sport": ("tvp-sport-40", "TVPSport.pl"), [cite: 71]
    "TVP Sport HD": ("tvp-sport-hd-39", "TVPSportHD.pl"), [cite: 71]
    "TVP Wilno": ("tvp-wilno", "TVPWilno.pl"), [cite: 71]
    "TVP World": ("tvp-world", "TVPWorld.pl"), [cite: 71]
    "TVS HD": ("tvs-hd-109", "TVSHD.pl"), [cite: 71]
    "TVT": ("tvt-500", "TVT.pl"), [cite: 71]
    "Twoja.TV": ("twoja-tv-514", "Twoja.TV.pl"), [cite: 71]
    "ViDoc TV": ("ctv9", "ViDocTV.pl"), [cite: 72]
    "VOX Music TV": ("vox-music-tv-193", "VOXMusicTV.pl"), [cite: 72]
    "Warner TV HD": ("tnt-hd-220", "WarnerTVHD.pl"), [cite: 72]
    "Water Planet HD": ("water-planet-hd-156", "WaterPlanetHD.pl"), [cite: 72]
    "WP": ("wp-532", "WP.pl"), [cite: 72]
    "WP HD": ("wp-hd-533", "WPHD.pl"), [cite: 72]
    "wPolsce24": ("wpolsce-pl-635", "wPolsce24.pl"), [cite: 72]
    "wPolsce24 HD": ("wpolsce-pl-hd-637", "wPolsce24HD.pl"), [cite: 72]
    "Wydarzenia 24 HD": ("superstacja-hd-550", "Wydarzenia24HD.pl"), [cite: 73]
    "XTREME TV": ("super-tv-690", "XTREMETV.pl"), [cite: 73]
    "ZOOM TV": ("zoom-tv-526", "ZOOMTV.pl"), [cite: 73]
    "ZOOM TV HD": ("zoom-tv-hd-527", "ZOOMTVHD.pl"), [cite: 73]
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

def clean_xml_text(text):
    if not text: return ""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return html.escape(text)

def get_deep_details(url):
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
        cast_ul = s.find('ul', class_='cast')
        if cast_ul:
            curr = None
            for li in cast_ul.find_all('li'):
                if 'header' in li.get('class', []): curr = li.get_text(strip=True).lower()
                else:
                    names = [n.strip() for n in li.get_text(separator=' ', strip=True).split(',') if n.strip()]
                    if curr and 'obsada' in curr: actors.extend(names)
                    elif curr and 'reżyseria' in curr: directors.extend(names)
        return rating, actors, directors, full_desc, age_limit
    except: return "", [], [], "", ""

def load_existing_epg():
    """Wczytuje istniejący plik GZ i wyciąga z niego audycje do słownika."""
    existing_data = {} # Klucz: (m3u_id, start_timestamp)
    if not os.path.exists(OUTPUT_FILE_GZ):
        return existing_data

    print(f"[INFO] Wczytywanie archiwalnych danych z {OUTPUT_FILE_GZ}...")
    try:
        with gzip.open(OUTPUT_FILE_GZ, 'rb') as f:
            content = f.read().decode('utf-8')
            soup = BeautifulSoup(content, 'xml')
            for prog in soup.find_all('programme'):
                chid = prog.get('channel')
                start = prog.get('start')
                # Przechowujemy cały obiekt tagu, aby go później odtworzyć
                existing_data[(chid, start)] = prog
    except Exception as e:
        print(f"[!] Nie udało się wczytać starego EPG: {e}")
    return existing_data

def fetch_day_data(name, slug, m3u_id, day_off):
    """Pobiera dane tylko dla jednego konkretnego dnia."""
    day_programmes = []
    base_date = (datetime.datetime.now() + datetime.timedelta(days=day_off)).replace(hour=0, minute=0, second=0, microsecond=0)
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
            start_dt = base_date + datetime.timedelta(days=shift, hours=h, minutes=m)
            titles_div = item.find('div', class_='titles')
            title_a = titles_div.find('a')
            if not title_a: continue
            
            p_url = title_a.get('href')
            rate, acts, dirs, f_desc, age = "", [], [], "", ""
            if DEEP_SCAN and p_url:
                rate, acts, dirs, f_desc, age = get_deep_details(p_url)
            
            day_programmes.append({
                'start_dt': start_dt,
                'title': title_a.get_text(strip=True),
                'desc': f_desc if f_desc else (item.find('p').get_text(strip=True) if item.find('p') else ""),
                'cat': item.find('span', class_='type').get_text(strip=True) if item.find('span', class_='type') else "",
                'age': age,
                'rate': rate,
                'acts': acts,
                'dirs': dirs
            })
    except: pass
    return day_programmes

def process_channel_smart(name, slug, m3u_id, existing_global_data):
    """Łączy stare dane z nowymi dla jednego kanału."""
    # 1. Wyciągnij stare audycje dla tego kanału
    current_channel_data = {k[1]: v for k, v in existing_global_data.items() if k[0] == m3u_id}
    
    # 2. Pobierz nowe dane dla wybranych dni
    new_progs = []
    for d in DAYS_TO_REFRESH:
        new_progs.extend(fetch_day_data(name, slug, m3u_id, d))
    
    # 3. Dodaj nowe do słownika (nadpisując stare jeśli się pokrywają startem)
    for p in new_progs:
        start_str = p['start_dt'].strftime("%Y%m%d%H%M00 +0100")
        current_channel_data[start_str] = p

    # 4. Sortowanie i wyliczanie STOP
    sorted_starts = sorted(current_channel_data.keys())
    final_xml_part = ""
    
    now_limit = (datetime.datetime.now() - datetime.timedelta(days=CATCHUP_DAYS)).strftime("%Y%m%d%H%M00")

    for i, start_key in enumerate(sorted_starts):
        # Retencja: usuń jeśli starsze niż 7 dni
        if start_key < now_limit: continue
            
        prog = current_channel_data[start_key]
        
        # Obliczanie stopu
        if i < len(sorted_starts) - 1:
            stop_val = sorted_starts[i+1]
        else:
            # Dla ostatniej audycji dodajemy 2h do startu
            d = datetime.datetime.strptime(start_key[:12], "%Y%m%d%H%M") + datetime.timedelta(hours=2)
            stop_val = d.strftime("%Y%m%d%H%M00 +0100")

        # Jeśli to stary tag BeautifulSoup, po prostu go doklejamy (z aktualizacją stopu)
        if hasattr(prog, 'name'):
            prog['stop'] = stop_val
            final_xml_part += str(prog) + "\n"
        else:
            # Jeśli to nowe dane (słownik), budujemy XML
            final_xml_part += f'  <programme start="{start_key}" stop="{stop_val}" channel="{m3u_id}">\n'
            final_xml_part += f'    <title lang="pl">{clean_xml_text(prog["title"])}</title>\n'
            if prog['desc']: final_xml_part += f'    <desc lang="pl">{clean_xml_text(prog["desc"])}</desc>\n'
            if prog['cat']: final_xml_part += f'    <category lang="pl">{clean_xml_text(prog["cat"])}</category>\n'
            if prog['age']: final_xml_part += f'    <rating system="advisory"><value>{prog["age"]}</value></rating>\n'
            if prog['acts'] or prog['dirs']:
                final_xml_part += '    <credits>\n'
                for d in prog['dirs']: final_xml_part += f'      <director>{clean_xml_text(d)}</director>\n'
                for a in prog['acts']: final_xml_part += f'      <actor>{clean_xml_text(a)}</actor>\n'
                final_xml_part += '    </credits>\n'
            final_xml_part += f'  </programme>\n'
            
    print(f"Zaktualizowano: {name:16}")
    return final_xml_part

def get_epg():
    if not os.path.exists(os.path.dirname(OUTPUT_FILE_GZ)): os.makedirs(os.path.dirname(OUTPUT_FILE_GZ))
    
    # KROK 1: Wczytaj to co już masz na GitHubie
    existing_global_data = load_existing_epg()
    
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="AzmanGrabber Hardcore v3.0">\n'
    for name, (_, m3u_id) in CHANNELS.items():
        xml_header += f'  <channel id="{m3u_id}"><display-name>{clean_xml_text(name)}</display-name></channel>\n'

    print(f"\n[INFO] Tryb Catchup: Odświeżanie dni {DAYS_TO_REFRESH}...")
    
    full_body = ""
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_channel_smart, name, slug, m3u_id, existing_global_data) 
                   for name, (slug, m3u_id) in CHANNELS.items()]
        for future in concurrent.futures.as_completed(futures):
            full_body += future.result()

    final_xml = xml_header + full_body + '</tv>'
    
    # KROK 2: Zapisz jako skompresowany GZ
    with gzip.open(OUTPUT_FILE_GZ, 'wt', encoding='utf-8') as f:
        f.write(final_xml)
        
    print(f"\n--- SUKCES! Archiwum EPG zapisane w GZ: {OUTPUT_FILE_GZ} ---")

if __name__ == "__main__":
    get_epg()
    print(f"\n[INFO] Czas operacji: {int((time.time() - start_time_pomiar)//60)} min {int((time.time() - start_time_pomiar)%60)} sek.")
