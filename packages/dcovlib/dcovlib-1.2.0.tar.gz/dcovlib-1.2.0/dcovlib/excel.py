# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 20:24:35 2023

@author: Sun Ling
"""
import pandas as pd
import os
class saveexcel:
    def __init__(self,filePath,model='a'):    
        if not os.path.exists(os.path.dirname(filePath)):
            os.makedirs(os.path.dirname(filePath))
        readers=[]
        if model=='a' and os.path.exists(filePath) and os.path.getsize(filePath)>1024:
            efile = pd.ExcelFile(filePath)
            sheet_names = efile.sheet_names
            readers = [(a, pd.read_excel(filePath, sheet_name=a,index_col=False)) for a in sheet_names]
            
        self._sheets=[]
        writer=pd.ExcelWriter(filePath,engine='openpyxl')
        self._readers = readers
        self._writer = writer
    def writer(self,data,sheet):
        padata=pd.DataFrame(data)
        padata.to_excel(self._writer,sheet_name=sheet)
        self._sheets.append(sheet)
    def __del__(self):
        
        if len(self._readers)>0:
            for sheet,reader in self._readers:
                if sheet not in self._sheets:
                    reader.to_excel(self._writer,sheet_name=sheet,index=False)
                else:
                    print(f"sheets {sheet} is already exists")
        self._writer.save()    
        self._writer.close()