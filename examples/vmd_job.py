#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import sys,os,time
import code
import argparse
import re, datetime
import json
    
SITE_config='./site_config.ini'
CASE_config="./case_config.ini"

actions_file=open("/home/myuser/actions.json",'r')
tiles_actions=json.load(actions_file)
#launch_actions()

config = configparser.ConfigParser()
config.optionxform = str

config.read(SITE_config)

TILEDOCKERS_path=config['SITE']['TILEDOCKER_DIR']
DOCKERSPACE_DIR=config['SITE']['DOCKERSPACE_DIR']
#NOVNC_URL=config['SITE']['NOVNC_URL']
GPU_FILE=config['SITE']['GPU_FILE']

HTTP_FRONTEND=config['SITE']['HTTP_FRONTEND']
HTTP_LOGIN=config['SITE']['HTTP_LOGIN']
HTTP_IP=config['SITE']['HTTP_IP']
init_IP=config['SITE']['init_IP']

config.read(CASE_config)

CASE=config['CASE']['CASE_NAME']
NUM_DOCKERS=int(config['CASE']['NUM_DOCKERS'])

CASE_DOCKER_PATH=config['CASE']['CASE_DOCKER_PATH']

network=config['CASE']['network']
nethost=config['CASE']['nethost']
domain=config['CASE']['domain']

OPTIONssh=config['CASE']['OPTIONssh']
SOCKETdomain=config['CASE']['SOCKETdomain']

DOCKER_NAME=config['CASE']['DOCKER_NAME']

DATA_PATH=config['CASE']['DATA_PATH']
DATA_MOUNT_DOCKER=config['CASE']['DATA_MOUNT_DOCKER']
DATA_PATH_DOCKER=config['CASE']['DATA_PATH_DOCKER']

BIN_PATH=config['CASE']['BIN_PATH']
PYTHON_PATH=config['CASE']['PYTHON_PATH']

OPTIONS=config['CASE']['OPTIONS'].replace("$","").replace('"','')
print("\nOPTIONS from CASE_CONFIG : "+OPTIONS)
def replaceconf(x):
    if (re.search('}',x)):
        varname=x.replace("{","").replace("}","")
        return config['CASE'][varname]
    else:
        return x
OPTIONS=OPTIONS.replace("JOBPath",JOBPath)
OPTIONS=OPTIONS.replace('{','|{').replace('}','}|').split('|')
OPTIONS="".join(list(map( replaceconf,OPTIONS)))


CreateTS='create TS='+TileSet+' Nb='+str(NUM_DOCKERS)

client.send_server(CreateTS)


# Global commands
# Execute on each/a set of tiles
ExecuteTS='execute TS='+TileSet+" "
# Launch a command on the frontend
LaunchTS='launch TS='+TileSet+" "+JOBPath+' '

# Build VMD dir
# client.send_server(LaunchTS+" mkdir "+CASE)
# print("Out of mkdir %s : %s" % (CASE, str(client.get_OK())))

# get TiledAstrochem package from Github
COMMAND_GIT="git clone https://github.com/mmancip/TiledAstrochem.git"
print("command_git : "+COMMAND_GIT)
os.system(COMMAND_GIT)

# Send CASE and SITE files
try:
    client.send_server(LaunchTS+' chmod og-rxw '+JOBPath)
    print("Out of chmod JOBPath : "+ str(client.get_OK()))
    
    send_file_server(client,TileSet,".", CASE_config, JOBPath)
    CASE_config=os.path.join(JOBPath,CASE_config)
    send_file_server(client,TileSet,".", SITE_config, JOBPath)
    SITE_config=os.path.join(JOBPath,os.path.basename(SITE_config))
    send_file_server(client,TileSet,".", "tagliste", JOBPath)
    send_file_server(client,TileSet,".", "list_hostsgpu", JOBPath)

except:
    print("Error sending files !")
    traceback.print_exc(file=sys.stdout)
    try:
        code.interact(banner="Try sending files by yourself :",local=dict(globals(), **locals()))
    except SystemExit:
        pass


COMMAND_TiledAstrochem=LaunchTS+COMMAND_GIT
client.send_server(COMMAND_TiledAstrochem)
print("Out of git clone TiledAstrochem : "+ str(client.get_OK()))

