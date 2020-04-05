import sqlite3
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


datex = datetime.now()
datenow = str(datex.day) + str(datex.month) + str(datex.year+543)
dataMenu = []

#---- ส่วนติดต่อฐานข้อมูล ---#
con = sqlite3.connect('coffee.db')
cur = con.cursor()

#----ส่วนออกแบบLayOut----#
window = Tk()
window.resizable(0, 0)
window.title("โปรแกรมหลังร้านกาแฟ")

noteStyler = ttk.Style()
noteStyler.configure("TNotebook")
noteStyler.configure("TNotebook.Tab", foreground='red', font='tahoma 12')
note = ttk.Notebook(window, style="TNotebook")
note.grid(row=1, column=0, columnspan=2)
frame_tab1 = ttk.Frame(note)
note.add(frame_tab1, text=" รายละเอียดการสั่งซื้อ ")
frame_tab2 = ttk.Frame(note)
note.add(frame_tab2, text=" สรุป/กราฟสินค้าในวันนี้ ")
frame_tab3 = ttk.Frame(note)
note.add(frame_tab3, text=" สรุป/กราฟสินค้าทั้งหมด ")
frame_tab4 = ttk.Frame(note)
note.add(frame_tab4, text=" เมนู/สินค้า ")


#--- Frame ในแท็บแรก ---#
fm1 = Frame(frame_tab1)
fm1.grid(row=0, column=0, pady=10, sticky=N)
fm12 = LabelFrame(frame_tab1)
fm12.grid(row=0, column=1, padx=10, pady=10, sticky=N)
fm2 = LabelFrame(frame_tab1)
fm2.grid(row=1, column=0, pady=10, padx=15, sticky=N, columnspan=3)

#--- ListBox สำหรับแสดงข้อมูล ---#
listData = Listbox(fm2, width=70, font="tahoma 16")
listData.grid(row=2, column=0)
Label(fm2, text="รายละเอียดสินค้า", font="tahoma 16").grid(row=0, column=0)

scroll_y = Scrollbar(fm2, orient=VERTICAL, command=listData.yview)
scroll_y.grid(row=2, column=1, sticky=N+S)
listData.config(yscrollcommand=scroll_y.set)

#--- ตัวแปรสำหรับเก็บค่าราคารวม ---#
strsumroww = IntVar()

#--- ลบข้อมูลใน LISTBOX ---#
def deletedata():
    x = listData.size()
    listData.delete(0, last=x)

def deletedata1():    
    x = listDatasum.size()
    listDatasum.delete(0, last=x)

def deletedata2():    
    x = listDatasum1.size()
    listDatasum1.delete(0, last=x)


#--- คิวรีข้อมูลจากคิว ---#
def querydata(queuedate, ID, queuestatus):
    global strsumroww
    bt_pay.config(command=lambda: updatestatus(queuedate,ID), state=NORMAL)
    if(int(queuestatus[int(ID)-1][1]) == 1):
            bt_pay.config(state=DISABLED)

    queuedateID = queuedate + str(ID)
    sql = 'SELECT * FROM coffeeorder WHERE ID = ?'
    cur.execute(sql, [queuedateID])
    row = cur.fetchall()
    deletedata()
    numlast = len(row)
    for (u,i) in enumerate(row):
        listData.insert(END, f'{u+1} จาก {numlast} : {i[1]}               จำนวน {i[2]} หน่วย')

    sql = 'SELECT SUM(price) FROM coffeeorder WHERE ID = ?'
    cur.execute(sql, [queuedateID])
    sumrow = cur.fetchone()

    if (sumrow == None):
        strsumroww.set(0)
    else:
        strsumroww.set(sumrow[0])

