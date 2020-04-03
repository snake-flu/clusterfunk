# return parameter if not a string
def check_str_for_bool(s):
    if isinstance(s, str):
        if s.lower() == 'true':
            return True
        elif s.lower() == 'false':
            return False

    return s
