#!/usr/bin/python3
import sys as _hidden_sys

_hidden_sys.path.append("/home/pi/vid-base/G2D/RestrictedPython-5.0/src")
_hidden_sys.path.append("/home/pi/vid-base/G2D/cairo")

from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals
from RestrictedPython.Guards import safe_builtins
from RestrictedPython.PrintCollector import PrintCollector

import cairo
from math import *
import random
import numpy as np
from colorsys import hsv_to_rgb
from colorsys import rgb_to_hsv
import sys

#linting code
import ast, traceback
import platform
if platform.processor() == "x86_64":
    sys.path.append("./G2D/x86")
else:
    sys.path.append("./G2D/arm")
import G2Dbase as STR
STR.Init();

surface = cairo.ImageSurface.create_for_data(STR.GetImgPtr(),cairo.FORMAT_ARGB32,320,240);

cr = cairo.Context(surface)

STR.GiveHostAccess()
class glbData:
   pass

GLB = glbData()

allowedObjects = [type(x).__name__ for x in [GLB,cr,STR]]

_print_ = PrintCollector

#helper functions for restricted python
def _write_(o):
   if type(o).__name__ in allowedObjects:
           return o
   else:
      print("_WRITE_:"+str(o))
      raise 

def _getattr_(o,m):
   if type(o).__name__ in allowedObjects:
           return o
   else:
      print("_GETATTR_:"+str(o))
      raise 
  


# Default program for when the program loaded isn't working or is too slow
def DefProgram():
   global Init
   global Render

   def Init():
      STR.ResetFParamNames()


   def Render(cr):
      # ---- clear screen
      cr.set_source_rgba(0,0,0,1)
      cr.rectangle(0,0,320,240)
      cr.fill()
      cr.set_source_rgba(1,1,1,1)
      cr.set_line_width(3)
      cr.move_to(0,0)
      cr.line_to(320,240)
      cr.move_to(0,240)
      cr.line_to(320,0)
      o = 40
      oh = o*(3/4)
      cr.rectangle(160-o,120-oh,o*2,oh*2)
      o = 100
      oh = o*(3/4)
      cr.rectangle(160-o,120-oh,o*2,oh*2)
      cr.stroke()


safe_globals['GLB'] = GLB
safe_globals['STR'] = STR
safe_globals['cr']  = cr

DefProgram()
Init()

cr.save()
cr.set_source_rgb(0,0,0)
cr.rectangle(0,0,320,240)
surface.flush()
cr.restore()

run = True

def ResetScreen():
   cr.set_source_rgba(0,0,0,1)
   cr.rectangle(0,0,320,240)
   cr.fill()

while(run):
   STR.WaitHostAccess()

   cmd = STR.CheckCmd()
   if cmd == "load":
      fname = STR.GetPgmFile()
      # TODO LOAD STUFF (LINT FILE)
      if fname == "":
         valid = False
         DefProgram()
         GLB = glbData()
         ResetScreen()
         Init()
      else:
         with open(fname) as f:
            source = f.read()
         valid = True
         try:
            ast.parse(source)
         except SyntaxError as ex:
            print("%s"%(ex))
            valid = False
            DefProgram()
            GLB = glbData()
            ResetScreen()
            Init()
            STR.SendPgmFail("syntax error")
         if valid:
            # Now we will try to exec first with restrictions and if that passes, exec into the namespace
            try:
               byte_code = compile_restricted(source,'<inline>','exec') 
               exec(byte_code,safe_globals,{})
            except Exception as e:
               print("ERROR:"+str(e))
               valid = False
               DefProgram()
               GLB = glbData()
               ResetScreen()
               Init()
               STR.SendPgmFail("unallowed code")
            if valid:
               exec(source)
               GLB = glbData()
               STR.ResetFParamNames()
               ResetScreen()
               Init()
   elif cmd == "init":
      GLB = glbData()
      ResetScreen()
      Init()
   if cmd == "exit":
      run = False

   cr.save()
   Render(cr)
   cr.restore()
   surface.flush()
   STR.GiveHostAccess()

