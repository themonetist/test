# Bitterzauber 20 ml Sprühflasche - Etikett, Übergabe an neue Session

Stand: 10.10.2026

Du übernimmst das Etikett für die 20 ml Bitterzauber (Bio-Kräuterbitter, Kräuterbergbauer, Landl im Gesäuse). Es gibt schon eine gelieferte Version (Stand 11.9.), die fertig gemacht werden muss. Flo (Florian Stangl) schreibt kurz und casual. So antworten: minimal, kein Lob am Anfang, nur Bindestriche (keine Gedankenstriche), nie etwas ändern, was er nicht verlangt hat.

## Was diese Session geklärt hat (7.-10.10.)

- **"Kleiner" ist erledigt.** Flo: "Nichts mehr", das hat sich mit der KARTON-Version erledigt. Wortmarke und Etikettgröße also nicht anfassen.
- **Die 20 ml wird manchmal einzeln verkauft** (ohne Karton). Folge: Alle Pflichtangaben müssen auf die Flasche. Variante (a), Zutaten nur auf den Karton, ist damit raus.
- **Zutaten-Rechnung, gemessen** (Liberation Sans Regular 4,9 pt, Zeilenabstand 1,15, mit PIL gesetzt). Die alte Schätzung "7-9 Zeilen" war falsch:

  | Spaltenbreite | Zeilen | Höhe |
  |---|---|---|
  | 26 mm | 14 | 27,8 mm |
  | 29 mm | 12 | 23,9 mm |
  | 55 mm (zwei Felder) | 6 | 11,9 mm |

  Die nutzbare Höhe ist 37 mm (40 mm minus 2 x 1,5 mm Sicherheitszone). Verzehrempfehlung und Hinweise stehen schon im Feld, deshalb passt es nicht.
- **x-Höhe 4,9 pt Liberation Sans = 0,91 mm.** Das liegt nur knapp über 0,9 mm. Die größte Fläche ist 8,7 x 4 = 34,8 cm², also unter 80 cm², deshalb gilt die Grenze von 0,9 mm. Kein Spielraum nach unten, und auch nicht auf eine Schrift mit kleinerer x-Höhe wechseln, ohne nachzumessen.
- **Offene Entscheidung, Flo hat noch keine Präferenz gegeben:**
  - (b) Größeres Etikett: Breiter geht nicht, weil der Umfang ca. 87 mm vorgibt. Höher geht nur bis unter den Sprühkopf, die Flasche ist 50 mm hoch. 45 mm bringen nur ca. 2,5 Zeilen mehr Platz, das reicht nicht. Realistisch bleibt ein **Booklet-Etikett** (Aufklapp-Etikett). Die Druckerei muss bestätigen, ob das bei Ø 2,8 cm geht.
  - (c) Texte kürzen: Die Liste braucht ca. 28 mm in einem Seitenfeld, dafür müsste der Rest dort fast ganz raus. Flo muss sagen, was raus darf.
  - **Nicht bauen, bevor Flo (b) oder (c) entschieden hat.**

## Start

