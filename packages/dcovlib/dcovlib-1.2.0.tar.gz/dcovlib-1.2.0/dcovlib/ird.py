# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 14:48:30 2022

@author: Sun Ling
"""
import numpy as np
class ird(object):
    def __init__(self):
        self._shape=None
        self._datatype=b'1' # irint32=1; irint64=2; float32=3; float64=4
        self._data=None
        
    def reset(self):
        #重置
        self._shape=None
        self._datatype=b'1' # irint32=1; irint64=2; float32=3; float64=4
        self._data=None
        
    def setdata(self,data):
        
        self._data=np.array(data)
        datashape=list(self._data.shape)+[0,0,0,0]
        self._shape=np.array(datashape)[:4]
        if self._data.dtype == np.int32:
            self._datatype = b'1'
        elif self._data.dtype == np.int64:
            self._datatype = b'2'
        elif self._data.dtype == np.float32:
            self._datatype = b'3'
        elif self._data.dtype == np.float64:
            self._datatype = b'4'
        else:
            raise Exception("Error data type") 
        
    def encode(self):
        #将数组及shape等编码成ird文件
        if self._data is None:
            raise Exception("Data is None error") 
        shapebyte   = bytearray(self._shape)
        bytedata    = bytearray(self._data)
        return b'ird' + shapebyte + self._datatype + bytedata
    
    def savefile(self,path):
        #手动保存文件
        if self._data is None:
            print("You should set data first") 
            return ''
        fi=open(path,'wb')
        fi.write(self.encode())
        fi.close()
  
    def savedata(self,data,path):
        #将np.array保存成ird文件
        self.setdata(data)
        self.savefile(path)
        
    def _decodeshape(self):
        shape=[a for a in self._shape if a !=0]
        return shape
    

    
    def decode(self, data):
        #解码文件
        if type(data) is not bytes:
            raise Exception("Input data should be bytes") 
        if data[:3] != b'ird':
            raise Exception("This file may not ird files") 
        self._shape = np.frombuffer(data[3:19],dtype=np.int32)
        dtypecode = data[19:20]
        if dtypecode == b'1': 
            dtype = np.int32   
        elif dtypecode == b'2': 
            dtype = np.int64
        elif dtypecode == b'3': 
            dtype = np.float32   
        elif dtypecode == b'4': 
            dtype = np.float64
        else:
            raise Exception("Error data type") 
                
        arrdata = np.frombuffer(data[20:],dtype=dtype)
        ret=None
        try:
            ret = arrdata.reshape(self._decodeshape())
        except Exception as e:
            print(e.args)
        return ret
    
    def readfile(self,path):
        #读取文件
        fi=open(path,'rb')
        return self.decode(fi.read())      
    
