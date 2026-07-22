# Hand Painter — Projektplan

## Mål

Ett Python-program som låter användaren rita på skärmen med sitt pekfinger,
spårat via webbkamera med hjälp av hand-tracking (MediaPipe). Programmet ska
byggas modulärt så att nya features (fler gester, penslar, lager, etc.) kan
läggas till senare utan att den befintliga koden behöver skrivas om.

## Översiktligt flöde

```
Webbkamera
    │  (bildruta, BGR)
    ▼
hand_tracker.py    → HandLandmarks (21 landmarks + handedness)
    │
    ▼
smoothing.py       → jämnar ut fingerposition mellan bildrutor
    │
    ▼
gestures.py        → GestureState (t.ex. is_drawing=True/False)
    │
    ▼
canvas.py          → ritar streck på en Pygame-yta utifrån GestureState + BrushSettings
    │
    ▼
main.py            → binder ihop hela loopen, kör varje bildruta
```

Alla moduler pratar med varandra via delade datatyper (dataclasses) i
`models.py` — ingen modul behöver veta hur en annan är implementerad internt.
Det är detta som gör det enkelt att byta ut t.ex. hand-trackingen mot en
annan lösning senare, eller lägga till fler gester, utan att röra resten.

## Filstruktur

```
hand_painter/
├── PLAN.md            # detta dokument
├── README.md
├── requirements.txt    # mediapipe, opencv-python, pygame
├── .gitignore
└── src/
    ├── models.py       # delade dataclasses (kontrakten mellan modulerna)
    ├── config.py       # alla inställningar/konstanter samlade
    ├── hand_tracker.py # MediaPipe-wrapper
    ├── smoothing.py    # utjämning av fingerposition
    ├── gestures.py     # tolkar landmarks till ritkommandon
    ├── canvas.py       # Pygame-yta, penseldata, ritlogik
    └── main.py         # huvudloop, limmar ihop allt
```

## Byggordning (beroendekedja)

| Ordning | Fil | Beror på | Kan testas utan kamera? |
|---|---|---|---|
| 1 | `models.py` | — | Ja |
| 2 | `config.py` | — | Ja |
| 3 | `smoothing.py` | `models.py` | Ja |
| 4 | `hand_tracker.py` | `models.py`, `config.py` | Ja (mocka MediaPipe) |
| 5 | `gestures.py` | `models.py`, `config.py` | Ja |
| 6 | `canvas.py` | `models.py` | Delvis (Pygame-rendering kräver visuell koll) |
| 7 | `main.py` | alla ovan | Nej, kräver riktig kamera/integrationstest |

## Filbeskrivningar

### `models.py`

Delade dataclasses som utgör kontraktet mellan alla andra moduler.

- `Point(x, y, z=0.0)` — en normaliserad koordinat (0.0–1.0).
- `HandLandmarks(points, handedness, confidence)` — 21 `Point`-objekt plus
  vilken hand ("Left"/"Right") ochträffsäkerhet. Metod `get_point(index)`
  för säker uppslagning.
- `GestureState(is_drawing, fingertip, gesture_name="none")` — tolkat
  resultat av en handställning.
- `BrushSettings(color, thickness, brush_type)` — penseldata, `frozen=True`
  eftersom instanser inte ska muteras (skapa en ny med `dataclasses.replace`
  vid ändring).

Inga beroenden till andra egna moduler. Testbar helt isolerat: skapa
instanser, kontrollera standardvärden, kontrollera att `frozen=True` kastar
fel vid mutationsförsök, kontrollera `==` mellan likadana objekt.

### `config.py`

Alla konstanter på ett ställe: kameraupplösning (`FRAME_WIDTH`,
`FRAME_HEIGHT`), MediaPipe-inställningar (`MAX_NUM_HANDS`,
`MIN_DETECTION_CONFIDENCE`, `MIN_TRACKING_CONFIDENCE`), landmark-index för
tumtopp/pekfingertopp, gest-tröskel (`PINCH_THRESHOLD`), smoothing-faktor
(`SMOOTHING_FACTOR`), samt standardvärden för canvas och pensel.