COMMAND_copy=LaunchTS+"cp -rp TiledAstrochem/vmd_client "+\
              "TiledAstrochem/kill_vmd "+\
              "TiledAstrochem/build_nodes_file "+\
              "TiledAstrochem/script_vmd_Spezia.py "+\
              "TiledAstrochem/script_vmd_Spezia.vmd "+\
                "./"

client.send_server(COMMAND_copy)
print("Out of copy scripts from TiledCourse : "+ str(client.get_OK()))

# Launch containers HERE
REF_CAS=str(NUM_DOCKERS)+" "+DATE+" "+DOCKERSPACE_DIR+" "+DOCKER_NAME

print("\nREF_CAS : "+REF_CAS)

COMMANDStop=os.path.join(TILEDOCKERS_path,"stop_dockers")+" "+REF_CAS+" "+os.path.join(JOBPath,GPU_FILE)
print("\n"+COMMANDStop)
sys.stdout.flush()

# Launch dockers
def Run_dockers():
    COMMAND="bash -vx -c \""+os.path.join(TILEDOCKERS_path,"launch_dockers")+" "+REF_CAS+" "+GPU_FILE+" "+HTTP_FRONTEND+":"+HTTP_IP+\
             " "+network+" "+nethost+" "+domain+" "+init_IP+" TileSetPort "+UserFront+"@"+Frontend+" "+OPTIONS+\
             " > "+os.path.join(JOBPath,"output_launch")+" 2>&1 \"" 

    print("\nCommand dockers : "+COMMAND)

    client.send_server(LaunchTS+' '+COMMAND)
    print("Out of launch dockers : "+ str(client.get_OK()))
    sys.stdout.flush()

Run_dockers()
sys.stdout.flush()

taglist = open("tagliste", "r")
# TODO : give a liste of lines !
# tab=taglist.readlines()
# line=tab[123]
# file_name=(line[1].split('='))[1].replace('"','')


# Build nodes.json file from new dockers list
def build_nodes_file():
    print("Build nodes.json file from new dockers list.")
    # COMMAND=LaunchTS+' chmod u+x build_nodes_file '
    # client.send_server(COMMAND)
    # print("Out of chmod build_nodes_file : "+ str(client.get_OK()))

    COMMAND=LaunchTS+' ./build_nodes_file '+os.path.join(JOBPath,CASE_config)+' '+os.path.join(JOBPath,SITE_config)+' '+TileSet
    print("\nCommand dockers : "+COMMAND)

    client.send_server(COMMAND)
    print("Out of build_nodes_file : "+ str(client.get_OK()))
    time.sleep(2)
    launch_nodes_json()

build_nodes_file()
sys.stdout.flush()
#get_file_client(client,TileSet,JOBPath,"nodes.json",".")

time.sleep(2)
# Launch docker tools
def launch_resize(RESOL="1440x900"):
    client.send_server(ExecuteTS+' xrandr --fb '+RESOL)
    print("Out of xrandr : "+ str(client.get_OK()))

launch_resize()

def launch_tunnel():
    client.send_server(ExecuteTS+' /opt/tunnel_ssh '+SOCKETdomain+' '+HTTP_FRONTEND+' '+HTTP_LOGIN)
    print("Out of tunnel_ssh : "+ str(client.get_OK()))

launch_tunnel()

def launch_vnc():
    client.send_server(ExecuteTS+' /opt/vnccommand')
    print("Out of vnccommand : "+ str(client.get_OK()))

launch_vnc()

def launch_one_client(script='vmd_client',tileNum=-1,tileId='001'):
    line=taglist.readline().split(' ')
    file_name=(line[1].split('='))[1].replace('"','')
    COMMAND=' '+CASE_DOCKER_PATH+script+' '+DATA_PATH_DOCKER+' '+file_name
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '            
    else:
        TilesStr=' Tiles=('+tileId+') '
    print("%s VMD command : %s" % (TilesStr,COMMAND))
    CommandTS=ExecuteTS+TilesStr+COMMAND
    client.send_server(CommandTS)

# TODO : give a list of lines !
def Run_clients():
    for i in range(NUM_DOCKERS):
        launch_one_client(tileNum=i)
    Last_Elt=NUM_DOCKERS-1

