class Event(object):

    def __init__(self):
        self.title          = ''
        self.abbrev         = ''
        self.chairs         = []
        self.location       = ''
        self.booktitle      = ''
        self.shortbooktitle = ''
        self.begin          = None #datetime type
        self.end            = None #datetime type
        self.month          = ''
        self.url            = ''
        self.publisher      = ''
        self.sig            = ''
        self.base_url       = '' #for TALN archives
        self.anthology      = ''
        self.tracks         = {}   #dict mapping track id with track object (formerly itself a dict)

    def __str__(self):
        s = ''
        for k,v in self.__dict__.items(): 
            if k != 'tracks':
                s += k + ':' + str(v) + '\n'
            else:
                for t,i in v.items():
                    s += '\n' + t + '\n'
                    for a,b in i.__dict__.items():
                        if type(b) == list: #articles
                            s += a + ':' + '\n  '.join(list(map(lambda x: str(x), b))) + '\n'
                        elif type(b) == dict: #authors
                            flat_list = [item for sublist in b.values() for item in sublist]
                            s += a + ':' + '\n  '.join(list(map(lambda x: str(x), flat_list))) + '\n'
                        else:
                            s += a + ':' + str(b) + '\n'
        return s
