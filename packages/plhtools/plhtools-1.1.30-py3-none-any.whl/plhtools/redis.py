#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''                                                                                                             
Author: penglinhan                                        
Email: 2453995079@qq.com                                
File: redis.py
Date: 2023/9/15 2:37 下午
'''
import redis
from plhtools.configuration import  configuration


class redis_class():
    def __init__(self, label=None, host=None, port=None, user=None, password=None, db=None):
        if label:
            config = configuration()
            self._host = config.get_label_value(label, 'host')
            self._port = int(config.get_label_value(label, 'port'))
            try:
                self._user = config.get_label_value(label, 'user')
                self._password = config.get_label_value(label, 'pass')
            except Exception as e:
                self._user =None
                self._password= None
            self._db_name = db if db else config.get_label_value(label, 'db')
        else:
            self._host = host
            self._port = port
            self._user = user
            self._password = password
            self._db_name = db
        self.__connect()

    def __connect(self):
        if self._password:
            self.__redis_pool = redis.ConnectionPool(host=self._host, port=self._port, db=self._db_name,password=self._password)
        else:
            self.__redis_pool = redis.ConnectionPool(host=self._host, port=self._port, db=self._db_name)

    def get_con(self):
        return redis.Redis(connection_pool=self.__redis_pool)

    def set(self,key,value):
        for i in range(3):
            try:
                con = self.get_con()
                con.set(str(key), str(value))
                return True
            except Exception as e:
                print(e)
        return False

    def get(self,key):
        for i in range(3):
            try:
                con = self.get_con()
                r = con.get(str(key)).decode()
                return r
            except Exception as e:
                print(e)
        return False