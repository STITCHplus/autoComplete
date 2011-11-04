#!/usr/bin/env python

##
## autocomplete.py - autocomplete
##
## copyright (c) 2011-2012 Koninklijke Bibliotheek - National library of the Netherlands.
##
## this program is free software: you can redistribute it and/or modify
## it under the terms of the gnu general public license as published by
## the free software foundation, either version 3 of the license, or
## (at your option) any later version.
##
## this program is distributed in the hope that it will be useful,
## but without any warranty; without even the implied warranty of
## merchantability or fitness for a particular purpose. see the
## gnu general public license for more details.
##
## you should have received a copy of the gnu general public license
## along with this program. if not, see <http://www.gnu.org/licenses/>.
##


import logging, ast, json
from pprint import pprint
from operator import itemgetter
import urllib
import cgi

__author__ = "Willem Jan Faber"

def term_suggestion(query):

    remove=("'","!",":",'"',",","`",".",")", "1", "2", "3", "]", ";")

    list=[]
    data=ast.literal_eval(urllib.urlopen('http://127.0.0.1:8080/solr/ggc/terms?terms.fl=fullrecord&terms.prefix='+urllib.quote(query.lower())+'&indent=true&wt=json&omitHeader=true&terms.limit=12').read())
    i=0
    ok={}
    #pprint(data)
    for item in data["terms"]["fullrecord"]:
        if not type(item) == int:
            nitem=item.split("(")[0]
            for i in range(0,10):
                for short in remove:
                    if nitem.endswith(short):
                        nitem=nitem[0:-1]
            if nitem not in ok.keys():
                ok[nitem] = True
                list.append(nitem) 
    return(list)

def creator_suggestion(query):
    creator_suggestions=[]
    nquery=False

    if len(query) > 1:
        if (query[0].isalpha()) and (query[0].islower()):
            nquery=query[0].upper()+query[1:]
    if nquery:
        query=nquery

    data=ast.literal_eval(urllib.urlopen('http://127.0.0.1:8080/solr/ggc/terms?terms.fl=creator_str&terms.prefix='+urllib.quote(query)+'&indent=true&wt=json&omitHeader=true&terms.limit=6&terms.sort=count').read())

    for item in data["terms"]["creator_str"]:
        if not type(item) == int:
            creator_suggestions.append(item.strip())

    if len(creator_suggestions) > 1:
        return(creator_suggestions)

    if len(query.split(" ")) == 2:
        if (query.split(" ")[1][0].isalpha()) and (query.split(" ")[1][0].islower()):
            query=query.split(" ")[0]+", "+query.split(" ")[1][0].upper()+query.split(" ")[1][1:]
    data=ast.literal_eval(urllib.urlopen('http://127.0.0.1:8080/solr/ggc/terms?terms.fl=creator_str&terms.prefix='+urllib.quote(query)+'&indent=true&wt=json&omitHeader=true&terms.limit=6&terms.sort=count').read())
    for item in data["terms"]["creator_str"]:
        if not type(item) == int:
            creator_suggestions.append(item.strip())

    return(creator_suggestions)


def title_suggestion(query):
    list=[]
    url=('http://127.0.0.1:8080/solr/ggc/select/?q=title:'+urllib.quote(query)+'&fl=title&rows=6&wt=json&omitHeader=true')
    data=ast.literal_eval(urllib.urlopen(url).read())
    title_list={}
    i=0
    if "response" in data.keys():
        for j in (data["response"]["docs"]):
            if j["title"][0].replace('"', '\"').strip() not in list:
                list.append(j["title"][0].replace('"', '\"').strip())
    #print(len(list))
    if len(list) < 5:
        if not query.find(" ")> -1:
            url=('http://127.0.0.1:8080/solr/ggc/select/?q=title:'+urllib.quote(query)+'*&fl=title&rows=6&wt=json&omitHeader=true')
            data=ast.literal_eval(urllib.urlopen(url).read())
            if "response" in data.keys():
                for j in (data["response"]["docs"]):
                    if j["title"][0].replace('"', '\"').strip() not in list:
                        list.append(j["title"][0].replace('"', '\"').strip())
    return(list)

def main():
    form = cgi.FieldStorage()
    query = form.getvalue("query")
    q = form.getvalue("q")
    list=[]

    creatorOnly=False
    titleOnly=False
    ismore=False


    print "Content-Type: text/html\n"

    if not query == None:
        if len(query) > 1:
            if (query.startswith("creator:")):
                creatorOnly=True
                query=query[len("creator:"):]
            else:
                if (query.startswith("title")):
                    titleOnly=True
                    query=query[len("title:"):]

            if not creatorOnly or titleOnly:
                list=json.dumps({ "terms" : term_suggestion(query), "persons" : creator_suggestion(query), "works" : title_suggestion(query) }, sort_keys=True, indent=4)
            print(list)
            return()

    if not q == None:
        if len(q) > 2:
            for item in term_suggestion(q.lower())+creator_suggestion(q.lower())+title_suggestion(q.lower()):
                item=item.lower() 
                if not item == q.lower():
                    list.append(item)
            list= [ q,  list ]
            list=json.dumps(list)
    print(list)
    return()


if __name__ == "__main__":
    main()
