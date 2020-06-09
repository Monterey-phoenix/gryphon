"""Highlight text under cursor as follows, even if in comment blocks:
    * (){}: highlight this and its mate.
    * OD, DO, IF, FI words.
    * All other words: highlight in all places in document.
"""

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QColor, QFont, QBrush
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QTextEdit


class MPCodeCursorHighlighter(QObject):
    def __init__(self, code_editor):
        super(MPCodeCursorHighlighter, self).__init__()
        self.code_editor = code_editor
        self.document = code_editor.document()

        # background color
        self.word_background_color = QColor("#e4ffe8")
        self.mate_background_color = self.word_background_color.darker(110)
        self.mateless_background_color = QColor("#ffd6cc")

        # connect
        code_editor.cursorPositionChanged.connect(self.highlight_extra)
        code_editor.textChanged.connect(self.highlight_extra)

        # regular expressions
        self.paren_expression = QRegularExpression("[\(\)]")   # "(" or ")"
        self.brace_expression = QRegularExpression("[\{\}]")   # "{" or "}"
        self.bracket_expression = QRegularExpression("[\[\]]")   # "[" or "]"
        self.if_expression = QRegularExpression("\\b(IF|FI)\\b") # IF or FI
        self.do_expression = QRegularExpression("\\b(DO|OD)\\b") # DO or OD
        if not self.paren_expression: raise Exception("Bad")
        if not self.brace_expression: raise Exception("Bad")
        if not self.if_expression: raise Exception("Bad")
        if not self.do_expression: raise Exception("Bad")
  
        # any selected word
        self.selected_word = ""

        # the QTextEdit.ExtraSelections objects to highlight
        self.extra_selections = list()

    # add pair type ExtraSelection
    def _add_mate_selection(self, cursor):
        extra_selection = QTextEdit.ExtraSelection()
        extra_selection.format.setBackground(self.mate_background_color)
        extra_selection.cursor = QTextCursor(cursor)
        self.extra_selections.append(extra_selection)

    # add mateless pair type ExtraSelection
    def _add_mateless_selection(self, cursor):
        extra_selection = QTextEdit.ExtraSelection()
        extra_selection.format.setBackground(self.mateless_background_color)
        extra_selection.cursor = QTextCursor(cursor)
        self.extra_selections.append(extra_selection)

    # add word type ExtraSelection
    def _add_word_selection(self, cursor):
        extra_selection = QTextEdit.ExtraSelection()
        extra_selection.format.setBackground(self.word_background_color)
        extra_selection.cursor = QTextCursor(cursor)
        self.extra_selections.append(extra_selection)

    # highlight mate going forward, cursor captures open_token
    def _highlight_pair_forward(self, expression, cursor):
        open_token = cursor.selectedText()
        if open_token == "(":
            close_token = ")"
        elif open_token == "{":
            close_token = "}"
        elif open_token == "[":
            close_token = "]"
        elif open_token == "IF":
            close_token = "FI"
        elif open_token == "DO":
            close_token = "OD"
        else:
            print("internal error highlight pair forward at %d: '%s'"%(
                                         cursor.position(), open_token))
            raise Exception("Bad")

        # highlight open token
        self._add_mate_selection(cursor)

        # remember open token cursor in case mate cannot be found
        open_token_cursor = QTextCursor(cursor)

        # clear selection since movePosition fails when there is a selection
        cursor.clearSelection()

        # find and highlight close token
        count = 1
        while True:


            # search forward to find mate
            cursor = self.document.find(expression, cursor)

            if not cursor.selectedText():
                # None so open token has no mate
                self._add_mateless_selection(open_token_cursor)
                break
            if cursor.selectedText() == open_token:
                count += 1
                continue
            if cursor.selectedText() == close_token:
                count -= 1
                if count == 0:
                    # at mate so add highlight
                    self._add_mate_selection(cursor)
                    break

    # highlight mate going backward, cursor captures close_token
    def _highlight_pair_backward(self, expression, cursor):
        close_token = cursor.selectedText()
        if close_token == ")":
            open_token = "("
        elif close_token == "}":
            open_token = "{"
        elif close_token == "]":
            open_token = "["
        elif close_token == "FI":
            open_token = "IF"
        elif close_token == "OD":
            open_token = "DO"
        else:
            print("internal error highlight pair backward at %d: '%s'"%(
                                         cursor.position(), close_token))
            raise Exception("Bad")

        # highlight close token
        self._add_mate_selection(cursor)

        # remember open token cursor in case mate cannot be found
        close_token_cursor = QTextCursor(cursor)

        # clear selection since movePosition fails when there is a selection
        cursor.clearSelection()

        # back up to behind this token
        cursor = self.document.find(expression, cursor,
                                    QTextDocument.FindBackward)

        # find and highlight open token
        count = 1
        while True:

            # search backward to find mate
            cursor = self.document.find(expression, cursor,
                                        QTextDocument.FindBackward)

            if not cursor.selectedText():
                # None so close token has no mate
                self._add_mateless_selection(close_token_cursor)
                break
            if cursor.selectedText() == close_token:
                count += 1
                continue
            if cursor.selectedText() == open_token:
                count -= 1
                if count == 0:
                    # at mate so add highlight
                    self._add_mate_selection(cursor)
                    break

    # highlight pair
    def _highlight_pair(self):
        # get the character the cursor is over
        cursor = self.code_editor.textCursor()

        # do not highlight if user selects a range
        if cursor.position() != cursor.anchor():
            return

        char = self.document.characterAt(cursor.position())

        # (
        if char == "(":
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
            self._highlight_pair_forward(self.paren_expression, cursor)

        # {
        elif char == "{":
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
            self._highlight_pair_forward(self.brace_expression, cursor)

        elif char == "[":
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
            self._highlight_pair_forward(self.bracket_expression, cursor)

        # )
        elif char == ")":
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
            self._highlight_pair_backward(self.paren_expression, cursor)

        # }
        elif char == "}":
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
            self._highlight_pair_backward(self.brace_expression, cursor)

        # ]
        elif char == "]":
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
            self._highlight_pair_backward(self.bracket_expression, cursor)

        # evaluate word
        else:

            # get word
            cursor.movePosition(QTextCursor.StartOfWord)
            cursor.movePosition(QTextCursor.EndOfWord,
                                QTextCursor.KeepAnchor)
            word = cursor.selectedText()

            # IF, FI, DO, OD
            if word == "IF":
                self._highlight_pair_forward(self.if_expression, cursor)
            elif word == "FI":
                self._highlight_pair_backward(self.if_expression, cursor)
            elif word == "DO":
                self._highlight_pair_forward(self.do_expression, cursor)
            elif word == "OD":
                self._highlight_pair_backward(self.do_expression, cursor)
            else:
                # not an IF or DO block
                pass

    # highlight open token, close token pair and anything matching selected_word
    @pyqtSlot()
    def highlight_extra(self):

        self.extra_selections.clear()

        # highlight any selected word
        if self.selected_word:
            word_expression = QRegularExpression("\\b%s\\b"%self.selected_word)

            # find word starting at the beginning
            cursor = QTextCursor()
            cursor.movePosition(QTextCursor.Start)

            while True:
                cursor = self.document.find(word_expression, cursor)
                if not cursor.selectedText():
                    break
                self._add_word_selection(cursor)

        # highlight any pair if cursor is on a pair side
        self._highlight_pair()

        # now apply the extra selections
        self.code_editor.setExtraSelections(self.extra_selections)

    # arrive here from mouse press from text edit
    def highlight_selection(self):

        # get word
        cursor = self.code_editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfWord)
        cursor.movePosition(QTextCursor.EndOfWord,
                            QTextCursor.KeepAnchor)
        self.selected_word = cursor.selectedText()

        # disallow word if it starts with potential regex control codes
        if len(self.selected_word) and self.selected_word[0] != "_" and \
                                      not self.selected_word[0].isalnum():
            self.selected_word = ""

        # now that the selected word is defined call higlight extra
        self.highlight_extra()