#--- ลบคิวออกจากฐานข้อมูล ---#
def deletequeue(queuedate, ID): 
    global strsumroww
    queuedateID = queuedate + str(ID)
    bt_delete = messagebox.askokcancel('ยืนยันการลบคิว',f'ยืนยันการลบข้อมูลของคิว {ID} ในวันที่ {queuedate}')
    if (bt_delete):
        sql = 'DELETE FROM coffeeorder WHERE ID = ?'
        cur.execute(sql, [queuedateID])
        con.commit()
        strsumroww.set(0)
        listData.delete(0,END)

#--- แก้ไขสถานะการชำระเงิน ---#
def updatestatus(queuedate, ID):
    queuedateID = str(queuedate) + str(ID)
    bt_update = messagebox.askokcancel('ยืนยันการชำระเงิน',f'ยืนยันการชำระเงินของคิว {ID} ในวันที่ {queuedate}')
    if(bt_update):
        sql = 'UPDATE coffeeorder SET status = 1 WHERE ID = ?'
        cur.execute(sql, [queuedateID])
        con.commit()
        queryqueue(queuedate)

#--- แสดงคิวจากวันที่ ---#
def queryqueue(queuedate):
    global strsumroww
    strsumroww.set(0)
    sql = 'SELECT DISTINCT(ID),status FROM coffeeorder WHERE Date = ?'
    cur.execute(sql, [queuedate])
    IDs = cur.fetchall()
    IDlast = len(IDs)
    ComboID = ttk.Combobox(fm12, values=list(range(1,IDlast+1)), width=3, font="tahoma 20")
    ComboID.grid(row=1, column=1, padx=5)
    
    if(IDs == []):
        deletedata()
        listData.insert(END, "ไม่มีข้อมูล")
        ComboID.set(0)
        numberID = 0

    else:
        for i in IDs:
            if(i[1] == 0):
                break
        numberID = int(i[0]) % int(queuedate+"0")
        ComboID.set(numberID)
        numberID = ComboID.get()
        ComboID.bind('<<ComboboxSelected>>', lambda e : querydata(queuedate,ComboID.get(),IDs))
        querydata(queuedate,ComboID.get(),IDs)
        bt = Button(fm2, text="ลบคิว", command=lambda: deletequeue(queuedate,numberID), font="tahoma 14", cursor = 'hand2')
        bt.grid(row=3, column=0)
        if(int(numberID) == 0):
            bt.config(state=DISABLED)
            bt_pay.config(state=DISABLED, text="ชำระเงิน")


#--- เลือกวันเดือนปี ---#
def dateclick():
    queuedate = str(comboday.get()) + str(thai_month.index(combomonth.get())+1) + str(comboyear.get())
    queryqueue(queuedate)


fp = mpl.font_manager.FontProperties(family='Tahoma',size=12)
fp1 = mpl.font_manager.FontProperties(family='Tahoma',size=20)

#--- แสดงกราฟจากข้อมูล (แท่ง) ---#
def plot(xplot, xlabelplot, ylabelplot):
    global fp, fp1
    xplot = np.arange(1, xplot+1)
    yplot = ylabelplot
    ax = plt.gca(yticks=xplot) 
    ax.set_yticklabels(xlabelplot, fontproperties=fp) 
    plt.scatter(yplot, xplot)
    plt.title("จำนวนที่ขายได้ทั้งหมด (หน่วย)", fontproperties=fp1)
    plt.barh(xplot,yplot, height=.1, zorder=-1)
    plt.axvline(x=15, color="green", alpha=.5, linestyle="--")
    plt.axvline(x=5, color="red", alpha=.5, linestyle="--")
    plt.show()

#--- แสดงกราฟจากข้อมูลในวันนี้ (วงกลม) ---#
def plotpie(xplot, yplot, xplode):
    global fp
    thaep, raikan, kha = plt.pie(yplot, labels=xplot, autopct='%d%%', shadow=1, counterclock=0, startangle=90, explode=xplode)
    plt.setp(raikan+kha, fontproperties=fp)
    plt.show()
    

