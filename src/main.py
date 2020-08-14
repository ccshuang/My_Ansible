#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17/11/17 23:25
# @Author  : Tiancc
# @Site    :
# @File    : main.py
# @Software: PyCharm


import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse,configparser,paramiko
from concurrent.futures import ThreadPoolExecutor
from conf import settings
from data import ErrorMessage as em

hostnum = []
class Asd(object):
    '''
    这是一个类似'Ansible'工具,但是只支持上传下载文件,与一部分bash命令
    '''

    def __init__(self,**kwargs):
        parser = argparse.ArgumentParser(description='This is a similar Ansible program, but it is not finished yet. Please contact me if you have any questions. Please contact me at tcc.soar@gmail.com')
        parser.add_argument('-s', '--server',action='store', help="Specify host IP or Hostname. Can't be empty!")   #default='localhost'
        parser.add_argument('-g', '--group', help='Specify host groups')
        parser.add_argument('-cmd', help='The command to send to a remote server')
        parser.add_argument('-action', help='The operation to be performed')
        parser.add_argument('-local', help='The absolute path of the local server file')
        parser.add_argument('-remote', help='Batch delete directory')
        self.args = parser.parse_args()
        self.help = parser.print_help
        self.private_key = paramiko.RSAKey.from_private_key_file(r'/root/.ssh/talk_rsa.tiancc','youPassword')
        #self.private_key = paramiko.RSAKey.from_private_key_file(r'/root/.ssh/talk_rsa.tiancc','youPassword')
        #self.private_key = paramiko.RSAKey.from_private_key_file(r'/root/.ssh/id_rsa.bsy')
        #self.private_key = paramiko.RSAKey.from_private_key_file(r'/root/.ssh/ks_server_root')
        #self.private_key = paramiko.RSAKey.from_private_key_file(r'/root/.ssh/tk_server_root')

        '''
        加载用户配置信息
        '''
        self.config = configparser.ConfigParser()
        self.config.read(settings.HOST_CONF)

        try:
            if kwargs['server'] :
                self.args.server = kwargs['server']
        except:
            pass


        try:
            # if kwargs['server']:
            #     self.args.server = kwargs['server']
            if kwargs['group'] :
                self.args.group = kwargs['group']
        except:
            pass

        try:
            if kwargs['cmd']:
                self.args.cmd =  kwargs['cmd']
        except:
            pass

        try:
             if kwargs['action']:
                 self.args.action = kwargs['action']
                 self.args.local = kwargs['local']
                 self.args.remote = kwargs['remote']
        except:
            pass
        '''
        得到去重后的用户列表;如果指定了组,组内的用户已通过了验证
        '''

        user_list = self.auth()

        '''
        筛选过的用户列表传给多线程执行对象
        '''
        result_list = self.allo_Thread(user_list)
        # print(user_list,'OK')

        for result in result_list:  # 等所有子进程都执行完毕后再`result()`取出
            # print('>>*10',result.result()[1])
            # print('##'*20,result.result()[1])
            # print(result.result()[0])
            try:
                # print('8888',len(result.result()))
                # print('##'*10,result.result()[2],result.result()[1])
                print('\033[32m##'*10,'\033[1;32m%s %s\033[0m'%(result.result()[1],result.result()[2]))
                print('\033[37m %s\033[0m'%result.result()[0])
                # print('3333',result.result()[2])
            except:
                pass


    def auth(self):
        '''
        判读用户输入的合法性,并去重算出共有几台设备.此处没有验证单个主机(-s)是否存在于配置文件,但是验证了群组.(遗留问题:群主名称不分大小写?)
        '''
        user_lsit = []
        if not self.args.server is None:
            user = (self.args.server).split(',')
            user_lsit.extend(user)
            # users = len(user)
        elif self.args.group is None and self.args.server is None:
            self.help()                  # 如果主机为空,并且主机群组也为空,直接退出程序
            print(em.EM.get('1'))
            exit()
        if not self.args.group is None:
            try:
                guser = self.config.get('GROUPS', self.args.group).split(',')
            except configparser.NoOptionError:
                print(em.EM.get('1'))
                exit()
            user_lsit.extend(guser)
        if self.args.cmd is None and self.args.action is None:
            self.help()
            exit()
        user_lsit = list(set(user_lsit))
        return user_lsit

    def parameter(self):
        '''
        确认用户输入的命令类型并反射给相应对象执行,但如果是上传下载命令则在返回给manager对象
        :return:
        '''
        # if not self.args.cmd is None:
        #     self.cmd()
        #     return
        # elif self.args.action is None and self.args.local is None and self.args.remote is None:
        #
        # list = [self.args.action,self.args.cmd,self.args.local,self.args.remote]
        # for comm in list:
        #     if hasattr(self,comm):
        #         return getattr(self,comm)
        #     else:
        #         print(em.EM.get('2'))
        #         exit()

        if not self.args.cmd is None:
            return self.cmd(self.args.cmd)
        if not self.args.action is None:
            return self.args.action

    def allo_Thread(self,users):
        '''
        开启多线程来执行任务
        :param users: 需要批量执行的用户
        :return: 所有用户执行的结果
        '''
        result_list = []
        Thread = ThreadPoolExecutor(20)
        # print('2222', users)
        for user in users:
            result_list.append(Thread.submit(self.manager,user))

        Thread.shutdown(wait=True)
        # print('11111',result_list)
        return result_list

    def manager(self,user):

        #_ip = self.config.get(user,'ip')
        #_port = self.config.get(user,'port')
        #_user = self.config.get(user,'user')
        #_pasd = self.config.get(user,'pasd')
        #_cmd = self.parameter()

        try:
            _ip = self.config.get(user,'ip')
            _port = self.config.get(user,'port')
            _user = self.config.get(user,'user')
            _pasd = self.config.get(user,'pasd')

        except configparser.NoOptionError as e:
            _port = '22'
            _user = 'root'
            _pasd = ''
            #print(e)
        _cmd = self.parameter()
        # if self.args.action == 'put':
        #     res = self._put(_ip,_port,_user,_pasd)
        #     return res
        if not self.args.action is None:
            res = self.action(_ip,_port,_user,_pasd,_cmd,user)
            return res
        else:
            res = self.ssh(_ip,_port,_user,_pasd,_cmd,user)
            return res

    def ssh(self,IP,Port,User,Passd,Cmd,Hostname):
        '''
        用户创建远程连接,并执行命令,得到返回结果
        :return: 命令执行的结果
        '''
        '''
        创建SSH对象
        允许连接不在know_hosts文件中的主机
        连接服务器
        '''

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #ssh.connect(hostname=IP, port=Port, username=User, password=Passd,pkey=private_key)
        #private_key = paramiko.RSAKey.from_private_key_file(r'/home/users/tiancc/.ssh/talk_rsa.tiancc','youPassword')
        #ssh.connect(hostname=IP, port=Port, username=User, password=Passd,pkey=private_key)
        ssh.connect(hostname=IP, port=Port, username=User, password=Passd,pkey=self.private_key)

        '''
        执行命令
        得到命令结果并反馈出去
        关闭连接
        '''
        stdin, stdout, stderr = ssh.exec_command(Cmd)
        result = stdout.read()
        return result.decode('utf-8'),IP,Hostname
        ssh.close()

    def action(self,i,p,u,pd,comm,hostname):
        '''
        展示闲置的...
        :param comm:
        :return:
        '''
        if hasattr(self,'_%s'%comm):
            # print('ccc',len(set(hostnum)))
            return getattr(self,'_%s'%comm)(i,p,u,pd,hostname)
        else:print('-bash: {}: {}'.format(comm,em.EM.get('3')))

    def cmd(self,comm):
        return comm

    def _put(self,IP,Port,User,Pasd,hostname):

        dir_res = self.remote()
        fil_res = self.local()

        transport = paramiko.Transport((IP, int(Port)))
        transport.connect(username=User, password=Pasd, pkey=self.private_key)
        #transport.connect(username=User, password=Pasd)

        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.put(fil_res, dir_res)
        except OSError:
            print('[%s] 输入有误!\n请确定远程主机存在此文件夹或确定输入文件名! 例: "/tmp/test.py"'%dir_res)
            exit()
        finally:
            transport.close()
        hostnum.append(hostname)
        print('\033[1;32m%s 向主机"%s"上传%s文件成功\033[0m'%(len(hostnum),hostname,dir_res))
        # print(len(set(hostnum)))
        # obj=print('向主机%s(%s)上传[%s]文件成功!'%(hostname,IP,dir_res))
        # print('123',len(obj))
        return
        # exit()

    def _get(self,IP,Port,User,Pasd,hostname):
        dir_res = self.remote()
        fil_res = self.args.local

        transport = paramiko.Transport((IP, int(Port)))
        transport.connect(username=User, password=Pasd,pkey=self.private_key)

        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.get(dir_res, fil_res)
        except OSError:
            print('[%s] 输入有误!\n请确定远程主机存在此文件夹或确定输入文件名! 例: "/tmp/test.py"'%dir_res)
            exit()
        finally:
            transport.close()
        #print('从主机%s下载[%s]文件成功!'%(IP,dir_res))
        print('\033[1;32m%s 从主机"%s"下载%s文件成功\033[0m'%(hostname,dir_res))
        return
        #exit()

    def remote(self):
        if not os.path.basename(self.args.remote) is None:
            return self.args.remote
        else:
            print(em.EM.get('4'))
            exit()

    def local(self):
        if not os.path.isfile(self.args.local):
            print('{c}: {f}: {e} '.format(c=self.args.action,f=self.args.local,e=em.EM.get('6')))
        else:return self.args.local


if __name__ == '__main__':
    Asd()
    # if  hostnum:
    #     print('\033[32m向%s主机传送成功\033[0m'%len(set(hostnum)))
    #     print(hostnumdic)
    # Asd(group='ks',cmd='df -h')


