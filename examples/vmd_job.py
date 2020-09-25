#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import sys,os,time
import code
import argparse
import re, datetime
import inspect
    
sys.path.append(os.path.realpath('/TiledViz/TVConnections/'))
from connect import sock

import json
    
# HPC Machine working directory
#In TVConnection :
# DATE=re.sub(r'\..*','',datetime.datetime.isoformat(datetime.datetime.now(),sep='_').replace(":","-"))
# TiledVizPath='/login/.tiledviz'
# JOBPath='/login/.tiledviz/VMD_'+DATE

# CASE_NAME in case_config:
#CASE="UREE"
#In TVConnection : TileSet="VMD"
SITE_config='./site_config.ini'
CASE_config="./case_config.ini"

def toggle_fullscr():
    for i in range(NUM_DOCKERS):
        client.send_server('execute TS='+TileSet+' Tiles=('+containerId(i+1)+') '+
                           '/opt/movewindows OpenGL -b toggle,fullscreen')
        client.get_OK()


if __name__ == '__main__':

    actions_file=open("/home/myuser/actions.json",'r')
    tiles_actions=json.load(actions_file)

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
    #print("OPTIONS before replacement : "+str(OPTIONS))

    OPTIONS="".join(list(map( replaceconf,OPTIONS)))
    print("OPTIONS after replacement : "+OPTIONS)
    

    CreateTS='create TS='+TileSet+' Nb='+str(NUM_DOCKERS)

    client.send_server(CreateTS)

    # We must mount CASE directory inside containers :
    # For docker swarm we can mount : "-v $(pwd):/home/myuser/CASE"
    # client.send_server('launch TS='+TileSet+" "+TiledVizPath+" mkdir VMD_"+DATE)
    # print("Out of mkdir VMD : "+ str(client.get_OK()))

    # Build VMD dir
    client.send_server('launch TS='+TileSet+" "+JOBPath+" mkdir "+CASE)
    print("Out of mkdir %s : %s" % (CASE, str(client.get_OK())))
    CASEdir=os.path.join(JOBPath,CASE)

    # get TiledAstrochem package from Github
    os.system("git clone https://github.com/mmancip/TiledAstrochem.git VMD")
    # Untar VMD package
    #("tar xfz VMD.tgz")
    
    command='launch TS='+TileSet+" "+TiledVizPath+" cp -p build_qr "+os.path.join(JOBPath,'..')
    print("cp build_qr : %s" % (command))
    client.send_server(command)
    print("Out of cp build_qr : %s" % (str(client.get_OK())))

    send_file_server(client,TileSet,"VMD","vmd_client",JOBPath)
    send_file_server(client,TileSet,"VMD", "kill_vmd", JOBPath)
    send_file_server(client,TileSet,"VMD", "build_nodes_file", JOBPath)
    send_file_server(client,TileSet,"VMD", "script_vmd_Spezia.py", JOBPath)
    send_file_server(client,TileSet,"VMD", "script_vmd_Spezia.vmd", JOBPath)

    # Send CASE and SITE files
    send_file_server(client,TileSet,".", CASE_config, CASEdir)
    CASE_config=os.path.join(CASEdir,CASE_config)
    send_file_server(client,TileSet,".", SITE_config, JOBPath)
    SITE_config=os.path.join(JOBPath,os.path.basename(SITE_config))
    send_file_server(client,TileSet,".", "tagliste", CASEdir)
    send_file_server(client,TileSet,".", "list_hostsgpu", CASEdir)

    # Launch containers HERE
    REF_CAS=str(NUM_DOCKERS)+" "+DATE+" "+DOCKERSPACE_DIR+" "+DOCKER_NAME

    print("\nREF_CAS : "+REF_CAS)

    COMMANDStop=os.path.join(TILEDOCKERS_path,"stop_dockers")+" "+REF_CAS+" "+os.path.join(CASEdir,GPU_FILE)
    print("\n"+COMMANDStop)

    # Launch dockers
    COMMAND=os.path.join(TILEDOCKERS_path,"launch_dockers")+" "+REF_CAS+" "+GPU_FILE+" "+HTTP_FRONTEND+":"+HTTP_IP+\
             " "+network+" "+nethost+" "+domain+" "+init_IP+" TileSetPort "+UserFront+"@"+Frontend+" "+OPTIONS

    print("\nCommand dockers : "+COMMAND)
    
    taglist = open("tagliste", "r")

    client.send_server('launch TS='+TileSet+" "+CASEdir+' '+COMMAND)
    #code.interact(local=locals())
    print("Out of launch dockers : "+ str(client.get_OK()))

    # TODO : give a liste of lines !
    # tab=taglist.readlines()
    # line=tab[123]
    # file_name=(line[1].split('='))[1].replace('"','')

    # Build nodes.json file from new dockers list
    COMMAND='launch TS='+TileSet+" "+CASEdir+' ../build_nodes_file '+CASE_config+' '+SITE_config
    print("\nCommand dockers : "+COMMAND)

    client.send_server(COMMAND)
    print("Out of build_nodes_file : "+ str(client.get_OK()))
    
    get_file_client(client,TileSet,CASEdir,"nodes.json",".")
    
    # Launch docker tools
    def launch_tunnel():
        client.send_server('execute TS='+TileSet+' /opt/tunnel_ssh '+SOCKETdomain+' '+HTTP_FRONTEND+' '+HTTP_LOGIN)
        print("Out of tunnel_ssh : "+ str(client.get_OK()))
    launch_tunnel()

    def launch_vnc():
        client.send_server('execute TS='+TileSet+' /opt/vnccommand')
        print("Out of vnccommand : "+ str(client.get_OK()))
    launch_vnc()

    def launch_resize(RESOL="1440x900"):
        client.send_server('execute TS='+TileSet+' xrandr --fb '+RESOL)
        print("Out of xrandr : "+ str(client.get_OK()))
    launch_resize()

    def launch_one_client(script='vmd_client',tileNum=-1,tileId='001'):
        line=taglist.readline().split(' ')
        file_name=(line[1].split('='))[1].replace('"','')
        COMMAND=' '+CASE_DOCKER_PATH+script+' '+DATA_PATH_DOCKER+' '+file_name
        if ( tileNum > -1 ):
            TilesStr=' Tiles=('+containerId(tileNum+1)+') '            
        else:
            TilesStr=' Tiles=('+tileId+') '
        print("%d VMD command : %s" % (i,COMMAND))
        CommandTS='execute TS='+TileSet+TilesStr+COMMAND
        client.send_server(CommandTS)
    
        client.get_OK()

    # TODO : give a list of lines !
    for i in range(NUM_DOCKERS):
        launch_one_client(tileNum=i)
    Last_Elt=NUM_DOCKERS-1
    
    def next_element(script='vmd_client',tileNum=-1,tileId='001'):
        line=taglist.readline().split(' ')
        file_name=(line[1].split('='))[1].replace('"','')
        COMMAND=' '+CASE_DOCKER_PATH+script+' '+DATA_PATH_DOCKER+' '+file_name
        COMMANDKill=' '+CASE_DOCKER_PATH+"kill_vmd"
        if ( tileNum > -1 ):
            TilesStr=' Tiles=('+containerId(tileNum+1)+') '
        else:
            TilesStr=' Tiles=('+tileId+') '
        print("%d VMD command : %s" % (i,COMMAND))

        CommandTSK='execute TS='+TileSet+TilesStr+COMMANDKill
        client.send_server(CommandTSK)
        client.get_OK()
        
        CommandTS='execute TS='+TileSet+TilesStr+COMMAND
        client.send_server(CommandTS)
        client.get_OK()

    client.send_server('execute TS='+TileSet+' wmctrl -l -G')
    print("Out of wmctrl : "+ str(client.get_OK()))

    def launch_changesize(RESOL="1920x1080",tileNum=-1,tileId='001'):
        if ( tileNum > -1 ):
            TilesStr=' Tiles=('+containerId(tileNum+1)+') '
        else:
            TilesStr=' Tiles=('+tileId+') '
        COMMAND='execute TS='+TileSet+TilesStr+' xrandr --fb '+RESOL
        print("call server with : "+COMMAND)
        client.send_server(COMMAND)
        print("server answer is "+str(client.get_OK()))
    
    def launch_smallsize(tileNum=-1,tileId='001'):
        print("Launch launch_changesize smallsize for tile "+str(tileNum))
        launch_changesize(tileNum=tileNum,RESOL="950x420")

    def launch_bigsize(tileNum=-1,tileId='001'):
        print("Launch launch_changesize bigsize for tile "+str(tileNum))
        launch_changesize(tileNum=tileNum,RESOL="1920x1200")

    def fullscreenApp(windowname="VMD 1.9.2 OpenGL Display",tileNum=-1):
        movewindows(windowname=windowname,wmctrl_option='toggle,fullscreen',tileNum=tileNum)

    def movewindows(windowname="VMD 1.9.2 OpenGL Display",wmctrl_option='toggle,fullscreen',tileNum=-1,tileId='001'):
        #remove,maximized_vert,maximized_horz
        #toggle,above
        #movewindows(windowname='glxgears',wmctrl_option="toggle,fullscreen",tileNum=2)
        if ( tileNum > -1 ):
            TilesStr=' Tiles=('+containerId(tileNum+1)+') '
        else:
            TilesStr=' Tiles=('+tileId+') '
        client.send_server('execute TS='+TileSet+TilesStr+'/opt/movewindows '+windowname+' -b '+wmctrl_option)
        client.get_OK()

    def kill_all_containers():
        client.send_server('execute TS='+TileSet+' killall Xvnc')
        print("Out of killall command : "+ str(client.get_OK()))
        client.send_server('launch TS='+TileSet+" "+JOBPath+" "+COMMANDStop)
        client.close()

    # Launch Server for commands from FlaskDock
    print("GetActions=ClientAction("+str(connectionId)+",globals=dict(globals()),locals=dict(**locals()))")
    sys.stdout.flush()

    try:
        GetActions=ClientAction(connectionId,globals=dict(globals()),locals=dict(**locals()))
        outHandler.flush()
    except:
        traceback.print_exc(file=sys.stdout)
        code.interact(banner="Error ClientAction :",local=dict(globals(), **locals()))

    print("Actions \n",str(tiles_actions))

    try:
        code.interact(banner="Code interact :",local=dict(globals(), **locals()))
    except SystemExit:
        pass
    
    client.send_server('execute TS='+TileSet+' killall Xvnc')
    print("Out of killall command : "+ str(client.get_OK()))

    client.send_server('launch TS='+TileSet+" "+JOBPath+" "+COMMANDStop)
    taglist.close()
    client.close()
    sys.exit(0)

    # 0x0140000d  0 935  747  499  147 vmd console
    # 0x01800009  0 602  -98  669  834 VMD 1.9.2 OpenGL Display
    # 0x01600004  0 6    26   470  190 VMD Main

