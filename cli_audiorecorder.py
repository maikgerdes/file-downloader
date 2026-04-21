"""
 Maik Gerdes
 Einsendeaufgabe 1
 Modul: objektorientierte Skriptsprachen

"""


import urllib.request
import time
import argparse
import threading
from tqdm import tqdm


def argument_parser():
    """ Argument Parser zum Aufrufen der Anwendung über das Terminal

    """
    parser = argparse.ArgumentParser(description='Downloads an mp3-stream')
    parser.add_argument('url', metavar='url', type=str,
                        help='The URL of the mp3-stream')
    parser.add_argument('--filename', metavar='filename',
                        type=str, help='Name of recording [default: myRadio].')
    parser.add_argument('--duration', metavar='duration',
                        type=int, help='Duration of recording in seconds [default: 30].')
    parser.add_argument('--blocksize', metavar='blocksize',
                        type=int, help='Block size for read/write in bytes [default: 64].')
    args = parser.parse_args()
    thread_handler(url=args.url, filename=args.filename if args.filename is not None else "myRadio.mp3",
                   duration=args.duration if args.duration is not None else 30, blocksize=args.blocksize if args.blocksize is not None else 64)


def thread_handler(url: str, filename: str, duration: int, blocksize: int):
    """ Thread Handler zum simultanen Download sowie Anzeigen des Fortschritts im Terminal.

    Args:
        url: URL der zu downloadenen Datei
        filename: Name und Endung der Datei (z.B. index.html, myRadio.mp3)
        duration: Dauer der Anzeige in Sekunden
        blocksize: Anzahl der gleichzeitig ausgelesenen Bytes
    """

    # Damit der media_downloader_thread dem display_progress_thread Statusupdates mitteilen kann
    success_flag = threading.Event()
    error_flag = threading.Event()
    thread1 = threading.Thread(target=media_downloader, kwargs={"url": url, "success_flag": success_flag, "error_flag": error_flag, "filename": filename,
                                                                "duration": duration, "blocksize": blocksize})
    thread1.start()

    thread2 = threading.Thread(target=display_progress, kwargs={"success_flag": success_flag, "error_flag": error_flag,
                                                                "duration": duration, "filename": filename})
    thread2.start()


def display_progress(success_flag: threading.Event, error_flag: threading.Event, duration: int, filename: str):
    """ Progressbar zum Stand des derzeitigen Downloads. 

    Args:
        error_flag: Error-Event über den der aufrufende Thread Informationen über Fehler während des Downloads erhält
        success_flag: Success-Event über den der aufrufende Thread über den erfolgreich abgeschlossenen Download informiert wird
        duration: Dauer der Anzeige in Sekunden
        filename: Name und Endung der Datei (z.B. index.html, myRadio.mp3)
    """
    t = tqdm(range(duration))
    for remaining_time in range(duration):
        if success_flag.is_set():
            t.update(duration - remaining_time)
            break
        elif error_flag.is_set():
            break

        time.sleep(1)
        t.update()

    time.sleep(1)  # Damit media_downloader Zeit hat das Event zu setzen.
    if (success_flag.is_set()):
        t.colour = 'GREEN'
        t.write(f"Your download of {filename} was successful!")
    else:
        t.colour = 'RED'
        t.write(f"Your download of {filename} was not successful!")
    t.refresh()
    t.close()


def media_downloader(url: str, success_flag: threading.Event, error_flag: threading.Event, filename: str, duration: int, blocksize: int):
    """ Downloadet eine Datei von einer gegebenen URL (html, mp3-Stream etc.)

    url: URL der zu downloadenen Datei
    filename: Name und Endung der Datei (z.B. index.html, myRadio.mp3)
    duration: Dauer des Downloads in Sekunden
    blocksize: Anzahl der gleichzeitig ausgelesenen Bytes
    error_flag: Error-Event über den der aufrufende Thread einen Fehler beim Download mitteilen kann
    success_flag: Success-Event über den der aufrufende Thread den Abschluss des Downloads mitteilen kann
    """
    try:
        with urllib.request.urlopen(url) as response:
            start_time = time.time()

            with open(filename, "wb") as file:
                while time.time() - start_time < duration:
                    chunk = response.read(blocksize)
                    if not chunk:
                        break

                    file.write(chunk)
                success_flag.set()
    except:
        error_flag.set()  # Scheint aufzutreten, wenn die Webseite kein HTTPS verwendet


if __name__ == "__main__":
    argument_parser()
