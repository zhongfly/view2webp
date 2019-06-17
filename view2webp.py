# encoding:UTF-8
# python3.6
import os
import io
import json
import zipfile
import re
import requests

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
    def unzip(file, target_dir):
        obj = zipfile.ZipFile(file)
        obj.extractall(target_dir)

    def generateHashKey(comicId, episodeId):
        n = [None for i in range(8)]
        e = int(comicId)
        t = int(episodeId)
        n[0] = t
        n[1] = t >> 8
        n[2] = t >> 16
        n[3] = t >> 24
        n[4] = e
        n[5] = e >> 8
        n[6] = e >> 16
        n[7] = e >> 24
        for idx in range(8):
            n[idx] = n[idx] % 256
        return n

    def unhashContent(hashKey, indexData):
        for idx in range(len(indexData)):
            indexData[idx] ^= hashKey[idx % 8]
        return bytes(indexData)

    key = generateHashKey(comicId, episodeId)
    with open(indexDataFile, 'rb') as f:
        indexData = f.read()
        indexData = list(indexData)[9:]
    indexData = unhashContent(hashKey=key, indexData=indexData)
    file = io.BytesIO(indexData)
    unzip(file, os.path.dirname(indexDataFile))
    json_file = os.path.join(indexDataFile)
    picData = json.load(open(json_file))["pics"]
    picDict = {}
    n = 1
    for pic in picData:
        picName = os.path.basename(pic).replace('.jpg', '.jpg.view')
        picDict[picName] = str(n)+'.webp'
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
            dirs = [entry.path for entry in os.scandir(ep) if entry.is_dir()]
            if len(dirs) < 1:
                path = ep
            else:
                path = dirs[0]
            fileList = [entry.path for entry in os.scandir(
                path) if entry.name.endswith("jpg.view")]
            filePath = sorted(fileList,  key=lambda x: os.path.getmtime(x))

            if os.path.exists(os.path.join(path, 'index.dat')):
                indexDataFile = os.path.join(path, 'index.dat')
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
                    newPath = os.path.join(os.path.dirname(file), f"{n}.webp".zfill(7))
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
