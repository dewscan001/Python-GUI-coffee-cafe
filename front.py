# Write your code here :-)
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
import sqlite3

con = sqlite3.connect('coffee.db', timeout=1)
cur = con.cursor()

#----วันเวลาปัจจุบัน----#
thai_day = ('อาทิตย์', 'จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์')
thai_month = ('มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม')
datex = datetime.now()
if (datex.weekday() == 6):
    weekday = 0
else:
    weekday = datex.weekday()+1

#----ส่วนออกแบบLayOut----#
window=Tk()
window.overrideredirect(True)

Label(window, text="โปรแกรมหน้าร้านกาแฟ", bg="#3e1900", fg="white", width=100, font="tahoma 12").grid(row=0, column=0, columnspan=2, sticky=NW)
Button(window,text="ปิดโปรแกรม", bg="red", fg="white", width=10, font="tahoma 12", command=window.destroy, cursor="hand2").grid(row=0, column=1, sticky=NE)

fm1 = Frame(window)
fm1.grid(row=1, column=0, pady=10)
fm12 = LabelFrame(window)
fm12.grid(row=1, column=1, padx=10, pady=10)
fm2 = LabelFrame(window)
fm2.grid(row=2, column=0, pady=10, padx=15, sticky=N, columnspan=2)
fm22 = Frame(fm12)
fm22.grid(row=3, column=0, columnspan =3, pady=15)

#---- สร้างแท็บใน fm2 ----#
noteStyler = ttk.Style()
noteStyler.configure("TNotebook")
noteStyler.configure("TNotebook.Tab", foreground='red', font='tahoma 12')
note = ttk.Notebook(fm2, style="TNotebook")
note.grid(row=0, column=0)
frame_tab1 = ttk.Frame(note)
note.add(frame_tab1, text=" เมนูร้อน ")
frame_tab2 = ttk.Frame(note)
note.add(frame_tab2, text=" เมนูเย็น ")
frame_tab3 = ttk.Frame(note)
note.add(frame_tab3, text=" เมนูปั่น ")
frame_tab4 = ttk.Frame(note)
note.add(frame_tab4, text=" เมนูของหวาน ")
framesummar = ttk.Frame(note)
note.add(framesummar, text=" สรุปการสั่งซื้อสินค้า ")


#----ประกาศตัวแปรเริ่มต้น IntVar----#
sum = 0
sumVar = IntVar()
stateok = False
o = []

#----รันคิว----#
queue1 = IntVar()
queuedate = str(datex.day)+str(datex.month)+str(datex.year+543)
for num in range(1, 100):
    queue1.set(num)
    queue2 = num
    ID = queuedate+str(queue2)
    ID = int(ID)
    sql = 'SELECT ID FROM coffeeorder WHERE ID = ?'
    cur.execute(sql, [ID])
    Ids = cur.fetchone()
    if Ids == None:
        break
 
#----ส่วนด้านบนของโปรแกรม----#
Label(fm1,text="โปรแกรมร้านกาแฟ", font='tahoma 20').grid(row=0, column=0, pady=20)
Label(fm1,text=f'วัน{thai_day[weekday]} ที่ {datex.day} เดือน {thai_month[datex.month-1]} พ.ศ. {datex.year+543}', font='tahoma 20').grid(row=1, column=0, pady=50, padx=100)