#--- Frame ในแท็บสอง ---#
ffm2 = Frame(frame_tab2)
ffm2.grid(row=0, column=0, padx=55)

#--- ส่วนการแสดงรายชื่อสินค้า ---#
Label(ffm2,text='รายละเอียดการสั่งซื้อสินค้าในวันนี้', font="tahoma 20").grid(row=0, column=0, pady=20, columnspan=2)
listDatasum1 = Listbox(ffm2, width=70, font="tahoma 16")
listDatasum1.grid(row=2, column=0, columnspan=2)

scroll_y1 = Scrollbar(ffm2, orient=VERTICAL, command=listDatasum1.yview)
scroll_y1.grid(row=2, column=2, sticky=N+S)
listDatasum1.config(yscrollcommand=scroll_y.set)

#---- คิวรีสรุปสินค้าวันนี้ ----#
def querysummaryone():
    global datenow
    deletedata2()
    sql21 = 'SELECT DISTINCT(Corder) FROM coffeeorder WHERE Date = ?'
    cur.execute(sql21, [datenow])
    xplot = cur.fetchall()
    yplot = []
    xplode = []
    numlast = len(xplot)
    for (u,i) in enumerate(xplot):
        sql22 = 'SELECT SUM(number) FROM coffeeorder WHERE Corder = ? AND Date = ?'
        cur.execute(sql22, [i[0],datenow])
        row22 = cur.fetchone()
        yplot.append(row22[0])
        xplode.append(.2)
        listDatasum1.insert(END, f'{u+1} จากทั้งหมด {numlast} : ชื่อสินค้า : {i[0]}         ขายได้ทั้งหมด {row22[0]} หน่วย')
    Button(ffm2, text="แสดงกราฟ", command=lambda: plotpie(xplot,yplot,xplode), cursor='hand2', font="tahoma 16").grid(row=5, column=1, pady=20)
Button(ffm2, text="รีเฟรชข้อมูล", command=querysummaryone, font="tahoma 16", cursor='hand2').grid(row=5, column=0, pady=20)
querysummaryone()


#--- Frame ในแท็บสาม ---#
ffm3 = Frame(frame_tab3)
ffm3.grid(row=0, column=0, padx=55)

#--- ส่วนการแสดงผลสินค้า ---#
Label(ffm3, text='รายละเอียดการสั่งซื้อสินค้าทั้งหมด', font="tahoma 20").grid(row=0, column=0, pady=20, columnspan=2)
listDatasum = Listbox(ffm3, width=70, font="tahoma 16")
listDatasum.grid(row=2, column=0, columnspan=2)

scroll_y = Scrollbar(ffm3, orient=VERTICAL, command=listDatasum.yview)
scroll_y.grid(row=2, column=2, sticky=N+S)
listDatasum.config(yscrollcommand=scroll_y.set)

#--- คิวรีผลสรุปทั้งหมด ---#
def querysummary():
    deletedata1()
    sql21 = 'SELECT DISTINCT(Corder) FROM coffeeorder'
    cur.execute(sql21)
    xlabelplot = cur.fetchall()
    ylabelplot = []
    numlast = len(xlabelplot)
    for (u,i) in enumerate(xlabelplot):
        sql22 = 'SELECT SUM(number) FROM coffeeorder WHERE Corder = ?'
        cur.execute(sql22, i)
        row22 = cur.fetchone()
        ylabelplot.append(row22[0])
        listDatasum.insert(END, f'{u+1} จากทั้งหมด {numlast} : ชื่อสินค้า : {i[0]}         ขายได้ทั้งหมด {row22[0]} หน่วย')
    Button(ffm3, text="แสดงกราฟ", command= lambda: plot(listDatasum.size(), xlabelplot, ylabelplot), font="tahoma 16", cursor = 'hand2').grid(row=5, column=1, pady=20)
Button(ffm3, text="รีเฟรชข้อมูล", command= querysummary, font="tahoma 16", cursor='hand2').grid(row=5, column=0, pady=20)
querysummary()

