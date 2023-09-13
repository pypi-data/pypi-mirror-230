import os, shutil, sys
from .        import taln_archives_parser as parser
from .Event   import Event
from .Article import Article
from .Author  import Author
from datetime import datetime
from tqdm     import tqdm

months = { 1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June',
           7:'July', 8:'August', 9:'September', 10:'October', 11:'November',
           12:'December' }

volumes = [ (u'long', 'Articles longs'), 
            (u'court', 'Articles courts'),
            (u'orig', 'Travaux originaux'),
            (u'parallel', 'Traductions d\'articles en cours de soumission dans des conférences internationales'),
            (u'resume', 'Résumés d\'articles publiés dans des conférences internationales'),
            (u'survey', 'Prises de position'),
            (u'papers', 'Articles sélectionnés'),
            (u'posters', 'Posters'),
            (u'poster', 'Posters'),            
            (u'articles', 'Articles'),
            (u'démonstration', 'Démonstrations'),
            (u'demonstration', 'Démonstrations'),
            (u'demo', 'Démonstrations'),
            (u'jep', 'Journées d\'Études sur la Parole'),
            (u'inter', 'Résumés d\'articles internationaux'),
            (u'tutoriel', 'Tutoriels'),
            (u'recital', 'REncontres jeunes Chercheurs en ' + \
             'Informatique pour le Traitement Automatique des Langues'),
            (u'invite', 'Conférences invitées'),
            (u'recitalposter', 'REncontres jeunes Chercheurs en ' + \
             'Informatique pour le Traitement Automatique des Langues (Posters)'),
            (u'recitalcourt', 'REncontres jeunes Chercheurs en ' + \
             'Informatique pour le Traitement Automatique des Langues (articles courts)'),
]

def read_xml(event, where, xmlfile):
    ## read input file
    pdf_dir  = os.path.join(os.path.dirname(xmlfile), 'actes')
    ## Conference data
    conf     = parser.content_handler(xmlfile)
    event.__dict__['title']     = conf.meta['conf_titre']
    event.__dict__['abbrev']    = conf.meta['acronyme'].split("'")[0]
    if 'anthology_id' not in event.__dict__.keys() or event.__dict__['anthology_id'] == "":    
        event.__dict__['anthology'] = conf.meta['acronyme'].split("'")[0].lower()
    event.__dict__['year']      = conf.meta['acronyme'].split("'")[1]
    general_chairs = filter(lambda x : x[2] is None, conf.meta['presidents'])
    event.__dict__['chairs']    = list(map(lambda x : x[1] + ', ' + x[0], \
                                           general_chairs))
    event.__dict__['booktitle'] = 'Actes de la ' + event.__dict__['title']
    event.__dict__['shortbooktitle'] = 'Actes de '+ conf.meta['acronyme']
    event.__dict__['location']  = conf.meta['ville']+', '+conf.meta['pays']
    event.__dict__['month']     = months[int(conf.meta['dateDebut'].split('-')[1])]
    event.__dict__['begin']     = datetime.strptime(conf.meta['dateDebut'], '%Y-%m-%d')
    event.__dict__['end']       = datetime.strptime(conf.meta['dateFin'], '%Y-%m-%d')
    event.__dict__['publisher'] = 'ATALA'
    event.__dict__['url']       = conf.meta['siteWeb']
    event.__dict__['tracks']    = {}
    suffix                      = 1
    id_shift                    = 0 # to give distinct paper id in tracks
    for t in conf.meta['typeArticles']:
        track                   = {}
        track['volume']         = t[0]
        if t[0] in dict(volumes):
            track['fullname']   = dict(volumes)[t[0]] #cf taln_parser
        else:
            print("\n[Warning] Unknown full track name for track: " + t[0], \
                  file=sys.stderr)
            track['fullname']   = t[1]
        suffix                 += 1
        track_chairs           = list(filter(lambda x : x[2] is not None and \
                                             t[0] in x[2].split(","), \
                                             conf.meta['presidents']))
        if len(track_chairs) > 0:
            track['chairs']    = ", ".join(list(map(lambda x : x[0] + ' ' + x[1], \
                                                    track_chairs))) 
        event.__dict__['tracks'][t[0]] = track 
    ## Article and authors data for each track
    #for vol_type, vol_title in volumes:
        vol_type = t[0]
        vol_title= dict(volumes)[t[0]] if t[0] in dict(volumes) else t[1]
        id_shift+= 1000 #to build unique paper ids (max. 1000 papers per track)
        articles = [] 
        authors  = {}
        vol_articles = [u for u in conf.articles if u['type'] == vol_type]
        if len(vol_articles) > 0:
            print('Processing track:', vol_title, file=sys.stderr)
        for article in tqdm(vol_articles):
            #print(article)
            paper = Article()
            archives_artid = article['id'] ## of the form taln-2008-long-001
            archives_id    = str(id_shift + \
                                 int(archives_artid[-3:])) ## new unique id of the form 1001
            new_filename   = event.__dict__['abbrev'] + '_' + \
                             event.__dict__['year'] + '_paper_' + archives_id
            if os.path.exists(os.path.join(pdf_dir, archives_artid+'.pdf')):
                shutil.copy(os.path.join(pdf_dir, archives_artid+'.pdf'), \
                            os.path.join(pdf_dir, new_filename+ '.pdf'))
            else:
                shutil.copy(os.path.join(where, 'tex', 'blank.pdf'), \
                            os.path.join(pdf_dir, new_filename+ '.pdf'))
            paper.__dict__['paperid']= archives_id
            paper.__dict__['url']    = os.path.join(os.getcwd(), pdf_dir, new_filename+'.pdf')
            paper.__dict__['track']  = vol_type
            aut = []
            affiliations = dict(article['affiliations'])
            #print(article['affiliations'])
            aut_pos = 0
            for prenom, nom, rank, email in article['auteurs']:
                aut_pos+= 1
                author  = Author()
                author.__dict__['firstname']  = prenom
                author.__dict__['lastname']   = nom
                author.__dict__['email']      = email
                author.__dict__['affiliation']= affiliations[rank]
                author.__dict__['paperid']    = paper.__dict__['paperid']
                author.__dict__['rank']       = aut_pos
                aut.append(prenom.strip() + ' ' + nom.strip())
                if paper.__dict__['paperid'] not in authors.keys():
                    authors[paper.__dict__['paperid']] = []
                authors[paper.__dict__['paperid']].append(author)
            paper.__dict__['authors'] = ', '.join(aut)
            if article['title'] == article['titre'] or article['titre'] == '':
                # the paper is in English
                paper.__dict__['title']    = article['title']
                paper.__dict__['language'] = 'en'
            else:
                paper.__dict__['title'] = article['titre']
                paper.__dict__['language'] = 'fr'
                paper.__dict__['title2'] = article['title']
                paper.__dict__['language2'] = 'en'
            if paper.__dict__['language'] == 'fr': 
                if article['mots_cles'] != '':
                    paper.__dict__['keywords'] = article['mots_cles']
                if article['resume'] != '':
                    paper.__dict__['abstract'] = article['resume']
            elif paper.__dict__['language'] == 'en':
                if article['keywords'] != '':
                    paper.__dict__['keywords'] = article['keywords']
                if article['abstract'] != '':
                    paper.__dict__['abstract'] = article['abstract']
            if article['pages'] != '':
                paper.__dict__['pages'] = article['pages']
            articles.append(paper)
        if len(articles) > 0:
            event.__dict__['tracks'][vol_type]['articles'] = articles
            event.__dict__['tracks'][vol_type]['authors']  = authors
    return event
