import tkinter as tk
from tkinter import ttk
import berechnungen as br
import traceback

class LeitungsberechnungGUI:
    def __init__(self, root):
        # Initialisiere das Hauptfenster
        self.root = root
        self.root.title("Leitungsberechnung")

        # Frame für die Eingaben und Labels
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Validierungsfunktion an Tkinter registrieren
        self.vcmd = (self.root.register(self.validate_float), '%P')

        # Initialisiere die GUI-Komponenten
        self.create_widgets()
    
    def berechnen_button(self):
        try:
            # 1.Variablen generieren
            leitungslange = float(self.leitungslange_var.get())
            I_B = float(self.betriebsstrom_var.get())
            cos_phi = float(self.wirkfaktor_var.get())
            E = float(self.spannungsfall_var.get())
            kappa = 56
            netzform = self.netzform_var.get()
             # Temperatur Faktor bekommen
            zBetriebstemperatur_dict = {
                'Gummi Leitung 60°C': 'Zulässige Betriebstemperatur 60 °C',
                'PVC z.B. NYM Leitung 70°C': 'Zulässige Betriebstemperatur 70 °C',
                'VPE Leitung 90°C': 'Zulässige Betriebstemperatur 90 °C'}
            umgebungstemperatur = int(self.umgebungstemperatur_var.get())
            zulässige_Betriebstemperatur = zBetriebstemperatur_dict.get(self.zBetriebstemperatur_var.get())
            faktor_Temperatur = br.get_TemperaturFaktor(umgebungstemperatur, zulässige_Betriebstemperatur)
            # Häufungsfaktor bekommen
            nLeitungenH = int(self.nLeitungenH_var.get())
            verlegeartHäufung_dict = { 'perf. Kabelrinne, mehrlagige Verlegung':'A_1',
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
                                    'Kabelpritschen 6':'F_4' }
            verlegeartHäufung = verlegeartHäufung_dict.get(self.verlegeartHäufung_var.get())
            faktor_Häufung = br.get_HäufungsFaktor(nLeitungenH, verlegeartHäufung)
            verlegeartStrombelastbarkeit = self.verlegeartStrombelastbarkeit_var.get()
            nennstrom = int(self.nennstrom_var.get())
            sicherungstyp = self.sicherungstyp_var.get()
            netzinnenwiderstand = int(self.netzinnenwiderstand_var.get())
            rcd_vorhanden = True if self.rcd_var.get() == "Ja" else False

            # 2.Berechnung der Querschnitte

            # Schutzmaßnahme
            # Ist ein RCD vorhanden kann auf die Rechnung verzichtet werden und die Ausnahme tritt in Kraft
            if rcd_vorhanden:
                rechnung_schutzmaßnahme = {
                "RCD vorhanden": rcd_vorhanden,
                "Ausnahme:":"Entfällt aufgrund RCD gem. DIN VDE 0100-520",
                "Querschnitt ": 1.5
                }
            else: 
                querschnitt_schutzmassnahme = br.berechne_schutzmassnahme(netzinnenwiderstand, sicherungstyp, nennstrom, leitungslange, kappa)
                rechnung_schutzmaßnahme = {
                    "RCD vorhanden": rcd_vorhanden,
                    "Netzinnenwiderstand in mOhm": netzinnenwiderstand,
                    "Sicherungstyp": sicherungstyp,
                    "Nennstrom": nennstrom,
                    "Leitungslänge in m": leitungslange,
                    "Leitwert": kappa,
                    "Querschnitt": querschnitt_schutzmassnahme
                }

            #Spannungsfall
            querschnitt_spannungsfall = br.berechne_spannungsfall(leitungslange, I_B, cos_phi, E, kappa, netzform)
            rechnung_spannungsfall = {
                "Leitungslänge in m": leitungslange,
                "Betriebsstrom in A": I_B,
                "Cos phi": cos_phi,
                "Netzform": netzform,
                "Faktor Spannungsfall": E
            }
            rechnung_spannungsfall.update(querschnitt_spannungsfall)

            #Strombelastbarkeit
            querschnitt_strombelastbarkeit = br.berechne_strombelastbarkeit(faktor_Temperatur, faktor_Häufung, I_B, verlegeartStrombelastbarkeit, netzform)
            rechnung_strombelastbarkeit = {
                "Umgebungstemperatur": umgebungstemperatur,
                "zulässige Betriebstemperatur": zulässige_Betriebstemperatur,
                "Temperaturfaktor aus TB S64": faktor_Temperatur,
                "Verlegeart Häufung": self.verlegeartHäufung_var.get(),
                "N Leitungen Häufung": nLeitungenH,
                "Häufungsfaktor aus TB S66": faktor_Häufung,
                "Betriebsstrom in A": I_B,
                "Verlegeart Strombelastbarkeit aus TB S63": verlegeartStrombelastbarkeit,
                "Netzform": netzform
            }
            try:
                rechnung_strombelastbarkeit.update(querschnitt_strombelastbarkeit)
            except:
                rechnung_strombelastbarkeit["Querschnitt ungültig Eingabe Überprüfen"] =  404

            #Überlastschutz
            querschnitt_überlastschutz = br.berechne_überlastschutz(faktor_Temperatur, faktor_Häufung, I_B, nennstrom, verlegeartStrombelastbarkeit, netzform)
            rechnung_überlastschutz = {
                "Umgebungstemperatur": umgebungstemperatur,
                "zulässige Betriebstemperatur": zulässige_Betriebstemperatur,
                "Temperaturfaktor aus TB S 64": faktor_Temperatur,
                "Verlegeart Häufung": self.verlegeartHäufung_var.get(),
                "N Leitungen Häufung": nLeitungenH,
                "Häufungsfaktor aus TB S 66": faktor_Häufung,
                "Betriebsstrom in A": I_B,
                "Verlegeart Strombelastbarkeit aus TB S63": verlegeartStrombelastbarkeit,
                "Netzform": netzform
            }
            try:
                rechnung_überlastschutz.update(querschnitt_überlastschutz)
            except:
                rechnung_überlastschutz["Querschnitt ungültig Eingabe Überprüfen"] =  404

            #Kurzschluss
            querschnitt_kurzschluss = br.berechne_kurzschlussstrom(sicherungstyp, nennstrom, netzinnenwiderstand, leitungslange)
            rechnung_kurzschluss = {
                "Sicherungstyp": sicherungstyp,
                "Nennstrom der Sicherung": nennstrom,
                "Netzinnenwiderstand in mOhm": netzinnenwiderstand,
                "Leitungslänge": leitungslange
            }
            try:
                rechnung_kurzschluss.update(querschnitt_kurzschluss)
            except:
                rechnung_kurzschluss["Querschnitt ungültig Eingabe Überprüfen"] =  404

            # Ergebnisse in einem Dict zusammenfassen
            Rechnungen = {
                "Schutzmaßnahme": rechnung_schutzmaßnahme,
                "Spannungsfall": rechnung_spannungsfall,
                "Strombelastbarkeit": rechnung_strombelastbarkeit,
                "Überlastschutz": rechnung_überlastschutz,
                "Kurzschluss aus TB S 68-70": rechnung_kurzschluss
            }

            # Ergebnis anzeigen
            self.anzeigen_ergebnis(Rechnungen)
        
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            print(f"Fehler bei der Berechnung: {e}")
            print(f"Fehler in Zeile: {tb[-1].lineno}")

    def anzeigen_ergebnis(self, rechnungen):
        ergebnis_fenster = tk.Toplevel()
        ergebnis_fenster.title("Ergebnis")

        # Ausgabe der Rechnungen
        col_counter = 0
        row_counter = 0
        for key in rechnungen.keys():
            ttk.Label(ergebnis_fenster, text=key).grid(row=row_counter, column=col_counter, padx=10, pady=5)
            col_counter += 1
        
        row_counter += 1
        max_values_length = max(len(v) for v in rechnungen.values())  # Maximale Anzahl an Werten finden
        for i in range(max_values_length):
            col_counter = 0
            for key, value in rechnungen.items():
                if isinstance(value, dict):
                    sub_keys = list(value.keys())
                    sub_values = list(value.values())
                    if i < len(sub_values):  # Überprüfen, ob es einen Wert gibt
                        ttk.Label(ergebnis_fenster, text=f"{sub_keys[i]}: {sub_values[i]}").grid(row=row_counter, column=col_counter, padx=10, pady=5)
                col_counter += 1
            row_counter += 1

        # Schließen-Button
        ttk.Button(ergebnis_fenster, text="Schließen", command=ergebnis_fenster.destroy).pack(pady=10)
    # Validierungsfunktion, um nur Zahlen und einen Punkt zuzulassen
    def validate_float(self, input_str):
        # Erlaubt leere Eingaben (wichtig, um Eingaben zu löschen)
        if input_str == "":
            return True
        try:
            # Prüfe, ob der Input in einen Float konvertierbar ist
            float(input_str)
            return True
        except ValueError:
            return False
    #Funktion zu erstellung des Widgets
    def create_widgets(self):
        # Eingabefeld RCD 
        self.rcd_var = tk.StringVar(value="Ja")
        ttk.Label(self.frame, text="RCD vorhanden (Ja/Nein):").grid(row=0, column=0, sticky=tk.W)
        self.rcd_dropdown = ttk.Combobox(self.frame, textvariable=self.rcd_var)
        self.rcd_dropdown['values'] = ('Ja', 'Nein')
        self.rcd_dropdown.grid(row=0, column=1)

        # Eingabefeld Leitungslänge
        self.leitungslange_var = tk.StringVar()
        ttk.Label(self.frame, text="Leitungslänge (m):").grid(row=1, column=0, sticky=tk.W)
        self.leitungslange_entry = ttk.Entry(self.frame, textvariable=self.leitungslange_var, validate="key", validatecommand=self.vcmd)
        self.leitungslange_entry.grid(row=1, column=1)

        # Eingabefeld Betriebsstrom
        self.betriebsstrom_var = tk.StringVar()
        ttk.Label(self.frame, text="Betriebsstrom I_B [A]:").grid(row=2, column=0, sticky=tk.W)
        self.betriebsstrom_entry = ttk.Entry(self.frame, textvariable=self.betriebsstrom_var, validate="key", validatecommand=self.vcmd)
        self.betriebsstrom_entry.grid(row=2, column=1)

        # Eingabefeld Wirkfaktor
        self.wirkfaktor_var = tk.StringVar(value = '0.95')
        ttk.Label(self.frame, text="Wirkfaktor cos φ:").grid(row=3, column=0, sticky=tk.W)
        self.wirkfaktor_entry = ttk.Entry(self.frame, textvariable=self.wirkfaktor_var, validate="key", validatecommand=self.vcmd)
        self.wirkfaktor_entry.grid(row=3, column=1)

        # Eingabefeld Spannungsfall in 0 - 1
        self.spannungsfall_var = tk.StringVar(value = '0.03')
        ttk.Label(self.frame, text="Spannungsfall [zwischen 0 - 1]:").grid(row=4, column=0, sticky=tk.W)
        self.spannungsfall_entry = ttk.Entry(self.frame, textvariable=self.spannungsfall_var, validate="key", validatecommand=self.vcmd)
        self.spannungsfall_entry.grid(row=4, column=1)

        # Eingabefeld netzform 
        self.netzform_var = tk.StringVar(value="Drehstrom")
        ttk.Label(self.frame, text="Netzform (Drehstrom/Wechselstrom):").grid(row=5, column=0, sticky=tk.W)
        self.netzform_dropdown = ttk.Combobox(self.frame, textvariable=self.netzform_var)
        self.netzform_dropdown['values'] = ('Drehstrom', 'Wechselstrom')
        self.netzform_dropdown.grid(row=5, column=1)

        #Eingabe Umgebungstemperatur
        self.umgebungstemperatur_var = tk.StringVar(value=30)
        ttk.Label(self.frame, text="Umgebungstemperatur in °C:").grid(row=6, column=0, sticky=tk.W)
        self.umgebungstemperatur_dropdown = ttk.Combobox(self.frame, textvariable=self.umgebungstemperatur_var)
        self.umgebungstemperatur_dropdown['values'] = (10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85)
        self.umgebungstemperatur_dropdown.grid(row=6, column=1)

        #Eingabe zulässige Betriebstemperatur Leitung
        self.zBetriebstemperatur_var = tk.StringVar(value='PVC z.B. NYM Leitung 70°C')
        ttk.Label(self.frame, text="Betriebstemperatur der Leitung:").grid(row=7, column=0, sticky=tk.W)
        self.zBetriebstemperatur_dropdown = ttk.Combobox(self.frame, textvariable=self.zBetriebstemperatur_var, width=30)
        self.zBetriebstemperatur_dropdown['values'] = ('Gummi Leitung 60°C', 'PVC z.B. NYM Leitung 70°C', 'VPE Leitung 90°C')
        self.zBetriebstemperatur_dropdown.grid(row=7, column=1)  

        #Eingabe Verlegeart Häufung 
        self.verlegeartHäufung_var = tk.StringVar(value='Unperforierte Kabelwanne 1')
        ttk.Label(self.frame, text="Verlegeart Häufung:").grid(row=8, column=0, sticky=tk.W)
        self.verlegeartHäufung_dropdown = ttk.Combobox(self.frame, textvariable= self.verlegeartHäufung_var, width=65)
        self.verlegeartHäufung_dropdown['values'] = ('perf. Kabelrinne, mehrlagige Verlegung',
                                                'Einlagig auf Wand/Boden mit Berührung',
                                                'Einlagig auf Wand/Boden mit Zwischenraum >Leitungsdurchmesser',
                                                'Einlagig unter Decke mit Berührung',
                                                'Einlagig unter Decke mit Zwischenraum >Leitungsdurchmesser',
                                                'Unperforierte Kabelwanne 1',
                                                'Unperforierte Kabelwanne 2',
                                                'Unperforierte Kabelwanne 3',
                                                'Unperforierte Kabelwanne 6',
                                                'Perforierte Kabelwanne 1',
                                                'Perforierte Kabelwanne 2',
                                                'Perforierte Kabelwanne 3',
                                                'Perforierte Kabelwanne 6',
                                                'Kabelpritschen 1',
                                                'Kabelpritschen 2',
                                                'Kabelpritschen 3',
                                                'Kabelpritschen 6'
                                                )
        self.verlegeartHäufung_dropdown.grid(row=8, column=1)

        
        # N Leitungen Häufung
        self.nLeitungenH_var = tk.StringVar()
        ttk.Label(self.frame, text="Anzahl der Leitungen (Häufung):").grid(row=9, column=0, sticky=tk.W)
        self.nLeitungenH_entry = ttk.Entry(self.frame, textvariable=self.nLeitungenH_var, validate="key", validatecommand=self.vcmd)
        self.nLeitungenH_entry.grid(row=9, column=1)
        
        #Eingabe Verlegeart Strombelastbarkeit
        self.verlegeartStrombelastbarkeit_var = tk.StringVar(value='C')
        ttk.Label(self.frame, text ="Verlegeart Strombelastbarkeit").grid(row=10, column=0, sticky=tk.W)
        self.verlegeartStrombelastbarkeit_dropdown = ttk.Combobox(self.frame, textvariable=self.verlegeartStrombelastbarkeit_var)
        self.verlegeartStrombelastbarkeit_dropdown['values'] = ('A1', 'A2', 'B1', 'B2', 'C', 'E')
        self.verlegeartStrombelastbarkeit_dropdown.grid(row=10, column=1) 

        #Eingabe Nennstrom Sicherung
        self.nennstrom_var = tk.StringVar()
        ttk.Label(self.frame, text="Nennstrom Sicherung").grid(row=11, column=0, sticky=tk.W)
        self.nennstrom_entry = ttk.Entry(self.frame, textvariable=self.nennstrom_var, validatecommand=self.vcmd)
        self.nennstrom_entry.grid(row=11, column=1)

        #Eingabe Sicherungstyp
        self.sicherungstyp_var = tk.StringVar(value='gG')
        ttk.Label(self.frame, text ="Sicherungstyp").grid(row=12, column=0, sticky=tk.W)
        self.sicherungstyp_dropdown = ttk.Combobox(self.frame, textvariable=self.sicherungstyp_var)
        self.sicherungstyp_dropdown['values'] = ('gG', 'B', 'C')
        self.sicherungstyp_dropdown.grid(row=12, column=1) 

        #Eingabe Netzinnenwiderstand in m Ohm
        self.netzinnenwiderstand_var = tk.StringVar()
        ttk.Label(self.frame, text="Netzinnenwiderstand in mOhm:").grid(row=13, column=0, sticky=tk.W)
        self.netzinnenwiderstand_entry = ttk.Entry(self.frame, textvariable=self.netzinnenwiderstand_var, validate="key", validatecommand=self.vcmd)
        self.netzinnenwiderstand_entry.grid(row=13, column=1)

        # Button zur Berechnung
        self.berechnen_button = ttk.Button(self.frame, text="Berechnen", command=self.berechnen_button)
        self.berechnen_button.grid(row=14, column=1, sticky=tk.E)

        # Label für die Ausgabe
        self.result_label = ttk.Label(self.frame, text="Ergebnis:")
        self.result_label.grid(row=15, column=0, sticky=tk.W)
        self.output_label = ttk.Label(self.frame, text="")
        self.output_label.grid(row=15, column=1, sticky=tk.W)


# Starten der Anwendung
if __name__ == "__main__":
    root = tk.Tk()
    app = LeitungsberechnungGUI(root)
    root.mainloop()
    