#--- ส่วนแสดงผล Frame 4 ---#
ffm4 = Frame(frame_tab4)
ffm4.grid(row=0, column=0, padx=25, columnspan=2 , pady=20)

#--- ส่วนแสดงเมนูสินค้า ---#
Label(ffm4,text='เมนูสินค้าทั้งหมด', font="tahoma 20").grid(row=0, column=0, pady=20)

ffm41 = Frame(frame_tab4)
ffm41.grid(row=1, column=0, padx=20, pady=10)

listDataMenu = Listbox(ffm41, width=27, height=15, font="tahoma 16", exportselect=0)
listDataMenu.bind('<<ListboxSelect>>', lambda e: selectList())
listDataMenu.grid(row=0, column=0)

scroll_y = Scrollbar(ffm41, orient=VERTICAL, command=listDataMenu.yview)
scroll_y.grid(row=0, column=1, sticky=N+S)
listDataMenu.config(yscrollcommand=scroll_y.set)

#--- ส่วนแสดงรายละเอียดสินค้า ---#
ffm42 = LabelFrame(frame_tab4)
ffm42.grid(row=1, column=1, padx=10, pady=10, sticky=N)

Label(ffm42, text="ชื่อสินค้า", font="tahoma 16").grid(row=0, column=0)
entry_name = Entry(ffm42, width=35, font="tahoma 16")
entry_name.grid(row=0, column=1, padx=5, pady=20, columnspan=6)

Label(ffm42, text="ราคาสินค้า", font="tahoma 16").grid(row=1, column=0)
entry_price = Entry(ffm42, width=5, font="tahoma 16" )
entry_price.grid(row=1, column=1, padx=5)
Label(ffm42, text="บาท", font="tahoma 16").grid(row=1, column=2, pady=20)

Catlist = ["ร้อน", "เย็น", "ปั่น", "ของหวาน"]
Label(ffm42, text="ประเภทสินค้า", font="tahoma 16").grid(row=1, column=4)
comboCat = ttk.Combobox(ffm42, value=Catlist, width=10, font="tahoma 16")
comboCat.grid(row=1, column=5, padx=5, pady=20)

#--- เรียกดูข้อมูลเมนูสินค้าจากฐานข้อมูล ---#
def Read_dataMenu():
    global dataMenu
    listDataMenu.delete(0, last=END)
    dataMenu.clear()
    sql = 'SELECT * FROM coffeeMenu'
    cur.execute(sql)
    row = cur.fetchall()
    numlast = len(row)
    for u,i in enumerate(row):
        dataMenu.append(i)
        listDataMenu.insert(END,f'{u+1}/{numlast} : {i[0]}')
Read_dataMenu()

#--- ฟังก์ชัน เรียกข้อมูล จากการคลิกที่ Listbox ---#
def selectList(e=None):
    cur_selection = listDataMenu.curselection()
    index = cur_selection[0]
    row = dataMenu[index]
    entry_clear()
    entry_name.insert(0, row[0])
    entry_price.insert(0, row[1])
    comboCat.set(row[3])

#--- ฟังก์ชัน ลบข้อมูล widget ใน ffm42 ---# 
def entry_clear():
    entry_name.delete(0, END)
    entry_price.delete(0, END)
    comboCat.set('')
    Read_dataMenu()

#--- ฟังก์ชัน บันทึกข้อมูลลงในฐานข้อมูล ---#
def savedataMenu():
    global dataMenu
    stateokupdate = False
    for i in dataMenu:
        if(i[0] == entry_name.get()):
            stateokupdate = True
            break

    if(stateokupdate):
        bt_save = messagebox.askokcancel('ยืนยันการแก้ไขสินค้า',f'ยืนยันการแก้ไขสินค้า {entry_name.get()}')
        sql = 'UPDATE coffeeMenu SET priceMenu = ?, catMenu = ? WHERE nameMenu = ?'
        cur.execute(sql, [entry_price.get(), comboCat.get(), entry_name.get()])
        con.commit()

    else:
        j = 0
        for i in dataMenu:
            if(i[3]== comboCat.get()):
                j = j + 1

        sql = 'INSERT INTO coffeeMenu VALUES (?,?,?,?,?)'
        cur.execute(sql, [entry_name.get(), entry_price.get(), 0, comboCat.get(), j])
        con.commit()

    entry_clear()

