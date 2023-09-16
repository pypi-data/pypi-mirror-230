#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''                                                                                                             
Author: penglinhan                                        
Email: 2453995079@qq.com                                
File: es.py
Date: 2022/8/3 4:22 下午
'''
from elasticsearch_dsl import connections,Search
from plhtools.configuration import  configuration
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from elasticsearch_dsl.query import MultiMatch, Match


def get_es_config(label='', host='', user='', password='',timeout=10):
    if label:
        con_obj = configuration()
        host = con_obj.get_label_value(label, 'host')
        user = con_obj.get_label_value(label, 'user')
        password = con_obj.get_label_value(label, 'pass')
    else:
        host = host
        user = user
        password = password
        label = 'default'
    if user and password:
        return connections.create_connection(alias=label, hosts=[host], http_auth=(user, password), timeout=timeout)
    return connections.create_connection(alias=label, hosts=[host], timeout=timeout)

def get_es_client(label='', host='', user='', password='',timeout=10):
    if label:
        con_obj = configuration()
        host = con_obj.get_label_value(label, 'host')
        user = con_obj.get_label_value(label, 'user')
        password = con_obj.get_label_value(label, 'pass')
    else:
        host = host
        user = user
        password = password
        label = 'default'
    if user and password:
        return Elasticsearch([host],http_auth=(user, password), timeout=timeout)
    return Elasticsearch([host])

class EsOp():
    def __init__(self, label='', host='', user='', password='', size=2000,timeout=10):
        self.conn = get_es_config(label=label, host=host, user=user, password=password,timeout=timeout)
        self.client =get_es_client(label=label, host=host, user=user, password=password,timeout=timeout)
        self.size = size
    def get_es_state(self):
        print(self.conn.cluster.state())
        print(self.conn.cluster.health())

    def get_es_info(self):
        return self.conn.info()

    def is_exists_index(self,index_name):
        if self.conn.indices.exists(index=index_name):return True
        else:return False

    def create_table(self,index_name,mapping):
        if self.conn.indices.exists(index=index_name) is not True:
            result = self.conn.indices.create(index=index_name,body={'mappings': mapping})
            print(result)
            if 'acknowledged' in result.keys() and result['acknowledged']:
                return '创建index成功'
            else:
                return '创建失败'
        else:
            return 'index已存在'
    def delete_index(self,index_name):
        if self.conn.indices.exists(index=index_name) :
            result = self.conn.indices.delete(index_name, ignore=[400, 404])
            if 'acknowledged' in result.keys() and result['acknowledged']:
                return '成功删除index'
            else:
                return '删除失败'
        else:
            return '没有对应的index'

    def bulk_to_es(self,index_name,bulk_list,**kwargs):
        _length = len(bulk_list)
        if _length > 100:
            for i in range(0, _length, 100):
                for i in range(3):
                    try:
                        bulk(self.conn, bulk_list[i: i + 100], index=index_name, **kwargs)
                        break
                    except Exception as e:
                        continue

        else:
            bulk(self.conn, bulk_list, index=index_name, **kwargs)

    def delete_by_id(self, index_name,id, **kwargs):
        self.conn.delete(index=index_name, id=id, ignore=[400, 404], **kwargs)

    def delete_by_query(self,index_name,query_dict,doc_type=''):
        body = {
            "query": {
                "match": query_dict
            },
        }
        self.conn.delete_by_query(index=index_name,doc_type=doc_type,body=body)

    def index_result_dict(self,result):
        if result:
            items = result['hits']['hits']
            result_list= []
            for i in items:
                temp_dict = i['_source']
                temp_dict['_id'] = i['_id']
                temp_dict['_score'] = i['_score']
                result_list.append(temp_dict)
            return result_list
        else:
            return '未查到'

    def index_search(self,index_name,body,size=1000,request_timeout=10):
        result =  self.conn.search(index=index_name,size=size,body=body,request_timeout=request_timeout)
        return self.index_result_dict(result)
    def index_search_all(self,index_name,pn=1,size=10000,doc_type='',request_timeout=10):
        body = {
            "query": {
                "match_all": {}
            },
            "from": (pn - 1) * size,
            "size": size,
        }
        result = self.conn.search(index=index_name,doc_type=doc_type, body=body,request_timeout=request_timeout)
        return self.index_result_dict(result)
    def index_search_absolute_match(self,index_name,query_dict,pn=1,size=10,doc_type='',request_timeout=10):
        new_dict= {}
        for i in query_dict.keys():
            if i == '_id':
                new_dict[i] = query_dict[i]
            else:
                new_dict[i+'.keyword'] =query_dict[i]
        iterator = Search(using=self.client, doc_type=doc_type, index=index_name).params(request_timeout=request_timeout).query("term", **new_dict)[(pn - 1) * size:pn*size]
        iterator = iterator.execute().to_dict()
        return self.index_result_dict(iterator)

    def index_search_fuzzy_match(self,index_name,query_dict,pn=1,size=10,doc_type='',request_timeout=10):
        iterator = Search(using=self.client, doc_type=doc_type,index=index_name).params(request_timeout=request_timeout).query("match", **query_dict)[(pn - 1) * size:pn*size]
        iterator = iterator.execute().to_dict()
        return self.index_result_dict(iterator)

    def index_MultiMatch(self,index_name,query_text,query_field_list,doc_type='',request_timeout=10):
        multi_match = MultiMatch(query=query_text, fields=query_field_list)
        iterator= Search(using=self.client,doc_type=doc_type,index=index_name).params(request_timeout=request_timeout).query(multi_match)
        result = []
        for i in iterator:
            result.append(i.to_dict())
        return result


if __name__ == '__main__':
    es = EsOp(host='http://192.168.6.157:9201')

    # s = es.create_table('standard_platform')
    # print(s)
    # s = es.delete_index('standard_platform')
    # print(s)
    # from  encryption_and_decryption import EncDec
    # rows = [{
    #     "_id": EncDec.uuid_encode('醉了1'),
    #     "question": '醉了1',
    #     "answer": '惆怅2'
    # }]
    # es.bulk_to_es('standard_platform',rows)
    #全量
    # s = es.index_search_all('standard_search')
    # print(s)
    s= es.index_search_absolute_match(index_name='water_graph',query_dict={'name':'黄河'})
    print(s)
    s = es.index_search_fuzzy_match('water_graph',{'name': '黄河'},pn=1,size=10,request_timeout=3)
    print(s)
    # s = es.index_MultiMatch('standard_platform','1',['question','answer'])
    # print(s)
    # s= es.index_search_one_fuzzy_match('standard_platform',{'question': '醉了'})
    # print(s)
    # s= es.delete_by_query('standard_platform',{'question':"醉了"})