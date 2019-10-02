import os
import numpy as np
from datetime import datetime
from functools import partial
from wordcloud import WordCloud
from PIL import Image, ImageFont, ImageDraw

def splitting(liste,split_elem):
    new_liste=[]
    for elem in liste:
        liste_split=elem.split(split_elem)
        new_liste+=liste_split
    return new_liste

def multi_splitting(text,split_elems):
    text=text.replace('\\n',' ')
    text=text.replace('\n',' ')
    liste=text.split(' ')
    for split_elem in split_elems:
        liste=splitting(liste,split_elem)
    return liste

def importation_year(path,year):
    remote_file=open(path+str(year)+'.txt','r',encoding='utf8')
    text=remote_file.read()
    remote_file.close()
    split_chars=['.',':',',',';',"'",'"','(',')','[',']','{','}','-','_']
    text=multi_splitting(text,split_chars)
    words={}
    for mot in text:
        x=''
        for char in mot:
            if char.isalpha():
                x+=char
        if len(x)>1:
            try:
                words[x]+=1
            except:
                words[x]=1
    return words

def importation(path,y_min,y_max):
    dico={}
    for year in range(y_min,y_max):
        x=importation_year(path,year)
        for word in x.keys():
            try:
                dico[word][year]=x[word]
            except:
                dico[word]={}
                dico[word][year]=x[word]
    return dico

def extract_year(frequencies):
    year=0
    maximum=0.0
    for y in frequencies.keys():
        if frequencies[y]>maximum:
            year=y
            maximum=frequencies[y]
    return year

def extract_frequency(frequencies):
    frequency=0
    for y in frequencies.keys():
        frequency+=frequencies[y]
    return frequency

def extract_resilience(frequencies):
    resilience=0
    resilience_max=0
    y_old=0
    for y in frequencies.keys():
        if y==y_old+1:
            resilience+=1
            resilience_max=max(resilience_max,resilience)
        else:
            resilience=1
            resilience_max=max(resilience_max,resilience)
        y_old=y
    return resilience_max

def generate_date_circle(matrix,dates,angles,pos_dep):
    res=matrix
    n=len(matrix)
    the_font_size=int(0.02*n)
    the_font=ImageFont.truetype('NotoSans-Regular.ttf',the_font_size)
    for i in range(len(dates)):
        the_text=dates[i]
        image=Image.new('RGB',(n,n),(0,0,0))
        draw=ImageDraw.Draw(image)
        w,h=draw.textsize(the_text,the_font)
        pos_x=int(0.5*n-0.5*w)
        pos_y=int((1.0-pos_dep)*0.5*n-0.5*h)
        draw.text((pos_x,pos_y),the_text,(255,255,255),the_font)
        rotation=image.rotate(angles[i])
        arr=np.asarray(rotation)
        res+=arr
        res[res>255]=255
    return res

def color_func(max_freq_col,words_carac,word,font_size,position,orientation,random_state=None,**kwargs):
    the_freq=min(words_carac[word][1],max_freq_col)
    the_value=int(250.0-(250.0*the_freq/max_freq_col))
    the_col='hsl('+str(the_value)+', 100%, 20%)'
    return the_col

def write_section(var_section,words_carac,name):
    fichier_section=open(name,'w',encoding='utf8')
    for line in var_section:
        mot=line[0][0]
        pos_x=str(line[2][0])
        pos_y=str(line[2][1])
        taille=str(line[1])
        ori_string=str(line[3])
        if ori_string=='None':
            ori='1'
        else:
            ori='2'
        frequency=str(line[0][1])
        resilience=str(words_carac[mot][2])
        year=str(words_carac[mot][0])
        fichier_section.write(mot+'\t'+pos_x+'\t'+pos_y+'\t'+taille+'\t'+ori+'\t'+frequency+'\t'+resilience+'\t'+year+'\n')
    fichier_section.close()   

