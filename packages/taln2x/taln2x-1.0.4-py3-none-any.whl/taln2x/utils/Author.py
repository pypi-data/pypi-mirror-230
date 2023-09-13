from unidecode   import unidecode

class Author(object): 

    def __init__(self):
        self.firstname   = ''
        self.lastname    = ''
        self.affiliation = ''
        self.paperid     = ''
        self.rank        = 0  #position among authors
        self.email       = ''

    def __name4ordering__(self): #method used to compute a sortable full name
        return (unidecode(self.lastname) + unidecode(self.firstname)).replace('~','')

    def __str__(self):
        s = ''
        for k,v in self.__dict__.items():
            s += k + ':' + str(v) + '\n'
        return s