Run_clients()
sys.stdout.flush()

def next_element(script='vmd_client',tileNum=-1,tileId='001'):
    line=taglist.readline().split(' ')
    file_name=(line[1].split('='))[1].replace('"','')
    COMMAND=' '+CASE_DOCKER_PATH+script+' '+DATA_PATH_DOCKER+' '+file_name
    COMMANDKill=' '+CASE_DOCKER_PATH+"kill_vmd"
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
    else:
        TilesStr=' Tiles=('+tileId+') '
    print("%s VMD command : %s" % (TilesStr,COMMAND))

    CommandTSK=ExecuteTS+TilesStr+COMMANDKill
    client.send_server(CommandTSK)
    client.get_OK()
    
    CommandTS=ExecuteTS+TilesStr+COMMAND
    client.send_server(CommandTS)
    client.get_OK()

def init_wmctrl():
    client.send_server(ExecuteTS+' wmctrl -l -G')
    print("Out of wmctrl : "+ str(client.get_OK()))

init_wmctrl()

def clear_vnc(tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
    else:
        TilesStr=' Tiles=('+tileId+') '
    client.send_server(ExecuteTS+TilesStr+' x11vnc -R clear-all')
    print("Out of clear-vnc : "+ str(client.get_OK()))

def clear_vnc_all():
    os.system('x11vnc -R clear-all')
    for i in range(NUM_DOCKERS):
        clear_vnc(i)
        #clear_vnc(tileId=containerId(i))

clear_vnc_all()

def toggle_fullscr():
    for i in range(NUM_DOCKERS):
        client.send_server(ExecuteTS+' Tiles=('+containerId(i+1)+') '+
                           '/opt/movewindows OpenGL -b toggle,fullscreen')
        client.get_OK()

def launch_changesize(RESOL="1920x1080",tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
    else:
        TilesStr=' Tiles=('+tileId+') '
    COMMAND=ExecuteTS+TilesStr+' xrandr --fb '+RESOL
    print("call server with : "+COMMAND)
    client.send_server(COMMAND)
    print("server answer is "+str(client.get_OK()))

def launch_smallsize(tileNum=-1):
    print("Launch launch_changesize smallsize for tile "+str(tileNum))
    launch_changesize(tileNum=tileNum,RESOL="950x420")

def launch_bigsize(tileNum=-1):
    print("Launch launch_changesize bigsize for tile "+str(tileNum))
    launch_changesize(tileNum=tileNum,RESOL="1920x1200")

def fullscreenApp(windowname="VMD 1.9.2 OpenGL Display",tileNum=-1):
    movewindows(windowname=windowname,wmctrl_option='toggle,fullscreen',tileNum=tileNum)

def showGUI(windowname="VMD Main",tileNum=-1):
    COMMAND='/opt/movewindows '+windowname+' -b '
    movewindows(windowname=windowname,wmctrl_option='toggle,fullscreen',tileNum=tileNum)
    
def movewindows(windowname="VMD 1.9.2 OpenGL Display",wmctrl_option='toggle,fullscreen',tileNum=-1,tileId='001'):
    COMMAND='/opt/movewindows '+windowname+' -b '+wmctrl_option
    #remove,maximized_vert,maximized_horz
    #toggle,above
    if ( tileNum > -1 ):
        TilesStr=' Tiles=('+containerId(tileNum+1)+') '
    else:
        TilesStr=' Tiles=('+tileId+') '
    client.send_server(ExecuteTS+TilesStr+COMMAND)
    client.get_OK()


def kill_all_containers():
    client.send_server(ExecuteTS+' killall Xvnc')
    print("Out of killall command : "+ str(client.get_OK()))
    client.send_server(LaunchTS+" "+COMMANDStop)
    taglist.close()
    client.close()

try:
    print("isActions: "+str(isActions))
except:
    print("isActions not defined.")

#isActions=True
launch_actions_and_interact()

kill_all_containers()

sys.exit(0)

# 0x0140000d  0 935  747  499  147 vmd console
# 0x01800009  0 602  -98  669  834 VMD 1.9.2 OpenGL Display
# 0x01600004  0 6    26   470  190 VMD Main

