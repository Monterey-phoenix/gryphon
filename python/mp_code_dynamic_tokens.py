"""Identify dynamically defined tokens of type: {root, atomic, composite}.
"""

from PyQt5.QtCore import QRegularExpression

# comments
comment_start_expression = QRegularExpression("/\\*")
comment_end_expression = QRegularExpression("\\*/")

# root names
root_name_expression = QRegularExpression(r"^\s*ROOT\s*(\w*)\s*:")

# composite names
composite_name_expression = QRegularExpression(r"^\s*(\w*)\s*:")

# schema names
schema_name_expression = QRegularExpression(r"^\s*SCHEMA\s*(\w*)")

# scan provided line
# NOTE: this does not correctly parse across lines, but dynamic tokens
# should not need this to.
def _scan_line(text, tokens):

    # ROOT
    match = root_name_expression.match(text)
    if match.hasMatch():
        tokens.append(("root", match.captured(1)))

    else:
        # SCHEMA
        match = schema_name_expression.match(text)
        if match.hasMatch():
            tokens.append(("schema", match.captured(1)))

        else:
            # composite
            match = composite_name_expression.match(text)
            if match.hasMatch():
                tokens.append(("composite", match.captured(1)))

# get dynamically defined tokens as list of tuple: (token_type, name)
def dynamic_tokens(document):
    tokens = list()
    in_comment = False
    start_index = 0

    # get first line
    text_block = document.begin()

    # loop to end
    while text_block != document.end():
        text = text_block.text()
    
        # handle multiline comment based on state of previous block
        if not in_comment:
            # not in comment so move start index forward
            match = comment_start_expression.match(text)
            start_index = match.capturedStart()

            if start_index == -1:
                # no comment so scan line
                _scan_line(text, tokens)
            else:
                if start_index >= 2:
                    # in comment so scan up to comment
                    _scan_line(text[:start_index-2], tokens)

                # find out if line ends in comment or not in comment
                # NOTE: We detect multiple comments on a line but we
                # do not process text bisected by multiple comments
                # on a line.
                while start_index >= 0:
                    match = comment_end_expression.match(text, start_index)
                    start_index = match.capturedStart()
                    if start_index == -1:
                        in_comment = True
                    else:
                        match = comment_start_expression.match(text,
                                                              start_index)
                        start_index = match.capturedStart()
                        in_comment = False

        else:
            # in comment so throw away line until not in comment
            match = comment_end_expression.match(text)
            start_index = match.capturedStart()

            if start_index == -1:
                # no end comment so throw line away
                pass
            else:
                # no longer in comment so scan remainder for comment
                # find out if line ends in comment or not in comment
                # NOTE: We detect multiple comments on a line but we
                # do not process text bisected by multiple comments
                # on a line.
                while start_index >= 0:
                    match = comment_start_expression.match(text, start_index)
                    start_index = match.capturedStart()
                    if start_index == -1:
                        in_comment = False
                    else:
                        match = comment_end_expression.match(text, start_index)
                        start_index = match.capturedStart()
                        in_comment = True

        # next
        text_block = text_block.next()

    return tokens

