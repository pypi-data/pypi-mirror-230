import os, shutil, re, sys, tqdm
import xml.etree.cElementTree as ET
from xml.dom             import minidom
from unidecode           import unidecode
from lxml                import etree
from ..exports.anthology import order_papers, order_session

DBLP_ID  = 'conf/taln'

def write_dblp_xml(event, stopwords, verbose, sessions):
    indir   = os.getcwd()
    xmldir  = os.path.join(indir, "out")
    # Preparing output dir
    eventname= 'dblp_' + unidecode(event.__dict__['abbrev']) + \
               '-' + str(event.__dict__['year'])
    if not os.path.exists(os.path.join(xmldir, eventname)):
        os.mkdir(os.path.join(xmldir, eventname))
    ## Process articles
    for i,t in enumerate(event.__dict__['tracks']):
        print('Processing track:', t, file=sys.stderr)
        #  Base url
        base_url = os.path.join('http://talnarchives.atala.org', \
                                event.__dict__['abbrev'], \
                                event.__dict__['abbrev'] +'-'+ str(event.__dict__['year'])) 
        if event.__dict__['tracks'][t].base_url != '':
            base_url = event.__dict__['tracks'][t].__dict__['base_url']
        else:
            print('[Warning] No base_url defined in track configuration (event.yml)\n' + \
                  'Default (TALN archives) URL used instead, please check output', \
                  file=sys.stderr)
        volumename = event.__dict__['booktitle'] + '. ' + \
                     event.__dict__['tracks'][t].__dict__['fullname'] 
        xmlfile  = os.path.join(xmldir, eventname, \
                                eventname.lower() + '-' + str(i+1) + '.xml')
        # Preparing XML content (DOM)
        root     = ET.Element('dblpsubmission')
        proc     = ET.SubElement(root, 'proceedings')
        ## Process edition
        ET.SubElement(proc, 'key').text = DBLP_ID
        for c in event.__dict__['chairs']:
            ET.SubElement(proc, 'editor').text = c.split(",")[1].strip() + " " + \
                                                 c.split(",")[0].strip()
        ET.SubElement(proc, 'title').text = volumename
        if event.__dict__['publisher'] != '':
            ET.SubElement(proc, 'publisher').text = event.__dict__['publisher']
        ET.SubElement(proc, 'year').text = str(event.__dict__['year'])
        conf = ET.SubElement(proc, 'conf')
        ET.SubElement(conf, 'acronym').text = event.__dict__['abbrev']
        ET.SubElement(conf, 'location').text= event.__dict__['location']
        span = str(event.__dict__['begin'].day) + '-' + str(event.__dict__['end'].day)
        if event.__dict__['begin'].day == event.__dict__['end'].day:
            span = str(event.__dict__['begin'].day)
        ET.SubElement(conf, 'date').text    = months[event.__dict__['begin'].month] + ' ' +\
                                              span + ', ' +\
                                              str(event.__dict__['end'].year)
        ET.SubElement(conf, 'url').text     = event.__dict__['url']
        toc = ET.SubElement(proc, 'toc')
        ## Processing papers
        # track's config overrides command line one
        order   = 'input' #default
        if event.__dict__['tracks'][t].order != '':
            order = event.__dict__['tracks'][t].__dict__['order']
        papers  = event.__dict__['tracks'][t].__dict__['articles']
        ordered = papers
        if sessions and event.__dict__['tracks'][t].sessions != '':
            ordered = order_session(papers, order, stopwords, verbose, \
                                    event.__dict__['tracks'][t])
        else:
            ordered = order_papers(papers, order, stopwords, verbose, \
                                   event.__dict__['tracks'][t].__dict__['authors'])
        # Track settings overwrite cli start option
        start    = 1 #default
        if int(event.__dict__['tracks'][t].startpage) > 0:
            start = int(event.__dict__['tracks'][t].__dict__['startpage'])
        current_pos = start
        for art in tqdm.tqdm(ordered):
            if art:
                ## Publication
                article = ET.SubElement(toc, 'publ')
                try:
                    for au in event.__dict__['tracks'][t].__dict__['authors'][int(art.__dict__['paperid'])]:
                        ET.SubElement(article, 'author').text = au.__dict__['firstname']+' '+\
                                                                au.__dict__['lastname']
                except KeyError:
                    for aut2 in art.__dict__['authors'].replace(' and ', ', ').split(', '):
                        aut     = re.sub(r'([^\\])~', r'\1 ', aut2)
                        fname   = aut.split(' ')[0]
                        lname   = ' '.join(aut.split(' ')[1:])
                        ET.SubElement(article, 'author').text = fname + ' ' + lname
                ## Title
                ET.SubElement(article, 'title').text = art.__dict__['title']
                pages = art.__dict__['pages']
                if pages == '':
                    pages = str(current_pos) + '-' + str(current_pos + art.__dict__['numpages']-1)
                current_pos += art.__dict__['numpages']
                ET.SubElement(article, 'pages').text=pages
                ET.SubElement(article, 'ee').text=os.path.join(base_url, \
                                                               art.__dict__['paperid']+'.pdf')
            else:
                current_pos += 1 # skip session's delimiter
        ## Printing and validating XML file
        xmltree = etree.fromstring(ET.tostring(root, short_empty_elements=False))
        dtd = etree.DTD(os.path.join(indir, 'out', 'dblpsubmission.dtd'))
        if not dtd.validate(xmltree):
            print('XML DTD validation error', file=sys.stderr)
            print(dtd.error_log.filter_from_errors(), file=sys.stderr)
            sys.exit(1)
        with open(xmlfile, 'w') as f:
            print(etree.tostring(xmltree, encoding="utf8", xml_declaration=True, \
                                 pretty_print=True, \
                                 doctype=\
                                 '<!DOCTYPE dblpsubmission SYSTEM "dblpsubmission.dtd">').\
                  decode(), file=f)
