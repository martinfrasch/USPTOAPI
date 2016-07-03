import json
from io import StringIO
from typing import List, Dict, Any
import requests
from toolz import pluck
import pytablewriter
from outputviewcontroller import viewoutput


BASE_PATENT ='http://www.patentsview.org/api/patents/query'
BASE_ASSIGNEE = 'http://www.patentsview.org/api/assignees/query'


def make_query(query: str, fields: List[str], options: Dict[str, Any]) -> str:
    '''
    Make a query string for USPTO API
    Parameters
        query: query string in json format
        fields: list of output fields
        options: dictionary of query options
    Returns
        json query string
    '''
    return ''.join(['q=', query,
                    '&f=', json.dumps(fields),
                    '&o=', json.dumps(options)])
     

def get_info(payload: str, base: str =BASE_PATENT) -> Any:
    '''
    Send Query to USPTO API endpoint and return results
    Parameters
        payload: json query string
        base: http address of USPTO API endpoint
    Returns
        requests object
    '''
    r = requests.get(BASE_PATENT, params=payload)
    if r.status_code == requests.codes.ok:
        return r
    else:
        r.raise_for_status()
    

def get_output(fields: List[str], response: Any) -> List[str]:
    '''
    Extract raw output from returned query dictionary
    Parameters
        fields: list of output fields
        response: dict from query response
    Returns
        list of tuples for output table
    '''
    patents = response['patents']
    return list(pluck(fields, patents))
    

def formated_output(fields: List[str], raw_output: List[str]) -> str:
    '''
    Make raw output into a HTML document with a formated HTML table
    Parameters
        fields: list of output fields
        raw_output: list of tuples for output table
    Returns
        HTML string containg formatted HTML table
    '''
    writer = pytablewriter.HtmlTableWriter()
    html_begin = '<!DOCTYPE HTML>\n<html>\n<head>\n'
    CSS = '''<style type="text/css">
             table {
                 padding: 0;
                 border-collapse: collapse;
                 border-spacing: 0;
                 font-size: 100%;
                 font: inherit;
                 border: 0;
                   }
        
              tbody {
                 margin: 0;
                 padding: 0;
                 border: 0;
                    }
        
              table tr {
                 border: 0;
                 border-top: 1px solid #CCC;
                 background-color: white;
                 margin: 0;
                 padding: 0;
                       }
        
              table tr:nth-child(2n) {
                 background-color: #F8F8F8;
                                      }
        
              table tr th, table tr td {
                border: 1px solid #CCC;
                text-align: left;
                margin: 0;
                padding: 0.5em 1em;
                                       }
        
              table tr th {
                font-weight: bold;
                          }
             </style> 
        '''
    html_inter = '\n</head>\n<body>'
    html_end = '\n</body>\n</html>'
    writer.table_name = 'Query Output\n'
    writer.header_list = fields
    writer.value_matrix = raw_output
    with StringIO() as f:
        f.write(html_begin)
        f.write(CSS)
        f.write(html_inter)
        writer.stream = f
        writer.write_table()
        f.write(html_end)
        html_text = f.getvalue()
    return html_text

def input2output(query: str, fields: List[str]) -> None:
    options = {'per_page':50}
    payload = make_query(query, fields, options)
    print('Query String\n', payload, '\n')
    r = get_info(payload)
    print('Encoded URL\n', r.url, '\n')
    print('Status Code\n', r.status_code, '\n')
    print('****Response****', '\n', r.json(), '\n\n')
    raw_output = get_output(fields, r.json())
    html_text = formated_output(fields, raw_output)
    viewoutput(html_text)
