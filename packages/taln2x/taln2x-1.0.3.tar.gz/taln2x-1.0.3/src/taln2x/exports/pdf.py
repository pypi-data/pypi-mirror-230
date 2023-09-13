import os, sys, re, shutil, subprocess, tqdm, pypdf, stat, json
from distutils             import dir_util
from urllib.parse          import quote
from pylatexenc.latex2text import LatexNodes2Text
from ..exports.anthology   import order_papers, order_session
from ..exports.archives    import texify

#months_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', \
#             'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']

def clean_tex(f):
    if os.path.exists(f):
        os.unlink(f)


def compile_tex(orig, dest, tex_template, tex_log):
    os.chdir(dest)    
    clean_tex(tex_template[:-4]+'.log')
    clean_tex(tex_template[:-4]+'.aux')
    clean_tex(tex_template[:-4]+'.out')
    clean_tex(tex_template[:-4]+'.toc')
    clean_tex('all_papers.aux')    
    subprocess.call(['pdflatex', tex_template], \
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL, \
                    timeout=30)
    subprocess.call(['pdflatex', tex_template], \
                    stdout=subprocess.DEVNULL, \
                    stderr=subprocess.DEVNULL, \
                    timeout=30)
    if not tex_log:
        clean_tex(tex_template[:-4]+'.log')
        clean_tex(tex_template[:-4]+'.aux')
        clean_tex(tex_template[:-4]+'.out')
        clean_tex(tex_template[:-4]+'.toc')
        clean_tex('all_papers.aux')    
    os.chdir(orig)

    
def getBookmarkPageNumber(filename):
    def review_bookmarks(pdf, bookmarks, label):
        res = -1
        for b in bookmarks:
            if type(b) == list:
                res = max(res, review_bookmarks(pdf, b, label))
            else:
                if b.title == label:
                    res = pdf.get_destination_page_number(b) + 1 #page count starts from 0
        return res
    with open(filename, "rb") as f:
       pdf = pypdf.PdfReader(f)
       return review_bookmarks(pdf, pdf.outline, 'EndofFrontmatter')


def updateTemplateString(file_in, chairs, event, t, exists, halid, sessions, start, paper_pdf, paper_title, paper_authors):
    # to replace: title - abbr - year - month - chairs - 
    # location - publisher - booktitle
    text_out = []
    for line_in in file_in:
        line_out = line_in 
        for check in ['background', 'logo', 'sponsors', 'credits', \
                      'message', 'preface', 'committee', 'invited', 'isbn']:
            if check in exists.keys():
                line_out = line_out.replace(check.upper()+'-PLACEHOLDER', \
                                            '\\'+check+'true')
            else:
                line_out = line_out.replace(check.upper()+'-PLACEHOLDER', \
                                            '\\'+check+'false')
        if halid:
            line_out = line_out.replace('HAL-PLACEHOLDER', \
                                        '\\HAL{\\halid}')
        else:
            line_out = line_out.replace('HAL-PLACEHOLDER', \
                                        '')
        if sessions:
            line_out = line_out.replace('SESSION-PLACEHOLDER', \
                                        '\\cursession,')
        else:
            line_out = line_out.replace('SESSION-PLACEHOLDER', \
                                        '')

        line_out = line_out.replace('TRACK-NAME-PLACEHOLDER', \
                                    event.__dict__['tracks'][t].texfullname)
        line_out = line_out.replace('PAGE-PLACEHOLDER',     \
                                    str(start))
        line_out = line_out.replace('PAPER-PDF',     \
                                    paper_pdf)
        line_out = line_out.replace('PAPER-TITLE',     \
                                    paper_title)
        line_out = line_out.replace('PAPER-AUTHORS',     \
                                    paper_authors)
        line_out = line_out.replace('TITLE-PLACEHOLDER',     \
                                    event.__dict__['textitle'] \
                                    if 'textitle' in event.__dict__ \
                                    else event.__dict__['title'])
        line_out = line_out.replace('ABBREV-PLACEHOLDER',    \
                                    event.__dict__['abbrev'])
        line_out = line_out.replace('SHORT-PLACEHOLDER',    \
                                    event.__dict__['shortbooktitle'])
        line_out = line_out.replace('YEAR-PLACEHOLDER',    \
                                    str(event.__dict__['year']))
        begin = event.__dict__['begin'].strftime('%Y-%m-%d')
        end   = event.__dict__['end'].strftime('%Y-%m-%d')
        datestr = '{\\origdate \\daterange{' + begin + '}{' + end +'} }' if begin != end else '{\\origdate \\printdate{' + begin + '} }'
        line_out = line_out.replace('DATE-PLACEHOLDER',      \
                                    datestr)
        line_out = line_out.replace('URL-PLACEHOLDER',      \
                                    str(event.__dict__['url']))
        line_out = line_out.replace('CHAIRS-PLACEHOLDER',     \
                                    chairs)
        line_out = line_out.replace('LOCATION-PLACEHOLDER',  \
                                    event.__dict__['location'])
        line_out = line_out.replace('PUBLISHER-PLACEHOLDER',  \
                                    event.__dict__['publisher'])
        line_out = line_out.replace('BOOK-PLACEHOLDER',      \
                                    event.__dict__['texbooktitle'] \
                                    if 'texbooktitle' in event.__dict__ \
                                    else event.__dict__['booktitle'])
        text_out.append(line_out)
    return ''.join(text_out)


