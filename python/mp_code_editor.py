
#
# Modification History:
#   180803 David Shifflett
#     Added scroll_to_bottom function
#

# Adapted from:
# https://stackoverflow.com/questions/33243852/codeeditor-example-in-pyqt
# http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QTextFormat
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRect
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QStringListModel
from PyQt5.QtCore import QRegularExpression
from mp_code_highlighter import MPCodeHighlighter
from mp_code_cursor_highlighter import MPCodeCursorHighlighter
from os_compatibility import control_modifier

_keywords = set()
for keyword in "ADD|AFTER|ALL|AND|BEFORE|BUILD|CHECK|CONTAINS|"\
            "COORDINATE|DISJ|DO|ELSE|ENCLOSING|ENSURE|EXISTS|FI|FOLLOWS|"\
            "FOREACH|FROM|IF|IN|IS|MAP|MARK|MAY_OVERLAP|NOT|OD|ON|ONFAIL|"\
            "OR|PRECEDES|REJECT|ROOT|SAY|SCHEMA|SHARE|SUCH|THAT|THEN|THIS|"\
            "WHEN|SORT|REVERSE|SHIFT_RIGHT|SHIFT_LEFT|CUR_FRONT|CUT_END|"\
            "FIRST|LAST".split("|"):
            _keywords.add(keyword)

def _refresh_word_list(code_editor, word_list_model):
    # regex for word
    word_expression = QRegularExpression("\\b\\w*")

    # get word at cursor
    cursor = code_editor.textCursor()
    cursor.movePosition(QTextCursor.StartOfWord)
    cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
    word_at_cursor = cursor.selectedText()

    # move to front of document
    cursor.movePosition(QTextCursor.Start)
 
    # get words from the document
    words = set()
    document = code_editor.document()
    while True:
        cursor = document.find(word_expression, cursor)
        word = cursor.selectedText()
        if word:
            # add word to Set
            words.add(word)
            cursor.movePosition(QTextCursor.NextWord)
        else:
            # done
            break

    # remove the word where the user is typing
    words.discard(word_at_cursor)

    # add keywords to set
    words.update(_keywords)

    # put words into word list
    word_list = list()
    for word in words:
        word_list.append(word)

        # sort word_list case-insensitive
        word_list.sort(key=str.lower)

    # update the word list model
    word_list_model.setStringList(word_list)

"""MPCodeEditor"""
class MPCodeEditor(QObject):
    def __init__(self, settings_manager, statusbar):
        super(MPCodeEditor, self).__init__()

        # the statusbar to report syntax checker errors to
        self.statusbar = statusbar

        self.code_editor = CodeEditor()
        self.code_highlighter = MPCodeHighlighter(self.code_editor.document(),
                                                  settings_manager)

    # move scroll bar to the bottom (for automatically added text)
    def scroll_to_bottom(self):
        textBlock = self.code_editor.document().lastBlock()
        self.code_editor.setTextCursor(QTextCursor(textBlock))

    # set text given mp_code_text
    def set_text(self, mp_code_text):
        self.code_editor.clear()
        self.code_editor.appendPlainText(mp_code_text)

        # scroll to top
        textBlock = self.code_editor.document().findBlockByNumber(0)
        self.code_editor.setTextCursor(QTextCursor(textBlock))

    # set syntax checker status
    @pyqtSlot(int, str)
    def set_syntax_status(self, line_number, status):

        # set the syntax error line number so painter can paint it differently
        self.code_editor.syntax_error_line_number = line_number

        # show status in statusbar
        self.statusbar.showMessage(status)

    def clear(self):
        self.code_editor.clear()

    def text(self):
        return self.code_editor.toPlainText()

    def set_error_line_number(self, line_number):
        textBlock = self.code_editor.document().findBlockByNumber(
                                                           line_number - 1)
        textCursor = QTextCursor(textBlock)
        self.code_editor.setTextCursor(textCursor)

    # returns schema name or SCHEMA not defined
    def schema_name(self):
        return self.code_highlighter.schema_name

