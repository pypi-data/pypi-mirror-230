import sqlite3
from sqlite3 import Error
from datetime import datetime
from calendar import monthrange


year = datetime.now().year
month = datetime.now().month
day = datetime.now().day


def create_connection(db_file):
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
      
    except Error as e:
        print(e)

    return con


def Insert_Update_Delete(cur, insert_update_check):
    try:
        c = cur.cursor()
        c.execute(insert_update_check)
      
    except Error as e:
        print(e)
      

def Check_Tables(cur, check_tables):
    try:
        c = cur.cursor()
        c.execute(check_tables)
        items = c.fetchall()
        for item in items[1::]:
            for i in item:
                print(f"> {i}")
              
    except Error as e:
        print(e)


def Check(cur, check):
    try:
        c = cur.cursor()
        for row in c.execute(check):
            r = []
            for i in row:
                c = i.replace(",", "")
                r.append(c)    
            print(f"> Name: {r[0]}")
            print(f"> Fees: {r[1]}")
            print(f"> Dues1: {r[2]}")
            print(f"> Dues2: {r[3]}")
            print(f"> Dues3: {r[4]}")
            print(f"> Dues4: {r[5]}")
            print("--------------------")
    except Error as e:
        print(e)
      
def Check_Dues(cur, check_dues):
    try:
        c = cur.cursor()
        for row in c.execute(check_dues):
            r = []
            for i in row:
                c = i.replace(",", "")
                r.append(c)    


            if (r[1][0] != "0" or r[2][0] != "0" or r[3][0] != "0" or r[4][0] != "0" or r[5][0] != "0"):
                print(f"> Name: {r[0]}")
          
            if ("0" != r[1][0]):
                print(f"> Fees: {r[1]}")
              
            if ("0" != r[2][0]):
                print(f"> Dues1: {r[2]}")
              
            if ("0" != r[3][0]):
                print(f"> Dues2: {r[3]}")
              
            if ("0" != r[4][0]):            
                print(f"> Dues3: {r[4]}")
              
            if ("0" != r[5][0]):            
                print(f"> Dues4: {r[5]}")
          
            print("--------------------")
          
    except Error as e:
        print(e)

def Check_Month(cur):
    try:
        c = cur.cursor()
        for row in c.execute(" SELECT num From RaDin where name = 'month' "):
            for i in row:
                return i

    except Error as e:
        print(e)


def Check_Year(cur):
    try:
        c = cur.cursor()
        for row in c.execute(" SELECT num From RaDin where name = 'year' "):
            for i in row:
                return i

    except Error as e:
        print(e)


def OriginalDate(d, m, y):
  
    return f"{d}-{m}-{y}"

print(OriginalDate(day, month, year))


def LastDay(d, m, y):
  
    input_dt = datetime(y, m, d)
    res = monthrange(input_dt.year, input_dt.month)
    day = res[1]
    
    return f"{day}-{input_dt.month}-{input_dt.year}"

print(LastDay(day, month, year))


def Get_Cls(cur):
    c = cur.cursor()
    c.execute("""SELECT name FROM sqlite_master""")
    tables = c.fetchall()
    LoC = []
    for clas in tables[1::]:
        for cls in clas:
            LoC.append(cls)
    return LoC         


def Addition_Subtraction(cur, cls, u_i, n, col):
  
    def Get_data(cur, get_data):
        try:
            c = cur.cursor()  
            for item in c.execute(get_data):
                for i in item:
                    return i
                  
        except Error as e:
            print(e)

    values = f""" SELECT {col} From Class_{cls} where name = '{n}' """  
  
    Data = Get_data(cur, values)  
    data = Data.split(",")
  
    plus = int(data[0]) + int(u_i[1::])
    minus = int(data[0]) - int(u_i[1::])

    def Records(u_i, n, col, cur, count):
    
        records = f"| {u_i} / {OriginalDate(day, month, year)} "
        first_words = f"{count},{data[1]}"
      
        m_d = first_words + records
      
        c = cur.cursor()
        c.execute(f""" Update Class_{cls} set {col} = '{m_d}' where name = '{n}' """)
        cur.commit()

    if u_i[0] == "+":  
        Records(u_i, n, col, cur, plus)       
        print(f"  {u_i[1::]} added successfully\n")
      
    elif u_i[0] == "-":
        Records(u_i, n, col, cur, minus)
        print(f"  {u_i[1::]} subtracted successfully\n")
        