def write_tex(event, stopwords, verbose, halid, sessions, tex_log, img, xlang):
    indir    = os.getcwd()
    outdir   = os.path.join(indir, "out")
    # Preparing output files
    eventname= event.__dict__['abbrev'] + \
               '-' + str(event.__dict__['year'])    
    if not os.path.exists(os.path.join(outdir, 'pdf_' + eventname)):
        os.mkdir(os.path.join(outdir, 'pdf_' + eventname))
    ## Process articles
    for t in event.__dict__['tracks']:
        print('Processing track:', t, file=sys.stderr)
        chairs = ', '.join(list(map(lambda x: x.split(', ')[1] + \
                                    ' ' + x.split(', ')[0], \
                                    event.__dict__['chairs'])))
        if event.__dict__['tracks'][t].chairs != '':
            chairs = event.__dict__['tracks'][t].chairs                
        source = indir
        dest   = os.path.join(outdir, 'pdf_' + eventname, t)
        if not os.path.exists(dest):
            os.mkdir(dest)
        if not os.path.exists(os.path.join(dest, 'pdf')):
            os.mkdir(os.path.join(dest, 'pdf'))
        if not os.path.exists(os.path.join(dest, 'pdf_out')):
            os.mkdir(os.path.join(dest, 'pdf_out'))
        allpapers = open(os.path.join(dest, 'all_papers.tex'), 'wt')
        ## Process paper in right order (cf automatic numbering)
        papers  = event.__dict__['tracks'][t].articles
        # track's config overrides command line one
        start = 1 #default
        if int(event.__dict__['tracks'][t].startpage) > 0:
            start = int(event.__dict__['tracks'][t].startpage)
        order = 'input' #default
        if event.__dict__['tracks'][t].order != '':
            order = event.__dict__['tracks'][t].order
        ordered     = papers
        if sessions and event.__dict__['tracks'][t].sessions != '':
            ordered = order_session(papers, order, stopwords, verbose, \
                                    event.__dict__['tracks'][t])
        else:
            ordered = order_papers(papers, order, stopwords, verbose, \
                                   event.__dict__['tracks'][t].authors)
        for art in tqdm.tqdm(ordered):
            if art:
                process_article(event, t, indir, os.path.join(outdir, 'pdf_' + eventname), \
                                art, allpapers, halid, sessions)
            #no else since session's separator pages (i.e. when art is None) are taken 
            #care of by latex
        allpapers.close()
        ## Compiling PDF proceedings
        ## Copy files
        TEXSOURCES  =['pre-proceedings.tex', 'pre-proceedings-en.tex', 'single_paper.tex', 'by.eps']
        EVENTSOURCES=['background.png', 'logo.png','sponsors.png', 'credits.tex']
        TRACKSOURCES=['message.tex', 'preface.tex', 'committee.tex', 'invited.tex', 'isbn.tex']
        exists      = {}
        for x in TEXSOURCES:
            shutil.copy(os.path.join(source,x), dest)
        for y in EVENTSOURCES: 
            if os.path.exists(os.path.join(source, y)):
                shutil.copy(os.path.join(source, y), dest)
                filename = y.split('.')[0]
                exists[filename] = True
            else:
                print('[Info] file ' + y + ' not found', \
                      file=sys.stderr)
        for z in TRACKSOURCES:
            if os.path.exists(os.path.join(source, t, z)):
                shutil.copy(os.path.join(source, t, z), dest)
                filename = z.split('.')[0]
                exists[filename] = True
            else:
                print('[Info] file ' + z + ' not found in ' + t, \
                      file=sys.stderr)
        ## Copy users' images if needed
        if img is not None and img != "":
            dir_util.copy_tree(img, dest)
        ## Prepare proceedings
        if xlang == 'fr':
            tex_input = 'pre-proceedings.tex'
        elif xlang == 'en':
            tex_input = 'pre-proceedings-en.tex'
        else:
            print('[Warning] Unknown language for pdf output, default one (fr) used.', file=sys.stderr)
        with open(os.path.join(dest, tex_input), 'rt') as file_in:
            text_out = updateTemplateString(file_in, chairs, event, t, exists, halid, sessions, \
                                            start, '', '', '')
            with open(os.path.join(dest, 'proceedings.tex'), 'wt') as file_out:            
                file_out.write(text_out)
        #Let us now compile the proceedings
        curdir = os.getcwd()
        try:
            compile_tex(curdir, dest, 'proceedings.tex', tex_log) ## actual compilation       
            # let us finally extract frontmatter and papers
            full_proc  = os.path.join(outdir, 'pdf_'+eventname,t, 'proceedings.pdf')
            pdfreader  = pypdf.PdfReader(full_proc, strict=False)
            endoffront = getBookmarkPageNumber(full_proc)
            if ordered and not(ordered[0]): #session
                endoffront += 1 
            frontprint = pypdf.PdfWriter() 
            for cpt in range(endoffront-1):
                PageObj = pdfreader.pages[cpt]
                cpt += 1
                frontprint.add_page(PageObj)
            frontout= open(os.path.join(outdir, 'pdf_' + eventname, t, 'frontmatter.pdf'), \
                           'wb')
            frontprint.write(frontout)
            frontout.close()
            # let us then compute papers' pages (to update their header/footer)
            print('Compiling pdfs of articles ...')
            shift = start
            for art in ordered:
                if art:
                    fname  = os.path.basename(art.__dict__['url'])[:-4]+'.tex'
                    fpath  = os.path.join(outdir, 'pdf_' + eventname, t, 'pdf_out', fname)
                    shutil.copy(os.path.join(source,'single_paper.tex'), fpath)
                    shutil.copy(os.path.join(source,'by.eps'), os.path.join(outdir, 'pdf_' + eventname, t, 'pdf_out', 'by.eps'))
                    with open(os.path.join(source,'single_paper.tex'), 'rt') as f_in:
                        t_out = updateTemplateString(f_in, chairs, event, t, exists, halid, sessions, \
                                                     shift, os.path.join('..','pdf',fname[:-4]+'.pdf'),\
                                                     art.__dict__['title'], art.__dict__['authors'])
                        with open(fpath, 'wt') as f_out:
                            f_out.write(t_out)
                    compile_tex(curdir, os.path.join(outdir, 'pdf_' + eventname, t, 'pdf_out'), \
                                fname, tex_log)
                    shift += art.__dict__['numpages']
                #we skip session's delimiter
                else:
                    shift += 1
                    
        except subprocess.TimeoutExpired as toe:
            print('\n!!!! LaTeX compilation failed !!!!\n', file=sys.stderr)
            #sys.exit(198)
            continue

