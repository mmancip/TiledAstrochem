#!/usr/bin/env python
# coding: utf-8

import os
os.getcwd()

os.chdir('/home/myuser/.vnc/')
os.getcwd()

from vmd import VMDevaltcl

countcolor="white"

# LENGTH=128


# import socket
# import threading, time
# import sys
# sys.setcheckinterval(1)

# class ClientThread(threading.Thread):

#     def __init__(self, ip, port, clientsocket):

#         threading.Thread.__init__(self)
#         self.ip = ip
#         self.port = port
#         self.clientsocket = clientsocket
#         print("init : [+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

#     def run(self): 
#         global rlock
#         print("run : Connection from client %s %s" % (self.ip, self.port, ))

#         while True:
#             time.sleep(0.1)
#             sys.stdout.flush()
#             r = self.clientsocket.recv(LENGTH)
# #            rlock.acquire(blocking=0)
#             strrecv=r.decode("UTF-8")
#             print('run : Message : |'+ strrecv+'|')
#             try:
#                 exec(strrecv)
#             except Exception:
#                 print "can't exec "+strrecv

#             strsocket= 'Message from server : received '+strrecv
#             self.clientsocket.send(strsocket)
#             rlock.release()

#             if ( strrecv == "closesocket" ):
#                 self.clientsocket.close()
#                 tcpsock.close()
#                 print('Client deconnected...')
#                 break



# tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# tcpsock.bind(("",15555))
# tcpsock.listen(1)

# (clientsocket, (ip, port)) = tcpsock.accept()

# rlock=threading.RLock()

# newthread = ClientThread(ip, port, clientsocket)
# newthread.start()

VMDevaltcl("source script_vmd_Spezia.vmd")
# VMDevaltcl('source do_bubble.tcl')
# VMDevaltcl('do_bubble')

import trans
# trans.rotate('x',90)

# use android vmd 
VMDevaltcl("mobile mode move")

# # en secondes
# AnimateSpeed=0.5

# from Molecule import *
import molecule, animate, display, graphics, atomsel, vmdcallbacks, axes
axes.set_location(axes.OFF)
#axes.set_location(axes.ORIGIN)


def ini():
    mol0=molecule.listall()[0]
    nframe=molecule.numframes(mol0)

    trans.resetview(mol0)

    #name0=molecule.name(mol0)
    all0=atomsel.atomsel("all")

    (min0,max0)=all0.minmax()
    print 'molecule min/max :',min0,max0

    #coords=((min0[0]+max0[0])/2,min0[1]+(max0[1]-min0[1])/4,(min0[2]+max0[2])/2)
    coords=((min0[0]+max0[0])/2,(min0[1]+max0[1])/2-(max0[1]-min0[1]),(max0[2]+min0[2])/2)
    print "coords : ",coords

    frame=molecule.get_frame(mol0)
    print("frame = ",frame)
    ListG=graphics.listall(mol0)
    if( len(ListG) > 1):
	 idcolor=ListG[0]
	 idtext=ListG[1]
         graphics.delete(mol0,idcolor)
         graphics.delete(mol0,idtext)
    graphics.color(mol0,countcolor)
    idtext=graphics.text(mol0,coords,str(frame),size=2.0)
    #graphics.delete(mol0,idtext)

    selN=atomsel.atomsel("name N and user > 0")
    coordsNold=(selN.get('x')[0],selN.get('y')[0],selN.get('z')[0]) 
    #print 'initial coords :',coordsNold

    coords=(coordsNold[0],coordsNold[1]-(max0[1]-min0[1]),coordsNold[2])
    #print "coords 1 : ",coords

    axes.set_location(axes.LOWERLEFT)
    #rans.resetview(mol0)
    
    #trans.translate(coordsNold[0],coordsNold[1],coordsNold[2])
    scaleN=trans.get_scale(mol0)*1.4
    trans.set_scale(mol0,scaleN)
    trans.translate(-coordsNold[0]*scaleN,
                     -coordsNold[1]*scaleN,
                     -coordsNold[2]*scaleN)
    return (mol0, nframe, selN, all0, min0,max0, frame, coords, coordsNold, scaleN)

(mol0, nframe, selN, all0, min0,max0, frame, coords, coordsNold, scaleN) = ini()

#VMDevaltcl("save_viewpoint; puts $viewpoints(0)")
#VMDevaltcl("puts $viewpoints(1)")

display.update()

import time
import os
#mytimestart=os.getenv('mytimestart')
# t = time.strftime("%m%d%H%M",time.localtime())
# while ( int(t) < int(mytimestart) ):
#     time.sleep(1)
#     t = time.strftime("%m%d%H%M",time.localtime())


def callback_frame(mol0,frame):
    global coordsNold
    ListG=graphics.listall(mol0)
    if( len(ListG) > 0):
	 idtext=ListG[1]
         graphics.delete(mol0,idtext)
    #print("frame = ",frame)
    #graphics.color(mol0,'white')

    #(min1,max1)=selN.minmax()
    #coords=((min1[0]+max1[0])/2,min1[1]+(max1[1]-min1[1])/4,(min1[2]+max1[2])/2)
    #coords=((min1[0]+max1[0])/2,(min1[1]+max1[1])/2,min1[2]+(max1[2]-min1[2])/8)
    #print 'frame min/max :',min1,max1

    coordsN=(selN.get('x')[0],selN.get('y')[0],selN.get('z')[0])
    coords=(coordsN[0],coordsN[1]-(max0[1]-min0[1]),coordsN[2])
    #print "coords 1 : ",coords
    idtext=graphics.text(mol0,coords,str(frame),size=2.0)
    #time.sleep(AnimateSpeed) 
    #trans.resetview(mol0)
    #print frame,": ",coordsN
    trans.translate((coordsNold[0]-coordsN[0])*scaleN,
                    (coordsNold[1]-coordsN[1])*scaleN,
                    (coordsNold[2]-coordsN[2])*scaleN)
    #VMDevaltcl("trans origin {"+str(coordsN[0])+" "+str(coordsN[1])+" "+str(coordsN[2])+"}")
    #trans.resetview(mol0)
    #VMDevaltcl("save_viewpoint; puts $viewpoints(0)")

    coordsNold=coordsN

#VMDevaltcl("set move_sel [atomselect 0 \"all\"]; $move_sel move $transformation_mat")

vmdcallbacks.add_callback("frame",callback_frame)

#animate.forward()


# while True:
#     r = clientsocket.recv(LENGTH)
#     strrecv=r.decode("UTF-8")
#     print("run : Reception du messaged: |", strrecv, "|")
#     try:
#         eval(strrecv)
#     except Exception:
#         print "can't eval "+strrecv
    
#     strsocket= u'Message from server : received '+strrecv
#     clientsocket.send(strsocket)

#     if ( strrecv == "closesocket" ):
#         clientsocket.close()
#         tcpsock.close()
#         print("Client deconnecté...")
#         break



# class ServerThread(threading.Thread):

#     def __init__(self):
#         threading.Thread.__init__(self)
#         print("Server thread.")
#         #while True:
#         (clientsocket, (ip, port)) = tcpsock.accept()
#         newthread = ClientThread(ip, port, clientsocket)
#         newthread.start()
#         #    break
#     def run(self):
#         print( "En ecoute...")

# newserverthread = ServerThread()
# newserverthread.start()