id = [323435, 527546, 734512]

prompt = int(input("user id: "))

def mainfunc():
    if (prompt in id):
        # database address
        database = r"school.db"
      
        # create a database connection
        con = create_connection(database)
    
        if con is not None:       
          
            if (OriginalDate(day, month, year) == LastDay(day, month, year) and Check_Month(con) == 1):
              
                cl = Get_Cls(con)
    
                def modify_data(cn):
                    c = con.cursor()
                    LoN = []
    
                    for name in c.execute(f""" SELECT name From {cn} """):
                        for n in name:
                            LoN.append(n)
                  
                    def mod(n):
                        con = create_connection(database)
                        c = con.cursor()
                        for row in c.execute(f"""SELECT fees, dues1, dues2, dues3, dues4 From {cn} where name = '{n}' """):
                            c.execute(f""" Update {cn} set dues4 = '{row[3]}' where name = '{n}' """)
                            c.execute(f""" Update {cn} set dues3 = '{row[2]}' where name = '{n}' """)
                            c.execute(f""" Update {cn} set dues2 = '{row[1]}' where name = '{n}' """)
                            c.execute(f""" Update {cn} set dues1 = '{row[0]}' where name = '{n}' """)
                            for f in c.execute(""" SELECT nToE, ninth, matric From RaDin where name = 'month' """):
                                if ("10" in cn):
                                    c.execute(f""" Update {cn} set fees = '{f[2]}, ' where name = '{n}' """)
                          
                                elif ("9" in cn):
                                    c.execute(f""" Update {cn} set fees = '{f[1]}, ' where name = '{n}' """)
                                    
                                else:
                                    c.execute(f""" Update {cn} set fees = '{f[0]}, ' where name = '{n}' """)
                            con.commit()
                          
                    list(map(mod, LoN))
                  
                list(map(modify_data, cl))
              
                def oneTimeRun():
                    c = con.cursor()
                    c.execute(" Update RaDin set num = 0 where name = 'month' ")
                    con.commit()
                    print("Month is changed")
                
                oneTimeRun()
    
          
            elif (OriginalDate(day, month, year) == OriginalDate(1, month, year)):
                c = con.cursor()
                c.execute(" Update RaDin set num = 1 where name = 'month' ")
                con.commit()
              
                print("Preparing resources...")
    
          
            else:
                while True:
                    user_input = input("\nWhat you want: ")
        
                    if(user_input == "exit"):
                        break
        
                    elif (user_input == "RaDin"):
                        insert_table = """ CREATE TABLE IF NOT EXISTS RaDin (name text, num integer, nToE integer, ninth integer, matric integer); """           
                        insert_values = """ INSERT INTO RaDin (name, num, nToE, ninth, matric) VALUES ("month", 1, 0, 0, 0) """            
                      
                        Insert_Update_Delete(con, insert_table)
                        Insert_Update_Delete(con, insert_values)
                        con.commit()
                      
                    elif (user_input == "change session"):
                      
                        cl = Get_Cls(con)
            
                        def cls_index(cl):
                          l = []
                          for i in range(len(cl)):
                              l.append(i)
                          return l
              
                        index = cls_index(cl)
            
                        def modify_data(cl, index, con):
                            c = con.cursor()
            
                            for i in index:                        
                                c.execute(f""" ALTER TABLE {cl[i]} RENAME TO C{i} """)  
            
                            c.execute(""" DROP TABLE IF EXISTS C0 """)
                            for i, n in zip(index[1::], index):
                                c.execute(f""" ALTER TABLE C{i} RENAME TO {cl[n]} """)           
                                
                        modify_data(cl, index, con)
                      
                        print("Session successfully changed")
                                               
                    elif (user_input == "fees"):
                        nTo8 = int(input("Nursery to Eight fees: "))
                        ninth = int(input("Ninth fees: "))
                        matric = int(input("Matric fees: "))
                      
                        update_fees1 = f""" Update RaDin set nToE = {nTo8} where name = 'month' """
                        update_fees2 = f""" Update RaDin set ninth = {ninth} where name = 'month' """
                        update_fees3 = f""" Update RaDin set matric = {matric} where name = 'month' """
                      
                        Insert_Update_Delete(con, update_fees1)
                        Insert_Update_Delete(con, update_fees2)
                        Insert_Update_Delete(con, update_fees3)
                        con.commit()
        
                    elif (user_input == "i class"):
                        cls = input("Class Name: ")
                        insert_table = f""" CREATE TABLE IF NOT EXISTS Class_{cls} (name text, fees text, dues1 text, dues2 text, dues3 text, dues4 text); """
            
                        Insert_Update_Delete(con, insert_table)
                      
                    elif (user_input == "c class"):
                        check_tables = """SELECT name FROM sqlite_master"""    
                      
                        Check_Tables(con, check_tables)
                      
                    elif (user_input == "r class"):
                        cls = input("Which class: ")
                        remove_tables = f""" DROP TABLE IF EXISTS Class_{cls} """
                      
                        Insert_Update_Delete(con, remove_tables)
                        print(f"Class_{cls} removed")
                      
                    elif (user_input == "i"):
                        cls = input("Which class: ")
                        n = input("Student Name: ")
                      
                        lOC = Get_Cls(con)              
                        c = con.cursor()
                      
                        for f in c.execute(""" SELECT nToE, ninth, matric From RaDin where name = 'month' """):
                            if (cls in lOC[0]):
                                insert_values = f""" INSERT INTO Class_{cls} (name, fees, dues1, dues2, dues3, dues4) VALUES ('{n}', '{f[2]}, ', '0, ', '0, ', '0, ', '0, '); """
                                Insert_Update_Delete(con, insert_values)
                                con.commit()
                              
                            elif (cls in lOC[1]):
                                insert_values = f""" INSERT INTO Class_{cls} (name, fees, dues1, dues2, dues3, dues4) VALUES ('{n}', '{f[1]}, ', '0, ', '0, ', '0, ', '0, '); """
                                Insert_Update_Delete(con, insert_values)
                                con.commit()
                              
                            else:
                                insert_values = f""" INSERT INTO Class_{cls} (name, fees, dues1, dues2, dues3, dues4) VALUES ('{n}', '{f[0]}, ', '0, ', '0, ', '0, ', '0, '); """
                                Insert_Update_Delete(con, insert_values)
                                con.commit()     
                      
                    elif (user_input == "c"):
                        cls = input("Which class: ")
                        n = input("Which student: ")
                        check_values = f""" SELECT * From Class_{cls} where name = '{n}' """
                      
                        Check(con, check_values)
        
                        while True:
                            u_i = input("Any add or sub: ")   
                            if (u_i == "exit"):
                                break
                            col = input("From: ")  
                          
                            Addition_Subtraction(con, cls, u_i, n, col)  
                          
                    elif (user_input == "c dues"):
                        cls = input("Which class: ")
                        check_dues = f""" SELECT * From Class_{cls} ORDER BY NAME """
                      
                        Check_Dues(con, check_dues)
        
                        while True:
                            u_i = input("  Any add or sub: ")   
                            if (u_i == "exit"):
                                break
                            col = input("  From: ")  
                          
                            Addition_Subtraction(con, cls, u_i, n, col)        
                      
                    elif (user_input == "c all"):
                        cls = input("Which class: ")
                        check_values = f""" SELECT * From Class_{cls} ORDER BY NAME """
                        
                        Check(con, check_values)
                      
                        while True:        
                            u_i = input("  Any add or sub: ")     
                            if (u_i == "exit"):
                                break
                            n = input("  Which student: ")                
                            col = input("  From: ")  
                          
                            Addition_Subtraction(con, cls, u_i, n, col)             
                      
                    elif (user_input == "u"):
                        cls = input("Which class: ")
                        n = input("What name: ")
                        f = int(input("New fees: "))
                        update_values = f""" Update Class_{cls} set fees = {f} where name = '{n}' """
                      
                        Insert_Update_Delete(con, update_values)
                        con.commit()
                      
                    elif (user_input == "r"):
                        cls = input("Which class: ")
                        n = input("What name: ")
                        delete_values = f""" DELETE from Class_{cls} where name = '{n}' """
                      
                        Insert_Update_Delete(con, delete_values)
                        con.commit()
                        print(f"{n} removed")
              
        else:
            print("Error! cannot create the database connection.")

    else:
        print("Wrong id")
      
if __name__ == '__main__':
    mainfunc()