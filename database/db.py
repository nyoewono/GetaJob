#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 11:43:58 2021

@author: nathanaelyoewono
"""

import os
import sqlite3
from sqlite3 import Error

class JobDB:
    
    path = '/Users/nathanaelyoewono/Project/GetaJob/database/jobdata.db'
    
    sql_create_job = """ CREATE TABLE IF NOT EXISTS job (
                                        id integer PRIMARY KEY,
                                        company_id integer NOT NULL,
                                        portal_id integer NOT NULL,
                                        role text NOT NULL,
                                        date_scraped DATE NOT NULL,
                                        applied_date text,
                                        applied integers DEFAULT 0,
                                        days_stored integers,
                                        link text NOT NULL,
                                        salary text,
                                        position_level text,
                                        location text,
                                        rejected integer DEFAULT 0,
                                        FOREIGN KEY(company_id) REFERENCES company (id),
                                        FOREIGN KEY(portal_id) REFERENCES portal (id),
                                        UNIQUE(company_id, role)
                                    ); """
    
    sql_create_company = """CREATE TABLE IF NOT EXISTS company (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL UNIQUE
                                );"""
    
    sql_create_portal = """CREATE TABLE IF NOT EXISTS portal (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL UNIQUE
                                );"""
    
    sql_create_group = """CREATE TABLE IF NOT EXISTS group_search (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL UNIQUE
                                );"""
    
    sql_create_group_job = """CREATE TABLE IF NOT EXISTS group_job (
                                    id integer PRIMARY KEY,
                                    group_id integer NOT NULL,
                                    job_id integer NOT NULL,
                                    FOREIGN KEY(group_id) REFERENCES company (id),
                                    FOREIGN KEY(job_id) REFERENCES job (id),
                                    UNIQUE(group_id, job_id)
                                );"""

    
    def create_connection(self):
        
        """ create a database connection to a SQLite database """
        """ Automatically create a new database if the file does not exist in
            the current working directory """
            
        self.conn = None
        try:
            self.conn = sqlite3.connect(JobDB.path)
            # print(sqlite3.version)
            return 1
        except Error as e:
            print(e)
            return 0
        # finally:
        #     if self.conn:
        #         self.conn.close()   
        
                
    def _set_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)
    
    def create_table(self):
        """
        Create tables for the database
        """
        
        # create a database connection
        self.create_connection()
        
        # create tables
        if self.conn is not None:
    
            # create company table
            self._set_table(JobDB.sql_create_company)
            
            # create portal table
            self._set_table(JobDB.sql_create_portal)
            
            # create job table
            self._set_table(JobDB.sql_create_job)
            
            # create group job table
            self._set_table(JobDB.sql_create_group)
            
            # create group table
            self._set_table(JobDB.sql_create_group_job)
        else:
            print("Error! cannot create the database connection.")
            
    def create_job(self, desc):
        
        sql = ''' INSERT INTO job(role,company_id,link,location,salary,portal_id, date_scraped)
              VALUES(?,?,?,?,?,?,?)'''
        
        cur = self.conn.cursor()
        cur.execute(sql, desc)
        self.conn.commit()
    
        return cur.lastrowid
    
    def create_company(self, desc):
        
        sql = ''' INSERT INTO company(name)
              VALUES(?) '''
              
        cur = self.conn.cursor()
        cur.execute(sql, desc)
        self.conn.commit()
    
        return cur.lastrowid
    
    def create_portal(self, desc):
        
        sql = ''' INSERT INTO portal(name)
              VALUES(?) '''
              
        cur = self.conn.cursor()
        cur.execute(sql, desc)
        self.conn.commit()
    
        return cur.lastrowid
    
    def create_group(self, desc):
        
        sql = ''' INSERT INTO group_search(name)
              VALUES(?) '''
              
        cur = self.conn.cursor()
        cur.execute(sql, desc)
        self.conn.commit()
    
        return cur.lastrowid
    
    def create_group_job(self, desc):
        
        sql = ''' INSERT INTO group_job(job_id, group_id)
              VALUES(?, ?) '''
              
        cur = self.conn.cursor()
        cur.execute(sql, desc)
        self.conn.commit()
    
        return cur.lastrowid
        
    
    def get_company_port_group_id(self, name, table):
        
        """
        Query tasks by priority
        :param conn: the Connection object
        :param priority:
        :return:
        """
        
        cur = self.conn.cursor()
        cur.execute(f"SELECT id FROM {table} WHERE name=?", (name,))
    
        rows = cur.fetchall()
    
        if len(rows)>0:
            return rows[0][0]  
        else:
            return None
    
    def query_jobs(self, group):
        
        """
        Query jobs by group search role
        :param conn: the Connection object
        :param priority:
        :return:
        """
        
        cur = self.conn.cursor()
        
        if group!='ALL':
        
            query = '''SELECT job.id, job.role, company.name, job.location, job.salary, job.date_scraped, portal.name
                       FROM 
                       group_search 
                       INNER JOIN group_job on group_search.id = group_job.group_id 
                       INNER JOIN job on group_job.job_id = job.id
                       INNER JOIN company on company.id = job.company_id
                       INNER JOIN portal on portal.id = job.portal_id
                       WHERE group_search.name=? AND job.applied = 0'''
            cur.execute(query, (group,))
        else:
            query = '''SELECT job.id, job.role, company.name, job.location, job.salary, job.date_scraped, portal.name
                       FROM 
                       group_search 
                       INNER JOIN group_job on group_search.id = group_job.group_id 
                       INNER JOIN job on group_job.job_id = job.id
                       INNER JOIN company on company.id = job.company_id
                       INNER JOIN portal on portal.id = job.portal_id
                       WHERE job.applied = 0'''
            cur.execute(query)
            
    
        rows = cur.fetchall()
    
        if len(rows)>0:
            return rows  
        else:
            return None
    
    def query_all_group_search(self):
        
        """
        Query jobs by group search role
        :param conn: the Connection object
        :param priority:
        :return:
        """
        
        cur = self.conn.cursor()
        query = '''SELECT name
                   FROM group_search '''
        cur.execute(query)
    
        rows = cur.fetchall()
    
        if len(rows)>0:
            return rows  
        else:
            return None
    
    def query_link(self, ID):
        
        """
        Query jobs by group search role
        :param conn: the Connection object
        :param priority:
        :return:
        """
        
        cur = self.conn.cursor()
        query = '''SELECT link
                   FROM job
                   WHERE ID=?'''
        cur.execute(query, (ID,))
    
        rows = cur.fetchall()
    
        if len(rows)>0:
            return rows[0][0]  
        else:
            return None
    
    def query_applied_rejected(self):
        cur = self.conn.cursor()
        query = '''SELECT applied, rejected
                   FROM job
                '''
        cur.execute(query)
        rows = cur.fetchall()
        # print(rows)
        
        if len(rows)>0:
            # print(rows)
            len_applied = len([1 for i in rows if i[0]==1])
            len_rejected = len([1 for i in rows if i[-1]==1])
            len_pending = len_applied-len_rejected
            return (len_applied, len_rejected, len_pending)
        else:
            #print(0, 0, 0)
            return (0, 0, 0)
    
    def update_applied(self, apply, ID):
        
        cur = self.conn.cursor()
        query = """UPDATE JOB
                   SET applied=?
                   WHERE id=?
                   """
        cur.execute(query, (apply,ID))
        self.conn.commit()
    
    def update_rejected(self, reject, ID):
        
        cur = self.conn.cursor()
        query = """UPDATE JOB
                   SET rejected=?
                   WHERE id=?
                   """
        cur.execute(query, (reject, ID))
        self.conn.commit()
    
    def query_job_by_status(self, status, group_search):
        
        """
        Query jobs by group search role
        :param conn: the Connection object
        :param priority:
        :return:
        """
        cur = self.conn.cursor()
        
        
        if status=='Applied':
            if group_search!=None:
                query = '''SELECT job.id, job.role, company.name, job.location, job.salary, job.date_scraped, portal.name, job.rejected
                           FROM 
                           group_search 
                           INNER JOIN group_job on group_search.id = group_job.group_id 
                           INNER JOIN job on group_job.job_id = job.id
                           INNER JOIN company on company.id = job.company_id
                           INNER JOIN portal on portal.id = job.portal_id
                           WHERE group_search.name=? AND job.applied = 1'''
                cur.execute(query, (group_search,))
            else:
                query = '''SELECT job.id, job.role, company.name, job.location, job.salary, job.date_scraped, portal.name, job.rejected
                           FROM 
                           group_search 
                           INNER JOIN group_job on group_search.id = group_job.group_id 
                           INNER JOIN job on group_job.job_id = job.id
                           INNER JOIN company on company.id = job.company_id
                           INNER JOIN portal on portal.id = job.portal_id
                           WHERE job.applied = 1'''
                cur.execute(query)
        
        elif status=='Pending':
            if group_search!=None:
                query = '''SELECT job.id, job.role, company.name, job.location, job.salary, job.date_scraped, portal.name, job.rejected
                       FROM 
                       group_search 
                       INNER JOIN group_job on group_search.id = group_job.group_id 
                       INNER JOIN job on group_job.job_id = job.id
                       INNER JOIN company on company.id = job.company_id
                       INNER JOIN portal on portal.id = job.portal_id
                       WHERE group_search.name=? AND job.applied = 1 AND job.rejected=0'''
                cur.execute(query, (group_search,))
            else:
                query = '''SELECT job.id, job.role, company.name, job.location, job.salary, job.date_scraped, portal.name, job.rejected
                           FROM 
                           group_search 
                           INNER JOIN group_job on group_search.id = group_job.group_id 
                           INNER JOIN job on group_job.job_id = job.id
                           INNER JOIN company on company.id = job.company_id
                           INNER JOIN portal on portal.id = job.portal_id
                           WHERE job.applied = 1 AND job.rejected=0'''
                cur.execute(query)
        
                
        else:
            if group_search!=None:
                query = '''SELECT job.id, job.role, company.name, job.location, job.salary, job.date_scraped, portal.name, job.rejected
                       FROM 
                       group_search 
                       INNER JOIN group_job on group_search.id = group_job.group_id 
                       INNER JOIN job on group_job.job_id = job.id
                       INNER JOIN company on company.id = job.company_id
                       INNER JOIN portal on portal.id = job.portal_id
                       WHERE group_search.name=? AND job.applied = 1 AND job.rejected=1'''
                cur.execute(query, (group_search,))
            else:
                query = '''SELECT job.id, job.role, company.name, job.location, job.salary, job.date_scraped, portal.name, job.rejected
                           FROM 
                           group_search 
                           INNER JOIN group_job on group_search.id = group_job.group_id 
                           INNER JOIN job on group_job.job_id = job.id
                           INNER JOIN company on company.id = job.company_id
                           INNER JOIN portal on portal.id = job.portal_id
                           WHERE job.applied = 1 AND job.rejected=1'''
                cur.execute(query)
    
        rows = cur.fetchall()
    
        if len(rows)>0:
            return rows
        else:
            return None
        

        
            

    
db = JobDB()
db.create_connection()
res = db.query_applied_rejected()
#print(res)
    
    