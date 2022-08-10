import re
'''
Add your credentials from Dashboard
'id' is Client ID key and 'secret' is 
the client secret key
'''
class credentials:
    __conf = {
        'id': '''
        'secret': '''
    }

    def obtain(name):
        key = credentials.__conf[name]
        key = re.findall('gitignore(.*)end',key)
        return key[0]
