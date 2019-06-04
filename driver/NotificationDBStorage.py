import psycopg2

class NotificationDatabase:
    
    def __init__(self,dbname,user,password,hostname="localhost"):
        self.dbname=dbname
        self.user=user
        self.password=password
        self.hostname=hostname
        
    def connect(self):
        sentence="host=%s dbname=%s user=%s password=%s"%(self.hostname,self.dbname,self.user,self.password)
        print("connecting to db:"+sentence)
        self.conn = psycopg2.connect(sentence)
        self.cur = self.conn.cursor()

        print(self.conn)
        
    def createNotificationTable(self,tableName):   
        
        sentence="""CREATE TABLE %s 
        (id SERIAL PRIMARY KEY,
         imei bigint,
         ip varchar(15), 
         fecha TIMESTAMP,
         ECNO int,
         rssi varchar(10),
         cellid int,
         logSize int,
         temp decimal,
         uptime int         
         );"""%(tableName)
        self.cur.execute(sentence)

    def creatAlertTable(self,tableName):   
        
        sentence="""CREATE TABLE %s 
        (id SERIAL PRIMARY KEY,
         imei bigint,
         ip varchar(15), 
         fecha TIMESTAMP,
         alert varchar(40)
         );"""%(tableName)
        self.cur.execute(sentence)

    def insertNotification(self,tableName,noti):
         
     #   self.cur.execute("INSERT INTO {} (imei,ip,fecha,ECNO,rssi,cellid,logSize,temp,uptime) VALUES (%d, %s,%s,%d,%s,%d,%d,%f,%d)".format(tableName),(noti['imei'],noti['ip'],noti['fecha'],noti['EC/NO'],noti['rssi'],noti['cellid'],noti['logSize'],noti['temp'],noti['uptime']))
      #  self.cur.execute("INSERT INTO {} (imei,ip) VALUES (%s, %s%s)".format(tableName),(noti['imei'],noti['ip']))
        self.cur.execute("INSERT INTO {} (imei,ip,fecha,ECNO,rssi,cellid,logSize,temp,uptime) VALUES (%s, %s,TO_TIMESTAMP(%s,'YY-MM-DD HH24:MI:SS'),%s,%s,%s,%s,%s,%s)".format(tableName),(noti['imei'],noti['ip'],noti['fecha'],noti['EC/NO'],noti['rssi'],noti['cellid'],noti['logSize'],noti['temp'],noti['uptime']))

    def insertAlert(self,tableName,noti):
        """
        "imei": 359486064904103,
        "ip": "192.168.210.18",
        "fecha": "19-5-14 15:48:27",
        "alert": "lastgasp sent"
        """
        self.cur.execute("INSERT INTO {} (imei,ip,fecha,alert) VALUES (%s, %s,TO_TIMESTAMP(%s,'YY-MM-DD HH24:MI:SS'),%s)".format(tableName),(noti['imei'],noti['ip'],noti['fecha'],noti['alert']))

    def storeNotification(self,tableName,notis):
        for noti in notis:
            if "alert" in noti:
                self.insertAlert(tableName+"_alert", noti)
            else:
                self.insertNotification(tableName, noti)
        self.commit()
            
    def checkIfTableExist(self,tableName):
        
        sentence="SELECT to_regclass('public.%s');"%(tableName)
        self.cur.execute(sentence)
        value=self.cur.fetchone()
        
        return value[0]==tableName
    
    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
     
    def doBasicSetup(self,tableName):
        
        if not self.checkIfTableExist(tableName):
            self.createNotificationTable(tableName)   
        
        if not self.checkIfTableExist(tableName+"_alert"):
            self.creatAlertTable(tableName+"_alert")
      
        self.commit()
        
test=False     
      
if test:
    db= NotificationDatabase("test","postgres","spikemon")
    db.connect()
    
    if not db.checkIfTableExist("notif"):
        db.createNotificationTable("notif")
        db.commit()
    
    newNoti={ 'imei':359486064904103 ,'ip':'192.168.210.18','fecha': '19-5-16 15:51:44','EC/NO':  32, 'rssi' : '-61 dbm','cellid': 141147,'logSize': 8333,'temp': 36.97,'uptime': 17593}
    #newNoti={'imei':34 ,'ip':'192.168.210.18','fecha': '19-5-15 15:59:11','EC/NO': 26 , 'rssi' : '-53 dbm','cellid': 141147,'logSize': 8263,'temp': 33.31,'uptime': 1624}
    db.insertNotification("notif",newNoti)
    db.commit()
    db.close()