1. **Kit holen:** `bitterzauber-20ml-kit.zip` liegt auf Flos Rechner unter `C:\Users\dermo\OneDrive\Desktop\claude\xeistee\label\final\handoff\`. Eine Cloud-Session hat keinen Zugriff darauf (kein device_stage_files). Flo hat gesagt, er lädt die ZIP ins Google Drive. Bei Übernahme im Drive nach `bitterzauber-20ml-kit` suchen. Bis 10.10. war sie dort noch nicht. Inhalt:
   - `Etikett-20ml/` - die gelieferten Versionen (.odg editierbar, PDFs, Vorschau-PNGs, SVG)
   - `Assets/` - 10+ freigestellte PNGs aus der Verpackung (Original-Artwork, nicht nachgebaut) + `_ASSETS.txt` + `_UEBERSICHT.png`
   - `brief/` - der ursprüngliche Brief (liegt auch im Drive: `bitterzauber-20ml-label-brief.md`, id `1rxkmIpjRHTQ8cSE1Uz_xRIV6dxoJYM0B`)
2. **Aktueller Stand ist die Variante KARTON** (`...-KARTON.odg`, `...-KARTON-87x40-bleed2.pdf`, `...-KARTON-vorschau.png`). Ansehen, bevor du irgendetwas änderst. Achtung: Der Name "KARTON" heißt hier "Pflichtangaben auf dem Karton". Das ist wegen Einzelverkauf jetzt nicht mehr ausreichend. Das Layout bleibt trotzdem die Basis.
3. **Das Skript, das die .odg erzeugt hat, existiert nicht mehr** (alte Session). Entweder die .odg direkt bearbeiten (LibreOffice headless, `soffice --headless`) oder neu aufbauen. Bei Neuaufbau das gelieferte Layout 1:1 treffen.
4. **Originalquelle der Verpackung:** Google Drive `Verpackung Bitterzauber 07.25.odg` (id `1EwbfH-2nUvbJcvOCpJGFnELHSba7qGn6`), alle Elemente liegen darin im Ordner `Pictures/`. Neuere Karton-Stände im Drive: `Bitterzauber Verpackung 2.0.pdf` (id `170CZk8r2gTnBrqnyy0yJZHE_mLfrVlSS`) und `... 2.0 with dielines.pdf` (id `1CNY8BrEt4qei9JmDXpb97_RdCuhT0msM`), beide vom 11.9.2025.
5. **Originales 50-ml-Etikett** liegt in Canva als "Etikette Bitterzauber" (Design DAEY7maxp0Q), nicht lokal. Der Canva-Connector war in dieser Session nicht autorisiert. Flo muss ihn in den claude.ai-Connector-Einstellungen verbinden, sonst ist kein Zugriff möglich.

## Flasche und Etikett

- 20 ml Sprühflasche (Spray, kein Pipettenfläschchen), Ø 2,8 cm, 5 cm hoch, Umfang ca. 8,8 cm
- Etikett gewickelt: 87 x 40 mm (Höhe 40 mm, nicht 45), 2 mm Beschnitt, 1,5 mm Sicherheitszone, ~1 mm Nahtlücke
- Layout: drei Felder à ca. 26-29 mm. Mitte = Front, links und rechts = Rückseiten
- Flo will kein Redesign, sondern das bestehende Design adaptieren, als editierbare Datei (.odg). Er hat noch kein Designprogramm außer ggf. LibreOffice. Ob es installiert ist, ist unklar, noch fragen.

## Aktuelles KARTON-Layout (Flos Richtung vom 11.9.)

- **Front:** `℮ 20ml` links, `alc. 42,0%vol` rechts, Wortmarke + Zauberstab (25 mm), Claim "Lass dich von der Kraft der Natur verzaubern" in Markengrün direkt unter der Wortmarke
- **Links:** Adresse (Kräuterbergbauer, Lainbach 25, 8921 Landl, AT), EU-Bio-Logo + lacon-Block, Feld "Losnr. / MHD:"
- **Rechts:** "BIO-Kräuterbergbauer", "Nahrungsergänzungsmittel · Mundspray", Verzehrempfehlung, NEM-Hinweis, Hinweise
- Am 11.9. gelöscht: Kräuterliste (ersetzt durch "21 Kräuter") und der Text unter dem Bio-Logo. Das ist seit 7.10. überholt, Flo will jetzt ALLE Zutaten wieder drauf (siehe Zutaten).

## Änderungen von Flo am 7.10.

1. **Alle Zutaten müssen aufs Etikett** (volle Kräuterliste statt "21 Kräuter"). Wie sie Platz bekommen, ist offen (siehe oben, (b) oder (c)).
2. **Der Hintergrund fehlt.** Die gelieferte Version hat nur einen Cremeverlauf. Das Original-Verpackungsartwork hat das Foto `Assets/hintergrund-kraeuterwiese.png` (600 x 900 px, deckend: gelb oben, Kräuterwiese, grüner Verlauf unten). Das war im Etikett nie drin.
   - **NEU 10.10.: Flo hat die Auflösung erhöht. Diese Datei verwenden:** `C:\Users\dermo\Downloads\hintergrund-kraeuterwiese_300dpi_2400x3600.png` (2400 x 3600 px, also 4 x das Original). Liegt auf Flos Rechner, nicht im Kit. Flo muss sie mit ins Drive laden.
     - Über die volle Breite mit Beschnitt (91 mm) gibt das ca. 670 dpi, damit ist die Auflösung kein Problem mehr.
     - Sie ist aus 600 x 900 hochgerechnet. Vor dem Einsatz bei 100 % ansehen: Ist sie scharf, gibt es Artefakte, ist die Farbe gleich wie im Original? Hochrechnen erzeugt keine echten Details, deshalb ehrlich sagen, falls es im Druck weich wirkt.
   - Alter Pfad (600 x 900, nur zum Vergleich), auf Flos Rechner nach dem Entpacken: `C:\Users\dermo\OneDrive\Desktop\claude\xeistee\label\final\handoff\bitterzauber-20ml-kit\Assets\hintergrund-kraeuterwiese.png`
   - Kandidat im Drive, **ungeprüft**, ob es dasselbe Bild ist: `Original Hintergrund.png` (id `1wI1SJoivP6cY73v_aa9OaLklBSl9XmYv`, Flos Konto, 2023; Kopie id `1CPZGH828EK-Oxx7L3HziRJNH24Af4yXl`). Vergleichen mit dem Bild in `Pictures/` der Verpackung 07.25.odg.
   - Prüfen, wie die 50-ml-Flasche (Canva) und der Karton den Hintergrund einsetzen, und das gleiche Prinzip übernehmen.
   - Text muss lesbar bleiben (Kontrast prüfen).
   - Das Original mit 600 x 900 px hätte nur ca. 175 dpi gegeben. Das ist mit der hochgerechneten Fassung erledigt (siehe oben). Bleibt offen, welcher Ausschnitt aufs Etikett kommt: Das Bild ist hochkant (2:3), das Etikett quer (87 x 40). Gleiches Prinzip wie 50 ml/Karton.

## Zutaten (von kraeuterbergbauer.at, Produktseite)

"Zutaten: BIO-Kornbrand, Auszug aus folgenden Kräutern (alle aus kontrolliert biologischer Landwirtschaft): Alantwurzel, Anisminze, Beifuß, Bohnenkraut, Ehrenpreis, Eisenkraut, Engelwurz, Kamille, Lavendelblüte, Löwenzahnwurzel, Mariendistel, Mutterkraut, Salbei, Schafgarbe, Spitzwegerich, Storchenschnabel, Thymian, Topinambur, Wermut, Wilde Möhre, Ysop."

- 21 Kräuter. Auf der Website stehen die Namen ohne lateinische Namen, auf dem Karton stehen sie voll.
- Gegen die Karton-Originaldatei im Drive prüfen. Weicht sie ab, gilt der Karton. Achtung: Mit lateinischen Namen wird die Liste deutlich länger als in der Rechnung oben.
- Allergene: Die Website sagt "auf der Flasche". Klären, ob ein Allergen gekennzeichnet werden muss (z. B. ein Sellerie- oder Korbblütlerhinweis). Nicht raten.
- Nicht die Schrift unter 4,9 pt drücken.

## Rechtlich (offen, nicht raten)

- Pflichtangaben hängen an der Verkaufseinheit (VO 1169/2011 Art. 2(2)(e)). **Flo hat am 10.10. bestätigt, dass die 20 ml manchmal einzeln verkauft wird.** Die Flasche braucht also die vollen Pflichtangaben, der Karton allein reicht nicht.
- Untergrenze für die Schriftgröße ist absolut: x-Höhe >= 1,2 mm, bei größter Fläche < 80 cm² 0,9 mm (Art. 13(2),(3)). Hier gilt 0,9 mm, gemessen sind 0,91 mm bei 4,9 pt. Kein Rabatt für lange Zutatenlisten, dann muss die Packung wachsen.
- Das Produkt ist als Nahrungsergänzungsmittel deklariert (so auf dem Karton), Alkohol 42,0 % vol.
- Bio: Code AT-BIO-402, Kontrollstelle lacon. Code + Herkunftszeile müssen im selben Sichtfeld wie das EU-Blatt bleiben (EU 2018/848 Art. 32), nicht abschneiden. Das lacon-Oval selbst ist freiwillig.
- Die Liste der Pflichtangaben für Spirituosen/NEM ist noch nicht endgültig bestätigt. Ein Lebensmittelrechtler sollte drüberschauen.

## Marken und Schrift

- Markensystem: Deep Green #1D3325, Gold #C08A3B, Cream #FBF6EC, Ink #211C14, Line #D8C9A6. Die Zauberstab-Grafik der Wortmarke ist ein Original-PNG, nie nachzeichnen.
- Verpackungsschrift ist Noto Sans / Liberation Sans, NICHT Cormorant/Inter (die gelten für die Website). Flo will für das Flaschenetikett die gleichen Schriften wie auf den neueren Packungen (ca. 2024).
- Das Weiß-Original des Claims ist auf Creme unsichtbar, `bitterzauber-claim-gruen.png` verwenden. Mit dem Wiesen-Hintergrund neu prüfen, welche Fassung lesbar ist.

## Regeln von Flo (aus allen Sessions)

- Ändere nur, was verlangt wird. Layout nicht nebenbei neu aufteilen. Er war zweimal wütend, als Text oder Layout umgebaut wurde, das er nicht verlangt hatte.
- Nie Original-Artwork von KI nachzeichnen oder per Heuristik umfärben. Original-PNGs verwenden.
- Bei Print-and-Cut: nie Umrandung auf das Artwork, nur Schnittmarken im Rand.
- Qualität: "spotless", bis es druckfertig ist.
- Beim Rendern immer ansehen und Abstände zur Schnittkante messen.
- QR-Codes mit pyzbar prüfen, nicht mit OpenCV.

## Deliverable

Druckfertig mit 300 dpi, CMYK, Beschnitt und Sicherheitszone, dazu eine flache Vorschau-PNG. Gleiche Benennung wie das 50-ml-Set, dazu die editierbare .odg. Das Druckerei-Datenblatt ist noch offen: Digital oder Flexo? Stanze? Material nassfest wegen Kondenswasser? Kann die Druckerei Booklet-Etiketten bei Ø 2,8 cm?

## Noch mit Flo zu klären

1. Zutaten: (b) Booklet/größeres Etikett oder (c) Texte kürzen, und wenn (c), welche Texte raus dürfen
2. Liegen die Kit-ZIP und `hintergrund-kraeuterwiese_300dpi_2400x3600.png` schon im Drive?
3. Allergenhinweis nötig?
4. Ist LibreOffice installiert, kann er die .odg öffnen?
5. Druckerei und Verfahren (siehe Deliverable)

## Umgebung (Cloud-Session)

- Vorhanden: `soffice`/`libreoffice`, Liberation-Fonts, Python mit PIL. Noto Sans vor dem Bauen prüfen (`fc-list | grep -i noto`).
- Google Drive per Connector lesbar. Canva nicht autorisiert. Kein Zugriff auf Flos Rechner.
