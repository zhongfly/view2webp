# view2webp
covert .view(from bilibili manga) to webp

## 主要原理

删除缓存图片文件的前9个字节

## 使用说明

将android手机中哔哩哔哩漫画的缓存文件夹（文件夹名为5位数字）复制到项目文件夹内，在联网状态下运行代码即可

***建议使用哔哩哔哩漫画app中的“缓存”功能下载漫画***，只有这样才可以保证图片顺序正确，下载的缓存保存在安卓手机`/storage/emulated/0/data/bilibili/comic/down`文件夹下，每个文件夹为一部漫画。

执行后将以漫画名/章节名 重命名 各级文件夹（当出现重复章节名时自动重命名为 章节名+章节数字id），并按文件修改顺序对漫画图片进行排序（可能并不准确）

图片重命名逻辑：

1，当文件夹下不存在index.dat时，按文件修改顺序排序命名（大多情况下顺序并不正确）

2，当文件夹下存在index.dat文件（使用哔哩哔哩漫画app中的“缓存”功能下载的漫画时会有此文件），解密为json文件，使得图片可以得到正确的按照顺序重命名
。此段代码来自[@lossme](https://github.com/lossme/TencentComicBook/blob/master/onepiece/site/bilibili.py）)
