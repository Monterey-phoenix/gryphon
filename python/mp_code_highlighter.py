
#
# Modification History:
#   180803 David Shifflett
#     Updated list of keywords
#     Changed number highlighting to exclude identifiers with digits
#   180830 David Shifflett
#     Added APPLY to the list of keywords
#

"""Manages MP Code syntax highlighting.
See http://doc.qt.io/qt-5/qtwidgets-richtext-syntaxhighlighter-example.html
Adapted from https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
Also ref. https://github.com/baoboa/pyqt5/blob/master/examples/richtext/syntaxhighlighter.py

For keywords: ref. MP documentation
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from PyQt5.QtGui import QTextCursor
from mp_code_dynamic_tokens import dynamic_tokens
from settings_manager import settings

# color is a valid QT color, format is one of "b" for bold or "i" for italic
def _text_char_format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    text_char_format = QTextCharFormat()
    text_char_format.setForeground(QColor(color))
    if style == 'b':
        text_char_format.setFontWeight(QFont.Bold)
    if style == 'i':
        text_char_format.setFontItalic(True)

    return text_char_format

class MPCodeHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for MP Code.
    """

    def __init__(self, document, settings_manager):
        super(MPCodeHighlighter, self).__init__(document)
        self.document = document
        self.skip_recalculate_names = False

        # highlighting rules
        self.dynamic_highlighting_rules = list()

        # define schema name
        self.schema_name = "SCHEMA not defined"

        # handle document change event
        document.contentsChanged.connect(self.recalculate_names)

        # handle settings change event to get changed colors
        settings_manager.signal_settings_changed.connect(self.set_colors)

        # atomic names are all words
        self.atomic_name_expression = QRegularExpression(r"\b\w*\b")

        # multiline comment expressions
        self.comment_start_expression = QRegularExpression("/\\*")
        self.comment_end_expression = QRegularExpression("\\*/")

        # keywords
        self.keyword_expression = QRegularExpression(r'\b(ADD|AFTER|ALL|AND|APPLY|AT|ATTRIBUTES|AVG|BEFORE|BUILD|CHAIN|CHECK|CONTAINS|COORDINATE|CUT_END|CUT_FRONT|DIAGRAM|DISJ|DO|ELSE|ENCLOSING|ENSURE|EXISTS|FI|FIRST|FOLLOWS|FOREACH|FROM|IF|IN|IS|LAST|LEAST|MAP|MARK|MAX|MAY_OVERLAP|MIN|NOT|OD|ON|ONFAIL|OR|PRECEDES|REJECT|REVERSE|ROOT|SAY|SCHEMA|SET|SHARE|SHIFT_LEFT|SHIFT_RIGHT|SORT|SUCH|SUM|THAT|THEN|THIS|TIMES|WHEN)\b')

        # meta-symbols
        self.meta_symbol_expression = QRegularExpression(r'\$\$(EVENT|ROOT|COMPOSITE|ATOM|scope)')

        # operators, any of: -+*=<>!(){}|
        self.operator_expression = QRegularExpression("[-+\/*=<>!\(\)\{\}\|]+")

        # numbers
        self.number_expression = QRegularExpression(r'[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')

        # variables
        self.variable_expression = QRegularExpression("(<.*>)?\$[a-z][a-z0-9_]*")

        # Double-quoted string, possibly containing escape sequences
        self.quoted_text_expression = QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"')

        # validate these hardcoded regular expressions, remove if desired
        if not self.atomic_name_expression: raise Exception("Bad")
        if not self.comment_start_expression: raise Exception("Bad")
        if not self.comment_end_expression: raise Exception("Bad")
        if not self.keyword_expression: raise Exception("Bad")
        if not self.meta_symbol_expression: raise Exception("Bad")
        if not self.operator_expression: raise Exception("Bad")
        if not self.number_expression: raise Exception("Bad")
        if not self.variable_expression: raise Exception("Bad")
        if not self.quoted_text_expression: raise Exception("Bad")

        # set colors
        self.set_colors()

    # scan for regex match and set any matches with the given color format
    # for numbers, don't re-format if the preceeding character
    # is a letter or underscore
    def _scan_numbers(self, color_format, text):
        match_iterator = self.number_expression.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            capStart = match.capturedStart()
            if capStart != 0:
                preceedingChar = text[capStart-1:capStart]
            else:
                preceedingChar = ""
            # dont reformat if,
            # the preceeding character is a letter or underscore
            # or if there is no preceeding character
            ignoreStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
            if ((preceedingChar in ignoreStr) and (preceedingChar != "")):
                pass
            else:
                self.setFormat(match.capturedStart(), match.capturedLength(),
                                                             color_format)

    # scan for regex match and set any matches with the given color format
    def _scan(self, regex, color_format, text):
        match_iterator = regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(),
                                                             color_format)

    # highlightBlock is called automatically by the QT rich text engine
    def highlightBlock(self, text):

        # atomic: start by calling all words atomic events
        self._scan(self.atomic_name_expression, self.atomic_name_format, text)

        # composite, root, schema
        for name, regex in self.dynamic_highlighting_rules:
            if name == "root":
                self._scan(regex, self.root_name_format, text)
            elif name == "schema":
                self._scan(regex, self.schema_name_format, text)
            elif name == "composite":
                self._scan(regex, self.composite_name_format, text)
            else:
                print("Warning: unrecognized name '%s'"%name)

        # keywords
        self._scan(self.keyword_expression, self.keyword_format, text)

        # operators
        self._scan(self.operator_expression, self.operator_format, text)

        # numbers
        self._scan_numbers(self.number_format, text)

        # variables
        self._scan(self.variable_expression, self.variable_format, text)

        # meta-symbols
        self._scan(self.meta_symbol_expression, self.meta_symbol_format, text)

        # quoted text which can override any previous tokens
        self._scan(self.quoted_text_expression, self.quoted_text_format, text)

        # now highlight any text in multiline comments
        # set initial state, 0=not in comment, 1=in comment
        self.setCurrentBlockState(0)
        start_index = 0

        # handle multiline comment based on state of previous block
        if self.previousBlockState() != 1:
            # move start index forward if not in comment
            match = self.comment_start_expression.match(text)
            start_index = match.capturedStart()
        # now process forward from start index
        while start_index >= 0:
            match = self.comment_end_expression.match(text, start_index)
            end_index = match.capturedStart()
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + \
                                                      match.capturedLength()
            self.setFormat(start_index, comment_length, self.comment_format)

            # move to next start expression after current end expression
            match = self.comment_start_expression.match(text, start_index+2)
            start_index = match.capturedStart()

    # set all clors
    # whenever color scheme changes recalculate colors
    @pyqtSlot()
    def set_colors(self):
        self.root_name_format = _text_char_format(
                                        settings["node_root_c"], "b")
        self.composite_name_format = _text_char_format(
                                        settings["node_composite_c"], "b")
        self.schema_name_format = _text_char_format(
                                        settings["node_schema_c"], "b")
        self.atomic_name_format = _text_char_format(
                                        settings["node_atomic_c"], "b")
        self.comment_format = _text_char_format(
                                        settings["mp_code_comment_c"], "i")
        self.keyword_format = _text_char_format(
                                        settings["mp_code_keyword_c"], "")
        self.meta_symbol_format = _text_char_format(
                                        settings["mp_code_meta_symbol_c"], "b")
        self.operator_format = _text_char_format(
                                        settings["mp_code_operator_c"], "")
        self.number_format = _text_char_format(
                                        settings["mp_code_number_c"], "")
        self.variable_format = _text_char_format(
                                        settings["mp_code_variable_c"], "")
        self.quoted_text_format = _text_char_format(
                                        settings["mp_code_quoted_text_c"], "")

        # rehighlight to get new color scheme
        self.rehighlight()

    # whenever document changes recalculate dynamic names
    # and colors
    @pyqtSlot()
    def recalculate_names(self):

        # clear schema name
        self.schema_name = "SCHEMA not defined"

        # clear dynamic rules
        self.dynamic_highlighting_rules.clear()

        # get dynamically generated tokens
        tokens = dynamic_tokens(self.document)

        # add dynamic rules
        for token_type, token_name in tokens:
            if token_type == "root":
                self.dynamic_highlighting_rules.append(("root",
                            QRegularExpression("\\b%s\\b"%token_name)))
            elif token_type == "composite":
                self.dynamic_highlighting_rules.append(("composite",
                            QRegularExpression("\\b%s\\b"%token_name)))
            elif token_type == "schema":
                self.dynamic_highlighting_rules.append(("schema",
                            QRegularExpression("\\b%s\\b"%token_name)))

                # track schema name too
                self.schema_name = token_name
            else:
                print("Warning: unrecognized token '%s'" % token_type)

        # prevent recursion
        if self.skip_recalculate_names:
            return

        self.skip_recalculate_names = True

        # rehighlight, this runs highlightBlock on everything
        self.rehighlight()
        self.skip_recalculate_names = False

