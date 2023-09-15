__author__ = "Henry Rosales-Méndez"
__version__ = "0.0.7"
__maintainer__ = "Henry Rosales-Méndez"
__email__ = "hrosmendez@gmail.com"
__status__ = "beta"


import os


class DDL_Handler:
    
    def file_parser(self, fn):
        if not os.path.isfile(fn):
            print(f'File {fn} not found')
            return None
        
        content = open(fn,'r').read()
        return self.ddl_parser(content)


    def ddl_parser(self, txt):
        schema = ''
        table = ''
        L = []
        field = ''
        ttype = ''
        comment = ''        
        ntxt = len(txt)
        i = -1
        state = 0
        while i+1 < len(txt):
            i = i+1
            ch = txt[i]
            if state == 0:    
                if txt[i:i+12].upper() in ['CREATE TABLE']:
                    i = i+12
                    state = 1
                    continue
                
                elif txt[i:i+21].upper() in ['CREATE EXTERNAL TABLE']:
                    i = i+21
                    state = 1
                    continue
                
                elif txt[i:i+23].upper() in ['CREATE OR REPLACE TABLE']:
                    i = i+23
                    state = 1
                    continue 
            
            elif state == 1:
                if ch == '`':
                    state = 2
                    schema = ''
                    continue
                
                elif ch in [' ','\t','\n']:
                    continue
                
                else:
                    state = 100002
                    schema = ch
                    
            elif state == 100002:
                if ch=='.':
                    state = 100003
                    table = ''
                    continue
                elif ch == ' ':
                    print("[Error] Expected format 'schema.table' ")
                    break
                elif ch == '(':
                    state = 100004
                    table = schema
                    schema = 'SCHEMA'
                else: 
                    schema = schema + ch
                    continue
                
            elif state == 100003:
                if ch == '(':
                    state = 100
                    continue
                else:
                    table = table + ch
                    continue
                    
            #elif state == 100004:
            #    if ch == '(':
            #        state = 100
            #    continue
                
                
                    
            elif state == 2:
                if ch == '.':
                    state = 3
                    table = ''
                    continue
                elif ch == ' ':
                    print("[Error] Expected format 'schema.table' ")
                    break
                elif ch == '`':
                    state = 4
                    table = schema
                    schema = 'SCHEMA'
                else: 
                    
                    schema = schema + ch
                    continue

            elif state == 3:
                if ch == '`':
                    state = 4
                    continue
                else:
                    table = table + ch
                    continue
                    
            elif state == 4:
                if ch == '(':
                    state = 100
                continue
            
            elif state == 100:                
                if ch == '`':
                    state = 101
                    field = ''
                    continue
                elif ch in [' ','\t','\n']:
                    continue
                else:
                    state = 100101
                    i = i-1
                    field = ''
                    continue
                    
            elif state == 100101:
                if ch in [' ','\n','\t']:
                    state = 100102
                    ttype = ''
                else:
                    field = field + ch
                    
                    
            elif state == 100102:
                if not ch in [' ','\n','\t']:
                    state = 100103
                    ttype = ttype + ''
                    i = i -1
                continue
            
            elif state == 100103:
                if ch == '(':
                    state = 100104
                    ttype = ttype + ch
                elif ch == ',':
                    L.append({'field':field.strip('\n\t '), 'ttype':ttype.strip('\n\t '), 'comment':comment})
                    state = 100
                elif ch == ')':
                    L.append({'field':field.strip('\n\t '), 'ttype':ttype.strip('\n\t '), 'comment':comment})
                    return [schema, table.strip('\n\t '), L]
                else:
                    ttype = ttype + ch
                
            elif state == 100104:
                ttype = ttype + ch
                if ch == ')':
                    state = 100103
                    
                
            elif state == 101:
                if ch == '`':
                    state = 1011
                    ttype = ''
                else:
                    field = field + ch
                   
            elif state == 1011:
                if not ch in [' ','\t','\n']: 
                    state = 102
                    i = i -1
                    continue
            
            elif state == 102:
                if ch == '(':
                    state = 1021
                    ttype = ttype + ch
                elif ch == ')':
                    state = 103
                    i = i-1
                elif ch in [' ','\t','\n']:
                    state = 103
                    comment = ''
                elif ch in [',']:
                    i = i -1
                    state = 103
                else:
                    ttype = ttype + ch
                    
            elif state == 1021:
                ttype = ttype + ch
                if ch == ')':
                    state = 102
                    
                    
            elif state == 103:
                if ch == ',':
                    state = 105
                elif ch == "'":
                    state = 104
                elif ch == ')':
                    L.append({'field':field, 'ttype':ttype, 'comment':comment})
                    return [schema, table, L]
                    
            elif state == 104:
                if ch == "'":
                    state = 103
                else:                    
                    comment = comment + ch
            
            elif state == 105:
                L.append({'field':field, 'ttype':ttype, 'comment':comment})
                state = 100
                
