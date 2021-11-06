#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 10:35:02 2021

@author: Andor Horvath
@license: GPLv2
"""

import pymysql
import re

class Repertoire_MySQL:
    """Represents a poetical repertory provided by a MySQL server."""

    def __init__(self, repid, dbhost, dbuser, dbpassword, dbname, description, curs):
        self.repid = repid
        self.description = description
        self.db = pymysql.connect(
            host=dbhost, user=dbuser, password=dbpassword, database=dbname)
        self.cur = self.db.cursor()
        self.tolerance = {' ': '', ',': ''}
        curs.execute(
            "SELECT parameter, code_search, code_show\
                FROM connector WHERE id_repertoire = "
            + str(self.repid) + ";")
        self.connector = {}
        for a in curs.fetchall():
            self.connector[a[0]] = a[1:5]
        self.main = self.search('mainlist')

    def close(self):
        """Close the database."""
        self.db.close()

    def replaceListSQL(self, column, dic):
        """Compose a REPLACE instruction based on the list of characters to be disregarded during search."""
        result = column
        for a, b in dic.items():
            result = "REPLACE(" + result + ", '" + a + "', '" + b + "')"
        return result

    def replaceList(self, text, dic):
        """Do replace operations on a text based on a dictionary."""
        for a, b in dic.items():
            text = text.replace(a, b)
        return text

    def executeQuery(self, query):
        """Execute the composed query on the database."""
        result = []
        # print(query)
        self.cur.execute(query)
        for a in self.cur.fetchall():
            result.append(a[0])
        return result

    def searchQuery(self, parameter, value, method):
        """Compose the search query."""
        column = 0
        if(value == ''):
            method = '='
        if(method == 'LIKE'):
            query = self.connector[parameter][column].replace('[[METHOD]]',
                                                              method).replace(
                ("[[VALUE]]"),
                ("'%" + self.replaceList(value, self.tolerance)) + "%'")
        else:
            query = self.connector[parameter][column].replace(
                '[[METHOD]]', method).replace(("[[VALUE]]"),
                                              ("'" + value + "'"))
        query1 = ""
        while query1 != query:
            query1 = query
            if(method == 'LIKE'):
                query = re.sub(r'(.*)\[\[(.*?)\]\](.*)', r'\1' +
                           self.replaceListSQL(r'\2', self.tolerance) +
                           r'\3', query)
            else:
                query = re.sub(r'(.*)\[\[(.*?)\]\](.*)', r'\1' + r'\2' + r'\3', query)
        # print(query)
        return query

    def search(self, parameter, value=[''], method='LIKE'):
        """Search a parameter for certain value(s) on the database."""
        result = []
        if(type(value) is not list):
            value = [value]
        for v in value:
            if(type(v) is list and len(v) == 2):
                if(v[0] == self.repid):
                    v = v[1]
            v = str(v)
            result = result + self.executeQuery(
                self.searchQuery(parameter, v, method))
        result = list(dict.fromkeys(result))
        # result = mark(self.repid, result)
        return result

    def show(self, parameter, idy):
        """Return a list of results."""
        result = []
        idy = retrieve(self.repid, idy)
        if(len(idy) > 0):
            column = 1
            for i in idy:
                # print(i)
                # res = mark(self.repid, [i])
                res = [i]
                for p in parameter:
                    r = self.executeQuery(
                        self.connector[p][column].replace(
                            '[[ID]]', "'" + str(i).strip("[]") + "'"))
                    res.append(' '.join(r))
                result.append(res)
            # for a in range(len(result[0])):
            #     c = []
            #     for b in range(len(parameter)):
            #         c.append(result[b][a])
            #     res.append(c)
        # result = mark(self.repid, result)
        return result


class MegaRep:
    """Represents a collection of poetical databases."""
    
    def __init__(self, dbhost, dbuser, dbpassword, dbname, selected=[0]):
        """Connect to the megarepdb database."""
        megarepdb = pymysql.connect(host=dbhost, user=dbuser,
                              password=dbpassword, database=dbname)
        cursor_megarepdb = megarepdb.cursor()
        cursor_megarepdb.execute(
            "SELECT id_repertoire, id_dbtype, host, username, password, dbname, description FROM repertoire;")
        self.rep = []
        for a in cursor_megarepdb.fetchall():
            if(selected == [0] or a[0] in selected):
                print("Loading database: " + a[6])
                if(a[1] == 1):
                    self.rep.append(Repertoire_MySQL(
                        a[0], a[2], a[3], a[4], a[5], a[6], cursor_megarepdb))
        megarepdb.close()
        self.main = self.search('mainlist')

    def search(self, parameter, value=[''], method='LIKE'):
        """Search all the databases."""
        res = []
        for a in self.rep:
            res = res + a.search(parameter, value, method)
        return res

    def show(self, parameter, idy):
        """Show a parameter of the results."""
        res = []
        for a in self.rep:
            res = res + a.show(parameter, idy)
        return res

    def msearch(self, parameter, value, method='LIKE'):
        """Search and return main variants belonging to the results."""
        a = self.search(parameter, value, method)
        a = self.search('mainvariant', a, '=')
        return a

    def searchm(self, parameter, value, method='LIKE'):
        """Search only the main variants."""
        a = self.search(parameter, value, method)
        return repAnd(a, self.main)

    def value(self, parameter, idy):
        """Return a list of values for a given parameter and ID list."""
        res = []
        result = set()
        for a in self.rep:
            res = res + retrieve(a.repid, a.show([parameter], idy))
        for b in res:
            result.add(b[1])
        return list(result)

def mark(identification, listVariable):
    """Replace the elements of a list with id-element pairs."""
    # for a in range(len(listVariable)):
    #     listVariable[a] = [identification, listVariable[a]]
    return listVariable


def retrieve(identification, listVariable):
    """retrieve the elements of a marked list with a specific id."""
    res = []
    if(type(listVariable) is not list):
        listVariable = [listVariable]
    for element in listVariable:
        if(re.sub(r'([0-9]+)\|(.+)', r'\1', element) == str(identification) or identification == 0):
            res.append(element)
    # print(identification)
    # print(res)
    return res


def repAnd(one, two):
    """Perform an AND logical operation on two lists."""
    return(list(set(one).intersection(two)))


def repOr(one, two):
    """Perform an OR logical operation on two lists."""
    return(list(dict.fromkeys(one+two)))


def repAndNot(one, two):
    """Perform an AND NOT logical operation on two lists."""
    return(list(set(one).difference(two)))


def repSort(result):
    """This one is not ready yet."""
    res = result
    for pos in range(len(result[0]))[::-1]:
        res = sorted(res, key=lambda x: x[pos])
    return res


def repSyll(data, index=1):
    """Return quantitative results on input data.

    Input data must be a list of lists, and index specifies which parameter
    to count.
    """
    count = 0
    result = {}
    for a in data:
        if len(a[index]) > 0:
            if(a[index] in result):
                result[a[index]][0] = result[a[index]][0] + 1
            else:
                result[a[index]] = [1]
            count = count + 1
    for b, c in result.items():
        result[b].append(str(round((result[b][0]*100)/count)) + '%')
    # res = sorted(sorted(result.items(), key=lambda kv: (kv[0])),
                 # key=lambda kv: (kv[1]), reverse=True).items()
    res = result
    for d in sorted(res):
        print((d, res[d]), end='\n')
    return res


def repValues(data, index=1):
    """Return the values in a result list.

    The index specifies which parameter to collect.
    """
    result = set()
    for a in data:
        if len(a[index]) > 0:
            result.add(a[index])
    return sorted(list(result))


def repDisplay(result):
    """Display results of a "show" command in a nicer way."""
    # res = repSort(result)
    res = result
    for a in res:
        print('----------------------------------')
        for b in a:
            print(b)
    print('==================================')
    print(str(len(res)) + ' results\n')
