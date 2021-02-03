#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 18:53:20 2021

@author: nathanaelyoewono
"""

# import dash components
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import dash_bootstrap_components as dbc

# data manipulatioon
import pandas as pd

# scrape 
import requests
from bs4 import BeautifulSoup

# auto open browser
from threading import Timer
import webbrowser

# add directories
import sys
sys.path.insert(1, '/Users/nathanaelyoewono/Project/GetaJob/database')
sys.path.insert(1,'/Users/nathanaelyoewono/Project/GetaJob/scraper')

# import db
from db import JobDB
# import scraper
from indeed import IndeedScrape
from seek import SeekScrape

# check database connection
db = JobDB()
if db.create_connection()==1:
    pass
else:
    raise("error, can't connect to database")

    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


######### -------------------- DEFAULT ---------------------- ###########

# set the dropdown values
drop_down = db.query_all_group_search()
drop_down_dic = [{'label': i[0], 'value': i[0]} for i in drop_down]

# set the page size for the table and its column
PAGE_SIZE = 15
col_lst = ['Index', 'ID', 'Role', 'Company', 'Location', 'Salary',
           'Date_Scraped', 'Portal']
table_col =[{"name": i, "id": i} for i in col_lst]

# Set the report card table column and its values for each status
rep_list = ['Status', 'Number']
report_col = [{"name": i, "id": i} for i in rep_list]
applied, rejected, pending = db.query_applied_rejected()
data_report = [('Applied', applied), ('Pending', pending), ('Rejected', rejected)]
report_df = pd.DataFrame(data_report, columns = ['Status', 'Number']).to_dict('records')

# close the database
db.conn.close()


######### -------------------- FUNCTION ---------------------- ###########

def get_text_indeed(link):
    page = requests.get(link)
    # parse with BFS
    soup = BeautifulSoup(page.text, 'html.parser')
    
    try:
        texts = soup.find(class_='jobsearch-jobDescriptionText').find_all('p')
    except:
        texts = ''
        
    all_text = []
    
    # iterate over all paragraph
    for i in texts:
        
        p = i.get_text()
        all_text.append(p)
        
        lists = extract_list(i)
        
        if lists != None:
            all_text.append(lists)

    return all_text

def extract_list(p):
    """Check if there is a list after p"""
    for sibling in p.next_siblings:
        if sibling.name == 'ul':
            return [li.text for li in sibling.find_all('li')]
        if sibling.name == 'p':
            return None 

def get_text_seek(link):
    page = requests.get(link)
    # parse with BFS
    soup = BeautifulSoup(page.text, 'lxml')
    all_text = []
    
    try:
        texts = soup.find(attrs={"data-automation" : "mobileTemplate"})
        texts = texts.find('div', {"class": "FYwKg WaMPc_4"})
        
        # iterate over all of the text element
        for i in texts:
            try:
                if i.name=='ul':
                    lists = [j.string for j in i]
                    all_text.append(lists)
                else:
                    if str(i.string)!='None':
                        all_text.append(str(i.string))
                        
            except:            
                pass
            
        all_text = [i for i in all_text if i!=' ']
    
        for each_sent in range(len(all_text)):
            sent = all_text[each_sent]

            if '\xa0' in sent and type(sent)==str:
                all_text[each_sent] = sent.replace('\xa0', '')
                
            # clean out the list part    
            elif type(sent)==list:
                all_text[each_sent] = [i for i in all_text[each_sent] if i != ' ']
                
                for each_each_sent in range(len(all_text[each_sent])):
                    new_sent = all_text[each_sent][each_each_sent]
                    if '\xa0' in new_sent:
                        all_text[each_sent][each_each_sent] = all_text[each_sent][each_each_sent].replace('\xa0', '')
    except:
        # failed to get the text
        all_text = ['']
    
    return all_text


def get_df(group_search):
    
    """Get the data for the jobs with no status"""
    
    if db.create_connection()==1:
        pass
    else:
        raise("error, can't connect to database")
        
    jobs = db.query_jobs(group_search)
    jobs_df = pd.DataFrame(jobs, columns = ['ID', 'Role', 'Company', 
                                                    'Location', 'Salary', 
                                                    'Date_Scraped',
                                                    'Portal'])
    jobs_df['Index'] = jobs_df.index
    
    return jobs_df

def get_df_status(status, group_search):
    
    """Get the data for the jobs with status"""
    
    if db.create_connection()==1:
        pass
    else:
        raise("error, can't connect to database")
    jobs = db.query_job_by_status(status, group_search)
    if jobs == None:
        return pd.DataFrame([])
    else:
        jobs_df = pd.DataFrame(jobs, columns = ['ID', 'Role', 'Company', 
                                                        'Location', 'Salary', 
                                                        'Date_Scraped',
                                                        'Portal', 'Rejected'])
        jobs_df['Index'] = jobs_df.index
        return jobs_df


def text_template(lists, link):
    
    """Template to print out the text detail"""
    
    text = [html.H3('Job details', style={'backgroundColor':'#327ba8',
                                          'color':'white',
                                          'padding':'5px',
                                          'border-radius': 10})]
    
    if len(lists)==0:
        text.append(html.P('Details not available, please visit the link directly'))
    for i in lists:
        if type(i)!=list:
            new_child = html.P(i)
            text.append(new_child)
        else:
            children_list=[html.Li(j) for j in i]
            text.append(html.Ul(children_list))

    text.append(dbc.CardLink(children="Apply", href=link, 
                             target="_blank", id='apply-set'))

    return text

def empty_template():
    
    """Template if no text is detected"""
    
    text = [html.H3('No details available', style={'backgroundColor':'#327ba8',
                                          'color':'white',
                                          'padding':'5px',
                                          'border-radius': 10})]
    return text

def update_applied(apply, ID):
    
    """Update the applied jobs"""
    
    if db.create_connection()==1:
        try:
            db.update_applied(apply, ID)
            if apply==1:
                print(f'Success apply {ID}')
            else:
                print(f'Success remove apply {ID}')
        except:
            print(f'Fail update apply {ID}')
    else:
        raise('Error connect db')

def update_rejected(reject, ID):
    
    """Update the rejected jobs"""
    
    # set by default for faulty input
    if reject not in [0, 1]:
        reject = 0
        
    if db.create_connection()==1:
        try:
            db.update_rejected(reject, ID)
            if reject==1:
                print(f'Rejected job {ID}')
            else:
                print(f'Undo rejected job {ID}')
        except:
            print(f'Fail reject job {ID}')
    else:
        raise('Error connect db')
            
        
######### -------------------- CALLBACKS ---------------------- ###########

# update the table job
@app.callback(
    Output('datatable-job', 'data'),
    Output('datatable-job', 'columns'),
    Output('datatable-job', 'dropdown'),
    Input('role-dropdown', 'value'),
    Input('datatable-report', 'selected_rows'),
    Input('datatable-job', "page_current"),
    Input('datatable-job', "page_size"))
def update_table(group_search, status, page_current, page_size):
    
    """ Callbacks for:
        - Data jobs in the table
        - Column in the table jobs
        - Dropdown rejected column in the table jobs
    """
    
    dic_report = {0:'Applied', 1:'Pending', 2:'Rejected'}
    
    # the status report was not touched
    if len(status)==0:
       
        # the group search was specified
        if group_search != None:
            col_lst = ['Index', 'ID', 'Role', 'Company', 'Location', 'Salary', 
                       'Date_Scraped', 'Portal']
            table_col =[{"name": i, "id": i} for i in col_lst]
            
            # get the data for the table
            df = get_df(group_search)
            
            if df.shape[0]!=0:
                return [df.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records'), table_col,{}]
            
            # returning empty table
            else:
                return [[],table_col,{}]
            
        # No group search, get all jobs
        else:
            col_lst = ['Index', 'ID', 'Role', 'Company', 'Location', 'Salary', 
                       'Date_Scraped', 'Portal']
            table_col =[{"name": i, "id": i} for i in col_lst]
            df = get_df('ALL')
            if df.shape[0]!=0:
                return [df.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records'), table_col,{}]
            
            # returning empty table
            else:
                return [[],table_col,{}]
            
    # there is status     
    else:
        col_lst = ['Index', 'ID', 'Role', 'Company', 'Location', 'Salary', 
                   'Date_Scraped', 'Portal']
        table_col =[{"name": i, "id": i} for i in col_lst]
        
        # set the dropdown column for rejected
        table_col.append({"name":"Rejected", "id":"Rejected", 
                          'presentation': 'dropdown'})
        dd = {'Rejected':{'options':[{'label':'Yes', 'value':1}, 
                                     {'label':'No', 'value':0}]}}
        
        # get the data based on the group search and status
        status = dic_report[status[0]]
        df = get_df_status(status, group_search)
        if df.shape[0]!=0:
            return [df.iloc[
                page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records'),table_col,dd]
        # returning empty table
        else:
            return [[],table_col,dd]

                

# update the detail of each job in right hand side
@app.callback(
    Output('job-details', 'children'),
    Input('datatable-job', 'selected_rows'),
    Input('datatable-job', 'data')
    )
def display_details(row, data):
    
    """ Callbacks for:
        - Displaying job details in the right hand side of the table
    """

    # check if there is no data and no selected row
    if data!=[] and len(row) != 0:
        cur_index = row[0]
        
        # clear out dropdown option
        if data == None:
            return empty_template()
        
        # current index of selected row is bigger than the number of data 
        if cur_index+1 > len(data):
            return empty_template()
        
        get_id = data[row[0]]['ID']
        portal = data[row[0]]['Portal']
        
        # set the template job details
        if db.create_connection()==1:
            query_link = db.query_link(get_id)
            #db.conn.close()
            
            if portal == 'Indeed':
                texts = get_text_indeed(query_link)
                texts = [i for i in texts if i != '']
                texts = text_template(texts, query_link)
                return texts
            elif portal == 'Seek':
                texts = get_text_seek(query_link)
                texts = text_template(texts, query_link)
                return texts
                
        else:
            raise("error, can't connect to database")

    else:
        return empty_template()

# update the job applied report
@app.callback(Output('datatable-report', 'data'),
              Output('datatable-job', 'selected_rows'),
              [Input('datatable-job', 'data_previous'),
               Input('datatable-report', 'selected_rows')],
              [State('datatable-job', 'data')])
def show_removed_rows(previous, status, current):
    
    """ Callbacks for:
        - Updating the job report table
        - Updating which rows to be selected in the job table
    """
    
    # get which click is triggered
    ctx = dash.callback_context
    
    # no table altered
    if previous==None:
        raise dash.exceptions.PreventUpdate()
        
    else:
        clicked = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # prevent table update caused by changing the table by status
        if clicked=='datatable-report':
            raise dash.exceptions.PreventUpdate()
        else:
            applied_id = [row['ID'] for row in previous if row not in current]
            
            try:
                # check if the rejected col has been changed
                prev_row = [row for row in previous if row['ID']==applied_id[0]][0]
                cur_row = [row for row in current if row['ID']==applied_id[0]][0]
                
                if prev_row['Rejected']!=cur_row['Rejected']:
                
                    #update to database first 
                    update_rejected(cur_row['Rejected'], applied_id[0])
                    applied, rejected, pending = db.query_applied_rejected()
                    data = [('Applied', applied), ('Pending', pending), 
                            ('Rejected', rejected)]
                    report_df = pd.DataFrame(data, columns = ['Status', 'Number'])
                    return [report_df.to_dict('records'), [0]]
            except:
                try:
                    # row does not exist, means removed
                    if prev_row['Rejected']==1:
                        update_rejected(0, applied_id[0])
                except:
                    pass
                
                if db.create_connection()==1:
                    applied, rejected, pending = db.query_applied_rejected()
                    
                    if len(applied_id)>0:
                        
                        # this indicate that the job report was not touched, only group search
                        # Thus, this will indicate that you are applying for a job
                        if len(status)==0:
                            update_applied(1, applied_id[0])
                            
                        else:
                            update_applied(0, applied_id[0])
                            
                        applied, rejected, pending = db.query_applied_rejected()
                        
                    data = [('Applied', applied), ('Pending', pending), 
                            ('Rejected', rejected)]
                    report_df = pd.DataFrame(data, columns = ['Status', 'Number'])
                    
                    # if there is still data in the table
                    if len(current)!=0:
                        return [report_df.to_dict('records'), [0]]
                    else:
                        return [report_df.to_dict('records'), []]
                    
                else:
                    raise("Can't connect to db")

# clear the report table selection
@app.callback(Output('datatable-report', 'selected_rows'),
              Input('clear-but', 'n_clicks'))
def clear_report_option(clear_but_clicks):
    
    """ Callbacks for:
        - Clear out all selected rows in the report table
    """
    
    ctx = dash.callback_context
    clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    if clicked=='clear-but':
        return []
    else:
        raise dash.exceptions.PreventUpdate()

@app.callback(Output('role-dropdown', 'value'),
              Output('role-dropdown', 'options'),
              [Input('find-new-jobs', 'n_clicks')],
              [State('new-role', 'value')])
def new_jobs(click, new_role):
    
    """ Callbacks for:
        - Updating which group search was picked in the dropdown at the top
        - Adding the option of the dropdown after getting new role
        
        This is where the scraping bot take actions!
        
        Using the state here enabled this callback to be triggered only if 
        the button was clicked
    """
     
    # enter here means find has been clicked 
    if new_role==None:
        raise dash.exceptions.PreventUpdate()
    else:
        new_role = new_role.lower()
        
        # get the bot up and running to scrape the new role
        try:
            indeed_jobs = IndeedScrape(new_role, 'Melbourne')
            indeed_jobs.run()
        except:
            indeed_jobs.run()
        
        try:
            seek_jobs = SeekScrape(new_role, 'Melbourne')
            seek_jobs.run()
        except:
            seek_jobs.run()
        
            
        if db.create_connection()==1:
            drop_down = db.query_all_group_search()
            drop_down_dic = [{'label': i[0], 'value': i[0]} for i in drop_down]
        else:
            raise("Can't connect to db")
        
        return [new_role, drop_down_dic]
    
    
    

######### -------------------- APP ---------------------- ###########


app.layout = html.Div([
    
    # Title
    html.H1(children='GetaJob', 
            style={
                'backgroundColor':'#327ba8',
                'verticalAlign':'middle',
                'border-radius': 10,
                'color':'white',
                'padding':'10px'
                }
            ),
    
    # display the role selection, new role and table result
    html.Div(children=[
        
        # display the role section and report applied
        html.Div(children=[
            
            # role and new role section
            html.Div(children=[
                
                # search current role you already have
                html.Div(children=[
                    html.Div(children='Role'),
                    html.Div(children=[
                        
                        # drop down
                        html.Div(
                            dcc.Loading(children=[
                                dcc.Dropdown(
                                    id='role-dropdown',
                                    options=drop_down_dic,
                                    value=drop_down[0][0]
                                )
                            ], id='loading-dropdown', type="default"),
                            style={'width':'70%',  'verticalAlign':'middle'}
                        ),
                    ])
                    
                ], style={'paddingLeft': '10px',}),
                
                # new roles
                html.Div(children=[
                    html.Div(children='New Role'),
                    html.Div(children=[
                        
                        # drop down
                        html.Div(
                            dcc.Input(
                                id='new-role',
                            ),
                            style={'width':'0.05%', 'display':'table-cell'}
                        ),
                        
                        # button
                        html.Div(
                            html.Button('Find', 
                                        id='find-new-jobs', 
                                        style={'backgroundColor':'#327ba8',
                                               'color':'white'}),
                            style={'width':'30%', 'display':'table-cell', 
                                   'paddingLeft':'1%'}
                        ),            
                    ]), 
                ], style={'paddingLeft':'10px', 
                          'paddingTop':'2%'}),
                          
            ], style={'display':'table-cell'}),
            
            # report table
            html.Div(children=[

                html.Center(children=[
                    
                    dash_table.DataTable(
                        id='datatable-report',
                        columns=report_col,
                        data=report_df,
                        style_cell={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'maxWidth':'10'
                        },
                        row_selectable='single',
                        selected_rows=[],
                    )])
                ], style={'display':'table-cell', 'paddingLeft':'10%'}),
            
            # clear button
            html.Div(children=[
                
                html.Button('Clear', id='clear-but', n_clicks=0,
                            style={'backgroundColor':'#327ba8',
                                               'color':'white'})
                
                ], style={'display':'table-cell', 'paddingLeft':'5%', 
                          'verticalAlign':'middle'})

        ], style={'verticalAlign':'middle'}),
            
        # display the job thable
        html.Div(children=[
            
            dash_table.DataTable(
                id='datatable-job',
                columns=table_col,
                style_cell={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'maxWidth':'5'
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'Salary'},
                     'width': '5%'},
                ],
                page_current=0,
                page_size=PAGE_SIZE,
                page_action='custom',
                row_selectable='single',
                row_deletable=True,
                selected_rows=[0],
                editable=True,
            )
        
        ], style={'paddingTop':'3%',
                  'paddingLeft':'10px',
                  'display':'table-cell',
                  'paddingRight':'10px',
                  'verticalAlign':'middle'}),
        
      ], style={'display':'table-cell', 'width':'49%', 'paddingRight':'2%',
                'verticalAlign':'middle'}),
    
    # display the job description and link
    html.Div(children=[
        dbc.Card(
            dbc.CardBody([]),
            id='job-details',
            style={"width": "100%", 
                   "height":"448px", 'marginLeft':'2%', 'paddingRight':'2%'}
    
        )], style={'display':'table-cell', 'width':'49%', 'marginLeft':'2%', 
                   'marginRight':'2%',
                   'height':'600px', 'overflow':'scroll', 'border':'1px solid',
                   'borderColor':'#327ba8','border-radius': 10})

])

def open_browser():
    webbrowser.open_new('http://127.0.0.1:8050/')
    
if __name__ == '__main__':
    # wait for 1 sec, then start browser
    Timer(1, open_browser).start()
    app.run_server(debug=True)
    