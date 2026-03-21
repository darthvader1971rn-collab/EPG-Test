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
    "13 Ulica": ("13-ulica-316", "13Ulica.pl"),
    "13 Ulica HD": ("13-ulica-hd-509", "13UlicaHD.pl"),
    "13th Street": ("13th-street-250", "13thStreet.pl"),
    "13.tv": ("13-tv-312", "13.tv.pl"),
    "2x2": ("2x2-604", "2x2.pl"),
    "2x2 HD": ("2x2-hd-613", "2x2HD.pl"),
    "360TuneBox": ("360tunebox-302", "360TuneBox.pl"),
    "360TuneBox HD": ("360tunebox-hd-304", "360TuneBoxHD.pl"),
    "3SAT": ("3sat-248", "3SAT.pl"),
    "4FUN DANCE": ("4fun-fit-dance-244", "4FUNDANCE.pl"),
    "4FUN KIDS": ("4fun-hits-283", "4FUNKIDS.pl"),
    "4FUN.TV": ("4fun-tv-269", "4FUN.TV.pl"),
    "Active Family": ("active-family-300", "ActiveFamily.pl"),
    "Active Family HD": ("active-family-hd-301", "ActiveFamilyHD.pl"),
    "Adult Channel": ("adult-channel-265", "AdultChannel.pl"),
    "Adventure": ("adventure-303", "Adventure.pl"),
    "Adventure HD": ("adventure-hd-305", "AdventureHD.pl"),
    "Al Jazeera": ("al-jazeera-31", "AlJazeera.pl"),
    "Al Jazeera HD": ("al-jazeera-hd-609", "AlJazeeraHD.pl"),
    "Ale kino+": ("ale-kino-319", "AlekinoPlus.pl"),
    "Ale kino+ HD": ("ale-kino-hd-262", "AlekinoPlusHD.pl"),
    "Alfa TVP": ("alfa-tvp", "AlfaTVP.pl"),
    "AMC": ("mgm-333", "AMC.pl"),
    "AMC HD": ("mgm-hd-68", "AMCHD.pl"),
    "Animal Planet HD": ("animal-planet-hd-284", "AnimalPlanetHD.pl"),
    "Animal Planet (niem.)": ("animal-planet-niem-264", "AnimalPlanet(niem.).pl"),
    "Antena": ("antena", "Antena.pl"),
    "ARD-alpha": ("ard-alpha-252", "ARD-alpha.pl"),
    "Arirang TV": ("arirang-tv-30", "ArirangTV.pl"),
    "Arte": ("arte-253", "Arte.pl"),
    "Arte HD": ("arte-hd-290", "ArteHD.pl"),
    "ATV": ("atv-251", "ATV.pl"),
    "AXN": ("axn-249", "AXN.pl"),
    "AXN Black": ("axn-black-271", "AXNBlack.pl"),
    "AXN HD": ("axn-hd-286", "AXNHD.pl"),
    "AXN Spin": ("axn-spin-294", "AXNSpin.pl"),
    "AXN Spin HD": ("axn-spin-hd-292", "AXNSpinHD.pl"),
    "AXN White": ("axn-white-272", "AXNWhite.pl"),
    "Baby TV": ("baby-tv-285", "BabyTV.pl"),
    "BBC Brit": ("bbc-brit-275", "BBCBrit.pl"),
    "BBC Brit HD": ("bbc-brit-hd-306", "BBCBritHD.pl"),
    "BBC CBeebies": ("bbc-cbeebies-2", "BBCCBeebies.pl"),
    "BBC Earth": ("bbc-earth-274", "BBCEarth.pl"),
    "BBC Earth HD": ("bbc-earth-hd-263", "BBCEarthHD.pl"),
    "BBC First": ("bbc-hd-261", "BBCFirst.pl"),
    "BBC Lifestyle": ("bbc-lifestyle-277", "BBCLifestyle.pl"),
    "BBC Lifestyle HD": ("bbc-lifestyle-hd-542", "BBCLifestyleHD.pl"),
    "BBC News": ("bbc-world-news-254", "BBCNews.pl"),
    "Beate-Uhse.TV": ("beate-uhse-tv-256", "Beate-Uhse.TV.pl"),
    "Belgia - TV1": ("belgia-tv1-268", "Belgia-TV1.pl"),
    "Belsat TV": ("belsat-tv-289", "BelsatTV.pl"),
    "Bibel TV": ("bibel-tv-266", "BibelTV.pl"),
    "Biznes24 HD": ("biznes24-hd-686", "Biznes24HD.pl"),
    "Bloomberg (ang.)": ("bloomberg-ang-245", "Bloomberg(ang.).pl"),
    "Blue Hustler": ("blue-hustler-280", "BlueHustler.pl"),
    "Bollywood HD": ("bollywood-hd-530", "BollywoodHD.pl"),
    "BR": ("br-255", "BR.pl"),
    "Brazzers TV Europe": ("brazzers-tv-europe-279", "BrazzersTVEurope.pl"),
    "CANAL+ 1": ("canal-1-295", "CANALPlus1.pl"),
    "CANAL+ 1 HD": ("canal-1-hd-299", "CANALPlus1HD.pl"),
    "CANAL+ 360": ("canal-family-296", "CANALPlus360.pl"),
    "CANAL+ 360 HD": ("canal-family-hd-297", "CANALPlus360HD.pl"),
    "CANAL+ 4K Ultra HD": ("canal-4k-ultra-hd-638", "CANALPlus4KUltraHD.pl"),
    "CANAL+ DOKUMENT": ("canal-discovery-307", "CANALPlusDOKUMENT.pl"),
    "CANAL+ DOKUMENT HD": ("canal-discovery-hd-308", "CANALPlusDOKUMENTHD.pl"),
    "CANAL+ DOMO": ("domo-106", "CANALPlusDOMO.pl"),
    "CANAL+ DOMO HD": ("domo-hd-437", "CANALPlusDOMOHD.pl"),
    "CANAL+ Film": ("canal-film-320", "CANALPlusFilm.pl"),
    "CANAL+ Film HD": ("canal-film-hd-278", "CANALPlusFilmHD.pl"),
    "CANAL+ KUCHNIA": ("kuchnia-489", "CANALPlusKUCHNIA.pl"),
    "CANAL+ KUCHNIA HD": ("kuchnia-hd-434", "CANALPlusKUCHNIAHD.pl"),
    "CANAL+ PREMIUM": ("canal-246", "CANALPlusPREMIUM.pl"),
    "CANAL+ PREMIUM HD": ("canal-hd-288", "CANALPlusPREMIUMHD.pl"),
    "CANAL+ Seriale": ("canal-seriale-293", "CANALPlusSeriale.pl"),
    "CANAL+ Seriale HD": ("canal-seriale-hd-298", "CANALPlusSerialeHD.pl"),
    "CANAL+ Sport": ("canal-sport-14", "CANALPlusSport.pl"),
    "CANAL+ Sport 2": ("canal-sport-2-15", "CANALPlusSport2.pl"),
    "CANAL+ Sport 2 HD": ("canal-sport-2-hd-13", "CANALPlusSport2HD.pl"),
    "CANAL+ Sport 3": ("canal-sport-3-674", "CANALPlusSport3.pl"),
    "CANAL+ Sport 3 HD": ("canal-sport-3-hd-676", "CANALPlusSport3HD.pl"),
    "CANAL+ Sport 4": ("canal-sport-4-675", "CANALPlusSport4.pl"),
    "CANAL+ Sport 4 HD": ("canal-sport-4-hd-677", "CANALPlusSport4HD.pl"),
    "CANAL+ Sport 5": ("nsport-19", "CANALPlusSport5.pl"),
    "CANAL+ Sport 5 HD": ("nsport-hd-17", "CANALPlusSport5HD.pl"),
    "CANAL+ Sport HD": ("canal-sport-hd-12", "CANALPlusSportHD.pl"),
    "Cartoon Network": ("cartoon-network-273", "CartoonNetwork.pl"),
    "Cartoon Network HD": ("cartoon-network-hd-310", "CartoonNetworkHD.pl"),
    "Cartoon Network/Warner TV": ("cartoon-network-tnt-313", "CartoonNetwork/WarnerTV.pl"),
    "Cartoonito": ("boomerang-270", "Cartoonito.pl"),
    "Cartoonito HD": ("boomerang-hd-616", "CartoonitoHD.pl"),
    "CI Polsat": ("ci-polsat-257", "CIPolsat.pl"),
    "CI Polsat HD": ("ci-polsat-hd-640", "CIPolsatHD.pl"),
    "Cinemax": ("cinemax-59", "Cinemax.pl"),
    "Cinemax HD": ("cinemax-hd-57", "CinemaxHD.pl"),
    "Cinemax2": ("cinemax2-58", "Cinemax2.pl"),
    "Cinemax2 HD": ("cinemax2-hd-56", "Cinemax2HD.pl"),
    "Clubbing TV": ("clubbing-tv-689", "ClubbingTV.pl"),
    "CNBC": ("cnbc-247", "CNBC.pl"),
    "CNN": ("cnn-258", "CNN.pl"),
    "Comedy Central": ("comedy-central-63", "ComedyCentral.pl"),
    "Comedy Central HD": ("comedy-central-hd-60", "ComedyCentralHD.pl"),
    "CT 1": ("ct-1-241", "CT1.pl"),
    "CT 2": ("ct-2-243", "CT2.pl"),
    "CTV - DLA CIEBIE": ("ctv-dla-ciebie", "CTV-DLACIEBIE.pl"),
    "Current Time": ("current-time", "CurrentTime.pl"),
    "Current Time HD": ("current-time-hd", "CurrentTimeHD.pl"),
    "Czwórka Polskie Radio": ("czworka-polskie-radio-133", "CzwórkaPolskieRadio.pl"),
    "Czwórka Polskie Radio HD": ("czworka-polskie-radio-hd-140", "CzwórkaPolskieRadioHD.pl"),
    "Da Vinci": ("da-vinci-learning-83", "DaVinci.pl"),
    "Da Vinci HD": ("da-vinci-hd-614", "DaVinciHD.pl"),
    "Dacha TV": ("dacha-tv", "DachaTV.pl"),
    "Dami Skarżysko-Kamienna": ("dami-skarzysko-kamienna-174", "DamiSkarżysko-Kamienna.pl"),
    "Das Erste": ("das-erste-350", "DasErste.pl"),
    "Disco Polo Music": ("disco-polo-music-191", "DiscoPoloMusic.pl"),
    "Discovery Channel": ("discovery-channel-202", "DiscoveryChannel.pl"),
    "Discovery Channel HD": ("discovery-channel-hd-67", "DiscoveryChannelHD.pl"),
    "Discovery Channel (niem.)": ("discovery-channel-niem-358", "DiscoveryChannel(niem.).pl"),
    "Discovery HD (niem.)": ("discovery-hd-niem-450", "DiscoveryHD(niem.).pl"),
    "Discovery Historia": ("discovery-historia-54", "DiscoveryHistoria.pl"),
    "Discovery Life": ("discovery-life-187", "DiscoveryLife.pl"),
    "Discovery Life HD": ("discovery-life-hd-547", "DiscoveryLifeHD.pl"),
    "Discovery Science": ("discovery-science-53", "DiscoveryScience.pl"),
    "Discovery Science HD": ("discovery-science-hd-52", "DiscoveryScienceHD.pl"),
    "Disney Channel": ("disney-channel-478", "DisneyChannel.pl"),
    "Disney Channel HD": ("disney-channel-hd-216", "DisneyChannelHD.pl"),
    "Disney Junior": ("disney-junior-469", "DisneyJunior.pl"),
    "Disney XD": ("disney-xd-235", "DisneyXD.pl"),
    "dlaCiebie.tv": ("dlaciebie-tv-442", "dlaCiebie.tv.pl"),
    "DMAX": ("dmax-428", "DMAX.pl"),
    "DocuBox": ("docubox-167", "DocuBox.pl"),
    "DocuBox HD": ("docubox-hd-175", "DocuBoxHD.pl"),
    "Dorcel TV": ("dorcel-tv-507", "DorcelTV.pl"),
    "Dorcel TV HD": ("dorcel-tv-hd-660", "DorcelTVHD.pl"),
    "Dorcel XXX": ("dorcel-xxx-506", "DorcelXXX.pl"),
    "Dorcel XXX HD": ("dorcel-xxx-hd-615", "DorcelXXXHD.pl"),
    "DR 1": ("dr-1-359", "DR1.pl"),
    "DR 2": ("dr-2-361", "DR2.pl"),
    "DTX": ("discovery-turbo-xtra-239", "DTX.pl"),
    "DTX HD": ("discovery-turbo-xtra-hd-189", "DTXHD.pl"),
    "ducktv": ("ducktv-94", "ducktv.pl"),
    "ducktv HD": ("ducktv-hd-151", "ducktvHD.pl"),
    "DW": ("dw-364", "DW.pl"),
    "E! Entertainment": ("e-entertainment-73", "E!Entertainment.pl"),
    "E! Entertainment HD": ("e-entertainment-hd-169", "E!EntertainmentHD.pl"),
    "Echo 24": ("echo-24-687", "Echo24.pl"),
    "EinsLive": ("einslive-427", "EinsLive.pl"),
    "Eleven Sports 1": ("eleven-208", "ElevenSports1.pl"),
    "Eleven Sports 1 4K": ("eleven-sports-1-4k-667", "ElevenSports14K.pl"),
    "Eleven Sports 1 HD": ("eleven-hd-227", "ElevenSports1HD.pl"),
    "Eleven Sports 2": ("eleven-sports-212", "ElevenSports2.pl"),
    "Eleven Sports 2 HD": ("eleven-hd-sports-228", "ElevenSports2HD.pl"),
    "Eleven Sports 3": ("eleven-extra-531", "ElevenSports3.pl"),
    "Eleven Sports 3 HD": ("eleven-extra-hd-534", "ElevenSports3HD.pl"),
    "Eleven Sports 4": ("eleven-sports-4-607", "ElevenSports4.pl"),
    "Eleven Sports 4 HD": ("eleven-sports-4-hd-611", "ElevenSports4HD.pl"),
    "English Club TV": ("english-club-tv-148", "EnglishClubTV.pl"),
    "English Club TV HD": ("english-club-tv-hd-181", "EnglishClubTVHD.pl"),
    "Epic Drama": ("epic-drama-610", "EpicDrama.pl"),
    "Epic Drama HD": ("epic-drama-hd-603", "EpicDramaHD.pl"),
    "Erox HD": ("erox-hd-520", "EroxHD.pl"),
    "Eroxxx HD": ("eroxxx-hd-512", "EroxxxHD.pl"),
    "Eska Rock TV": ("hip-hop-tv-511", "EskaRockTV.pl"),
    "Eska TV": ("eska-tv-114", "EskaTV.pl"),
    "Eska TV Extra": ("eska-tv-extra-597", "EskaTVExtra.pl"),
    "Eska TV HD": ("eska-tv-hd-221", "EskaTVHD.pl"),
    "E-SPORT": ("e-sport-555", "E-SPORT.pl"),
    "E-SPORT HD": ("e-sport-hd-556", "E-SPORTHD.pl"),
    "Espreso TV": ("espreso-tv", "EspresoTV.pl"),
    "Euronews": ("euronews-367", "Euronews.pl"),
    "Euronews HD": ("euronews-hd-617", "EuronewsHD.pl"),
    "Eurosport 1": ("eurosport-1-93", "Eurosport1.pl"),
    "Eurosport 1 HD": ("eurosport-1-hd-97", "Eurosport1HD.pl"),
    "Eurosport 1 (niem.)": ("eurosport-niem-366", "Eurosport1(niem.).pl"),
    "Eurosport 2": ("eurosport-2-76", "Eurosport2.pl"),
    "Eurosport 2 HD": ("eurosport-2-hd-120", "Eurosport2HD.pl"),
    "EWTN": ("ewtn-207", "EWTN.pl"),
    "Extreme Channel": ("extreme-sports-channel-231", "ExtremeChannel.pl"),
    "Extreme Channel HD": ("extreme-sports-channel-hd-217", "ExtremeChannelHD.pl"),
    "Fashion TV": ("fashion-tv-233", "FashionTV.pl"),
    "Fashion TV HD": ("fashion-tv-hd-125", "FashionTVHD.pl"),
    "FashionBox HD": ("fashionbox-hd-171", "FashionBoxHD.pl"),
    "Fast&amp;FunBox HD": ("fast-funbox-hd-104", "Fast&amp;FunBoxHD.pl"),
    "FightBox": ("fightbox-436", "FightBox.pl"),
    "FightBox HD": ("fightbox-hd-453", "FightBoxHD.pl"),
    "FighTime": ("fighttime", "FighTime.pl"),
    "Fightklub": ("fightklub-78", "Fightklub.pl"),
    "Fightklub HD": ("fightklub-hd-168", "FightklubHD.pl"),
    "FILMAX": ("filmax", "FILMAX.pl"),
    "FilmBox Action": ("filmbox-action-451", "FilmBoxAction.pl"),
    "FilmBox Arthouse": ("filmbox-arthouse-183", "FilmBoxArthouse.pl"),
    "FilmBox Arthouse HD": ("filmbox-arthouse-hd-190", "FilmBoxArthouseHD.pl"),
    "FilmBox Extra HD": ("filmbox-extra-hd-86", "FilmBoxExtraHD.pl"),
    "FilmBox Family": ("filmbox-family-103", "FilmBoxFamily.pl"),
    "FilmBox Premium HD": ("filmbox-premium-85", "FilmBoxPremiumHD.pl"),
    "Fokus TV": ("fokus-tv-46", "FokusTV.pl"),
    "Fokus TV HD": ("fokus-tv-hd-47", "FokusTVHD.pl"),
    "Folx TV": ("folx-tv-206", "FolxTV.pl"),
    "Food Network": ("polsat-food-157", "FoodNetwork.pl"),
    "Food Network HD": ("polsat-food-network-hd-209", "FoodNetworkHD.pl"),
    "Food Network HD - EN": ("food-network-hd-240", "FoodNetworkHD-EN.pl"),
    "France 2 - PL": ("france-2-pl-329", "France2-PL.pl"),
    "France 24": ("france-24-491", "France24.pl"),
    "France 24 - EN": ("france-24-en-70", "France24-EN.pl"),
    "France 24 HD": ("france-24-hd-632", "France24HD.pl"),
    "France 24 HD - EN": ("france-24-en-hd-657", "France24HD-EN.pl"),
    "Freedom": ("uatv-549", "Freedom.pl"),
    "FunBox UHD": ("funbox-4k-605", "FunBoxUHD.pl"),
    "FX": ("fox-127", "FX.pl"),
    "FX Comedy": ("fox-comedy-75", "FXComedy.pl"),
    "FX Comedy HD": ("fox-comedy-hd-405", "FXComedyHD.pl"),
    "FX HD": ("fox-hd-128", "FXHD.pl"),
    "Gametoon HD": ("gametoon-hd-602", "GametoonHD.pl"),
    "Ginx eSports TV": ("ginx-tv-503", "GinxeSportsTV.pl"),
    "Ginx eSports TV HD": ("ginx-tv-hd-504", "GinxeSportsTVHD.pl"),
    "GM24": ("hse-24-457", "GM24.pl"),
    "God TV": ("god-tv-683", "GodTV.pl"),
    "Goldstar TV": ("goldstar-tv-371", "GoldstarTV.pl"),
    "Golf Zone": ("golf-channel-553", "GolfZone.pl"),
    "Golf Zone HD": ("golf-channel-hd-554", "GolfZoneHD.pl"),
    "HBO": ("hbo-23", "HBO.pl"),
    "HBO HD": ("hbo-hd-26", "HBOHD.pl"),
    "HBO2": ("hbo2-24", "HBO2.pl"),
    "HBO2 HD": ("hbo2-hd-27", "HBO2HD.pl"),
    "HBO3": ("hbo-3-25", "HBO3.pl"),
    "HBO3 HD": ("hbo-3-hd-28", "HBO3HD.pl"),
    "Heimatkanal": ("heimatkanal-372", "Heimatkanal.pl"),
    "HGTV": ("tvn-meteo-active-79", "HGTV.pl"),
    "HGTV HD": ("hgtv-hd-558", "HGTVHD.pl"),
    "HISTORY": ("history-91", "HISTORY.pl"),
    "HISTORY HD": ("history-hd-92", "HISTORYHD.pl"),
    "HISTORY HD (niem.)": ("history-hd-niem-458", "HISTORYHD(niem.).pl"),
    "HISTORY2": ("h2-203", "HISTORY2.pl"),
    "HISTORY2 HD": ("h2-hd-205", "HISTORY2HD.pl"),
    "HOME TV": ("tvr-132", "HOMETV.pl"),
    "HOME TV HD": ("tvr-hd-170", "HOMETVHD.pl"),
    "HR": ("hr-374", "HR.pl"),
    "Hustler HD": ("hustler-hd-138", "HustlerHD.pl"),
    "Hustler TV": ("hustler-tv-107", "HustlerTV.pl"),
    "ID": ("id-117", "ID.pl"),
    "ID HD": ("id-hd-188", "IDHD.pl"),
    "INULTRA": ("insight-tv-uhd-682", "INULTRA.pl"),
    "iTVS": ("itvs-661", "iTVS.pl"),
    "JAZZ HD": ("jazz-650", "JAZZHD.pl"),
    "Junior Music": ("top-kids-jr-685", "JuniorMusic.pl"),
    "Junior Music HD": ("top-kids-jr-hd-664", "JuniorMusicHD.pl"),
    "Kabaret TV": ("kabaret-tv", "KabaretTV.pl"),
    "Kabel Eins": ("kabel-eins-376", "KabelEins.pl"),
    "KBS World HD": ("kbs-world-hd", "KBSWorldHD.pl"),
    "KI.KA": ("ki-ka-377", "KI.KA.pl"),
    "Kino Polska": ("kino-polska-324", "KinoPolska.pl"),
    "Kino Polska HD": ("kino-polska-hd-658", "KinoPolskaHD.pl"),
    "Kino Polska Muzyka": ("kino-polska-muzyka-426", "KinoPolskaMuzyka.pl"),
    "Kino TV": ("filmbox-84", "KinoTV.pl"),
    "Kino TV HD": ("kino-tv-hd-663", "KinoTVHD.pl"),
    "Kus Kus": ("kus-kus", "KusKus.pl"),
    "Kvartal TV": ("kvartal-tv", "KvartalTV.pl"),
    "Lubelska.tv": ("lubelska-tv-210", "Lubelska.tv.pl"),
    "M 6": ("m-6-215", "M6.pl"),
    "MCM Top": ("mcm-top-459", "MCMTop.pl"),
    "MDR": ("mdr-381", "MDR.pl"),
    "METRO": ("metro-535", "METRO.pl"),
    "METRO HD": ("metro-hd-536", "METROHD.pl"),
    "Mezzo": ("mezzo-234", "Mezzo.pl"),
    "Mezzo Live HD": ("mezzo-live-hd-398", "MezzoLiveHD.pl"),
    "MiniMini+": ("minimini-236", "MiniMiniPlus.pl"),
    "MiniMini+ HD": ("minimini-hd-435", "MiniMiniPlusHD.pl"),
    "MIXTAPE": ("mixtape", "MIXTAPE.pl"),
    "Motorvision": ("motorvision-341", "Motorvision.pl"),
    "Motowizja": ("motowizja-178", "Motowizja.pl"),
    "Motowizja HD": ("motowizja-hd-194", "MotowizjaHD.pl"),
    "MTV Europe": ("mtv-europe-118", "MTVEurope.pl"),
    "MTV Germany": ("mtv-germany-382", "MTVGermany.pl"),
    "MTV Polska": ("mtv-polska-7", "MTVPolska.pl"),
    "MTV Polska HD": ("mtv-polska-hd-557", "MTVPolskaHD.pl"),
    "muenchen.tv": ("muenchen-tv-486", "muenchen.tv.pl"),
    "Museum TV 4K": ("museum-tv-4k", "MuseumTV4K.pl"),
    "Music Box": ("music-box-538", "MusicBox.pl"),
    "Music Box HD": ("music-box-hd-539", "MusicBoxHD.pl"),
    "MyZen 4K": ("myzen-4k", "MyZen4K.pl"),
    "MyZen.tv HD": ("myzen-tv-hd-396", "MyZen.tvHD.pl"),
    "NASA TV": ("nasa-tv", "NASATV.pl"),
    "Nat Geo People": ("nat-geo-people-625", "NatGeoPeople.pl"),
    "Nat Geo People HD": ("nat-geo-people-hd-211", "NatGeoPeopleHD.pl"),
    "National Geographic": ("national-geographic-channel-32", "NationalGeographic.pl"),
    "National Geographic HD": ("national-geographic-channel-hd-34", "NationalGeographicHD.pl"),
    "National Geographic Wild": ("nat-geo-wild-77", "NationalGeographicWild.pl"),
    "National Geographic Wild HD": ("nat-geo-wild-hd-121", "NationalGeographicWildHD.pl"),
    "Nautical Channel": ("nautical-channel-116", "NauticalChannel.pl"),
    "Nautical Channel HD": ("nautical-channel-hd-626", "NauticalChannelHD.pl"),
    "NDR": ("ndr-383", "NDR.pl"),
    "News24": ("news24", "News24.pl"),
    "NHK World TV": ("nhk-world-tv-11", "NHKWorldTV.pl"),
    "NICK": ("nick-488", "NICK.pl"),
    "Nick Jr.": ("nick-jr-45", "NickJr..pl"),
    "Nick Jr. HD": ("nick-jr-hd-662", "NickJr.HD.pl"),
    "Nickelodeon": ("nickelodeon-42", "Nickelodeon.pl"),
    "Nicktoons": ("nickelodeon-hd-44", "Nicktoons.pl"),
    "Nicktoons HD": ("nicktoons-hd-631", "NicktoonsHD.pl"),
    "Nitro": ("rtl-nitro-545", "Nitro.pl"),
    "Nova": ("nova-331", "Nova.pl"),
    "Novela tv": ("novela-tv-461", "Novelatv.pl"),
    "Novela tv HD": ("novela-tv-hd-155", "NovelatvHD.pl"),
    "Novelas+": ("novelas", "NovelasPlus.pl"),
    "Novelas+1": ("dizi-692", "NovelasPlus1.pl"),
    "Nowa TV": ("nowa-tv-528", "NowaTV.pl"),
    "Nowa TV HD": ("nowa-tv-hd-529", "NowaTVHD.pl"),
    "NPO 1": ("npo-1-385", "NPO1.pl"),
    "NPO 2": ("npo-2-505", "NPO2.pl"),
    "NPO 3": ("npo-3-387", "NPO3.pl"),
    "n-tv": ("n-tv-388", "n-tv.pl"),
    "Nuta Gold": ("nuta-gold", "NutaGold.pl"),
    "Nuta.TV": ("nuta-tv-214", "Nuta.TV.pl"),
    "Nuta.TV HD": ("nuta-tv-hd-213", "Nuta.TVHD.pl"),
    "ONE": ("einsfestival-363", "ONE.pl"),
    "ONTV": ("ontv-137", "ONTV.pl"),
    "ONTV HD": ("ontv-hd-161", "ONTVHD.pl"),
    "ORF 1": ("orf-1-390", "ORF1.pl"),
    "ORF 2": ("orf-2-393", "ORF2.pl"),
    "Paramount Network": ("paramount-channel-hd-65", "ParamountNetwork.pl"),
    "Phoenix": ("phoenix-391", "Phoenix.pl"),
    "Planete+": ("planete-349", "PlanetePlus.pl"),
    "Planete+ HD": ("planete-hd-432", "PlanetePlusHD.pl"),
    "Playboy TV": ("playboy-tv-482", "PlayboyTV.pl"),
    "Polo TV": ("polo-tv-135", "PoloTV.pl"),
    "Polonia 1": ("polonia-1-328", "Polonia1.pl"),
    "Polsat": ("polsat-38", "Polsat.pl"),
    "Polsat 1": ("polsat-1-36", "Polsat1.pl"),
    "Polsat 2": ("polsat-2-327", "Polsat2.pl"),
    "Polsat 2 HD": ("polsat-2-hd-218", "Polsat2HD.pl"),
    "Polsat Café": ("polsat-caf-110", "PolsatCafé.pl"),
    "Polsat Café HD": ("polsat-caf-hd-219", "PolsatCaféHD.pl"),
    "Polsat Comedy Central Extra": ("comedy-central-family-61", "PolsatComedyCentralExtra.pl"),
    "Polsat Comedy Central Extra HD": ("comedy-central-family-hd-612", "PolsatComedyCentralExtraHD.pl"),
    "Polsat Doku": ("polsat-doku-548", "PolsatDoku.pl"),
    "Polsat Doku HD": ("polsat-doku-hd-551", "PolsatDokuHD.pl"),
    "Polsat Film": ("polsat-film-123", "PolsatFilm.pl"),
    "Polsat Film HD": ("polsat-film-hd-162", "PolsatFilmHD.pl"),
    "Polsat Games": ("polsat-games-653", "PolsatGames.pl"),
    "Polsat Games HD": ("polsat-games-hd-670", "PolsatGamesHD.pl"),
    "Polsat HD": ("polsat-hd-35", "PolsatHD.pl"),
    "Polsat JimJam": ("polsat-jimjam-89", "PolsatJimJam.pl"),
    "Polsat Music": ("polsat-music-564", "PolsatMusic.pl"),
    "Polsat Music HD": ("muzo-tv-200", "PolsatMusicHD.pl"),
    "Polsat News": ("polsat-news-100", "PolsatNews.pl"),
    "Polsat News 2": ("polsat-news-2-471", "PolsatNews2.pl"),
    "Polsat News 2 HD": ("polsat-news-2-hd-671", "PolsatNews2HD.pl"),
    "Polsat News HD": ("polsat-news-hd-229", "PolsatNewsHD.pl"),
    "Polsat News Polityka": ("polsat-news-polityka", "PolsatNewsPolityka.pl"),
    "Polsat Play": ("polsat-play-21", "PolsatPlay.pl"),
    "Polsat Play HD": ("polsat-play-hd-22", "PolsatPlayHD.pl"),
    "Polsat Rodzina": ("polsat-rodzina-651", "PolsatRodzina.pl"),
    "Polsat Rodzina HD": ("polsat-rodzina-hd-672", "PolsatRodzinaHD.pl"),
    "Polsat Seriale": ("polsat-romans-173", "PolsatSeriale.pl"),
    "Polsat Sport 1": ("polsat-sport-334", "PolsatSport1.pl"),
    "Polsat Sport 1 HD": ("polsat-sport-hd-96", "PolsatSport1HD.pl"),
    "Polsat Sport 2": ("polsat-sport-extra-485", "PolsatSport2.pl"),
    "Polsat Sport 2 HD": ("polsat-sport-extra-hd-144", "PolsatSport2HD.pl"),
    "Polsat Sport 3": ("polsat-sport-news-431", "PolsatSport3.pl"),
    "Polsat Sport 3 HD": ("polsat-sport-news-hd-543", "PolsatSport3HD.pl"),
    "Polsat Sport Extra 1": ("polsat-sport-premium-3-645", "PolsatSportExtra1.pl"),
    "Polsat Sport Extra 2": ("polsat-sport-premium-4-646", "PolsatSportExtra2.pl"),
    "Polsat Sport Extra 3": ("polsat-sport-premium-5-642", "PolsatSportExtra3.pl"),
    "Polsat Sport Extra 4": ("polsat-sport-premium-6-641", "PolsatSportExtra4.pl"),
    "Polsat Sport Fight": ("polsat-sport-fight-546", "PolsatSportFight.pl"),
    "Polsat Sport Fight HD": ("polsat-sport-fight-521", "PolsatSportFightHD.pl"),
    "Polsat Sport Premium 1": ("polsat-sport-premium-1-643", "PolsatSportPremium1.pl"),
    "Polsat Sport Premium 2": ("polsat-sport-premium-2-644", "PolsatSportPremium2.pl"),
    "Polsat Viasat Explore HD": ("polsat-viasat-explore-hd-82", "PolsatViasatExploreHD.pl"),
    "Polsat Viasat History HD": ("polsat-viasat-history-hd-71", "PolsatViasatHistoryHD.pl"),
    "Polsat Viasat Nature HD": ("polsat-viasat-nature-413", "PolsatViasatNatureHD.pl"),
    "Polskie Radio Program 1": ("polskie-radio-program-1-460", "PolskieRadioProgram1.pl"),
    "Polskie Radio Program 2": ("polskie-radio-program-2-494", "PolskieRadioProgram2.pl"),
    "Power TV": ("power-tv-176", "PowerTV.pl"),
    "Power TV HD": ("power-tv-hd-177", "PowerTVHD.pl"),
    "Private TV HD": ("private-tv-351", "PrivateTVHD.pl"),
    "PRO 7": ("pro-7-395", "PRO7.pl"),
    "PROART HD": ("proart-hd-606", "PROARTHD.pl"),
    "PULS 2": ("puls-2-439", "PULS2.pl"),
    "PULS 2 HD": ("puls-2-hd-199", "PULS2HD.pl"),
    "QVC": ("qvc-397", "QVC.pl"),
    "Radio 357": ("radio-357", "Radio357.pl"),
    "Radio Nowy Świat": ("radio-nowy-swiat", "RadioNowyŚwiat.pl"),
    "Radio Silesia": ("radio-silesia", "RadioSilesia.pl"),
    "RAI 1": ("rai-1-338", "RAI1.pl"),
    "RAI 2": ("rai-2-336", "RAI2.pl"),
    "RAI 3": ("rai-3-337", "RAI3.pl"),
    "Rai News 24": ("rai-news-24", "RaiNews24.pl"),
    "RBB": ("rbb-466", "RBB.pl"),
    "Reality Kings TV": ("reality-kings-tv-223", "RealityKingsTV.pl"),
    "Record TV": ("record-tv-64", "RecordTV.pl"),
    "Redlight": ("redlight-499", "Redlight.pl"),
    "Redlight HD": ("redlight-hd-498", "RedlightHD.pl"),
    "Republika": ("tv-republika-18", "Republika.pl"),
    "Republika HD": ("tv-republika-hd-16", "RepublikaHD.pl"),
    "RFM TV": ("rfm-tv-95", "RFMTV.pl"),
    "Romance TV": ("romance-tv-129", "RomanceTV.pl"),
    "Romance TV HD": ("romance-tv-hd-139", "RomanceTVHD.pl"),
    "RTL": ("rtl-401", "RTL.pl"),
    "RTL 102.5": ("rtl-102-5-43", "RTL102.5.pl"),
    "RTL HD": ("rtl-hd-204", "RTLHD.pl"),
    "RTLZWEI": ("rtl-2-399", "RTLZWEI.pl"),
    "RTS Deux": ("rts-deux-411", "RTSDeux.pl"),
    "RTS Un": ("rts-un-410", "RTSUn.pl"),
    "SAT.1": ("sat-1-404", "SAT.1.pl"),
    "SBN": ("sbn-630", "SBN.pl"),
    "SCI FI": ("scifi-universal-20", "SCIFI.pl"),
    "SCI FI HD": ("sci-fi-hd-628", "SCIFIHD.pl"),
    "Show TV": ("etv-473", "ShowTV.pl"),
    "Show TV HD": ("etv-hd-154", "ShowTVHD.pl"),
    "sixx": ("sixx-447", "sixx.pl"),
    "Sky Action": ("sky-action-368", "SkyAction.pl"),
    "Sky Cinema": ("sky-cinema-480", "SkyCinema.pl"),
    "Sky Cinema Special": ("sky-nostalgie-421", "SkyCinemaSpecial.pl"),
    "Sky Fussball Bundesliga": ("sky-fussball-bundesliga-449", "SkyFussballBundesliga.pl"),
    "Sky Krimi": ("sky-krimi-422", "SkyKrimi.pl"),
    "Sky News": ("sky-news-340", "SkyNews.pl"),
    "Sky Sport Austria": ("sky-sport-austria-444", "SkySportAustria.pl"),
    "Sky Sport HD 1": ("sky-sport-hd-1-445", "SkySportHD1.pl"),
    "Spiegel Geschichte": ("spiegel-geschichte-379", "SpiegelGeschichte.pl"),
    "Sport 1": ("sport-1-362", "Sport1.pl"),
    "Sportklub": ("sportklub-29", "Sportklub.pl"),
    "Sportklub HD": ("sportklub-hd-620", "SportklubHD.pl"),
    "Sportowa.TV": ("sportowatv", "Sportowa.TV.pl"),
    "Spreekanal": ("spreekanal-502", "Spreekanal.pl"),
    "SRF 1": ("srf-1-406", "SRF1.pl"),
    "SRF Zwei": ("srf-zwei-407", "SRFZwei.pl"),
    "STARS.TV": ("stars-tv-149", "STARS.TV.pl"),
    "STARS.TV HD": ("stars-tv-hd-122", "STARS.TVHD.pl"),
    "Stingray Classica": ("classica-259", "StingrayClassica.pl"),
    "Stingray Classica HD": ("classica-hd-281", "StingrayClassicaHD.pl"),
    "Stingray CMusic": ("c-music-tv-260", "StingrayCMusic.pl"),
    "Stingray DJAZZ": ("djazz-tv-196", "StingrayDJAZZ.pl"),
    "Stingray DJAZZ HD": ("stingray-djazz-hd-619", "StingrayDJAZZHD.pl"),
    "Stingray Festival 4K": ("festival-4k-544", "StingrayFestival4K.pl"),
    "Stingray iConcerts": ("stingray-iconcert-601", "StingrayiConcerts.pl"),
    "Stingray iConcerts HD": ("stingray-iconcerts-hd-681", "StingrayiConcertsHD.pl"),
    "Stingray Juicebox HD": ("stingray-juicebox-hd-655", "StingrayJuiceboxHD.pl"),
    "Stingray Loud HD": ("stingray-loud-hd-654", "StingrayLoudHD.pl"),
    "Stingray Retro": ("stingray-retro-668", "StingrayRetro.pl"),
    "STOPKLATKA": ("stopklatka-tv-185", "STOPKLATKA.pl"),
    "STOPKLATKA HD": ("stopklatka-hd-186", "STOPKLATKAHD.pl"),
    "StudioMED TV": ("studiomed-tv-688", "StudioMEDTV.pl"),
    "Sundance TV": ("sundance-channel-237", "SundanceTV.pl"),
    "Sundance TV HD": ("sundance-channel-hd-392", "SundanceTVHD.pl"),
    "Super Polsat": ("super-polsat-541", "SuperPolsat.pl"),
    "Super Polsat HD": ("super-polsat-hd-560", "SuperPolsatHD.pl"),
    "Super RTL": ("super-rtl-400", "SuperRTL.pl"),
    "SWR": ("swr-408", "SWR.pl"),
    "Syfy": ("syfy-402", "Syfy.pl"),
    "TBN Polska": ("tbn-polska-598", "TBNPolska.pl"),
    "TBN Polska HD": ("tbn-polska-hd-621", "TBNPolskaHD.pl"),
    "TeenNick": ("teennick", "TeenNick.pl"),
    "Tele 5": ("tele-5-352", "Tele5.pl"),
    "Tele 5 HD": ("tele-5-hd-147", "Tele5HD.pl"),
    "Tele 5 (niem.)": ("tele-5-niem-448", "Tele5(niem.).pl"),
    "teleTOON+": ("teletoon-232", "teleTOONPlus.pl"),
    "teleTOON+ HD": ("teletoon-hd-438", "teleTOONPlusHD.pl"),
    "Telewizja Pomerania": ("telewizja-pomerania-41", "TelewizjaPomerania.pl"),
    "TLC": ("tlc-238", "TLC.pl"),
    "TLC HD": ("tlc-hd-163", "TLCHD.pl"),
    "Top Kids": ("top-kids-225", "TopKids.pl"),
    "Top Kids HD": ("top-kids-hd-224", "TopKidsHD.pl"),
    "TOYA": ("toya-467", "TOYA.pl"),
    "Travel Channel": ("travel-channel-201", "TravelChannel.pl"),
    "Travel Channel HD": ("travel-channel-hd-152", "TravelChannelHD.pl"),
    "Travelxp 4K": ("travelxp-4k-659", "Travelxp4K.pl"),
    "Travelxp HD": ("travelxp-hd-656", "TravelxpHD.pl"),
    "TTV": ("ttv-624", "TTV.pl"),
    "TTV HD": ("ttv-33", "TTVHD.pl"),
    "TV 4": ("tv-4-360", "TV4.pl"),
    "TV 4 HD": ("tv-4-hd-222", "TV4HD.pl"),
    "TV 5 Monde Europe": ("tv-5-monde-europe-412", "TV5MondeEurope.pl"),
    "TV 6": ("tv-6-429", "TV6.pl"),
    "TV 6 HD": ("tv-6-hd-561", "TV6HD.pl"),
    "TV ASTA": ("tv-asta-495", "TVASTA.pl"),
    "TV ASTA HD": ("tv-asta-hd-552", "TVASTAHD.pl"),
    "TV Okazje": ("tvo-600", "TVOkazje.pl"),
    "TV Okazje HD": ("tv-okazje-hd-633", "TVOkazjeHD.pl"),
    "TV Puls": ("tv-puls-332", "TVPuls.pl"),
    "TV Puls HD": ("tv-puls-hd-197", "TVPulsHD.pl"),
    "TV Regio": ("tv-regio-679", "TVRegio.pl"),
    "TV Regionalna Lubin": ("tv-regionalna-lubin-166", "TVRegionalnaLubin.pl"),
    "TV Relax": ("tv-relax-496", "TVRelax.pl"),
    "TV Trwam": ("tv-trwam-108", "TVTrwam.pl"),
    "TV.Berlin": ("tv-berlin-414", "TV.Berlin.pl"),
    "TVC": ("ntl-radomsko-184", "TVC.pl"),
    "TVE": ("tve-330", "TVE.pl"),
    "TVN": ("tvn-357", "TVN.pl"),
    "TVN 24": ("tvn-24-347", "TVN24.pl"),
    "TVN 24 HD": ("tvn-24-hd-158", "TVN24HD.pl"),
    "TVN 7": ("tvn-7-326", "TVN7.pl"),
    "TVN 7 HD": ("tvn-7-hd-142", "TVN7HD.pl"),
    "TVN Fabuła": ("tvn-fabula-4", "TVNFabuła.pl"),
    "TVN Fabuła HD": ("tvn-fabula-hd-37", "TVNFabułaHD.pl"),
    "TVN HD": ("tvn-hd-98", "TVNHD.pl"),
    "TVN Style": ("tvn-style-472", "TVNStyle.pl"),
    "TVN Style HD": ("tvn-style-hd-141", "TVNStyleHD.pl"),
    "TVN Turbo": ("tvn-turbo-346", "TVNTurbo.pl"),
    "TVN Turbo HD": ("tvn-turbo-hd-143", "TVNTurboHD.pl"),
    "TVN24 BiS": ("tvn-24-biznes-i-swiat-6", "TVN24BiS.pl"),
    "TVN24 BiS HD": ("tvn-24-biznes-i-swiat-hd-537", "TVN24BiSHD.pl"),
    "TVP 1": ("tvp-1-321", "TVP1.pl"),
    "TVP 1 HD": ("tvp-1-hd-380", "TVP1HD.pl"),
    "TVP 2": ("tvp-2-323", "TVP2.pl"),
    "TVP 2 HD": ("tvp-2-hd-145", "TVP2HD.pl"),
    "TVP 3": ("tvp-3-172", "TVP3.pl"),
    "TVP 3 Białystok": ("tvp-3-bialystok-5", "TVP3Białystok.pl"),
    "TVP 3 Bydgoszcz": ("tvp-3-bydgoszcz-378", "TVP3Bydgoszcz.pl"),
    "TVP 3 Gdańsk": ("tvp-3-gdansk-386", "TVP3Gdańsk.pl"),
    "TVP 3 Gorzów Wielkopolski": ("tvp-3-gorzow-wielkopolski-342", "TVP3GorzówWielkopolski.pl"),
    "TVP 3 Katowice": ("tvp-3-katowice-394", "TVP3Katowice.pl"),
    "TVP 3 Kielce": ("tvp-3-kielce-475", "TVP3Kielce.pl"),
    "TVP 3 Kraków": ("tvp-3-krakow-403", "TVP3Kraków.pl"),
    "TVP 3 Lublin": ("tvp-3-lublin-409", "TVP3Lublin.pl"),
    "TVP 3 Łódź": ("tvp-3-lodz-416", "TVP3Łódź.pl"),
    "TVP 3 Olsztyn": ("tvp-3-olsztyn-339", "TVP3Olsztyn.pl"),
    "TVP 3 Opole": ("tvp-3-opole-335", "TVP3Opole.pl"),
    "TVP 3 Poznań": ("tvp-3-poznan-425", "TVP3Poznań.pl"),
    "TVP 3 Rzeszów": ("tvp-3-rzeszow-433", "TVP3Rzeszów.pl"),
    "TVP 3 Szczecin": ("tvp-3-szczecin-440", "TVP3Szczecin.pl"),
    "TVP 3 Warszawa": ("tvp-3-warszawa-446", "TVP3Warszawa.pl"),
    "TVP 3 Wrocław": ("tvp-3-wroclaw-454", "TVP3Wrocław.pl"),
    "TVP ABC": ("tvp-abc-182", "TVPABC.pl"),
    "TVP Dokument": ("tvp-dokument", "TVPDokument.pl"),
    "TVP HD": ("tvp-hd-101", "TVPHD.pl"),
    "TVP Historia": ("tvp-historia-74", "TVPHistoria.pl"),
    "TVP Info": ("tvp-info-462", "TVPInfo.pl"),
    "TVP Info HD": ("tvp-info-hd-525", "TVPInfoHD.pl"),
    "TVP Kobieta": ("tvp-kobieta", "TVPKobieta.pl"),
    "TVP Kultura": ("tvp-kultura-477", "TVPKultura.pl"),
    "TVP Kultura HD": ("tvp-kultura-hd-680", "TVPKulturaHD.pl"),
    "TVP Nauka": ("tvp-nauka", "TVPNauka.pl"),
    "TVP Polonia": ("tvp-polonia-325", "TVPPolonia.pl"),
    "TVP Rozrywka": ("tvp-rozrywka-159", "TVPRozrywka.pl"),
    "TVP Seriale": ("tvp-seriale-130", "TVPSeriale.pl"),
    "TVP Sport": ("tvp-sport-40", "TVPSport.pl"),
    "TVP Sport HD": ("tvp-sport-hd-39", "TVPSportHD.pl"),
    "TVP Wilno": ("tvp-wilno", "TVPWilno.pl"),
    "TVP World": ("tvp-world", "TVPWorld.pl"),
    "tvregionalna.pl": ("tvregionalna-pl-622", "tvregionalna.pl.pl"),
    "TVS": ("tvs-90", "TVS.pl"),
    "TVS HD": ("tvs-hd-109", "TVSHD.pl"),
    "TVT": ("tvt-500", "TVT.pl"),
    "Twoja Telewizja Morska": ("twoja-telewizja-morska-490", "TwojaTelewizjaMorska.pl"),
    "Twoja.TV": ("twoja-tv-514", "Twoja.TV.pl"),
    "ULTRA TV 4K": ("ultra-tv-4k-669", "ULTRATV4K.pl"),
    "ViDoc TV": ("ctv9", "ViDocTV.pl"),
    "ViDoc TV1": ("red-top-tv", "ViDocTV1.pl"),
    "Vivid RED HD": ("vivid-red-hd-627", "VividREDHD.pl"),
    "Vivid Touch": ("vivid-touch-636", "VividTouch.pl"),
    "VOX": ("vox-418", "VOX.pl"),
    "VOX Music TV": ("vox-music-tv-193", "VOXMusicTV.pl"),
    "Warner TV": ("tnt-72", "WarnerTV.pl"),
    "Warner TV HD": ("tnt-hd-220", "WarnerTVHD.pl"),
    "Water Planet": ("water-planet-415", "WaterPlanet.pl"),
    "Water Planet HD": ("water-planet-hd-156", "WaterPlanetHD.pl"),
    "WDR": ("wdr-420", "WDR.pl"),
    "WELT": ("n-24-384", "WELT.pl"),
    "WP": ("wp-532", "WP.pl"),
    "WP HD": ("wp-hd-533", "WPHD.pl"),
    "wPolsce24": ("wpolsce-pl-635", "wPolsce24.pl"),
    "wPolsce24 HD": ("wpolsce-pl-hd-637", "wPolsce24HD.pl"),
    "WTK": ("wtk-492", "WTK.pl"),
    "Wydarzenia 24": ("superstacja-69", "Wydarzenia24.pl"),
    "Wydarzenia 24 HD": ("superstacja-hd-550", "Wydarzenia24HD.pl"),
    "XSport": ("xsport", "XSport.pl"),
    "XTREME TV": ("super-tv-690", "XTREMETV.pl"),
    "ZDF": ("zdf-417", "ZDF.pl"),
    "ZDF HD": ("zdf-hd-136", "ZDFHD.pl"),
    "ZDF Info": ("zdf-info-430", "ZDFInfo.pl"),
    "ZOOM TV": ("zoom-tv-526", "ZOOMTV.pl"),
    "ZOOM TV HD": ("zoom-tv-hd-527", "ZOOMTVHD.pl"),
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
