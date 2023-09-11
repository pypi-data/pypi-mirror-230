# Enflame Jfrog Downloader

## 介绍

- 第一次使用时引导token配置到`/home目录`，后续无论docker内外都无需重复配置，新起docker后只需`pip install efjdown`
- 支持文件和目录的下载，完全同步目录树，自动跳过上级目录和空文件夹
- 支持全局命令调用
- 支持Python导入使用
- 添加 -l参数下载完毕后支持打印目录树与文件大小
- ERROR后面都跟着HINT提示以方便快速解决问题

## 原理

通过携带header方式直接访问jfrog的HTTP接口，通过正则表达式取出所有a标签中的链接，如果是目录就递归调用，规避上级目录链接，以此实现了同步整个目录下载的功能。

## 安装

直接 `pip install efjdown` 就好了,然后在任何地方shell 输入`efjdown`即可使用。![d](/Users/liangdong/Library/Application Support/typora-user-images/截屏2023-09-10 02.59.19.png)

**文件：**

```shell
 efjdown -u https://art.xxxxx.com/blabla.xx. -p `保存路径不要写文件名`
```

**目录** 

```shell
efjdown -u https://art.xxxxx.com/blabla/ -p `保存父目录的名字，不写就是同步原父目录名`
```

**第一次使用会出现以下提示**

**![截屏2023-09-10 03.25.08](/Users/liangdong/Library/Application Support/typora-user-images/截屏2023-09-10 03.25.08.png)**

直接把公共账号的token 粘贴到这回车即可，带不带前缀那个Bearer  都行，代码里做了宽容。

然后就已经开始正常下载了。

下载完毕后会出现FileTree以遍核对目录的正确性和文件的大小 （前提是带了-l (--list)，没有做成默认是因为信息多，有些打扰）

![截屏2023-09-10 03.37.57](/Users/liangdong/Library/Application Support/typora-user-images/截屏2023-09-10 03.37.57.png)

## 环境和依赖

- Python >= 3.6 ｜应该不比这个低都能用
- pip3 ｜buildtools
- re ｜正则取<a>标签
- requests | http请求库
- loguru ｜log分级打印
- tqdm ｜进度条

## CLI调用

可以通过配置文件配置token，在CLI第一次运行时，会检测本地有没有配置文件，没有的话会引导创建

如果有现成的配置文件，就直接执行下载，但是判断到403的权限错误的话，会提示错误，并引导重建配置
为了支持测试环境，也支持 shell中 -t + token的方式，但是这种方式不会保存token，只会在这次调用中生效。
举个例子

```shell
efjdown -u https://art.xxxxx.com/blabla.xx. -p 保存路径不要写文件名 -t token
```



## 导入引用

```python
import efjdown
# 下载单个文件
efjdown.download_file(url="file.url",save_path="/path/you/want/save",save_name="不写这个参数就是原名字")
# 下载整个目录
efjdown.download_dir(url="dir.url",save_path="/path/you/want/save",save_name="不写这个参数就是原名字")
```

## 更换Token

直接输入` efjdown -c` 即可删除配置文件，然后可以重新配置

![截屏2023-09-10 03.23.18](/Users/liangdong/Library/Application Support/typora-user-images/截屏2023-09-10 03.23.18.png)

## 错误定位

404：一般是没权限或者url给的不对，也有可能这个资源点的文件已经被删除

403：登录的token错误或无权访问该资源

5xx：内部服务错误，先手动试试可以访问不

‼️下载单文件的时候，路径直接写到保存的dir，不要写到文件名，‼️否则会在创建一个文件名同名的文件夹

❌ -p /path/you/want/save/file.onnx

✅ -p /path/you/want/save/