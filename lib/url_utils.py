def get_code_from_url(url):
    """Extract YouTube video code from URL"""
    n = 11
    s_st = 'v='
    index = url.find(s_st)
    if index > -1:
        code = url[index+len(s_st):index+n+len(s_st)]
        return code
    s_st = 'be/'
    index = url.find(s_st)
    if index > -1:
        code = url[index+len(s_st):index+n+len(s_st)]
        return code
    return None