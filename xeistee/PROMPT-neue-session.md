# X'Eistee Etikett - Übergabe an neue Session (Stand 10.10.)

Du übernimmst die Finalisierung des X'Eistee-Etiketts (Kräuterbergbauer, Bio-Kräutereistee, 330 ml). Flo (Florian Stangl) bearbeitet selbst in Inkscape und will druckfertige Drop-in-Dateien. Er schreibt kurz, casual, auf Deutsch/Englisch gemischt. Antworten: minimal, kein Lob am Anfang, nur Bindestriche (keine Gedankenstriche).

Vorige Session lief in der Cloud (Branch `claude/inspiring-shannon-gd9j3h` im Repo `themonetist/test`, Ordner `xeistee/`). Dieses Kit ist der aktuelle Stand daraus.

## Erste Schritte
1. `xeistee-build-kit-v2.zip` entpacken (Flo legt es nach `C:\Users\dermo\OneDrive\Desktop\claude\xeistee\label\final\handoff\`, ggf. per device_stage_files holen). Ordner `build/`.
2. `pip install --break-system-packages cairosvg pillow fonttools numpy qrcode pyzbar python-barcode` (+ `apt install libzbar0` falls pyzbar meckert).
3. `cd build && python3 fmt.py 155x80` baut livetext-SVG, outlines-SVG, PNG, Druck-PDF, Beschnitt-Proof, A4-1:1-PDF nach `out/formate/155x80/`.
4. `python3 gs_varianten.py` rendert die aktuelle Gesäuse-Variante G nach `out/gesaeuse-varianten/` (liegt schon gerendert bei).
5. Arbeite nur mit diesem Kit. Alles ist SVG, per Python erzeugt, mm als Einheit.

## Format: 155 x 80 mm Endformat, 1,5 mm Beschnitt (158 x 83), nur `bg_tone='gelb'`

## Erledigt in der Cloud-Session
- **MHD + Los eingebaut** (`label_v2.py`, Suche `_mhd`): feste Zeilen "Mindestens / haltbar bis Ende: / 10/2028 / L-202765071". "Los:" entfällt, weil die Losnummer selbst mit L beginnt (RL 2011/91/EU) und "Los: L-202765071" nicht in die 11,9 mm Spalte passt. Flo informiert, kein Widerspruch.
- **Barcode geprüft**: Prüfziffer von 912004893866 = 8, also 9120048938668 korrekt. pyzbar dekodiert aus dem Render bei 600/300/200/150 dpi, auch mit Unschärfe. Vergleich mit der alten Flasche fehlt noch - **Flo um Foto des alten Barcodes bitten**.
- **Barcode-Größe**: Urteil an Flo: nicht weiter verkleinern. Modul 0,264 mm = Minimum, Balken schon 8,5 statt ~18 mm. 7,5 und 7,0 mm dekodieren in Software, aber das sagt wenig über Kassenscanner, Gewinn nur 1,5 mm. Nur nach Scan-Test am Ausdruck.
- **Selbst prüfen (Flo erklärt)**: A4-1:1 bei 100 % drucken, mit Handy scannen; alte Flasche scannen und vergleichen; GS1-Prüfziffernrechner (gs1.at / gs1.org); GS1 Austria / Verified by GS1 für die Registrierung.
- **Gesäuse-Partner-Logo**: lag vorher in reinem Schwarz `#000000` - jetzt überall in Tinte `#2E3524` (`svg_place_visual(..., fill=INK)`, Ausrichtung an der sichtbaren Kontur `GS_BOX`, nicht am viewBox).

## Gesäuse-Logo: Stand der Auswahl
`configure(..., gs_mode=...)` in `label_v2.py`. Durchprobiert und von Flo **abgelehnt**: B/C (unter dem Barcode), D (Siegelreihe neben EU-Blatt - passt nicht, 3,6 mm zu hoch), E (QR | URL | Logo ohne Story - zu viel Luft über/unter der URL), F/H/I (URL unter QR, QR breit, gespiegelt).

**Flo mag G** (`gs_mode='qr-text'`), rechtes Panel unterste Reihe: QR | Story 2 Zeilen + Pfeil + URL | Gesäuse-Logo rechtsbündig mit den Claim-Marken, mittig zur QR-Höhe. Auf seinen Wunsch nachgeschärft:
- QR 7,5 mm (Modul 0,227 mm - **nicht kleiner**, dekodiert bei 600/300/200 dpi)
- Story 1,18 mm Versalhöhe (Untergrenze freiwilliger Text), URL 1,32 mm
- Logo 10,1 x 6,3 mm (vorher 8,0 x 5,0)
- Nebeneffekt, weil das Logo links weg ist: unterer linker Block 1,3 mm tiefer, "Österreich-Landwirtschaft" jetzt auf gleicher Linie wie die QR-Unterkante; Hinweise wieder 1,34 mm statt geschrumpft 1,19.

**Offen: Flos OK zu G in dieser Größe.** Danach: in `fmt.py` bei `FORMATE["155x80"]` `gs_mode='qr-text'` ergänzen (Default in `label_v2.py` ist noch `'mhd'` = altes Layout mit Logo unter MHD), `python3 fmt.py 155x80`, rendern, anschauen, committen.

## Harte Regeln (alle von Flo, nie brechen)
- Nur Markenfarben: Tinte `#2E3524`, Wortmarken-Rot `#C00015`, Berg-Gold `#CDA15D`, Creme `#ECE0D0`
- **Das Band (Kräuter/Bäume) nie strecken oder stauchen.** Zu groß = überlappen und abschneiden. Nie Raster-Retusche am Band.
- **Nur ändern, was verlangt wurde.** Layout nicht nebenbei neu aufteilen. "kürzer" = Breite.
- Front (Wortmarke, BIO links, ℮ 330 ml rechts, Kräutersaftgetränk / aus dem Gesäuse, Berg) bleibt unangetastet
- Holunderbeeren nicht an der Schnittkante abschneiden (4,6 mm Luft unten)
- Jedes Objekt in Inkscape benannt (`inkscape:label`), Ebenen als `inkscape:groupmode="layer"`
- Fertige Dateien nach `C:\Users\dermo\OneDrive\Desktop\claude\xeistee\label\final\formate\155x80\` committen (device_commit_files)

## Rechtliches (nicht ändern ohne Rücksprache)
- LMIV Art. 13(2): Pflichtangaben x-Höhe >= 1,2 mm, Oswald x/Versal 0,714 -> Versal >= 1,68 mm. `CAP_B = CAP_S = 1,70`. Freiwilliger Text (Hinweise, Story, URL) darf kleiner, Untergrenze 1,18.
- MHD-Wortlaut "Mindestens haltbar bis Ende" ist Pflicht (LMIV Anhang X), keine Abkürzung "MHD".
- ℮ >= 3 mm hoch. EU-Bio-Blatt min. 13,5 x 9 mm mit AT-BIO-402 und "Österreich-Landwirtschaft".

## Technik
- `FORMATE["155x80"]` = `trim_w=155, bleed=1.5, ean_bar=8.5, mark_d=8.2, qr_s=8.0, margin=4.0, top=5.2, bottom=48.3, cap_v=1.34, ean_gap=2.0` (in `qr-text` setzt der Builder QR fest auf 7,5)
- Band: Mittelschnitt aus `art/bandF-wide.png` bei 35,413 px/mm, nie skaliert. Hintergrund Vektor-Radialverlauf.
- QR: Rundmodule, ECC H, 33 Module, Ziel https://www.kraeuterbergbauer.at
- Nährwerte, Zutaten: unverändert final (siehe `label_v2.py`)

## Danach offen
- Foto alter Barcode -> vergleichen
- PDF/X-4 mit Stanzkontur + CMYK sobald das Datenblatt vom Drucker da ist; Eckenradius (EAN liegt 2,5 mm von der linken Schnittkante, bei r=3 mm ggf. nach innen); V-Label-Lizenz falls offizielles Vegan-Zeichen; Wasserfrage bei "Bergquellwasser"-Claims

Vor dem Liefern immer rendern und anschauen (Seitenflächen einzeln croppen), Abstände zur Schnittkante messen.
