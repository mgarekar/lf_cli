
#use-case:
    #code.py region principal(regex) 
    #returns json of specific permisisons

#permissions_json is the dict that has data
#principal is the argument



import json,argparse
import subprocess
import sys


def parse_args():
    ''' Arg Parsing, invalid input handling, and setting global command'''
    list_principals()
    parser = argparse.ArgumentParser()
    parser.add_argument("--region",help='enter the aws region that you want to work in,\n Default us-east-1',default='us-east-1')
    parser.add_argument("principal",help='Name of Principal')
    parser.add_argument("--resource",help='''
    \n TableWithColumns
    \n Table
    \n Database
    \n Catalog
    \n DataLocation
    ''',default='ALL')
    args=parser.parse_args()

    return ( {
        'region':args.region,
        'principal':args.principal,
        'resource':args.resource
    }  )



def run_command(cmd,debug=False):
    '''run the damm command using subprocess, prints stderr, stdout, process id'''
    p=subprocess.Popen(cmd,shell = True,stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding='utf-8')
    stdout,stderr=p.communicate(timeout=60)
    if (p.returncode != 0):
        sys.exit(1)
    if (debug):
        print ('process id is {}'.format(p.pid))
        print (p.returncode)
        print('stderr is \n{}'.format(stderr))
        print('stdout is \n{}'.format(stdout))
    #all good, successful stdout was returned
    return stdout

def list_principals():
    '''List all roles in this account with lf in their name '''
    print ("Here are all the principals in this accounti")
    roles_dict=run_command('aws iam list-roles',debug=False)
    roles_dict=json.loads(roles_dict)
    for role_obj in roles_dict['Roles']:
        if "lf" in role_obj['RoleName']:
            print ( role_obj['RoleName'])
        # print (role_obj)

def permission_type_identifier(perm_obj):
    '''Return type of perm obj '''
    #{"TableWithColumns":{"DatabaseName":"cloudtrail","Name":"test__cloudtrail","ColumnWildcard":{}}}
    t_d=perm_obj["Resource"]
    permobj_type=list(t_d.keys())[0]
    return permobj_type


#constants:
perm_types=["TableWithColumns","Table","Database","Catalog","DataLocation"]

#PARSE ARGS
args=parse_args()
print (args)
principal=args['principal']
region=args['region']
resource=args['resource']

#API CALLS
cmd = 'aws lakeformation list-permissions --region {}'.format(region)
permission_str=run_command(cmd,debug=False)

#MAIN
permissions_json=json.loads(permission_str)
permission_list=permissions_json['PrincipalResourcePermissions']

#sample permission object
# {"Principal":{"DataLakePrincipalIdentifier":"arn:aws:iam::898179183470:role/LakeFormationWorkflowRole"},"Resource":{"TableWithColumns":{"DatabaseName":"cloudtrail","Name":"test__cloudtrail","ColumnWildcard":{}}},"Permissions":["SELECT"],"PermissionsWithGrantOption":["SELECT"]}

#iterate through list -> creating a new dict to hold permission obj per type
# how to dientify if permission obj is of given type?
# permission_type_identifier()
t_d={}
for perm_obj in permission_list:
    perm_type=permission_type_identifier(perm_obj)
    try:
        t_l=t_d[perm_type]
        "already exists in dictionary --> append to list"        
        t_l = t_d[perm_type] 
        t_l.append(perm_obj)
        t_d[perm_type] = t_l
    except KeyError:
        "first match --> create empty list, add obj to list, and add to dictionary based on obj type"
        t=[]
        t.append(perm_obj)
        t_d[perm_type] = t
    except:
        print ("Falling to last except, check logic")
        pass

#PPrint dictionary based on the keys
for k,v in t_d.items():
    print ("The type of permission is {}".format(k).upper())
    for perm_obj in v:
        print (perm_obj)
        
    print("\n")
        
#checking user input for principal and printing principals's permissino

for k,v in t_d.items():
    for perm_obj in v:
        if principal in perm_obj['Principal']['DataLakePrincipalIdentifier']:
            print(json.dumps(perm_obj,indent=4))

