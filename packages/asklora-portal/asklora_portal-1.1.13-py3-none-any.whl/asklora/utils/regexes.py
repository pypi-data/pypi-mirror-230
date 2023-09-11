class RegexPatterns:
    email = r"^[A-Za-z0-9][A-Za-z0-9._%+-]{0,63}@(?:(?=[A-Za-z0-9-]{1,63}[.])[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*[.]){1,8}[A-Za-z]{2,63}$"
    salutation = r"^[M][A-Za-z]{1,4}\.?"
    prefix = r"\b[a-z]{3,6}\b"
