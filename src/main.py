#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17/11/17 23:25
# @Author  : Tiancc
# @Site    : 
# @File    : main.py
# @Software: PyCharm

import argparse,configparser,paramiko
from concurrent.futures import ThreadPoolExecutor
from conf import settings
from data import ErrorMessage as em
import os

class Asd(object):
    '''
    这是一个类似'Ansible'工具,但是只支持上传下载文件,与一部分bash命令
    '''

    def __init__(self):
        parser = argparse.ArgumentParser(description='Used to open the FTP client')
        parser.add_argument('-s', '--server',action='store', help="Specify host IP or Hostname. Can't be empty!")   #default='localhost'
        parser.add_argument('-g', '--group', help='Specify host groups')
        parser.add_argument('-cmd', help='The command to send to a remote server')
        parser.add_argument('-action', help='The operation to be performed')
        parser.add_argument('-local', help='The absolute path of the local server file')
        parser.add_argument('-remote', help='Batch delete directory')
        self.args = parser.parse_args()
        self.help = parser.print_help

        '''
        加载用户配置信息
        '''
        self.config = configparser.ConfigParser()
        self.config.read(settings.HOST_CONF)

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
            print('##'*20,result.result()[1])
            print(result.result()[0])

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

        for user in users:
            result_list.append(Thread.submit(self.manager,user))

        Thread.shutdown(wait=True)
        return result_list

    def manager(self,user):

        _ip = self.config.get(user,'ip')
        _port = self.config.get(user,'port')
        _user = self.config.get(user,'user')
        _pasd = self.config.get(user,'pasd')
        _cmd = self.parameter()

        # if self.args.action == 'put':
        #     res = self._put(_ip,_port,_user,_pasd)
        #     return res
        if not self.args.action is None:
            res = self.action(_ip,_port,_user,_pasd,_cmd)
            return res
        else:
            res = self.ssh(_ip,_port,_user,_pasd,_cmd)
            return res

    def ssh(self,IP,Port,User,Passd,Cmd):
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
        ssh.connect(hostname=IP, port=Port, username=User, password=Passd)

        '''
        执行命令
        得到命令结果并反馈出去
        关闭连接
        '''
        stdin, stdout, stderr = ssh.exec_command(Cmd)
        result = stdout.read()
        return result.decode('utf-8'),IP
        ssh.close()

    def action(self,i,p,u,pd,comm):
        '''
        展示闲置的...
        :param comm:
        :return:
        '''
        if hasattr(self,'_%s'%comm):
            return getattr(self,'_%s'%comm)(i,p,u,pd)
        else:print('-bash: {}: {}'.format(comm,em.EM.get('3')))

    def cmd(self,comm):
        return comm

    def _put(self,IP,Port,User,Pasd,):
        dir_res = self.remote()
        fil_res = self.local()

        transport = paramiko.Transport((IP, int(Port)))
        transport.connect(username=User, password=Pasd)

        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.put(fil_res, dir_res)
        except OSError:
            print('[%s] 输入有误!\n请确定远程主机存在此文件夹或确定输入文件名! 例: "/tmp/test.py"'%dir_res)
            exit()
        finally:
            transport.close()
        print('向主机%s上传[%s]文件成功!'%(IP,dir_res))
        exit()

    def _get(self,IP,Port,User,Pasd):
        dir_res = self.remote()
        fil_res = self.args.local

        transport = paramiko.Transport((IP, int(Port)))
        transport.connect(username=User, password=Pasd)

        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.get(dir_res, fil_res)
        except OSError:
            print('[%s] 输入有误!\n请确定远程主机存在此文件夹或确定输入文件名! 例: "/tmp/test.py"'%dir_res)
            exit()
        finally:
            transport.close()
        print('从主机%s下载[%s]文件成功!'%(IP,dir_res))
        exit()

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



