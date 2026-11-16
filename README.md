# Hand Painter

Rita på skärmen med händerna via webbkameran. Programmet spårar båda händerna i realtid med MediaPipe. Höger pekfinger styr penseln och vänster hand bestämmer när det ritas: nyp ihop tumme och pekfinger för att rita, släpp för att lyfta penseln.

Fönstret är delat i två delar. Till vänster syns kamerabilden med en markör på pekfingret, och till höger syns ritytan.

## Kom igång

Kräver Python 3.11 och en webbkamera.

```sh
python -m venv .venv
.venv\Scripts\activate        # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python src/main.py
```

Avsluta med `Esc`.

## Så fungerar det

Varje bildruta går genom en kedja av moduler som bara pratar med varandra via delade dataklasser i `src/models.py`:

```
webbkamera (BGR)
  → hand_tracker.py   MediaPipe Hand Landmarker → 21 landmärken per hand + vänster/höger
  → gestures.py       vänster hand: nypgest (avstånd tumme–pekfinger) → rita / inte rita
                      höger hand: pekfingrets position
  → smoothing.py      exponentiell utjämning av fingerpositionen mot darr
  → canvas.py         ritar linjer mellan på varandra följande punkter på en Pygame-yta
  → main.py           binder ihop loopen och visar kamera + rityta
```

Eftersom modulerna bara beror på dataklasserna går det att byta hand-tracking, lägga till gester eller penslar utan att röra resten av koden. Alla inställningar (upplösning, tröskelvärden, utjämning, penslar) finns i `src/config.py`.

## Teknik

- [MediaPipe](https://developers.google.com/mediapipe) Hand Landmarker (modellen ligger i `models/`)
- OpenCV för kamerainläsning
- Pygame för fönster och ritning
- NumPy

## Planerat

Designen och nästa steg (fler gester, penslar, sudd) finns i [PLAN.md](PLAN.md).
