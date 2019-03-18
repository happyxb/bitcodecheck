#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re

def removefile(filepath):
    os.popen("rm -rf '{}'".format(filepath))

def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize/float(1024*1024)
    return str(round(fsize,2))

def isBitcode(filepath, archs):
    result = False
    if '.framework' in filepath and 'arm64' in archs:
        thinname = filepath + "-arm64"
        os.popen("lipo '{}' -thin arm64 -output '{}'".format(filepath, thinname))
        info = os.popen("otool -l '{}' | grep LLVM".format(thinname)).read()
        # print("otool info:", info)
        removefile(thinname)
        if info != None and len(info) > 0:
            result = True
    if '.a' in filepath and 'arm64' in archs:
        thinname = filepath + "-arm64"
        os.popen("lipo '{}' -thin arm64 -output '{}'".format(filepath, thinname))
        info = os.popen("otool -l '{}' | grep bitcode".format(thinname)).read()
        # print("otool info:", info)
        removefile(thinname)
        if info != None and len(info) > 0:
            result = True
    return result

def lipoinfo(libname, filepath):
   # print(filepath)
   if '-arm64' in filepath:
        return
   info = os.popen("lipo -info '{}'".format(filepath)).read()
   infosplit = info.split(': ')
   archs = infosplit[-1]
   # print(archs)
   archs = archs.strip().replace(' ', ',')
   isBitcodeValue = isBitcode(filepath, archs)
   filesize = get_FileSize(filepath)
   relpath = os.path.relpath(filepath, os.curdir)
   print('{} {} {} {} {}'.format(libname,isBitcodeValue,archs, filesize + 'MB',relpath))

def searchfile(rootDir, filename):
    if os.path.islink(rootDir):
        return None
    result = None
    for lists in os.listdir(rootDir):
        path = os.path.join(rootDir, lists)
        if os.path.isdir(path):
            dirresult = searchfile(path, filename)
            if dirresult != None:
                result = dirresult
        elif os.path.isfile(path) and lists == filename:
            result = path
    return result

def search(rootDir):
    for lists in os.listdir(rootDir):
        path = os.path.join(rootDir, lists)
        if os.path.isdir(path):
            if ".framework" in lists:
                name = lists[:-10]
                filepath = searchfile(path, name)
                lipoinfo(lists,filepath)
            else:
                search(path)
        elif os.path.isfile(path):
            if ".a" in lists:
                lipoinfo(lists,path)

print('libname  isBitcode  archs libsize filepath')
curdir = os.path.abspath('.')
search(curdir)
