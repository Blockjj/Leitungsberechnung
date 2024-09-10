import pandas as pd

querschnitts_liste = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 75, 95, 120, 150, 185, 240, 300]

def berechne_schutzmassnahme(netzinnenwiderstand: float, Sicherungstyp: str, nennstrom: int, leitungslänge: float, kappa: float):
    
    # Berechnet den minimalen Querschnitt basierend auf der Schutzmaßnahme.
    
    faktor_dict = {'B': 5, 'C' : 10, 'gG' : 6}
    faktor = faktor_dict.get(Sicherungstyp)
    # benötigter Kurzschlussstrom der Sicherung berrechnen
    I_A = nennstrom * faktor
    #benötigter Leitungswiderstand für den Kurzschlussstrom berrechnen
    R_leitung = 230.0 / I_A - netzinnenwiderstand / 1000

    #benötigter Querschnitt berrechnen und runden
    A = (2*leitungslänge)/(kappa * R_leitung)
    A = querschnitt_runden(A)
    return A
    
def berechne_spannungsfall(Leitungslänge: float, I_B: float, cos_phi: float, kappa: float, E_Spannungsfall: float, netzform: str):
    # Auswahl der Netzform
    if netzform == "Drehstrom":
        # Berechnet absoluten Spannungsfall nach Netzform
        U_V = E_Spannungsfall * 400
        # Berechnet Querschnitt 
        A = (Leitungslänge * I_B * (3 ** 0.5) * cos_phi) / (U_V * kappa)
    else:
        U_V = E_Spannungsfall * 230
        A = (2 * Leitungslänge * I_B * cos_phi) / (U_V * kappa)

    # Ergebnisse in einem Dictonary zusammenfassen und Querschnitt runden, DICT zurückgeben
    spannungsfall = {"Spannungsfall absolut": U_V, "Querschnitt" : querschnitt_runden(A)}
    return spannungsfall
    """
    Argumente:
    Leitungslänge = Länge des Kabels in m
    I_B = Betriebsstrom in A
    cos_phi = Wirkleistungsfaktor zwischen 0 - 1
    kappa = Leitwert Material i.d.R. Kupfer 56
    E = Spannungsfall Faktor 0 - 1
    netzform = 'Drehstrom' OR 'Wechselstrom'
    """

def querschnitt_runden(A):
    # Rundet den Eingegebenen Querschnitt auf den nächst größtmöglichen, Maximal bis 300.
    for querschnitt in querschnitts_liste:
        if A <= querschnitt:
            return querschnitt
    raise ValueError("Querschnitt zu groß!")

def get_TemperaturFaktor(umgebungstemperatur, temp_isolierung):
    # CSV-Datei laden
    df = pd.read_csv(r'.\Tabellen\Umrechnungsfaktor Temperatur.csv', index_col='Umgebungstemperatur (°C)')

    # Überprüfen, ob die Umgebungstemperatur und die Betriebstemperatur gültig sind
    if umgebungstemperatur not in df.index:
        raise ValueError("Umgebungstemperatur nicht in der Tabelle gefunden.")
    
    if temp_isolierung not in df.columns:
        raise ValueError("Zulässige Betriebstemperatur nicht in der Tabelle gefunden.")
    
    # Wert aus der Tabelle extrahieren
    value = df.at[umgebungstemperatur, temp_isolierung]
    
    return value
    """
    Beispiel
    umgebungstemperatur = 25
    betriebstemperatur = 'Zulässige Betriebstemperatur 70 °C'

    value = get_TemperaturFaktor(30, 'Zulässige Betriebstemperatur 70 °C')
    value = 
    """

