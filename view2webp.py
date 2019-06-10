# encoding:UTF-8
# python3.6

import os
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
			data=r.json()
			return data['data']
		except Exception as e:
			print(e)
	else:
		print(f"getComicDetail fail,id={id},{r.status_code}")
	return 0

def getEpDict(ep_list):
	epDict={}
	for ep in ep_list:
		epDict[str(ep['id'])]=ep['short_title']
	return epDict

def view2webp(file):
	with open(file,'rb') as f:
		data=f.read()
	with open(file,'wb') as f:
		f.write(data[9:])

def main():
	comics=[entry.path for entry in os.scandir(workDir) if entry.is_dir() and re.match(r'\d+$',entry.name) != None]
	for comic in comics:
		folderName=os.path.basename(comic)
		detail=getComicDetail(folderName)
		name=detail['title']
		epDict=getEpDict(detail['ep_list'])

		epDirs=[entry.path for entry in os.scandir(comic) if entry.is_dir() and re.match(r'\d+$',entry.name) != None]
		for ep in epDirs:
			dirs=[entry.path for entry in os.scandir(ep) if entry.is_dir()]
			if len(dirs)<1:
				path=ep
			else:
				path=dirs[0]
			fileList = [entry.path for entry in os.scandir(path) if entry.name.endswith("jpg.view")]
			filePath = sorted(fileList,  key=lambda x: os.path.getmtime(x))
			n=1
			for file in filePath:
				view2webp(file)
				newPath=os.path.join(os.path.dirname(file),f"{n}.webp".zfill(7))
				os.rename(file,newPath)
				n=n+1
			epName=epDict[os.path.basename(ep)]
			newPath=os.path.join(os.path.dirname(ep),epName)
			os.rename(ep,newPath)

		newPath=os.path.join(workDir,name)
		os.rename(comic,newPath)
		

if __name__ == '__main__':
	main()