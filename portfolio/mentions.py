import re


MENTION_PATTERN = re.compile(
    r'(?<![\w@])@([\w+-]+(?:\.[\w+-]+)*)',
    re.UNICODE,
)
