#!/opt/rh/rh-python36/root/usr/bin/python3

import datetime
import subprocess as sp
import smtplib
import psycopg2

'''Database connection variables'''
connect_str = "dbname='backups' user='postgres' host='mail.novusgroup.co.za' password='supersecretpassword'"
conn = psycopg2.connect(connect_str)
cur = conn.cursor()

'''Timestamp for logs'''
time = str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))

'''Email method'''
def send_mail():
    log_file = open('/usr/scripts/backup_report/veeam_backup.log', 'r')
    log_msg = log_file.read()
    mail_srv = 'mail.novusgroup.co.za'
    mail_port = '25'
    mail_name = 'backups@novusgroup.co.za'
    mail_recip = ['itmonitor@novusgroup.co.za']
    mail_sub = 'Backup report'
    mail_msg = 'Subject: {0}\n\n{1}'.format(mail_sub, log_msg)
    smtpServ = smtplib.SMTP(mail_srv, mail_port)
    smtpServ.sendmail(mail_name, mail_recip, mail_msg)
    log_file.close()
    smtpServ.quit()
    print('Sending email notification to: %s' % mail_recip)


'''Dictionary of servers to check'''
servers = {#'NOVUS-PROD': '129.232.218.34',
           'MELTWATER-PROD': '129.232.233.234',
           'MARKET-IQ': '197.189.215.18',
           'LOCALPRINT-SERVER': '192.168.1.210',
           'PRINT-BACKUP': '192.168.1.211',
           'BROADCAST-0': '192.168.1.14',
           'BROADCAST-1': '192.168.1.15',
           'NOVOCR1': '192.168.1.16',
           'NOVOCR2': '192.168.1.17',
           'NOVWEBSQLASSET': '192.168.5.2',
           'ZABBIX-PROXY': '192.168.1.21',
           }

media_servers = {'MEDIA7': '104.140.20.110',
                 'MEDIA6': '173.232.227.23',
                 'MEDIA5': '104.140.20.116',
                 'MEDIA4': '104.206.168.123',
                 'MEDIA3': '104.140.20.10',
                 'MEDIA2': '104.206.168.216',
                 'MEDIA1': '173.232.227.22',
                 'MEDIA': '50.3.231.139',
                }


'''New line method'''
def new_line():
    f.write('\n')
    f.write('')
    f.write('\n')


'''Backup report for servers'''
with open('/usr/scripts/backup_report/veeam_backup.log', 'w') as f:
    for server_name, server_ip in servers.items():

        backup_status = 'veeamconfig session list --24'
        cmd = 'ssh root@{0} {1}'.format(server_ip, backup_status)

        res = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        output, error = res.communicate()
        output = output.decode('ascii')
        error = error.decode('ascii')

        if output:
            print(server_name)
            print(output)
            f.write(server_name)
            f.write('\n')
            f.write(output)
            f.write('\n')
            
            output_lst = output.split() 
            print(output_lst[12]) 
            
            INSERT_INTO = "INSERT INTO status(name,state,start_date,start_time,end_date,end_time,type) \
                           VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}');".format(server_name,
                                                                                 output_lst[12],
                                                                                 output_lst[13],
                                                                                 output_lst[14],
                                                                                 output_lst[15],
                                                                                 output_lst[16],
                                                                                 output_lst[10])

            cur.execute(INSERT_INTO)
            conn.commit()

             
        elif error:
            print(server_name)
            print(error)
            f.write(error)
            f.write('\n')
        else:
            print(server_name)
            print(time, 'problem with script')
            f.write(time + ' problem with script')
            f.write('\n')


'''Backup report for media servers'''
with open('/usr/scripts/backup_report/veeam_backup.log', 'a') as f:
    for media_server_name, media_server_ip in media_servers.items():
        res = sp.Popen('ssh root@{} cat /var/log/x_backup.log'.format(media_server_ip), shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        output, error = res.communicate()
        output = output.decode('ascii')
        error = error.decode('ascii')
    
        if output:
            print(media_server_name)
            f.write('{}'.format(media_server_name))
            f.write('\n')
            if '0' in output :
                print('success')
                f.write('success')
                new_line()
            else:
                print('failed')
                print(output)
                f.write('failed')
                new_line()
        elif error:
            print(media_server_name)
            f.write('{}'.format(media_server_name))
            f.write('\n')      
            print(error)
            f.write(error)
            new_line()
        else:
            print(media_server_name)
            f.write('{}'.format(media_server_name))
            f.write('\n')      
            print(time, 'ERROR: problem with script')
            f.write(time + ' ERROR: problem with script')
            new_line()


'''Website backup'''
with open('/usr/scripts/backup_report/veeam_backup.log', 'a') as f:
    res = sp.Popen('ssh root@192.168.1.210 cat /var/log/website_backup_notification.log', shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    output, error = res.communicate()
    output = output.decode('ascii')
    error = error.decode('ascii')

    if output:
        print('WEBSITE')
        f.write('WEBSITE')
        f.write('\n')
        f.write(str(output))
        new_line()
    elif error:
        print('WEBSITE')
        f.write('WEBSITE')
        f.write('\n')
        print(time, 'ERROR:', str(error))
        f.write(time, 'ERROR:', str(error))
        new_line()


cur.close()
conn.close()
send_mail()
