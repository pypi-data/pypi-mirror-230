from .dict_project import dict_ui
from pathlib import Path
import nltk
import nltk.downloader
import sys
from PyQt5.QtWidgets import (
    QApplication
)


def main():
    dest_path = Path.home()
    download_status = nltk.downloader.Downloader()
    if not download_status.is_installed('wordnet'):
        nltk.download('wordnet', download_dir=dest_path)
    app = QApplication(sys.argv)
    f = dict_ui()
    f.show()
    sys.setswitchinterval(0.006)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
