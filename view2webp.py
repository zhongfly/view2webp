#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import re
import requests
import sys

try:
    workDir=os.path.expanduser(sys.argv[1])
except:
    workDir=os.getcwd()

def getComicDetail(id):
    url = "https://manga.bilibili.com/twirp/comic.v2.Comic/ComicDetail"
    payload = "device=android&comic_id="+str(id)
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'user-agent': "Mozilla/5.0 BiliComic/1.9.0",
        'Host': "manga.bilibili.com",
        'cache-control': "no-cache"
    }
    r = requests.post(url, data=payload, headers=headers)
    if r.status_code == requests.codes.ok:
        try:
            data = r.json()
            return data['data']
        except Exception as e:
            print(e)
    else:
        print(f"getComicDetail fail,id={id},{r.status_code}")
    return 0


def getEpDict(ep_list):
    epDict = {}
    for ep in ep_list:
        epDict[str(ep['id'])] = ep['short_title']
    return epDict


def getpicDict(comicId, episodeId, indexDataFile):
    json_file = os.path.join(indexDataFile)
    picData = json.load(open(json_file))
    picDict = {}
    n = 1
    for pic in picData:
        picName = os.path.basename(pic['path']).replace('.png', '.png.view').replace('.jpg','.jpg.view')
        picDict[picName] = str(n)+os.path.splitext(pic['path'])[-1]
        n = n+1
    return picDict


def view2webp(file):
    with open(file, 'rb') as f:
        data = f.read()
    with open(file, 'wb') as f:
        f.write(data[9:])


def main():
    comics = [entry.path for entry in os.scandir(
        workDir) if entry.is_dir() and re.match(r'\d+$', entry.name) != None]
    for comic in comics:
        folderName = os.path.basename(comic)
        detail = getComicDetail(folderName)
        name = detail['title']
        epDict = getEpDict(detail['ep_list'])

        epDirs = [entry.path for entry in os.scandir(
            comic) if entry.is_dir() and re.match(r'\d+$', entry.name) != None]
        for ep in epDirs:
            path = ep
            fileList = [entry.path for entry in os.scandir(
                path) if entry.name.endswith(".view")]
            filePath = sorted(fileList,  key=lambda x: os.path.getmtime(x))

            if os.path.exists(os.path.join(path, 'int', 'index.dat')):
                indexDataFile = os.path.join(path, 'int', 'index.dat')
                comicId = folderName
                episodeId = os.path.basename(ep)
                picDict = getpicDict(comicId, episodeId, indexDataFile)
            else:
                picDict = False

            n = 1
            for file in filePath:
                view2webp(file)
                if picDict != False:
                    newName = picDict[os.path.basename(file)]
                    newPath = os.path.join(os.path.dirname(file), newName)
                else:
                    newPath = os.path.join(os.path.dirname(file), (f"{n}"+os.path.splitext(file.replace('.view', ''))[-1]).zfill(7))
                os.rename(file, newPath)
                n = n+1

            epName = epDict[os.path.basename(ep)]
            newPath = os.path.join(os.path.dirname(ep), epName)
            try:
                os.rename(ep, newPath)
            except OSError as e:
                os.rename(ep, newPath+os.path.basename(ep))
            print(f"{epName} has done")

        newPath = os.path.join(workDir, name)
        os.rename(comic, newPath)
        print(f"{name} completed\n")


if __name__ == '__main__':
    main()