def make_chronocloud(words_carac,n,resiliences,periods,name):
    debut=datetime.now()
    data=np.zeros((n,n,3),dtype=np.uint8)
    dates=[]
    dates.append(str(periods[-1])+' | '+str(periods[0]))
    for i in range(1,len(periods)-1):
        dates.append(str(periods[i]))
    angles=[0,315.0,270.0,225.0,180.0,135.0,90.0,45.0]
    data=generate_date_circle(data,dates,angles,0.95)
    data=255-data
    the_font='NotoSans-Regular.ttf'
    param_max_font_size=0.03*n
    param_relative_scaling=0.3
    resilience=resiliences[0]
    r_1=0.45*(n/5)
    a,b=n/2,n/2
    y,x=np.ogrid[0:n,0:n]
    condition=(x-a)*(x-a)+(y-b)*(y-b)>r_1*r_1
    the_mask=np.zeros((n, n),dtype=np.int)
    the_mask[condition]=[255]*len(the_mask[condition])
    the_frequencies={}
    for word in words_carac.keys():
        if words_carac[word][2]>=resilience:
            the_frequencies[word]=words_carac[word][1]
    var_1=[]
    var_2=[]
    if len(the_frequencies)>0:
        wc=WordCloud(font_path=the_font,background_color='white',max_words=50000,mask=the_mask,stopwords=[],prefer_horizontal=0.5,width=the_mask.shape[0],height=the_mask.shape[1],relative_scaling=param_relative_scaling,max_font_size=param_max_font_size)
        wc.generate_from_frequencies(the_frequencies)
        var_1+=wc.words_
        var_2+=wc.layout_
    os.makedirs(name+'_sections',exist_ok=True)
    write_section(var_2,words_carac,name+'_sections/'+name+'_'+str(resilience)+'.txt')
    fin=datetime.now()
    print('resilience '+str(resilience)+' => done / '+str(fin-debut))
    c_1=[0*y>(x-a),(y-b)>-(x-a)]
    c_2=[(y-b)<-(x-a),(y-b)>x*0]
    c_3=[(y-b)<x*0,(y-b)>(x-a)]
    c_4=[(y-b)<(x-a),(x-a)<y*0]
    c_5=[(x-a)>y*0,(y-b)<-(x-a)]
    c_6=[(y-b)>-(x-a),(y-b)<x*0]
    c_7=[(y-b)>x*0,(y-b)<(x-a)]
    c_8=[(y-b)>(x-a),0*y<(x-a)]
    arretes=[c_1,c_2,c_3,c_4,c_5,c_6,c_7,c_8]
    for res_ind in range(4):
        resilience_sup=resiliences[res_ind]
        resilience_inf=resiliences[res_ind+1]
        debut=datetime.now()
        for indice in range(len(periods[:-1])):
            years_inf=periods[indice]
            years_sup=periods[indice+1]
            r_1=0.45*(res_ind+2)*(n/5)
            r_2=0.45*(res_ind+1)*(n/5)
            condition_1=(x-a)*(x-a)+(y-b)*(y-b)>r_1*r_1
            condition_2=(x-a)*(x-a)+(y-b)*(y-b)<r_2*r_2
            the_mask=np.zeros((n,n),dtype=np.int)
            the_mask[condition_1]=[255]*len(the_mask[condition_1])
            the_mask[condition_2]=[255]*len(the_mask[condition_2])
            the_mask[arretes[indice][0]]=list([255]*len(the_mask[arretes[indice][0]]))
            the_mask[arretes[indice][1]]=list([255]*len(the_mask[arretes[indice][1]]))
            the_frequencies={}
            for word in words_carac:
                res_bol=words_carac[word][2]>=resilience_inf and words_carac[word][2]<resilience_sup
                year_bol=words_carac[word][0]>=years_inf and words_carac[word][0]<years_sup
                if res_bol and year_bol:
                    the_frequencies[word]=words_carac[word][1]
            if len(the_frequencies)>0:
                wc=WordCloud(font_path=the_font,background_color='white',max_words=50000,mask=the_mask,stopwords=[],prefer_horizontal=0.5,width=the_mask.shape[0],height=the_mask.shape[1],max_font_size=param_max_font_size)
                wc.generate_from_frequencies(the_frequencies)
                var_1+=wc.words_
                var_2+=wc.layout_
                write_section(wc.layout_,words_carac,name+'_sections/'+name+'_'+str(resilience_inf)+'_'+str(years_inf)+'.txt')
        wc_montre=WordCloud(font_path=the_font,background_color='white',width=n,height=n)
        wc_montre.words_=var_1
        wc_montre.layout_=var_2
        color_func_apply=partial(color_func,2000,words_carac)
        wc_montre.recolor(color_func=color_func_apply)
        data_1=255-data
        data_2=255-wc_montre.to_array()
        data_3=data_1+data_2
        data_3[data_3>255]=255
        data_3=255-data_3
        fin=datetime.now()
        print('resilience '+str(resilience_inf)+' => done / '+str(fin-debut))
    Image.fromarray(data_3,'RGB').save(name+'.png')

def chronocloud(resolution,resiliences,periods,data_folder):
    debut=datetime.now()
    path=data_folder+'/'
    words_frequencies=importation(path,periods[0],periods[-1])
    words_carac={}
    for word in words_frequencies:
        year=extract_year(words_frequencies[word])
        frequency=extract_frequency(words_frequencies[word])
        resilience=extract_resilience(words_frequencies[word])
        words_carac[word]=[year,frequency,resilience]
    resiliences.sort(reverse=True)
    make_chronocloud(words_carac,resolution,resiliences,periods,'chronocloud_'+data_folder+'_'+str(resolution))
    fin=datetime.now()
    print('chronocloud => done / '+str(fin-debut))     

#data_folder='legislation'
#periods=[1900,1910,1920,1930,1940,1950,1960,1970,1980]
data_folder='exports_min'
periods=[1980,1985,1990,1995,2000,2005,2010,2015,2020]
resiliences=[0,5,10,15,20]
resolution=5000
chronocloud(resolution,resiliences,periods,data_folder)
