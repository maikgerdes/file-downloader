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
import os


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
    parser.add_argument('--filepath', metavar='filepath',
                        type=str, help='Relative path from this app, where your file is getting stored')
    args = parser.parse_args()
    thread_handler(url=args.url, filename=args.filename if args.filename is not None else "myRadio.mp3",
                   duration=args.duration if args.duration is not None else 30, blocksize=args.blocksize if args.blocksize is not None else 64, filepath=args.filepath if args.filepath is not None else "")


def thread_handler(url: str, filename: str, duration: int, blocksize: int, filepath: str):
    """ Thread Handler zum simultanen Download sowie Anzeigen des Fortschritts im Terminal.
    Ruft zwei Threads zur parallelen Abarbeitung auf und schreibt anschließend die File-Location mit Timestamp in eine .txt Datei

    Args:
        url: URL der zu downloadenen Datei
        filename: Name und Endung der Datei (z.B. index.html, myRadio.mp3)
        filepath: Relativer Pfad vom Standort der Applikation (z.B files oder files/audio)
        duration: Dauer der Anzeige in Sekunden
        blocksize: Anzahl der gleichzeitig ausgelesenen Bytes
    """
    absolute_path_app = os.path.dirname(__file__)
    absolute_path_file = os.path.join(absolute_path_app, filepath)
    file_location = os.path.join(absolute_path_file, filename)

    if not os.path.exists(absolute_path_file):
        os.makedirs(absolute_path_file)

    # Damit der media_downloader_thread dem display_progress_thread Statusupdates mitteilen kann
    success_flag = threading.Event()
    error_flag = threading.Event()
    thread1 = threading.Thread(target=media_downloader, kwargs={"url": url, "success_flag": success_flag, "error_flag": error_flag,
                                                                "duration": duration, "blocksize": blocksize, "file_location": file_location})
    thread1.start()

    thread2 = threading.Thread(target=display_progress, kwargs={"success_flag": success_flag, "error_flag": error_flag,
                                                                "duration": duration, "filename": filename})
    thread2.start()
    thread1.join()
    thread2.join()

    # Download war erfolgreich
    if (success_flag.is_set()):
        current_time_formatted = time.asctime(
            # time-Module geht 2 Stunden zurück, daher + 7200 Sekunden
            time.localtime(time.time() + 7200))
        with open("files_list.txt", "at") as list:
            list.write(
                f"{filename} in: {absolute_path_file} ({current_time_formatted}) \n")
            list.close()


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


def media_downloader(url: str, success_flag: threading.Event, error_flag: threading.Event, duration: int, blocksize: int, file_location: str):
    """ Downloadet eine Datei von einer gegebenen URL (html, mp3-Stream etc.)

    url: URL der zu downloadenen Datei
    file_location: Absoluter Pfad zur Datei + Name und Endung der Datei (z.B. User\\files\\index.html, User\\files\\audio\\myRadio.mp3) 
    duration: Dauer des Downloads in Sekunden
    blocksize: Anzahl der gleichzeitig ausgelesenen Bytes
    error_flag: Error-Event über den der aufrufende Thread einen Fehler beim Download mitteilen kann
    success_flag: Success-Event über den der aufrufende Thread den Abschluss des Downloads mitteilen kann
    """

    try:
        with urllib.request.urlopen(url) as response:
            start_time = time.time()

            with open(file_location, "wb") as file:
                while time.time() - start_time < duration:
                    chunk = response.read(blocksize)
                    if not chunk:
                        break

                    file.write(chunk)
                file.close()
                success_flag.set()

    except:
        error_flag.set()  # Scheint aufzutreten, wenn die Webseite kein HTTPS verwendet


if __name__ == "__main__":
    argument_parser()
