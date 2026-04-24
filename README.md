## Audio Recorder CLI

Kleine Python-CLI zum Herunterladen von Streams und anderen Medieninhalten ueber eine URL.
Die Anwendung schreibt die Daten in eine Datei und zeigt parallel den Fortschritt im Terminal.

## Voraussetzungen

- Docker (laufender Daemon)
- Git
- Eine der folgenden IDEs:
	- VS Code mit Erweiterung "Dev Containers"
	- PyCharm Professional mit Dev-Container-Unterstuetzung

## Projekt klonen

```bash
git clone <repo-url>
cd vscode-remote-try-python
```

## Devcontainer in VS Code starten

1. Docker starten.
2. In VS Code die Erweiterung **Dev Containers** installieren.
3. Projektordner in VS Code oeffnen.
4. Befehlspalette oeffnen (`Ctrl+Shift+P`).
5. `Dev Containers: Reopen in Container` auswaehlen.

Beim ersten Start wird das Container-Image gebaut und anschliessend automatisch `pip3 install -r requirements.txt` ausgefuehrt.

## Devcontainer in PyCharm starten

1. Docker starten.
2. PyCharm Professional oeffnen.
3. **File > Open** und den Projektordner waehlen.
4. In den Einstellungen zu **Python Interpreter** gehen.
5. **Add Interpreter > On Docker > Dev Container** (bzw. "From Dev Container") waehlen.
6. Die Datei `.devcontainer/devcontainer.json` aus diesem Projekt verwenden und den Container erstellen lassen.

## Alternative ohne Devcontainer

Alternativ kann auch nur die Datei `cli_audiorecorder.py` heruntergeladen und lokal ausgefuehrt werden.
Installiere dafuer die benoetigten Module:

```bash
pip install tqdm argparse
```

## Anwendung starten

```bash
python cli_audiorecorder.py <url> [--filename=<name>] [--duration=<sekunden>] [--blocksize=<bytes>] [--filepath=<location>]
```

Beispiel:

```bash
python cli_audiorecorder.py https://moodle.oncampus.de/ --filename=index.html --duration=10 --blocksize=64 --filepath=files/html
```

## Parameter

- `url` (Pflicht): Ziel-URL der Quelle
- `--filename` (optional): Dateiname der Ausgabe, Standard: `myRadio.mp3`
- `--duration` (optional): Laufzeit des Downloads in Sekunden, Standard: `30`
- `--blocksize` (optional): Leseblockgroesse in Bytes, Standard: `64`
- `--filepath` (optional): Relativer Pfad zur Datei von der Applikation

## Hinweise

- Es koennen nicht nur MP3-Streams, sondern auch andere Medientypen heruntergeladen werden.
- Das Sequenzdiagramm zum Programmablauf liegt im Projekt als `Sequenzdiagramm.drawio.png`.


