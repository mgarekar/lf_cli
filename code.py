
#use-case:
    #code.py region principal(regex) 
    #returns json of specific permisisons

#permissions_json is the dict that has data
#principal is the argument



import json,argparse
import subprocess
import sys

def list_principals():
    print ("Here are all the principals in this account")

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
# print (permission_list)

# #iterate through list
t_l=[]
for permission_obj in permission_list:
    if principal in permission_obj['Principal']['DataLakePrincipalIdentifier']:
        #print (permission_obj)
        t_l.append(permission_obj)
print (json.dumps(t_l,indent=4))