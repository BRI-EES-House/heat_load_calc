def convert_wall(d1):
    if int(d1['type'])==1:
        d_insulation=round(max(0,(1/float(d1['Ua'])-(0.090+0.0095/0.22+0.090))*0.05),3)
        Layers= {'Layer1':{'material':'GW10K','d':d_insulation,'λ':0.05,'Cρ':8}, 
                 'Layer2':{'material':'GPB','d':0.0095,'λ':0.22,'Cρ':830}, 
                 'Layer3':{'material':None,'d':None,'λ':None,'Cρ':None}, 
                 'Layer4':{'material':None,'d':None,'λ':None,'Cρ':None}}    
    elif int(d1['type'])==2:
        d_insulation=round(max(0,(1/float(d1['Ua'])-(0.11+0.012/0.16+0.09+0.0095/0.22+0.11))*0.045),3)
        Layers= {'Layer1':{'material':'PED','d':0.012,'λ':0.16,'Cρ':720}, 
                 'Layer2':{'material':'GW16K','d':d_insulation,'λ':0.045,'Cρ':13},
                 'Layer3':{'material':'Air','d':1,'λ':round(1/0.090,2),'Cρ':0},
                 'Layer4':{'material':'GPB','d':0.0095,'λ':0.22,'Cρ':830}}
    elif int(d1['type'])==3:
        d_insulation=round(max(0,(1/float(d1['Ua'])-(0.15+0.012/0.16+0.15))*0.045),3)
        Layers= {'Layer1':{'material':'PED','d':0.012,'λ':0.16,'Cρ':720}, 
                 'Layer2':{'material':'GW16K','d':d_insulation,'λ':0.045,'Cρ':13}, 
                 'Layer3':{'material':None,'d':None,'λ':None,'Cρ':None}, 
                 'Layer4':{'material':None,'d':None,'λ':None,'Cρ':None}} 
        
    return {'name': d1['name'],
            'type': d1['type'],
            'Ua': d1['Ua'],
            'Layers':Layers}