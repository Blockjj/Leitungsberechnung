import tkinter as tk
from GUI import LeitungsberechnungGUI


def splash_screen():
    splash = tk.Tk()
    splash.title("Lädt...")
    splash.geometry("450x300")
    #splash.iconbitmap('Grafiken\Kabellänge.ico')

    label = tk.Label(splash, text="Leitungsberechnungsprogramm", font=("Arial", 18))
    label.pack(pady=50)

    # Fenster für 3 Sekunden anzeigen, bevor es schließt und die Haupt-GUI startet
    splash.after(2000, splash.destroy)
    splash.mainloop()


if __name__ == "__main__":
    splash_screen()
    root = tk.Tk()
    #root.iconbitmap('Grafiken\Kabellänge.ico') 
    app = LeitungsberechnungGUI(root)
    root.mainloop()
