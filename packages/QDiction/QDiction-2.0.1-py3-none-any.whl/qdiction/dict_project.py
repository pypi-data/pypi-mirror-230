#!/usr/bin/python3
'''
This file handles the display logic for this app, including fetching search results and 
displaying it back to the user.
'''

from collections import deque
from nltk.corpus import wordnet as wn
import sys
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QMessageBox,
                             QDialog,
                             QListWidget,
                             QVBoxLayout,
                             QTextBrowser,
                             )
from os import path
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from .dictionary_auto_gen import *


class dict_ui(QMainWindow):

    __slots__ = ()

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.cur_dir = path.dirname(__file__)
        self.setWindowIcon(QIcon(path.join(self.cur_dir, "icons",
                                           "window_icon.png")))
        self.setWindowTitle("QDiction")
        self.ui.verticalLayout.setContentsMargins(2, 0, 2, 0)
        # This would connect when the RET (enter) key is pressed
        self.ui.lineEdit.returnPressed.connect(self.display_defs)
        # This would connect when the search button is clicked
        self.ui.pushButtonSearch.clicked.connect(self.display_defs)
        # This is to connect the exit actions to the close method
        self.ui.pushButtonSearch.setIcon(QIcon(path.join(self.cur_dir, "icons",
                                                         "search_icon.png")))
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionExit.setIcon(QIcon(path.join(self.cur_dir, "icons",
                                                   "exit.png")))
        self.ui.actionAbout.triggered.connect(self.display_about)
        self.ui.actionAbout.setIcon(QIcon(path.join(self.cur_dir, "icons",
                                                    "about_icon.png")))
        self.ui.pushButtonHistory.clicked.connect(self.display_hist)
        self.ui.pushButtonHistory.setIcon(QIcon(path.join(self.cur_dir,
                                                          "icons",
                                                          "history.png")))
        # History keeps a limited search queries of 10 searches
        self.history = deque(maxlen=10)
        self.positions = {'n': 'noun',
                          'v': 'verb',
                          'r': 'adverb',
                          's': 'sat adj',
                          'a': 'adj'
                          }

        self.show()

    def display_defs(self) -> None:

        '''This is the driver for displaying definitions in \
        the textLabel area'''

        search_word = self.ui.lineEdit.text()
        self.ui.textBrowser.setText("")
        self.get_defs(search_word)

    def get_defs(self, search_word) -> None:

        ''' This method displays all definitions for the searched word  '''

        if search_word:
            make_synset = wn.synsets(search_word)
            synonyms = self.get_synonyms(self.stripper
                                         (make_synset), search_word)
            lemmas = [lem.lemmas() for lem in make_synset]
            antonyms = self.get_antonyms(lemmas)
            related_words = self.get_related_words(make_synset, search_word)
            self.history.append(f"{search_word}")
            if len(make_synset) > 0:
                idx = 1
                for syns in make_synset:
                    if syns.definition():
                        pos = syns.pos()
                        definition = syns.definition()
                        self.ui.textBrowser.append(
                            f"{idx}.\t<u>{self.positions[pos]}</u>.\t{definition}.")
                        idx += 1
                    if syns.examples():
                        example = syns.examples()
                        self.ui.textBrowser.append(
                            f"\tExample: \"<em>{example[0]}</em>\"")

                if related_words:
                    self.ui.textBrowser.append("\n")
                    self.ui.textBrowser.append(
                        f"<u>Related words</u>: {related_words}")
                if synonyms:
                    self.ui.textBrowser.append("\n")
                    self.ui.textBrowser.append(
                        f"<u>Synonyms</u>: {synonyms}")
                if antonyms:
                    self.ui.textBrowser.append("\n")
                    self.ui.textBrowser.append(
                        f"<u>Antonyms</u>: {antonyms}")
            else:
                self.ui.textBrowser.insertHtml(
                    "<p style='font-family: Sans-serif; font-size: 24px;' >"
                    f'Search result: No results found for <i>"{search_word}"</i>'
                    '</p>'

                )
        else:
            pass

    def get_related_words(self, synset, search_word):
        '''returns a string consisting of words related to
        search word
        '''

        lemmas = [synset.lemma_names() for synset in synset]
        related_words = [word for tups in lemmas for word in tups if word
                         not in self.get_synonyms
                         (self.stripper(synset), search_word)
                         and
                         word != search_word]
        return ', '.join(set(related_words))

    def get_synonyms(self, tup_of_synsets, word) -> str:
        '''
        Given a collection of syn tuples obtained from a search word,
        returns a string of all the synonyms of the search word
        '''
        syns = [syn[0] for syn in tup_of_synsets
                if (syn[0] != word)]
        return ', '.join(set(syns))

    def get_antonyms(self, lemma_set):

        antonyms = [lemma.antonyms() for lists in lemma_set for lemma in
                    lists if lemma.antonyms()]
        return ', '.join(set([lemma[0].name() for lemma in antonyms]))

    def stripper(self, synset) :
        '''Strips a synset object to return tuples of \
        name, pos, number for extraction
        '''
        return [(syn.name().partition('.')[0],
                 syn.pos(),
                 syn.name()[-2:])
                for syn in synset]

    def close(self) -> None:
        sys.exit(0)

    def display_hist(self):
        dialog = QDialog()
        dialog.setWindowTitle("Search History")
        dialog.setWindowIcon(QIcon(path.join(self.cur_dir, "icons", "history.png")))
        dialog.resize(451, 721)
        dialog.setToolTip("Showing your last 10 searched words")
        max_size = QSize(452, 722)
        min_size = QSize(450, 719)
        dialog.setMaximumSize(max_size)
        dialog.setMinimumSize(min_size)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        layout.setContentsMargins(1, 1, 1, 1)
        listwidget = QListWidget()
        layout.addWidget(listwidget)
        listwidget.insertItems(len(self.history), self.history)
        dialog.exec_()

    def display_about(self):

        about_dialog = QDialog()
        about_dialog.setWindowTitle("About")
        about_dialog.resize(750, 470)
        about_dialog.setMinimumSize(750, 470)
        about_dialog.setMaximumSize(750, 470)
        layout = QVBoxLayout()
        widget = QTextBrowser()
        about_dialog.setLayout(layout)
        layout.addWidget(widget)
        layout.setContentsMargins(0, 1, 0, 0)
        about_dialog.setWindowIcon(QIcon(path.join(self.cur_dir, "icons",
                                                   "info_icon.png")))
        widget.insertHtml("""   <html>
                                   <head>

                                   </head>
                                   <body>
                                    <p style='font-weight: 450;
                                         text-align: center;'>
                                         <b>QDiction</b> Version 2.0.1
                                    </p>
                                     <p style='color: blue; text-align:
                                       center'>
                                       Copyright (c) 2021 Rasaq O Alli</p>
                                     <p>This dictionary program
                                        is based on the Wordnet
                                        <a href=
                                        "https://wordnet.princeton.edu/">
                                         lexical Database</a> from Princeton
                                        University.
                                     </p>
                                     <p>This program is licensed under the
                                         <a href=
                                         "https://www.gnu.org/licenses/gpl-3.0.html">
                                         GNU Public License Version 3
                                         (GPL.v3)</a>
                                     </p>
                                     <p> This program is distributed
                                         in the hope that it
                                         will be useful,
                                         but WITHOUT ANY WARRANTY;
                                         without even the
                                         implied warranty of
                                         MERCHANTABILITY or
                                         FITNESS FOR A PARTICULAR
                                         PURPOSE.
                                     </p>
                                     <p><u>Credits</u></p>
                                     <blockquote>
                                         <i>Natural Language
                                         Processing with Python</i>.
                                         O’Reilly Media Inc. </p>Bird, Steven,
                                         Edward Loper
                                         and
                                         Ewan Klein (2009)<br><br>
                                     </blockquote>
                                 </body>
                         </html>
                       """)

        widget.setOpenExternalLinks(True)
        about_dialog.setWindowIcon(QIcon(path.join(self.cur_dir, "icons",
                                                   "about_icon.png")))
        about_dialog.exec_()
