import yaml
from .           import Event, Track

def get_meta(config, anthology_id):
    event = Event()
    doc = {}
    with open(config, 'r') as f:
        try:
            doc = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)
            pm = exc.problem_mark
            print("Your file {} has an issue on line {} at position {}".
                  format(pm.name, pm.line, pm.column))
        #print(doc)
    # Feed an Event object
    for k,v in doc.items():
        #print('**',k,v)
        if k == 'tracks': #v is then a dict mapping trackid with a dict
            for x in v.keys():
                t = Track(x)
                t.volume = x  # Add volume name (for anthology)
                for y in v[x].keys(): # Turn track's dict into an object
                    t.__dict__[y] = v[x][y]
                    if y == 'fullname':
                        t.__dict__['texfullname'] = t.__dict__['fullname']
                        t.__dict__['fullname']    = t.__dict__['fullname'].replace('\\','').replace('--','-')
                event.__dict__['tracks'][x] = t
        else:
            event.__dict__[k] = v
    # Command line flag anthology overrides config file's value
    if anthology_id is not None:
        event.__dict__['anthology'] = anthology_id
    # Auto-completions: (mandatory fields for anthology)
    if event.__dict__['shortbooktitle'] == '':
        if 'short_booktitle' in event.__dict__:
            event.__dict__['shortbooktitle'] = event.__dict__['short_booktitle']
        else:
            event.__dict__['shortbooktitle'] = event.__dict__['booktitle']
    if event.__dict__['begin'] is not None :
        event.__dict__['month'] = event.__dict__['begin'].month
        event.__dict__['year']  = event.__dict__['begin'].year
    # Convenience for LaTeX-PDF export (newlines in title and booktitle)
    event.__dict__['textitle'] = event.__dict__['title'].replace(' ; ','\\\\%\n')
    event.__dict__['title']    = event.__dict__['title'].replace('\\','').replace('--', '-')
    event.__dict__['texbooktitle'] = event.__dict__['booktitle']
    event.__dict__['booktitle']    = event.__dict__['booktitle'].replace('\\','').replace('--', '-')
    return event
