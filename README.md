# My_ansible
## 适用版本 UNIX
### Python 3.6
### 一个类型于简易版本的Ansible
### 基于concurrent模块开启多线程;远程连接是基于paramiko模块编写
### 启动文件在bin目录下
### 在这之前请先编辑conf目录下的host.conf文件,把您需要的远程批量执行命令的主机信息等填写好. 当然,也提供了组的方式,但是组内的组机还是单独要在定义组机时定义一次.
### 您可以执行python start_asd.py -h 来查看具体参数命令

参数介绍(-s与-g参数都需提前在host.conf里定义好)

> -s  [虚拟主机名称]          远程主机,多个可以逗号分开

> -g  [组名称]               如果在host.conf文件里定义了组名称,即为组内

> -cmd       [cmd]             需要批量执行的命令

> -action   [put][get]      现指支持上传'put' 与下载 'get' 

> -local    [filename]      需要上传或下载的文件名

> -remoet   [filename]      需要操作远程服务器的文件名称  (注意:此处建议为绝对路径的文件名字)

示例:

#远程批量上传文件

  python3 start_asd.py -s cy -g WebServer -action put -local Install.py -remote /App/bin
  
#批量查看主机磁盘信息

  python3 start_asd.py -s cy,Soar -gWebServer,FortServer -cmd "df -h"