#############################################################
# private support for MPCodeEditor
#############################################################
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        # the cursor highlighter manages cursor highlighting on mouse click
        self.mp_code_cursor_highlighter = MPCodeCursorHighlighter(self)

        # the word list model provides the list model for MP Code keywords
        self.mp_code_string_list_model = QStringListModel()

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)

        self.lineNumberArea = LineNumberArea(self)
        self.updateLineNumberAreaWidth(0)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        # monospace
        # https://stackoverflow.com/questions/13027091/how-to-override-tab-width-in-qt
        font = QFont()
        font.setFamily("Courier")
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.setFont(font)

        # tab stop
        tab_stop = 4
        metrics = QFontMetrics(font)
        self.setTabStopWidth(metrics.width(' ') * tab_stop)

        # line number of syntax error or 0 for no syntax error line
        self.syntax_error_line_number = 0
        self.syntax_error_color = QColor("#cc0000")

        # code completer
        self.completer = QCompleter(self.mp_code_string_list_model, None)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.activated.connect(self.insert_completion_text)

    # insert the right portion of the completion text at the end of the cursor
    @pyqtSlot(str)
    def insert_completion_text(self, completion_text):
        tc = self.textCursor()
        extra = (len(completion_text) - len(self.completer.completionPrefix()))
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion_text[-extra:])
        self.setTextCursor(tc)

    # intercept keyPress to work with completer
    @pyqtSlot(QKeyEvent)
    def keyPressEvent(self, e):

        # disregard these keystrokes if the completer popup is active
        if self.completer.popup().isVisible():
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape,
                                               Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                return

        # recognize the CTRL-Spacebar shortcut
        is_shortcut = (e.modifiers() == control_modifier()) and \
                                                 e.key() == Qt.Key_Space

        # forward all but the CTRL-Spacebar shortcut to superclass
        if not is_shortcut:
            super(CodeEditor, self).keyPressEvent(e)

        # recognize CTRL or SHIFT
        ctrl_or_shift = e.modifiers() & (control_modifier() | Qt.ShiftModifier)

        # disregard CTRL or SHIFT without character
#        if ctrl_or_shift and not e.text():
        if ctrl_or_shift and e.key() > 255: # modifier codes are above ASCII
            return

        # recognize non-ctrl_or_shift modifier
        has_modifier = e.modifiers() != Qt.NoModifier and not ctrl_or_shift

        # require cursor to be at the end of word and without range selection
        cursor = self.textCursor()
        position = cursor.position()
        anchor = cursor.anchor()
        cursor.select(QTextCursor.WordUnderCursor)
        word_end_position = cursor.position()
        word_end_anchor = cursor.anchor()
        at_end_of_word = position == anchor and position == word_end_position \
                         and word_end_position != word_end_anchor
        if not at_end_of_word:
            self.completer.popup().hide()
            return

        # find user's completion text prefix
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        completion_prefix = cursor.selectedText()

        # recognize an invalid keystroke
        text = e.text()
        is_invalid_key = not text.isalnum() and text != "_"

        # abort completer under these conditions:
        if not is_shortcut:
            if has_modifier or not text or len(completion_prefix)<3 or \
                                                        is_invalid_key:
                self.completer.popup().hide()
                return

        # set the completion text prefix
        self.completer.setCompletionPrefix(completion_prefix)
        _refresh_word_list(self, self.mp_code_string_list_model)
        self.completer.popup().setCurrentIndex(
                            self.completer.completionModel().index(0,0))

        # configure and open popup
        cursor_rectangle = self.cursorRect()
        cursor_rectangle.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursor_rectangle)

    # intercept mouse press for cursor highlighting
    @pyqtSlot(str)
    def mousePressEvent(self, event):
        super(CodeEditor, self).mousePressEvent(event)
        self.mp_code_cursor_highlighter.highlight_selection()

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    @pyqtSlot(int)
    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    @pyqtSlot(QRect, int)
    def updateLineNumberArea(self, rect, dy):

        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(),
                                       self.lineNumberArea.width(),
                                       rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)


    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect();
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                                        self.lineNumberAreaWidth(),
                                        cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(
                                            self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # paint the visible line numbers
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                if block_number+1 == self.syntax_error_line_number:
                    painter.setPen(self.syntax_error_color)
                else:
                    painter.setPen(Qt.black)
                line_number_string = str(block_number + 1)
                painter.drawText(0, top, self.lineNumberArea.width(),
                                 height, Qt.AlignRight, line_number_string)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

