
# coding: utf-8

# In[3]:


import re
import json
import requests
import pdb
import datetime


# ```
# For alle objekttyper: 
#         For alle områdetyper: 
#             for alle vegkategorikombinasjoner:
#                  "antall" : Totalt antall
#                  per egenskapsverdi:   
#                     {'prosent': '<span class="v0-20 ">34.0%</span>',
#                      'url': '',
#                     'antall': 1667} 
# ```
# 
# vegkategorikombinasjoner: ```['erf', 'f', 'er']```
# 
# områdetyper = alle regioner, alle fylker. => "region5", "fylke1" 
# ```['region5', 'region4', 'fylke5', 'fylke50', 'fylke20', 'fylke11', 'fylke10', 'fylke12', 'fylke15', 'fylke14', 'fylke4', 'fylke19', 'fylke18', 'fylke7', 'region3', 'region2', 'region1', 'fylke6', 'fylke1', 'fylke3', 'fylke2', 'fylke9', 'fylke8']```
# 

# In[7]:



def prosentklasser( ant, tot_antall ): 
# '<span class="v80-100 ">92.0%</span>'

    if tot_antall > 0: 
        prosent =  round( 100 * ant / tot_antall, 1) 

        if prosent == 100.0: 
            pk = 'v100'
        elif prosent >= 80: 
            pk = 'v80-100'
        elif prosent >= 60: 
            pk = 'v60-80'
        elif prosent >= 40: 
            pk = 'v40-60'
        elif prosent >= 20: 
            pk = 'v20-40'
        else: 
            pk = 'v0-20'

        return '<span class="' + pk + '">' + str(prosent) + '%</span>'
    else: 
        prosent = 'N/A'
        pk = 'vnull'

        return '<span class="' + pk + '">' + prosent + '</span>'


        
def lagurl( vegobjekttypeid, omraadetype, omraadenummer, egenskapid, vegreferanser):
 
    
    url = 'https://www.vegvesen.no/vegkart/vegkart/#kartlag:geodata/hva:(~(id:' 
        
    url += str(vegobjekttypeid) + ',filter:(~(type_id:' + str( egenskapid ) 
    url += ",operator:'*21*3d,verdi:null)),farge:'0_0))/hvor:("
    url +=  omraadetype + ':(~' + str(omraadenummer) +  '))/@600000,7225000,3' 

#     print( url )
    return url 
    
def anrope( vegobjekttypeid, omraadefilter=None, egenskapfilter=None, testrun=False): 
    headers = { 'accept' : 'application/vnd.vegvesen.nvdb-v2+json', 
                            'X-Client' : 'nvdbapi.py',
                            'X-Kontaktperson' : 'jan.kristian.jensen@vegvesen.no'}
    apiurl = 'https://www.vegvesen.no/nvdb/api/v2/vegobjekter/'
    
    params = {}
    if omraadefilter: 
        params.update(omraadefilter)

    if egenskapfilter:
        params.update( egenskapfilter)
        
    r = requests.get( apiurl + str( vegobjekttypeid ) + '/statistikk', 
                     headers=headers, params=params )
    outdata = r.json()
    if testrun:
        print( '---- ')
        print( r.url )
        print( outdata )
#     print( r.url )
    return int( outdata['antall'] )



def hentstatistikk( typedefinisjon, testrun=False):
    
    omraader = ['region5', 'region4', 'fylke5', 'fylke50', 'fylke20', 'fylke11', 'fylke10', 'fylke12', 
     'fylke15', 'fylke14', 'fylke4', 'fylke19', 'fylke18', 'fylke7', 'region3', 
     'region2', 'region1', 'fylke6', 'fylke1', 'fylke3', 'fylke2', 'fylke9', 'fylke8']
    
    
    vegkategorier = ['erf', 'er', 'f']

    if testrun: 
        omraader = omraader[1:2]
        vegkategorier = vegkategorier[0:1]

    
    statistikk = {}
    for omr in omraader: 
        m = re.match(r"([a-z]+)([0-9]+)", omr) 
        b = m.groups()
        omraadefilter = { b[0] : b[1] }
        
        statistikk[omr] = {}

        for vegkat in vegkategorier: 
            # Hent total antall: 
            statistikk[omr][vegkat] = {}
            omraadefilter['vegreferanse'] = list( vegkat )
            tot_antall = anrope( typedefinisjon['id'], omraadefilter=omraadefilter ) 
            statistikk[omr][vegkat]['antall'] = tot_antall 
            
            for eg in typedefinisjon['egenskapstyper']: 
                egfilter = { 'egenskap' : str(eg['id']) + "!=null" }
                ant = anrope( typedefinisjon['id'], omraadefilter=omraadefilter, egenskapfilter=egfilter, testrun=testrun)
                prosent = prosentklasser( ant, tot_antall)
                # vegkarturl = lagurl( typedefinisjon['id'], b[0], b[1], eg['id'])

                statistikk[omr][vegkat][eg['navn']] = { 'prosent' : prosent,
                                        'url' : '', 
                                       'antall' : ant}
            
    return statistikk

def hentvegobjekter(testrun=False ):

    directory = '/home/jajens/nvdb-kontoutskrift/' 
    with open( directory + 'datasett1.json') as f: 
        data1 = json.load(f)
        
    with open( directory + 'datasett2.json') as f: 
        data2 = json.load(f)
    
    with open( directory + 'datasett3.json') as f: 
        data3 = json.load(f)
    
    definisjoner = data1 + data2 + data3 
    
    if testrun: 
        definisjoner = definisjoner[0:3]
    
    statistikk = {}
    count = 0
    for typedefinisjon in definisjoner:
        count += 1
        print( typedefinisjon['navn'], count, 'av', len(definisjoner))
        delstatistikk = hentstatistikk( typedefinisjon, testrun=testrun)
        
        statistikk[ typedefinisjon['id'] ] = delstatistikk 
    
    # historikk/2018-12-01.json
    fname = directory + 'historikk/' + datetime.datetime.today().strftime('%Y-%m-%d') + '.json'
    with open( fname, 'w') as f: 
        json.dump(statistikk, f, ensure_ascii=True)


# In[4]:


hentvegobjekter(testrun=False)

