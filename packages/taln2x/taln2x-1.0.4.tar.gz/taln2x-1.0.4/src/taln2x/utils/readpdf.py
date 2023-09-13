import os, sys, shutil, re, subprocess, pypdf
from   langdetect  import detect

def read_pdf(article, indir, path, default_title, ignore_pdf, verbose):
    pdf      = pypdf.PdfReader(os.path.join(indir, 'pdf', path), \
                                strict=False)
    numpages = pdf.trailer['/Root']['/Pages']['/Count']
    #print(article.__dict__['paperid'], numpages,'pages')
    article.__dict__['numpages'] = numpages
    try:
        if shutil.which('pdftotext') is None:
            print('[Error] pdftotext is missing. ' + \
                  'Please install the xPdf command line tools,' + \
                  '(see http://www.xpdfreader.com/pdftotext-man.html).', \
                  file=sys.stderr)
            sys.exit(199)
        args = ["pdftotext",
                '-nopgbrk',
                os.path.join(indir, 'pdf', path),
                '-']
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        paper_content = res.stdout.decode('utf-8')
        #print('*',paper_content)
        m = None
        if article.__dict__['language'] == 'fr':
            #Searching French Abstract:
            mabs = re.search('[ÉE]\s*S\s*U\s*M\s*[ÉE][\_\.]*\n*(.+?)\n+' + \
                             'A\s*B\s*S\s*T\s*R\s*A\s*C\s*T', \
                             paper_content, re.DOTALL)
            #Search French keywords:
            mkey = re.search('M\s*O\s*T\s*S\s*-\s*C\s*L\s*[ÉE]\s*S\s*:\s*(.+?)\n+' + \
                             'K\s*E\s*Y\s*', \
                             paper_content, re.IGNORECASE|re.DOTALL)
            #Searching English Title:
            m = re.search('B\s*S\s*T\s*R\s*A\s*C\s*T\s*\_*\n+([^\.]+?)\.', \
                          paper_content, re.DOTALL)
        else:
            #Searching Englich Abstract:
            mabs = re.search('A\s*B\s*S\s*T\s*R\s*A\s*C\s*T\s*[\_\.]*\n*(.+?)\n+' + \
                             '(M\s*O\s*T\s*S|R\s*[ÉE]\s*S\s*U)', \
                             paper_content, re.IGNORECASE|re.DOTALL)
            #Search English keywords:
            mkey = re.search('K\s*E\s*Y\s*W\s*O\s*R\s*D\s*S\s*:\s*(.+?)\n+' + \
                             '1\s*', \
                             paper_content, re.IGNORECASE|re.DOTALL)
            #Searching French Title:
            m = re.search('[ÉE]\s*S\s*U\s*M\s*[ÉE]\n+([^\.]+?)\.', \
                          paper_content, re.IGNORECASE|re.DOTALL)
            if m: #secondary title found (right after RÉSUMÉ / ABSTRACT)
                #in case the title is split over lines, we keep lines which
                #do not start with an upper case letter (except when the preceding 
                #line ends with more than 3 letters, e.g. it is not the determiner "A") 
                title2 = re.sub(r'([\w-]{4,})(\s*[\?”"]?)\s*\n+[A-Z]', r'\1\2~', \
                                m.group(1)).split('~')[0].replace('\n', ' ')
                #print('\n*** before:', article.__dict__['paperid'], m.group(1), '***\n')
                #print('\n*** found:', article.__dict__['paperid'], title2, '***\n')
                article.__dict__['title2']    = title2
                article.__dict__['language2'] = detect(title2)
            else: # for one paper, unicode was needed
                if verbose > 2:
                    print('[Warning] Secondary title extraction failed for paper ', \
                          article.__dict__['title'])
                        #print(paper_content)
            if mabs and (not ignore_pdf or article.__dict__['abstract'] == ''):
                article.__dict__['abstract'] = mabs.group(1).replace('\n', ' ')
                #print('*',article.__dict__['abstract'])
            if mkey and (not ignore_pdf or article.__dict__['keywords'] == ''):
                article.__dict__['keywords'] = mkey.group(1).replace('\n',' ')
                #print('*',article.__dict__['keywords'])
    except UnicodeDecodeError as ud:
        if verbose >= 0:
            print('[Warning] encoding error, ' + \
                  'paper ignored for pdf title/abstract extraction:', \
                  article.__dict__['title'], '('+article.__dict__['paperid']+')', \
                  file=sys.stderr)
        #English title read in column 4 in csv file (fallback)
        article.__dict__['title2'] = default_title