def get_HäufungsFaktor(n_Leitungen: int, Verlegeart: str):
    '''
    Verlegearten kommen als Value an SOLLTEN
    verlegeartHäufung_dict = {'perf. Kabelrinne, mehrlagige Verlegung':'A_1',
                                    'Einlagig auf Wand/Boden mit Berührung':'B_1',
                                    'Einlagig auf Wand/Boden mit Zwischenraum >Leitungsdurchmesser':'B_2',
                                    'Einlagig unter Decke mit Berührung':'C_1',
                                    'Einlagig unter Decke mit Zwischenraum >Leitungsdurchmesser':'C_2',
                                    'Unperforierte Kabelwanne 1':'D_1',
                                    'Unperforierte Kabelwanne 2':'D_2',
                                    'Unperforierte Kabelwanne 3':'D_3',
                                    'Unperforierte Kabelwanne 6':'D_4',
                                    'Perforierte Kabelwanne 1':'E_1',
                                    'Perforierte Kabelwanne 2':'E_2',
                                    'Perforierte Kabelwanne 3':'E_3',
                                    'Perforierte Kabelwanne 6':'E_4',
                                    'Kabelpritschen 1':'F_1',
                                    'Kabelpritschen 2':'F_2',
                                    'Kabelpritschen 3':'F_3',
                                    'Kabelpritschen 6':'F_4'}'''
    # CSV-Datei laden
    df = pd.read_csv(r'.\Tabellen\Faktor Häufung.csv', index_col='Verlegeart')
    # Überprüfen, ob die Verlegeart gültig ist
    if Verlegeart not in df.index:
        raise ValueError("Verlegeart nicht in der Tabelle gefunden.")
    
    # begrenzt die Leitungen auf 9
    if n_Leitungen > 9:
        n_Leitungen = 9

    n_Leitungen = str(n_Leitungen)

    if n_Leitungen not in df.columns:
        raise ValueError("Zulässige n_Leitungen nicht in der Tabelle gefunden.")
    
    # Wert aus der Tabelle extrahieren
    f_H = df.at[Verlegeart, n_Leitungen]
    
    return f_H

def berechne_strombelastbarkeit(f_T: float, f_H: float, I_B: float, Verlegeart: str, Netzform: str):
    # I_fiktiv berechnen
    I_fiktiv = I_B / (f_T * f_H)
    
    # CSV-Datei laden
    df = pd.read_csv(r'.\Tabellen\Strombelastbarkeit.csv', index_col='Querschnitt')

    #Verlegeart für CSV Datei optimieren in abhängigkeit von der Netzform
    if Netzform == "Drehstrom":
        Verlegeart = ' ' + Verlegeart + ' ' + str(3)
    else:
        Verlegeart = ' ' + Verlegeart + ' ' + str(2)

    # Überprüfen, ob die Verlegeart gültig ist    
    if Verlegeart not in df.columns:
        raise ValueError("Zulässige Verlegeart nicht in der Tabelle gefunden.")
    
    #Erstelle Variablen I_r Zulässiger Strom Leitung aus Tabelle und den dazugehörigen Querschnitt A
    I_r = 0
    A = 0

    #Schleife um den niedrigsten Querschnitt zu finden
    for querschnitt in df.index:
        A = querschnitt
        # Lese I_r aus Tabelle ab         
        I_r = df.at[A, Verlegeart]

        # Wenn I_r größer gleich I_fiktiv ist, dann wird die Schleife beendet
        if I_r >= I_fiktiv:
            break
        
    # Speicher die Daten in einem Dictionary
    strombelastbarkeit = {'I_r': float(I_r), 'Querschnitt': A}

    return strombelastbarkeit

    '''
    Gültige Verlegearten
    A1 , A1 , A2 , A2 , B1 , B1 , B2 , B2 , C , C , E , E 
    '''