#----คลาสสำหรับแสดงข้อมูลสินค้า----#
class Showvalue:

    #---- แสดงคิว ----#
    def queueshow(self):
        global queue1
        Label(fm12,text="คิวที่", font='tahoma 16').grid(row=0, column=0, pady=20)
        Entry(fm12,textvariable=queue1, font='tahoma 16', width=4, state=DISABLED).grid(row=0, column=1, padx=25, sticky=W)
        self.update()

    def __init__(self, name, price,i):
        global queue2
        self.name = name
        self.price = price
        self.i = i
        self.intvar = IntVar()
        self.number = 0
        self.sum = 0
        self.queue = queue2
        self.queueshow()

    #----อัพเดทจำนวนสินค้าในฐานข้อมูล----#
    def update(self):
        sql = 'UPDATE coffeeMenu SET numberMenu = ? WHERE nameMenu = ?'
        cur.execute(sql, [self.number, self.name])
        con.commit()

    #----เมื่อคลิกปุ่ม +/- ----#
    def onclick(self,e):
        global sum
        self.e = e

        if(self.e == 1)and(self.number >= 0):
            self.intvar.set(self.intvar.get()+1)
            self.number = self.number + 1
            sum = sum + self.price
        elif(self.e == 2)and(self.number > 0):
            self.intvar.set(self.intvar.get()-1)
            self.number = self.number - 1
            sum = sum - self.price

        sumVar.set(sum)
        self.summary(0)
        self.update()


    #----เมื่อคลิกปุ่ม ยืนยัน หรือ รีเซ็ต----#
    def nextqueue(self, ch):
        global queuedate
        global queue1
        global sum
        global sumVar
        global cur
        global con
        if(ch == 1):
            if(self.number != 0):
                queuedate1 = queuedate + str(self.queue)
                sql = 'INSERT INTO coffeeorder VALUES (?,?,?,?,?,?)'
                cur.execute(sql,[queuedate1, self.name, self.number, self.price*self.number, queuedate, 0])
                con.commit()
            sql = 'UPDATE coffeeMenu SET numberMenu = 0'
            cur.execute(sql)
            con.commit()
            sql = 'SELECT ID FROM coffeeorder WHERE Date = ?'
            cur.execute(sql, [queuedate])
            row = cur.fetchall()
            for i in row:
                self.queue = i[0] % int(queuedate) + 1
                queue1.set(self.queue)
        self.number = 0
        self.intvar.set(0)
        sum = 0
        sumVar.set(0)
        self.queueshow()


    #---- แสดงสรุปผล ----#
    def summary(self, tab):
        if(tab == 1):
            self.j = 0
        elif(tab == 2):
            self.j = 6
        elif(tab == 3):
            self.j = 12
        elif(tab == 4):
            self.j = 18

        Label(framesummar, text = self.name, font='tahoma 12').grid(row=self.i, column=self.j, padx=10, pady=10)
        Button(framesummar, text="-", command = lambda: self.onclick(2), cursor="hand2").grid(row=self.i, column=self.j+1, padx=5, pady=10)
        Label(framesummar, textvariable=self.intvar, font='tahoma 12', width=3).grid(row=self.i, column=self.j+2)
        Button(framesummar, text="+", command = lambda: self.onclick(1), cursor="hand2").grid(row=self.i, column=self.j+3, padx=5, pady=10)
        Label(framesummar, text = "ชิ้น", font='tahoma 12').grid(row=self.i, column=self.j+4)

        Label(fm12, text="ราคารวม ", font="tahoma 16").grid(row=1, column=0)
        Entry(fm12, textvariable=sumVar, font="tahoma 16", width=5, state=DISABLED, bg="white").grid(row=1, column=1)
        Label(fm12, text=" บาท", font="tahoma 16").grid(row=1, column=2, pady=17)


    #---- ฟังก์ชัน แสดงผลเมนู ----#
    def show(self, tab):
        if(tab == 1):
            fm2_sub = LabelFrame(frame_tab1)
        elif(tab == 2):
            fm2_sub = LabelFrame(frame_tab2)
        elif(tab == 3):
            fm2_sub = LabelFrame(frame_tab3)
        elif(tab == 4):
            fm2_sub = LabelFrame(frame_tab4)

        fm2_sub.grid(row=self.i//5, column=self.i%5, padx=20, pady=20)

        Label(fm2_sub, text=self.name, font="tahoma 12", width=15).grid(row=0, column=0, columnspan=3, pady=5)

        Label(fm2_sub, text="ราคา", font="tahoma 12").grid(row=1, column=0)
        Label(fm2_sub, text=str(self.price), font="tahoma 12").grid(row=1, column=1)
        Label(fm2_sub, text="บาท", font="tahoma 12").grid(row=1, column=2)

        Button(fm2_sub, text="-", command = lambda: self.onclick(2), cursor="hand2").grid(row=2, column=0, padx=5, pady=10)
        Label(fm2_sub, textvariable=self.intvar, font="tahoma 12").grid(row=2, column=1)
        Button(fm2_sub, text="+", command = lambda: self.onclick(1), cursor="hand2").grid(row=2, column=2, padx=5, pady=10)

        self.summary(tab)


#----ส่วนเรียกข้อมูลเพื่อแสดงข้อมูล----#
def queryshow(s,c):
    global o
    sql = 'SELECT nameMenu, priceMenu, catMenu, rowMenu FROM coffeeMenu'
    cur.execute(sql)
    row = cur.fetchall()
    for j,i in enumerate(row):
        if(s == False):
            o.append(Showvalue(i[0],i[1],i[3]))
            if(i[2] == "ร้อน"):
                o[j].show(1)
            elif(i[2] == "เย็น"):
                o[j].show(2)
            elif(i[2] == "ปั่น"):
                o[j].show(3)
            elif(i[2] == "ของหวาน"):
                o[j].show(4)

        else:
            o[j].nextqueue(c)

queryshow(stateok,0)


#----ฟังก์ชัน กำหนดค่าศูนย์ ----#
def setzero(changer):
    global o
    global sum
    global stateok

    if(changer == 1):
        bt_ok = messagebox.askokcancel('ยืนยันการสั่งสินค้า','ยืนยันการสั่งซื้อสินค้าเป็นจำนวนเงิน '+str(sum)+' บาท')
        if (bt_ok):
            stateok = True

    else:
        bt_cancel = messagebox.askokcancel('ยืนยันการรีเซ็ต','ยืนยันการรีเซ็ตการสั่งซื้อสินค้า')
        if (bt_cancel):
            stateok = True

    if(sum != 0)and(stateok == True):
        sum = 0
        sumVar.set(0)
        queryshow(stateok,changer)
        
        
#---- ปุ่มกด ยืนยัน/รีเซ็ต ----#
Button(fm22, text="ยืนยัน", font="tahoma 14", command= lambda: setzero(1), width=5, cursor="hand2").grid(row=0, column=0, pady=5, padx=35)
Button(fm22, text="รีเซ็ต", font="tahoma 14", command= lambda: setzero(2), width=5, cursor="hand2").grid(row=0, column=1, pady=5, padx=35)

window.mainloop()
