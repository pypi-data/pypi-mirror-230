class Regex:
    def __init__(self, pattern):
        """
        Initialize a Regex instance with a regular expression pattern.

        :param pattern: The regular expression pattern to match.
        """
        self.pattern = pattern
        self.groups = []

    def match(self, text):
        """
        Match the regular expression pattern against the given text.

        :param text: The text to match against the pattern.
        :return: True if the pattern matches the text, otherwise False.
        """
        return self._match_from_index(0, 0, text)

    def _match_from_index(self, pattern_index, text_index, text):
        """
        Recursively match the regular expression pattern starting from a specific index in the text.

        :param pattern_index: The index in the pattern to start matching from.
        :param text_index: The index in the text to start matching from.
        :param text: The text to match against the pattern.
        :return: True if the pattern matches the text, otherwise False.
        """
        if pattern_index == len(self.pattern) and text_index == len(text):
            return True

        if pattern_index == len(self.pattern):
            return False

        if pattern_index + 1 < len(self.pattern) and self.pattern[pattern_index + 1] == '*':
            if (
                (self.pattern[pattern_index] == text[text_index] or self.pattern[pattern_index] == '.') and
                text_index < len(text)
            ):
                return (
                    self._match_from_index(pattern_index, text_index + 1, text) or
                    self._match_from_index(pattern_index + 2, text_index, text)
                )
            else:
                return self._match_from_index(pattern_index + 2, text_index, text)

        if pattern_index + 1 < len(self.pattern) and self.pattern[pattern_index + 1] == '+':
            if (
                (self.pattern[pattern_index] == text[text_index] or self.pattern[pattern_index] == '.') and
                text_index < len(text)
            ):
                return (
                    self._match_from_index(pattern_index, text_index + 1, text) or
                    (
                        self._match_from_index(pattern_index, text_index, text) and
                        self._match_from_index(pattern_index + 2, text_index + 1, text)
                    )
                )
            else:
                return False

        if pattern_index + 1 < len(self.pattern) and self.pattern[pattern_index + 1] == '?':
            if self.pattern[pattern_index] == text[text_index] or self.pattern[pattern_index] == '.':
                return (
                    self._match_from_index(pattern_index, text_index + 1, text) or
                    self._match_from_index(pattern_index + 2, text_index, text)
                )
            else:
                return self._match_from_index(pattern_index + 2, text_index, text)

        if pattern_index + 2 < len(self.pattern) and self.pattern[pattern_index + 2] == '{' and self.pattern[pattern_index + 4] == '}':
            min_count = int(self.pattern[pattern_index + 1])
            max_count = int(self.pattern[pattern_index + 3])
            if min_count <= max_count:
                for i in range(min_count):
                    if (
                        (self.pattern[pattern_index] == text[text_index] or self.pattern[pattern_index] == '.') and
                        text_index < len(text)
                    ):
                        if i == min_count - 1 and i < max_count - 1:
                            return (
                                self._match_from_index(pattern_index, text_index + 1, text) or
                                self._match_from_index(pattern_index + 6, text_index + 1, text)
                            )
                        elif i < max_count - 1:
                            if self._match_from_index(pattern_index, text_index + 1, text):
                                text_index += 1
                        else:
                            return self._match_from_index(pattern_index + 6, text_index, text)
                    else:
                        break
                return False
            else:
                raise ValueError("Invalid quantifier: min_count > max_count")

        if self.pattern[pattern_index] == '[':
            end_bracket_index = self.pattern.find(']', pattern_index)
            if end_bracket_index == -1:
                raise ValueError("Invalid character class: missing ']'")
            char_class = self.pattern[pattern_index + 1:end_bracket_index]
            if (
                (text[text_index] in char_class) or
                (len(char_class) >= 3 and char_class[1] == '-' and
                 char_class[0] <= text[text_index] <= char_class[2])
            ):
                return self._match_from_index(end_bracket_index + 1, text_index + 1, text)
            return False

        if self.pattern[pattern_index] == '(':
            end_paren_index = self.pattern.find(')', pattern_index)
            if end_paren_index == -1:
                raise ValueError("Invalid grouping: missing ')'")
            group_pattern = self.pattern[pattern_index + 1:end_paren_index]
            group_matched = False

            for i in range(text_index, len(text) + 1):
                if self._match_from_index(0, i, text):
                    group_matched = True
                    break

            if group_matched:
                self.groups.append(text[text_index:i])
                return (
                    self._match_from_index(end_paren_index + 1, i, text) or
                    (
                        self._match_from_index(pattern_index + 1, text_index, text) and
                        self._match_from_index(end_paren_index + 1, i, text)
                    )
                )
            else:
                return False

        if self.pattern[pattern_index] == '^':
            if text_index == 0:
                return self._match_from_index(pattern_index + 1, text_index, text)
            return False

        if self.pattern[pattern_index] == '$':
            if text_index == len(text):
                return self._match_from_index(pattern_index + 1, text_index, text)
            return False

        if self.pattern[pattern_index] == '\\':
            if (
                self.pattern[pattern_index + 1] == 'd' and text[text_index].isdigit() or
                self.pattern[pattern_index + 1] == 'w' and text[text_index].isalnum() or
                self.pattern[pattern_index + 1] == 's' and text[text_index].isspace() or
                self.pattern[pattern_index + 1] == text[text_index]
            ):
                return self._match_from_index(pattern_index + 2, text_index + 1, text)
            elif self.pattern[pattern_index + 1].isdigit() and int(self.pattern[pattern_index + 1]) <= len(self.groups):
                group_index = int(self.pattern[pattern_index + 1])
                if text_index + len(self.groups[group_index]) <= len(text) and text[text_index:text_index + len(self.groups[group_index])] == self.groups[group_index]:
                    return self._match_from_index(pattern_index + 2, text_index + len(self.groups[group_index]), text)
                return False
            return False

        if (
            (self.pattern[pattern_index] == text[text_index] or self.pattern[pattern_index] == '.') and
            text_index < len(text)
        ):
            return self._match_from_index(pattern_index + 1, text_index + 1, text)

        return False
