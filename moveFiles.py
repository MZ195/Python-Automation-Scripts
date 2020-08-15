from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import time
import json
import os


class MyHandler(FileSystemEventHandler):

    def __init__(self, src_folder, dest_folder):
        self.src_folder = src_folder
        self.dest_folder = dest_folder

    def on_modified(self, event):
        for fileName in os.listdir(self.src_folder):
            source = self.src_folder + "/" + fileName
            destination = self.dest_folder + "/" + fileName
            os.rename(source, destination)


if __name__ == "__main__":
    src_folder = ""
    dest_folder = ""

    eventHandler = MyHandler(src_folder, dest_folder)
    observer = Observer()

    observer.schedule(eventHandler, src_folder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
