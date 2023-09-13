import pandas as pd
import numpy as np
import re
import Levenshtein as lev

#Functions to comapre numerical attributes
def num_sim(n1, n2):
    return 1 - abs(n1 - n2) / (n1 + n2)

def numerical_comparison(df,col_x,col_y,scores=False):
    try:
        df[col_x] = df[col_x].astype('float64')
        df[col_y] = df[col_y].astype('float64')
    except Exception as e:
        print('Error occured while converting columns to numeric format, returning zero similarities')
        print(e)
        return np.zeros(df.shape[0])
    df['similarity'] = num_sim(df[col_x], df[col_y])
    if not scores:
        
        return np.where(df['similarity']>=0.99,'true',
                              (np.where(df['similarity'].isna(),'missing','false')))
    else:
        return df['similarity'].fillna(0)

#Functions to compare text attributes

def isintersection(list1, list2):
    a =list(set(list1))
    b =list(set(list2))
    i=0
    for x in a:
        if x in b:
            i=i+1

    return i==len(a)

def check_intersection(df,col_x,col_y):
    df = df[[col_x ,col_y ]].drop_duplicates()
    df['new'] = np.where((df.apply(lambda x: isintersection(x[col_x].split(','), x[col_y].split(',')),axis=1))|
           (df.apply(lambda x: isintersection(x[col_y].split(','), x[col_x].split(',')),axis=1)),df[col_x],df[col_y])
    return df[[col_x,col_y,'new']]


def check_substring(df,col_x,col_y):
    df = df[[col_x ,col_y ]].drop_duplicates()
    df['new'] = np.where((df.apply(lambda x: re.sub(r'[^a-zA-Z0-9]','',x[col_y]) in re.sub(r'[^a-zA-Z0-9]','',x[col_x]), axis=1))|(df.apply(lambda x: re.sub(r'[^a-zA-Z0-9]','',x[col_x]) in re.sub(r'[^a-zA-Z0-9]','',x[col_y]), axis=1)),
                                   df[col_x],df[col_y])
    df['new'] = np.where((df.apply(lambda x: x['new'] in x[col_x], axis=1))|(df.apply(lambda x: x[col_x] in x['new'], axis=1)),
                                   df[col_x],df['new'])
    return df[[col_x,col_y,'new']]

def lev_sim(seq1,seq2):
    try:
        return 1-lev.distance(seq1,seq2)/max(len(seq1),len(seq2))
    except:
        return

def common_characters(row,A,B):
    try:
        set_A = set(row[A])
        set_B = set(row[B])
        return len(''.join(sorted(set_A.intersection(set_B))))/max(len(set_A),len(set_B))
    except:
        return 0

def text_comparison(df,col_x,col_y,inter=True,subst=True,thresh1=0.7,thresh2=0.7,scores=False):
    try:
        df[col_x]=df[col_x].str.lower()
        df[col_y]=df[col_y].str.lower()
    except Exception as e:
        print('Error occured while converting columns to lower case format, returning zero similarities')
        print(e)
        return np.zeros(df.shape[0])
    
    
    df[col_x] = df[col_x].str.replace('color','',regex=True).str.replace('finish','',regex=True)
    df[col_x]= np.where((df[col_x]=='nan')|
                      (df[col_x].isna())|
                      (df[col_x]=='')|
                      (df[col_x]==' ')|
                      (df[col_x]=='na'),'nannan',df[col_x])
    df[col_x] = df[col_x].str.strip()
    
    df[col_y] = df[col_y].str.replace('color','',regex=True).str.replace('finish','',regex=True)
    df[col_y]= np.where((df[col_y]=='nan')|
                      (df[col_y].isna())|
                      (df[col_y]=='')|
                      (df[col_y]==' ')|
                     (df[col_y]=='na'),'nannan',df[col_y])
    df[col_y] = df[col_y].str.strip()
    
    if inter:
        temp = check_intersection(df,col_x,col_y)
        a=temp.columns[0]
        b= temp.columns[1]
        c=temp.columns[2]
        #print(a,b)
        df=df.merge(temp, on = [a,
                                b])
        df=df.drop([b],axis=1)
        df.rename(columns={c:b},inplace=True)
        del temp
    if subst:
        temp = check_substring(df,col_x,col_y)
        a=temp.columns[0]
        b= temp.columns[1]
        c=temp.columns[2]
        #print(a,b)
        df=df.merge(temp,
                           on = [a,
                                b])
        df=df.drop([b],axis=1)
        df.rename(columns={c:b},inplace=True)
        del temp

    df[col_x] = np.where(df[col_x]=='nannan',None, df[col_x])
    df[col_y] = np.where(df[col_y]=='nannan',None, df[col_y])

    temp = df[[col_x ,col_y]].drop_duplicates().copy()
    temp['similarity']=temp.apply(lambda x:lev_sim(x[col_x],x[col_y]),
                                              axis=1)
    temp['common_len']=temp.apply(lambda x: common_characters(x,col_x,col_y), axis=1)

    a=col_x
    b= col_y
    
    df=df.merge(temp,on = [a,b])
    df.sort_index(inplace=True)

    df['similarity_state'] = np.where(
                        (((df['similarity']>=thresh1)&
                          (df['common_len']>=thresh2))|
                          ((df['similarity']>=(thresh1-0.1))&
                           (df['common_len']>=(thresh2+0.1)))
                        )&
                            (~df[a].isna())&
                            (~df[b].isna())&
                            (df[a]!='nannan')&
                            (df[b]!='nannan'),'true',
                             np.where((df[a]!='nannan')&
                                      (df[a]!=' ')&
                                      (df[a]!='')&
                                      (~df[a].isna())&
                                      (~df[b].isna())&
                                      (df[b]!=' ')&
                                      (df[b]!='')&
                                      (df[b]!='nannan')&
                                      (df['common_len']>(0.1)),'false'
                                             ,'missing')
                                    )
    if not scores:
        return df.drop(['similarity','common_len'],axis=1)
    
    else:
        return df.drop(['similarity_state','common_len'],axis=1)