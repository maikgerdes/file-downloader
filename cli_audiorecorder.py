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
                        help='The URL of the media')
    parser.add_argument('--filename', metavar='filename',
                        type=str, help='Name of recording [default: myRadio.mp3].')
    parser.add_argument('--duration', metavar='duration',
                        type=int, help='Duration of recording in seconds [default: 30].')
    parser.add_argument('--blocksize', metavar='blocksize',
                        type=int, help='Block size for read/write in bytes [default: 64].')
    parser.add_argument('--filepath', metavar='filepath',
                        type=str, help='Relative path from this app, where your file is getting stored [default: current directory].')
    parser.add_argument('--historypath', metavar='historypath',
                        type=str, help='Relative path from this app, where you want the download history to be stored [default: current directory].')
    parser.add_argument('--showhistory', metavar='showhistory',
                        type=bool, help='Whether or not you want so see the contents of the history file after the download [default: False].')
    args = parser.parse_args()
    thread_handler(url=args.url, filename=args.filename if args.filename is not None else "myRadio.mp3",
                   duration=args.duration if args.duration is not None else 30,
                   blocksize=args.blocksize if args.blocksize is not None else 64,
                   filepath=args.filepath if args.filepath is not None else "",
                   history_path=args.historypath if args.historypath is not None else "",
                   show_history=args.showhistory if args.showhistory is not None else False)


def thread_handler(url: str, filename: str, duration: int, blocksize: int, filepath: str, history_path: str, show_history: bool):
    """ Thread Handler zum simultanen Download sowie Anzeigen des Fortschritts im Terminal.
    Ruft im Anschluss manage_history auf um die Downloadhistorie zu verwalten.

    Args:
        url: URL der zu downloadenen Datei
        filename: Name und Endung der Datei (z.B. index.html, myRadio.mp3)
        filepath: Relativer Pfad vom Standort der Applikation (z.B files oder files/audio)
        duration: Dauer der Anzeige in Sekunden
        blocksize: Anzahl der gleichzeitig ausgelesenen Bytes
        history_path: Relativer Pfad vom Standort der Applikation (z.B history oder today/history)
        show_history: Ob nach dem Download die Historie ausgegeben werden soll 
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
        absolute_path_history = os.path.join(absolute_path_app, history_path)
        manage_history(absolute_path_history=absolute_path_history, show_history=show_history,
                       new_download_name=filename, new_download_location=absolute_path_file)


def manage_history(absolute_path_history: str, show_history: bool, new_download_name: str, new_download_location: str):
    """ Methode zum Verwalten der Download-Historie.
    Schreibt einen Eintrag in die Download-Historie und liest optional die Historie und gibt sie im Terminal aus.

    Args:
        absolute_path_history: Absoluter Pfad zur Historie (ohne Dateiname und Endung z.B.: User\\history\\, User\\downloads\\history\\) 
        show_history: Ob nach dem Eintrag des neuen Downloads die Download-Historie im Terminal ausgegeben werden soll
        new_download_name: Name und Endung der gedownloadeten Datei (z.B. index.html, myRadio.mp3)
        new_download_location: Absoluter Pfad zur gedownloadeten Datei (ohne Dateiname und Endung)
    """
    if not os.path.exists(absolute_path_history):
        os.makedirs(absolute_path_history)

    history_location = os.path.join(absolute_path_history, "history_file.txt")

    current_time_formatted = time.asctime(
        # time-Module geht 2 Stunden zurück, daher + 7200 Sekunden
        time.localtime(time.time() + 7200))

    with open(history_location, "at") as list:
        list.write(
            f"{new_download_name} in: {new_download_location} ({current_time_formatted}) \n")
        list.close()

    if (show_history):
        print("List of all downloads: ")
        with open(history_location, "r") as list:
            for line in list:
                print(line.strip())
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