#--- ฟังก์ชัน ลบข้อมูลออกจากฐานข้อมูล ---#
def deletedataMenu():
    if(entry_name.get() != ''):    
        bt_delete = messagebox.askokcancel('ยืนยันการลบสินค้า',f'ยืนยันการลบสินค้า {entry_name.get()}')
        if (bt_delete):
            sql = 'DELETE FROM coffeeMenu WHERE nameMenu = ?'
            cur.execute(sql, [entry_name.get()])
            con.commit()
    entry_clear()

#--- ส่วนแสดงปุ่มกด ของ ffm42 ----#
ffm43 = Frame(ffm42)
ffm43.grid(row=2, column=0, columnspan=6)

Button(ffm43, text="เพิ่มข้อมูล", font="tahoma 16", command=entry_clear, cursor='hand2').grid(row=3, column=0, pady=20, padx=15)
Button(ffm43, text="บันทึกข้อมูล", font="tahoma 16", command=savedataMenu, cursor='hand2').grid(row=3, column=2, pady=20, padx=15)
Button(ffm43, text="ลบข้อมูล", font="tahoma 16",  command=deletedataMenu, cursor='hand2').grid(row=3, column=4, pady=20, padx=15)


#--- ส่วนแสดงผล fm1 ----#
Label(fm1,text="โปรแกรมร้านกาแฟ", font='tahoma 20').grid(row=0, column=0, pady=20, columnspan=7)
thai_month = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
Label(fm1, text="วันที่", font="tahoma 16").grid(row=1, column=0, padx=5)
comboday = ttk.Combobox(fm1, value=list(range(1, 32)), width=2, font="tahoma 16")
comboday.grid(row=1, column=1, padx=5)
comboday.set(datex.day)
Label(fm1, text="เดือน", font="tahoma 16").grid(row=1, column=2, padx=5)
combomonth = ttk.Combobox(fm1, value=thai_month, width=10, font="tahoma 16")
combomonth.grid(row=1, column=3, padx=5)
combomonth.set(thai_month[datex.month-1])
Label(fm1, text="ปี พ.ศ.", font="tahoma 16").grid(row=1, column=4, padx=5)
comboyear = ttk.Combobox(fm1, value=list(range(2563,2600)), width=5, font="tahoma 16")
comboyear.grid(row=1, column=5, padx=5)
comboyear.set(datex.year+543)
Button(fm1, text="ยืนยัน", command=dateclick, font="tahoma 16", cursor='hand2').grid(row=1, column=6, padx=5)


#--- ส่วนแสดง fm12 ---#
Label(fm12, text="คิวที่ ", font="tahoma 20").grid(row=1, column=0 , pady=5, padx=5)
Entry(fm12, text="0", font="tahoma 20", width=4, state=DISABLED).grid(row=1, column=1, padx=5)
bt_pay = Button(fm12, text="ชำระเงิน", font="tahoma 16", cursor = 'hand2',state=DISABLED)
bt_pay.grid(row=1, column=2, padx=5)
Label(fm12, text="ราคารวม", font="tahoma 20").grid(row=2, column=0, pady=10)
Entry(fm12, textvariable=strsumroww, font="tahoma 20", width=5, state=DISABLED).grid(row=2, column=1, pady=10)
Label(fm12, text='บาท', font="tahoma 20").grid(row=2, column=2, pady=10)


mainloop()