def process_article(event, track, idir, odir, art, allpapersh, halid, sessions):
    origfile= os.path.join(idir, track, 'pdf', os.path.basename(art.__dict__['url']))
    outfile = os.path.join(odir, track, 'pdf', os.path.basename(art.__dict__['url']))
    shutil.copy(origfile, outfile)
    os.chmod(outfile, stat.S_IRUSR | stat.S_IWUSR) #set read/write rights
    ## Extract hyperlinks using pax/PDFBox
    if shutil.which('pdfannotextractor') is None:
        print('Error: pax tex package is missing ' + \
              '(https://www.ctan.org/tex-archive/macros/latex/contrib/pax), ' + \
              'in deb-based linux, it is part of texlive-latex-extra.', file=sys.stderr)
        sys.exit(199)
    else:
        os.environ["CLASSPATH"] = os.path.join('tex','PDFBox-0.7.3.jar')
        try:
            subprocess.call(['pdfannotextractor',outfile], \
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        except subprocess.TimeoutExpired as toe:
            print('Hyperlink extraction failed', file=sys.stderr)
    ## Update allpapers.tex
    hal = ''
    if halid:
        if art.__dict__['idhal']=='':
            out = subprocess.check_output(["curl", "-s", \
                                           'https://api.archives-ouvertes.fr/search/?q=title_s:\"'\
                               + quote(LatexNodes2Text().latex_to_text(art.__dict__['title'])).replace('%C2%A0', '%20')\
                                           .replace('%20%20%20', '%26') + '\"&fl=halId_s'])
            if int(json.loads(out.decode())['response']['numFound']) == 1:
                hal = json.loads(out.decode())['response']['docs'][0]['halId_s']
            elif int(json.loads(out.decode())['response']['numFound']) > 1:
                hal = json.loads(out.decode())['response']['docs'][0]['halId_s']
                print('[Warning] Several HAL identifiers found for paper ' + art.__dict__['paperid'] \
                      + '. Using ' + hal, \
                      file=sys.stderr)
            else:
                print('[Warning] HAL identifier not found for paper ' + art.__dict__['paperid'], \
                      file=sys.stderr)
        else:
            hal = art.__dict__['idhal']
            print('[Info] Using default id-hal from the csv file for paper ' + art.__dict__['paperid'] \
                  + ' (' + hal + ')', \
                  file=sys.stderr)
    session = ''
    if sessions and art.__dict__['session'] != '':
        session = art.__dict__['session']
    s = '\\goodpaper{pdf/' + os.path.basename(art.__dict__['url']) + '}{' \
        + texify(art.__dict__['title']) + '}%\n{' + \
        texify(art.__dict__['authors'].replace(' and ', ', ')) + \
        '}{'+hal+'}{'+session+'}\n\n' 
    allpapersh.write(s)
