import os, sys, shutil, subprocess, json, tqdm
from urllib.parse          import quote
from pylatexenc.latex2text import LatexNodes2Text
from ..exports.anthology   import order_papers, order_session

def get_id(event, indir, stopwords, verbose, sessions):
    for t in event.__dict__['tracks']:
        print('Processing track:', t, file=sys.stderr)
        idfile = open(os.path.join(indir, 'idhal-' + event.__dict__['abbrev'] + '-' + \
                                   str(event.__dict__['year']) + '-' + t +'.csv'),'w')
        papers  = event.__dict__['tracks'][t]['articles']
        order = 'input'
        if 'order' in event.__dict__['tracks'][t].keys():
            order = event.__dict__['tracks'][t]['order']
        ordered     = papers
        if sessions and event.__dict__['tracks'][t].sessions != '':
            ordered = order_session(papers, order, stopwords, verbose, \
                                    event.__dict__['tracks'][t])
        else:
            ordered = order_papers(papers, order, stopwords, verbose, \
                                   event.__dict__['tracks'][t]['authors'])
        for art in tqdm.tqdm(ordered):
            if art:
                get_id_article(art, idfile, verbose)
        idfile.close()

def get_id_article(art, idfile, verbose):
    command = ["curl", "-s", \
               'https://api.archives-ouvertes.fr/search/?q=title_s:\"'\
               + quote(LatexNodes2Text().latex_to_text(art.__dict__['title'])).\
               replace('%C2%A0', '%20').replace('%20%20%20', '%26')\
               + '\"&fl=halId_s']
    out = subprocess.check_output(command)
    nb_id = int(json.loads(out.decode())['response']['numFound'])
    if nb_id > 0:
        hal = ';'.join(set([json.loads(out.decode())['response']['docs'][i]['halId_s'] \
                        for i in range(nb_id)]))
        s   = [art.__dict__['paperid'], art.__dict__['title'], hal] 
        print('\t'.join(s),file=idfile)
        if nb_id > 1 and verbose > 1:
            print('[Info] Several HAL identifiers found for paper ' + art.__dict__['paperid'], \
              file=sys.stderr)
    else:
        if verbose > 1:
            print('[Info] HAL identifier not found for paper ' + art.__dict__['paperid'], \
                  file=sys.stderr)
            print('[Info] command used:\n' + ' '.join(command), file=sys.stderr)
            print('[Info] paper title :\n' + art.__dict__['title'], file=sys.stderr)
        s   = [art.__dict__['paperid'], art.__dict__['title'], 'NOT AVAILABLE']
        print('\t'.join(s),file=idfile)