Inga beroenden. Test: importera modulen, kontrollera att värden har rimliga
typer/intervall (t.ex. trösklar mellan 0 och 1).

### `smoothing.py`

Jämnar ut brus i fingerpositionen mellan bildrutor så linjerna inte blir
skakiga. Föreslagen klass `ExponentialSmoother(alpha)` med metod
`smooth(new_point: Point) -> Point` som viktar ny position mot föregående
utjämnade position:

```
smoothed = alpha * new_point + (1 - alpha) * previous_smoothed
```

Specialfall: första anropet på en ny instans har ingen tidigare position att
jämna mot — returnera då den råa punkten oförändrad.

Beror på `models.Point`. Tester: konstant input upprepade gånger → oförändrad
output; brusig input kring ett medelvärde → lägre varians i output än input;
första anropet → returnerar exakt inmatad punkt.

### `hand_tracker.py`

Enda modulen som får importera `mediapipe` direkt. Wrapper-klass
`HandTracker` med metod `process(frame) -> HandLandmarks | None`:

1. Konvertera bildrutan från BGR (OpenCV) till RGB (MediaPipe).
2. Kör MediaPipes `hands.process()`.
3. Ingen hand hittad → returnera `None`.
4. Hand hittad → bygg en `HandLandmarks`-instans av MediaPipes råa
   landmark-lista.

Beror på `models.HandLandmarks`, `config.py` för initieringsparametrar.
Tester: mocka MediaPipes returvärde (ingen kamera behövs) och kontrollera att
omvandlingen blir korrekt — 21 punkter, rätt handedness, rätt confidence.
Testa även fallet "ingen hand i bild" → ska ge `None`, inte krascha.

### `gestures.py`

Tolkar en `HandLandmarks` till en `GestureState`. Funktion
`interpret(landmarks: HandLandmarks) -> GestureState`:

1. Hämta tumtopp och pekfingertopp via `landmarks.get_point(...)` med index
   från `config.py`.
2. Beräkna euklidiskt avstånd mellan dem.
3. Avstånd < `config.PINCH_THRESHOLD` → `is_drawing=True`,
   `gesture_name="pinch"`, `fingertip` = pekfingrets position.
4. Annars → `is_drawing=False`, `gesture_name="none"`.

Ny gest i framtiden (t.ex. "två fingrar = sudda") = ny funktion i den här
filen, inget annat behöver ändras.

Beror på `models.py`, `config.py`. Tester: syntetisk `HandLandmarks` med
fingrarna nära varandra → `is_drawing=True`; långt ifrån → `False`;
gränsfall exakt på tröskeln; kontrollera att `fingertip` faktiskt är
pekfingrets position och inte tummens.

### `canvas.py`

Pygame-yta som håller reda på penseldata och ritar streck utifrån
`GestureState` + `BrushSettings`. Ansvarar för att skala normaliserade
koordinater (0–1) till skärmpixlar, samt rita linjer mellan förra och nya
positionen när `is_drawing=True`.

Naturlig plats att bygga ut med fler penslar, lager eller ångra-funktion
senare.

Beror på `models.py`. Tester: testa koordinat-skalning som en ren funktion
separat från Pygame-anropen; kontrollera att en linje faktiskt ritas mellan
två punkter genom att läsa av pixelfärger på ytan efteråt.

### `main.py`

Huvudloopen — så tunn som möjligt, bara "lim":

```
läs kamera → hand_tracker.process() → smoothing.smooth() →
gestures.interpret() → canvas.update()/render()
```

Beror på alla övriga moduler. Svår att enhetstesta fullt ut (kräver riktig
kamera) — testa istället manuellt, eller kör loopen mot en inspelad
testvideo och kontrollera att den går igenom t.ex. 100 bildrutor utan att
krascha.

### `requirements.txt`

`mediapipe`, `opencv-python`, `pygame` (samt eventuellt `numpy`, som är ett
beroende till de andra men bra att pinna explicit).