def berechne_überlastschutz(f_T, f_H, I_B, I_N, Verlegeart, Netzform):
    #Variablen in float umwandeln
    f_T = float(f_T)
    f_H = float(f_H)
    I_B = float(I_B)
    I_N = float(I_N)
    I_r = 0
    I_Z = 0
    A = 0

    # CSV-Datei laden
    df = pd.read_csv(r'.\Tabellen\Strombelastbarkeit.csv', index_col='Querschnitt')

    if Netzform == "Drehstrom":
        Verlegeart = ' ' + Verlegeart + ' ' + str(3)
    else:
        Verlegeart = ' ' + Verlegeart + ' ' + str(2)

    # Überprüfen, ob die Verlegeart gültig ist    
    if Verlegeart not in df.columns:
        raise ValueError("Zulässige Verlegeart nicht in der Tabelle gefunden.")

    for querschnitt in df.index:
        A = querschnitt
        # Lese I_r aus Tabelle ab         
        I_r = df.at[A, Verlegeart]

        #Berechne I_Z
        I_Z = I_r * f_H * f_T

        # Wenn I_r größer gleich I_fiktiv ist, dann wird die Schleife beendet
        if I_Z >= I_N:
            break
        
    # Regel String erstellen
    regel = str(I_B) + '≤' + str(I_N) + '≤' + str(round(I_Z, 2))

    # Speicher die Daten in einem Dictionary
    strombelastbarkeit = {'I_r': float(I_r), 'I_B ≤ I_N ≤ I_Z':regel, 'Querschnitt': A}

    return strombelastbarkeit

def berechne_kurzschlussstrom(Sicherungstyp, Nennstromsicherung, Netzinnenwiderstand, Leitungslänge):
    if Sicherungstyp == 'gG':
        # CSV-Datei laden
        df = pd.read_csv(r'.\Tabellen\Grenzlänge gG.csv', index_col='Querschnitt')
    elif Sicherungstyp =='B':
        # CSV-Datei laden
        df = pd.read_csv(r'.\Tabellen\Grenzlänge B.csv', index_col='Querschnitt')
    elif Sicherungstyp == 'C':
        # CSV-Datei laden
        df = pd.read_csv(r'Tabellen\Grenzlänge C.csv', index_col='Querschnitt')
    else:
        return {'Sicherungstyp noch nicht implementiert' : 1}

    # Sicherstellen, dass alle Spalten, die Leitungslängen darstellen, als numerische Werte behandelt werden
    df = df.apply(pd.to_numeric, errors='coerce')

    # Filtern nach dem Nennstrom der Sicherung
    gefilterte_daten = df[df['Bemessungsstrom'] == Nennstromsicherung]
        
    # Netzinnenwiderstand aufrunden
    widerstandswerte = [10, 50, 100, 200, 300, 400, 500, 600, 700]
    R_N = 0
    for R in widerstandswerte:
        if Netzinnenwiderstand <= R:
            R_N = R
            break

    # Überprüfen, ob der Netzinnenwiderstand in den Daten enthalten ist
    if str(R_N) not in gefilterte_daten.columns:
        return {'Kein passender Netzinnenwiderstand in den Daten gefunden.' : 2}

    # Daten nach dem passenden Netzinnenwiderstand filtern
    gefilterte_daten = gefilterte_daten[gefilterte_daten[str(R_N)] >= Leitungslänge]

    if gefilterte_daten.empty:
        return {'Kein passender Querschnitt für diese Leitungslänge gefunden.' : 3}

    # Den kleinsten Querschnitt und die maximale Länge ermitteln
    A = gefilterte_daten.index[0]
    l_max = gefilterte_daten[str(R_N)].iloc[0]

    # Ergebnis in einem Dictionary speichern
    kurzschluss = {'Maximal Länge': float(l_max), 'Querschnitt': float(A)}

    return kurzschluss
           

#print(get_TemperaturFaktor(30, 'Zulässige Betriebstemperatur 70 °C'))
#print(get_HäufungsFaktor(3, 'A_1'))
#print(berechne_strombelastbarkeit(get_TemperaturFaktor(30, 'Zulässige Betriebstemperatur 70 °C'), get_HäufungsFaktor(3, 'A_1'), 14, 16, 'A2', 'Drehstrom'))
#print(berechne_überlastschutz(get_TemperaturFaktor(30, 'Zulässige Betriebstemperatur 70 °C'), get_HäufungsFaktor(3, 'A_1'), 14, 16, 'A2', 'Drehstrom'))
#print(berechne_kurzschlussstrom('C', 16, 34, 100))