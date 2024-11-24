import customtkinter as ctk
import wikipediaapi
from CTkTable import *
import sqlite3
import numpy as np
import  matplotlib.pyplot as plt
import tkinter
from matplotlib.backends.backend_tkagg import *
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


class stack: #Used to store coordinate points for the energy per fission graph
    def __init__(self,size):
        self.size = size
        self.stack = ['NULL']*self.size
        self.pointer = 0
    def empty(self):
        if self.pointer == 0:
            return True
        else:
            return False
    def size(self):
        return self.pointer+1
    def top(self):
        return self.stack[self.pointer]
    def push(self, value):
        if self.pointer < self.size:
            self.stack[self.pointer] = value
            self.pointer+=1
    def pop(self):
        if not self.empty():
            place = self.stack[self.pointer-1]
            self.stack[self.pointer-1] = "NULL"
            self.pointer-=1
            return place
    def view(self):
        for i in self.stack:
            print(i)

coordinates_stack = stack(100)


def EPF_graphing_points(num_of_points=100):#Runs every year after calculate_EPF clears out data points
    x = np.random.normal(loc=0, scale=0.0000000001, size=num_of_points)
    xl = []
    coords_x = []
    coords_y = []
   
    for i in range(len(x)):
        coords_x.append(i)
        coords_y.append(0.000000000032*i+x[i])#3.2x10^-11 Joules = uranium 235 energy per fission
        #4.9x10^13 = Energy released for 1 kg of uranium 235
        xl.append(0.000000000032*i)
        coordinates_stack.push([i,0.000000000032*i+x[i]])
       
    return coords_x, xl, coords_y
def calculate_EPF(): #run every year with the new databases
    coords_x = []
    coords_y = []
    while not coordinates_stack.empty():
        temp = coordinates_stack.pop() #temporarily stores the first coordinate
        coords_x.append(temp[0])
        coords_y.append(temp[1])
    x_sum = 0
    y_sum = 0
    xy_sum = 0
    xsquared_sum = 0
    for i in coords_x:
        x_sum+=i
        xsquared_sum+=i**2
    for i in coords_y:
        y_sum+=i
    for i in range(len(coords_x)):
        xy_sum+=coords_x[i]*coords_y[i]

    return (xy_sum - (x_sum*y_sum)/len(coords_x))/(xsquared_sum - (x_sum**2)/len(coords_x)) #formula for gradient of line of regression from an array of points on a scatter graph

"""EPF_graphing_points() #initialises the 2 lists, terms will be added on every year of the simulation
x=calculate_EPF() #Gets a value for the energy released per fission for uranium-235
print(x)"""

class circular_queue:
    def __init__(self,size):
        self.auto_save_number = 1
        self.queue = ['NULL']*size
        self.fpointer = 0
        self.bpointer = 0
    def View(self):
        print(self.queue)
    def Check_Empty(self):
        Empty = True
        for i in self.queue:
            if i not in ["NULL"]:
                Empty = False
        return Empty
    def Push(self,year,yearly_energy,total_energy):
        x = True
        for i in self.queue:
            if i == 'NULL':
                x = False
        if x == True:
            self.Pop()
            self.Push(year,yearly_energy,total_energy)
        else:
            try:
                self.queue[self.bpointer] = (f"Autosave {self.auto_save_number}",year,yearly_energy,total_energy)
                self.auto_save_number+=1
                self.bpointer+=1
            except:
                self.bpointer = 0
                self.queue[self.bpointer] = (f"Autosave {self.auto_save_number}",year,yearly_energy,total_energy)
                self.auto_save_number+=1
                self.bpointer+=1
    def Pop(self):
        x = True
        for i in self.queue:
            if i != 'NULL':
                x = False
        if x == True:
            print('queue empty')
        else:
            try:
                self.queue[self.fpointer] = 'NULL'
                self.fpointer+=1
            except:
                self.fpointer = 0
                self.queue[self.fpointer] = 'NULL'
                self.fpointer+=1
           
    def reset_queue(self):
        while not self.Check_Empty():
            self.Pop()
        self.auto_save_number = 0
        self.fpointer = 0
        self.bpointer = 0
    def return_queue(self):
        return self.queue
       
autosave_queue = circular_queue(10)

class database_shell: #Interface for table subclasses, defines common methods, attributes and outputs
    def __init__(self):
        self.conn = sqlite3.connect('shell.db') #This database will not actually be used, it is a shell that helps form the interface that will be used in the 2 subclasses
        self.c = self.conn.cursor()
    def initialise_tables(self): #
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS users(Username TEXT PRIMARY KEY, Password TEXT,
        Online INTEGER, Link INTEGER)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS saves(Username VARCHAR(255) PRIMARY KEY,
        Fuel_type TEXT, Year INTEGER, Total_Energy INTEGER, Moderator TEXT, Coolant TEXT, Control_Rod TEXT,
        Save_Num TEXT)''')
        self.c.execute("""CREATE TABLE IF NOT EXISTS auto_saves(Username TEXT PRIMARY KEY,
        Fuel_type TEXT, Year INTEGER, Total_Energy INTEGER, Moderator TEXT, Coolant TEXT, Control_Rod TEXT,
        Save_Num TEXT)""")
        self.conn.commit()
    def add_row(self, elements, table): #This is an interface for adding a row
        self.c = self.conn.cursor()
        self.c.execute("""""")
        self.finalise_changes()
    def close_db(self): #Destroys connection to the database
        self.conn.close()
    def finalise_changes(self): #
        self.c = self.conn.cursor()
        self.conn.commit()
    def clear(self, cursor):
        self.c = self.conn.cursor()
        self.c.execute("DELETE FROM users")
        self.finalise_changes()
x = database_shell()

class user_database(database_shell):
    def __init__(self):
        super().__init__()
    def create_table(self):
        x = ('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, Username TEXT, Password TEXT,
        Online INTEGER, Link INTEGER)''')
        self.c.execute(x)
        self.conn.commit()
        self.initialise_tables()
    def initialise_tables(self):#overriding
        self.c = self.conn.cursor()
        for i in range(10):
            data = [(i,"empty","empty",0,i)]
            self.c.executemany("INSERT INTO users(id, Username, Password, Online, Link) VALUES (?,?,?,?,?)", data)
        self.conn.commit()
    def add_user(self, username, password, pos, old_pos):
        query = "UPDATE users SET Link = ? WHERE id = ?"
        self.c.execute(query, (pos, old_pos))
        self.conn.commit()
        print("Add user: ", username, password, pos, old_pos)
        query1 = f"UPDATE users SET Username = ? WHERE id = ?"
        self.c.execute(query1, (username, pos))
        self.conn.commit()
        query2 = f"UPDATE users SET Password = ? WHERE id = ?"
        self.c.execute(query2, (password, pos))
        self.conn.commit()
#        self.close()
        print("Successfully updated: ", username, password, pos)
    def check_signup_valid(self, username, password):
        self.c.execute("SELECT * FROM users")
        rows = self.c.fetchall()
        for i in rows:
            (x1,x2,x3,x4,x5) = i
            if x2.lower() == username.lower():
                return False
        if len(password)<8 or len(username)<8 or username.lower() == username:#checks length and if username has a uppercase
            return False
        return True
       
    def sign_up_db(self,username,password):
        position = self.hashing_algorithm(password)
        self.search(username, password, position, position)
    def log_out_db(self):
        query = "UPDATE users SET Online = 0"
        self.c.execute(query)
        self.conn.commit()
    def rehashing(self):
        self.c.execute("SELECT COUNT(*) FROM users") #aggregate SQL, gets num of rows
        num_of_rows = self.c.fetchone()
        for i in range(num_of_rows[0],num_of_rows[0]+5): #adds 5 more rows to the table when it's full
            data = [(i,"empty","empty",0,i)]
            self.c.executemany("INSERT INTO users(id, Username, Password, Online, Link) VALUES (?,?,?,?,?)", data)
        self.conn.commit()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        cur.close()
        for i in rows:
            print(i)
    def search(self, username, password, var_position, const_position):
        self.c.execute("SELECT COUNT(*) FROM users") #aggregate SQL, gets num of rows
        num_of_rows = self.c.fetchone()
       
        if var_position == num_of_rows[0]: #checks if the table is full, rehashes if it is
            self.rehashing()
        self.c.execute("SELECT * FROM users")
        rows = self.c.fetchall()
        print(f"current position: {rows[var_position]}")
       
        (x1,x2,x3,x4,x5) = rows[var_position]
        if x2 == 'empty' and x3 == 'empty':
            self.add_user(username,password,var_position, const_position)
        else:
            self.search(username,password,(var_position+1),const_position) #Recursion
    def close_db(self):
        self.c.close()
        self.conn.close()
    def hashing_algorithm(self,password):
        num = 0
        for i in password:
            num+=ord(i)
        return num%10
    def validate_login(self,username,password):
        self.c.execute("SELECT * FROM users")
        rows = self.c.fetchall()
        for i in range(len(rows)):
            (ID,c_username,c_password,logged_in,link) = rows[i]
            if c_username == username and c_password == password:
                query1 = f"UPDATE users SET Online = ? WHERE id = ?"
                self.c.execute(query1, (1, i))
                self.conn.commit()
                return True
        return False
    def display_database(self):
        self.c.execute("SELECT * FROM users")
        rows = self.c.fetchall()
        print(rows)
        for i in rows:
            print(i)
    def return_database(self):
        self.c.execute("SELECT * FROM users")
        rows = self.c.fetchall()
        return rows
    def logged_in(self):
        pass

class saves_database(database_shell):
    def __init__(self):
        super().__init__()
        self.dic1 = {"Row 1":1, "Row 2":2, "Row 3":3, "Row 4":4, "Row 5":5, "Row 6":6, "Row 7":7, "Row 8":8, "Row 9": 9, "Row 10": 10}
    def create_table(self):
        x = ('''CREATE TABLE IF NOT EXISTS saves(save_name TEXT, Coolant TEXT, Control_rod TEXT,
        Moderator TEXT, Nuclear_Fuel TEXT, year INTEGER, Tot_Eng INTEGER, User TEXT, row_num INTEGER)''')
        self.c.execute(x)
        self.conn.commit()
        self.initialise_tables()
    def initialise_tables(self):#overriding
        self.c = self.conn.cursor()
        for i in range(1,11):
            data = [("empty","empty","empty","empty","empty",0,0,"empty",i)]
            self.c.executemany("""INSERT INTO saves(save_name, Coolant, Control_rod, Moderator, Nuclear_Fuel,year,
                              Tot_Eng,User, row_num) VALUES (?,?,?,?,?,?,?,?,?)""", data)
        self.conn.commit()
    def update_row(self, row, in1,in2,in3,in4,in5,in6,in7,in8):
        query = """UPDATE saves SET save_name = ?, Coolant=?, Control_rod=?, Moderator=?, Nuclear_Fuel=?, year=?,
                Tot_Eng=? ,User=?, row_num=? WHERE row_num = ?"""
        self.c.executemany(query, [(in1,in2,in3,in4,in5,in6,in7,in8,self.dic1[row],self.dic1[row])])
        self.conn.commit()
    def display_database(self):
        self.c.execute("SELECT * FROM saves")
        rows = self.c.fetchall()
        for i in rows:
            print(i)
    def return_database(self):
       
        def update_format(list_of_tuples):
            new = []
            for i in list_of_tuples:
                a,b,c,d,e,f,g,h,i = i
                new.append((a,b,c,d,e))
            return new
       
        self.c.execute("SELECT * FROM saves")
        rows = self.c.fetchall()
        """print("The table\n")
        print(rows, "\nDONE")
        print(update_format(rows))"""
        return update_format(rows)
    def fetch_names(self): #Returns names for all the saves
        self.c.execute("SELECT save_name FROM saves")
        rows = self.c.fetchall()
        print(f"ROWS ROWS ROWS {rows}")
        return rows
    def get_save_specs(self,name): #Returns specs for loaded old saves
        #returns Coolants, ControlRod, Moderator, Fuel_type
        self.c.execute(f"SELECT Coolant, Control_rod, Moderator, Nuclear_Fuel FROM saves WHERE save_name = '{name}'")
        rows = self.c.fetchall()
        return rows
   
def merge(list1, list2):
    list3 = ["NONE"] * (len(list1) + len(list2))
    list1_pointer, list2_pointer, list3_pointer = 0, 0, 0
   
    while list3_pointer<len(list1)+len(list2):
        if list1[list1_pointer] < list2[list2_pointer]:
            list3[list3_pointer] = list1[list1_pointer]
            list3_pointer+=1
            list1_pointer+=1
        else:
            list3[list3_pointer] = list2[list2_pointer]
            list3_pointer+=1
            list2_pointer+=1
        if list1_pointer == len(list1) or list2_pointer == len(list2):
            break
    if list1_pointer == len(list1):
        for term in list2[list2_pointer:len(list2)]:
            list3[list3_pointer] = term
            list3_pointer+=1
    else:
        for term in list1[list1_pointer:len(list1)]:
            list3[list3_pointer] = term
            list3_pointer+=1
    return list3

def merge_sort(random_list):
    if len(random_list) == 1:
        return random_list

    middle = len(random_list)//2
   
    left = merge_sort(random_list[:middle])
    right = merge_sort(random_list[middle:])
   
   
    return merge(left, right)
   
   
def sort_row(list2, row_to_sort): #Takes a whole 3d array input and sorts it based on 1 column
    sort = []

    #Fills sort with the column within the table that should be sorted by
    for i in range(len(list2)):
        sort.append(list2[i][row_to_sort])

    x = merge_sort(sort)

    print(x)
   
    place_holder = list2
    final = []
   
    counter=0
    while len(place_holder) > 0:
        for i in range(len(place_holder)):
            if place_holder[i][row_to_sort] == x[counter]:
                final.append(place_holder[i])
                #print("place1", place_holder)
                place_holder.pop(i)
                #print("place2", place_holder)
                counter+=1
                break
    return final



class save_interface(saves_database):
    def __init__(self,e1, e2, e3, e4, e5):
        super().__init__()
        self.e11, self.e22, self.e33, self.e44, self.e55 = e1, e2, e3, e4, e5
        self.create_table(self.return_database())
    def change_table_order(self,choice):
        row_mapper = {"Fuel Type":3,"Control Rod":4, "Save Name":0, "Coolant":1, "Moderator":2}
        print("SORTING\nSORTING\nSORTING\nSORTING")
       
        #print(self.return_database())
        print("YESYESYES", self.return_database())
        self.root.destroy()
        self.create_table(sort_row(self.return_database(),row_mapper[choice]))
    def create_table(self,x):

        self.root = ctk.CTk()
        self.root.geometry("700x500")

        value = x
        print("VALUE", value)

        """value = [(1,2,3,4,5),
                 (1,2,3,4,5),
                 (1,2,3,4,5),
                 (1,2,3,4,5),
                 (1,2,3,4,5)]"""

        text = ["Fuel Type","Control Rod", "Save Name", "Coolant", "Moderator"]
        self.combobox4 = ctk.CTkComboBox(self.root, values=text, width=100,command=self.change_table_order, state = "readonly")
        self.combobox4.grid(row=1,column=1, columnspan=1)  
        label5 = ctk.CTkLabel(self.root,text="Sort By").grid(row=1,column=0,pady=20)

        text2 = []

        for i in range(1,11):
            text2.append(f"Row {i}")
        self.combobox5 = ctk.CTkComboBox(self.root, values=text2, width=100, state = "readonly")
        self.combobox5.grid(row=1,column=4, columnspan=1)  
        self.combobox5.set("Row 1")
        label6 = ctk.CTkLabel(self.root,text="Save To").grid(row=1,column=3,pady=20)

        label7 = ctk.CTkLabel(self.root,text="Save Name").grid(row=2,column=0)
        label8 = ctk.CTkLabel(self.root,text="Coolant").grid(row=2,column=1)
        label9 = ctk.CTkLabel(self.root,text="Moderator").grid(row=2,column=2)
        label10 = ctk.CTkLabel(self.root,text="Fuel Type").grid(row=2,column=3)
        label11 = ctk.CTkLabel(self.root,text="Control Rod").grid(row=2,column=4)

        self.table = CTkTable(master=self.root, row=10, column=5, values=value)
        self.table.grid(row=3, column = 0, rowspan = 10, columnspan=5, pady = 5)
        label = ctk.CTkLabel(master=self.root, text="Hello").grid(column=0,columnspan=5,row=0)
   
        entry1 = ctk.CTkEntry(self.root, placeholder_text="Enter Savename...")
        entry1.grid(row=14,column=0, columnspan=5)
       
        self.button1 = ctk.CTkButton(self.root, text="Save",hover_color="green", command= lambda: self.add_row(self.combobox5,entry1))
        self.button1.grid(row=15,column=1,pady=10, columnspan=2)

        self.button2 = ctk.CTkButton(self.root, text="Exit", width=3,hover_color="red", command=self.quit)
        self.button2.grid(row=15,column=0,pady=10, columnspan=1)
       
        self.button3 = ctk.CTkButton(self.root, text="View Autosaves",hover_color="blue", command=self.view_autosave)
        self.button3.grid(row=15,column=3,pady=10, columnspan=2)

        self.root.mainloop()
    def add_row(self, entry1, entry2):
        if len(entry2.get())>=5:
            self.update_row(entry1.get(),entry2.get(),self.e11, self.e22, self.e33, self.e44, 1, 1, "f")
            self.root.destroy()
            self.create_table(self.return_database())
        else:
            label12 = ctk.CTkLabel(self.root,text="Invalid Save Name").grid(column=3, row = 14)
            self.root.mainloop()
    def quit(self):
        self.root.destroy()
        self.root.update()
    def view_autosave(self):
        self.root2 = ctk.CTk()
        self.root2.geometry("570x400")
       
        label1 = ctk.CTkLabel(self.root2,text="Save Name").grid(row=0,column=0)
        label2 = ctk.CTkLabel(self.root2,text="Year").grid(row=0,column=1)
        label3 = ctk.CTkLabel(self.root2,text="Energy This Year").grid(row=0,column=2)
        label4 = ctk.CTkLabel(self.root2,text="Total Energy").grid(row=0,column=3)
       
        self.button4 = ctk.CTkButton(self.root2, text="Exit",hover_color="red", command=self.quit_autosave)
        self.button4.grid(row=11,column=0,pady=10, columnspan=4)
       
        self.table2 = CTkTable(master=self.root2, row=10, column=4, values=autosave_queue.return_queue())
        self.table2.grid(row=1, column = 0, rowspan = 10, columnspan=4, pady=20)
        self.root2.mainloop()
    def quit_autosave(self):
        self.root2.destroy()
        self.root2.update()
#x = save_interface()

class simulation_window:
    def __init__(self, e1, e2, e3, e4, e5):
        print("ITS WORKING")
        #Coolants, Control Rod, Moderator, FuelType, Autosave(0/1)
        self.e1, self.e2, self.e3, self.e4, self.e5 = e1, e2, e3, e4, e5
        self.year = 0
        self.total_energy = 0
        self.YearEnergyOneTonne = 0
        self.heat_loss_multiplier = 0
        self.value_of_widget = 0
       
       
        self.fissions_per_kg = {"Uranium-235": 7.5*(10**20),"Uranium-236": 5*(10**20),
                               "Plutonium-239": 4*(10**20),"Thorium-412": 6*(10**20)}
       
        self.heat_loss_coolants = {"Heavy Water":0.5,"Light Water":0.6,"Liquid Sodium":0.2, "Liquid Helium": 0.3}
        self.heat_transfer_coefficient = {"Graphite":0.3, "Sodium": 0.5, "Heavy Water": 0.7}
        self.reactor_temp = {"Heavy Water": 0.5, "Light Water": 0.5, "Graphite": 0.3}
       
        self
        #https://www.reddit.com/r/allthemods/comments/krze05/best_coolant_for_bigger_reactors_test_results/
       
        self.coords_x, self.xl, self.coords_y = EPF_graphing_points()
       
        self.create_window(False)
    def create_window(self,started):
        #self.coords_x, self.xl, self.coords_y = EPF_graphing_points()
       
        self.window = ctk.CTk()
        self.window.geometry("500x600")
       
        if started:
            self.button2 = ctk.CTkButton(self.window, text="Next Year", command = self.increment)
        else:
            self.button2 = ctk.CTkButton(self.window, text="Start Simulation", command = self.increment)
        self.button2.grid(row=4,column=2)
       
        self.button1 = ctk.CTkButton(self.window, text="Save",hover_color="green", command = self.save)
        self.button1.grid(row=4,column=1)
       
        self.button3 = ctk.CTkButton(self.window, text="Quit",hover_color="red", command = self.quit)
        self.button3.grid(row=5,column=1,columnspan=2,pady=30)
       
        self.button4 = ctk.CTkButton(self.window, text="View Scatter Plot", command = self.scatter)
        self.button4.grid(row=3,column=2)
       
        self.button5 = ctk.CTkButton(self.window, text="View Regression Line", command = self.regresion)
        self.button5.grid(row=3,column=1)
       
        self.label1 = ctk.CTkLabel(self.window,text=f"Total Energy: {self.total_energy}")
        self.label1.grid(row=2,column=2)
        self.label2 = ctk.CTkLabel(self.window,text=f"Yearly Energy: 0 J")
        self.label2.grid(row=2,column=1)
        self.label3 = ctk.CTkLabel(self.window,text=f"Year: {self.year}")
        self.label3.grid(row=1,column=1,columnspan=2)
        self.label4 = ctk.CTkLabel(self.window,text=f"Fuel:\n0")
        self.label4.grid(row=0,column=0)
        self.label5 = ctk.CTkLabel(self.window,text=f"Nuclear Reactor Simulator")
        self.label5.grid(row=0,column=1, columnspan=2)
       
        slider1 = ctk.CTkSlider(self.window, from_=0, to=100, command=self.yes, orientation="vertical",
                                number_of_steps=20, width=20, height = 400, progress_color = "red")
        slider1.set(0)
        slider1.grid(row=1, column = 0, rowspan=4)
        self.window.mainloop()
    def yes(self, value):
        self.value_of_widget = value
        self.label2.configure(text=f"Yearly Energy: {self.value_of_widget*self.YearEnergyOneTonne} Joules")
        self.label4.configure(text= f"Fuel:\n{self.value_of_widget} tonnes")
    def save(self):
        print("hi")
        x = save_interface(self.e1, self.e2, self.e3, self.e4, self.e5)
    def increment(self):
        self.total_energy+=self.value_of_widget*self.YearEnergyOneTonne
        autosave_queue.Push(self.year,self.value_of_widget*self.YearEnergyOneTonne,self.total_energy)
        self.calculateenergy()
        self.year+=1
        self.window.destroy()
        x = self.create_window(True)
    def calculateenergy(self): #Calculates the energy for 1 tonne for the next year
        def round_num(num, length=5):
            temp = str(num)
            final = ""
            counter = 0

            for i in temp:
                if counter < length:
                    final+=i
                else:
                    final+="0"
                counter+=1
            return int(final)
           
        self.coords_x, self.xl, self.coords_y = EPF_graphing_points() #Generates new set of data points
        energy_per_fission = calculate_EPF()
        self.heat_loss_multiplier = 1 - (self.heat_loss_coolants[self.e1]*self.heat_transfer_coefficient[self.e3])
       
        self.YearEnergyOneTonne = round_num(energy_per_fission * self.fissions_per_kg[self.e4] * self.heat_loss_multiplier * 1000) #Energy per tonne
    def quit(self):
        self.window.destroy()
        self.window.update()
    def scatter(self):
        try:
            self.window2.destroy()
        except:
            pass
        fig = Figure(figsize=(4, 4), dpi=100)
        fig.add_subplot(111).scatter(self.coords_x,self.coords_y)
        self.window3 = ctk.CTk()
        self.window3.geometry("400x400")
        self.window3.title("Energy per fission data points")

        canvas = FigureCanvasTkAgg(fig, master=self.window3)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        button1 = ctk.CTkButton(self.window3, text="Regression Line", command=self.regresion).pack(pady=20)

        self.window3.mainloop()
    def regresion(self):
        try:
            self.window3.destroy()
        except:
            pass
        fig = Figure(figsize=(4, 4), dpi=100)
        fig.add_subplot(111).plot(self.coords_x,self.xl)
        self.window2 = ctk.CTk()
        self.window2.geometry("400x400")
        self.window2.title("Energy per fission Regression line")

        canvas = FigureCanvasTkAgg(fig, master=self.window2)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        button1 = ctk.CTkButton(self.window2, text="Scatter Plot", command=self.scatter).pack(pady=20)

        self.window2.mainloop()

class info_tab:
    def __init__(self):
        self.window2 = ctk.CTk()
        self.window2.geometry("400x600")
        self.button1 = ctk.CTkButton(self.window2, text="Coolant", command = lambda: window1("coolant")).pack(pady=30)
        self.button2 = ctk.CTkButton(self.window2, text="Nuclear Fuel", command = lambda: window1("nuclear fuel")).pack(pady=30)
        self.button3 = ctk.CTkButton(self.window2, text="Heat Loss", command = lambda: window1("heat loss")).pack(pady=30)
        self.button4 = ctk.CTkButton(self.window2, text="Nuclear Fusion", command = lambda: window1("nuclear fusion")).pack(pady=30)
        self.button5 = ctk.CTkButton(self.window2, text="Nuclear Fission", command = lambda: window1("nuclear fission")).pack(pady=30)
        self.button7 = ctk.CTkButton(self.window2, text = 'Exit',
                                    fg_color="yellow",
                                    text_color="red",
                                    hover_color="white",
                                    border_color="black", border_width = 2,
                                    command = self.close,
                                    corner_radius=5).pack()
        self.window2.mainloop()
    def close(self):
        self.window2.destroy()
class window1:
    def __init__(self, *category):
       
        def format_text(text):
            new_text = ""
            for i in range((len(text)//100)+1):
                new_text = new_text+"\n"+text[100*i:(100*i+100)]
            return new_text
       
        self.category = category[0]
        self.window = ctk.CTk()
        self.window.title("Information Centre")
        self.window.geometry("900x540")
        wiki_wiki = wikipediaapi.Wikipedia('WikipediaAPI', 'en')
        page_py = wiki_wiki.page(self.category)
        print(page_py.summary[0:6000])

        self.label = ctk.CTkLabel(self.window, text=self.category,
                                 fg_color="red",
                                 text_color="white",
                                 corner_radius = 10).pack(pady=10)
       
       
        self.label = ctk.CTkLabel(self.window, text=format_text(page_py.summary[0:1800]),
                                  fg_color="transparent", font=('Helvetica bold', 14)).pack(padx=100)
        self.button = ctk.CTkButton(self.window, text = 'Exit',
                                   fg_color="yellow",
                                   text_color="red",
                                   hover_color="white",
                                   border_color="black", border_width = 2,
                                   command = self.close,
                                   corner_radius=5).pack(pady=30)

        self.window.mainloop()
    def close(self):
        self.window.destroy()
class get_specifications:
    def __init__(self):
        self.root2 = ctk.CTk()
        self.root2.title("Setup")
        self.root2.geometry("400x500")
        self.root2.focus
        label = ctk.CTkLabel(self.root2, text="Reactor Specifications")
        label.grid(row=0,column=0,pady=20)
        coolants = ["Light Water","Heavy Water", "Liquid Helium", "Liquid Sodium"]
        combobox1 = ctk.CTkComboBox(self.root2, values=coolants, state = "readonly")
        combobox1.grid(row=1,column=1)  
        combobox1.set("Light Water")
        label2 = ctk.CTkLabel(self.root2,text="Coolant").grid(row=1,column=0,padx=75,pady=20)  
        control_rod = ["Lead","Boron", "Cadmium"]
        combobox2 = ctk.CTkComboBox(self.root2, values=control_rod, state = "readonly")
        combobox2.grid(row=2,column=1)  
        combobox2.set("Lead")
        label3 = ctk.CTkLabel(self.root2,text="Control Rod").grid(row=2,column=0,padx=75,pady=20)
       
        moderator = ["Graphite","Sodium","Heavy Water"]
        combobox3 = ctk.CTkComboBox(self.root2, values=moderator, state = "readonly")
        combobox3.grid(row=3,column=1)  
        combobox3.set("Graphite")
        label4 = ctk.CTkLabel(self.root2,text="Coolant").grid(row=3,column=0,padx=75,pady=20)
       
        fuel_type = ["Uranium-235","Uranium-236","Plutonium-239","Thorium-412"]
        combobox4 = ctk.CTkComboBox(self.root2, values=fuel_type, state = "readonly")
        combobox4.grid(row=4,column=1)  
        combobox4.set("Uranium-235")
        label5 = ctk.CTkLabel(self.root2,text="Fuel Type").grid(row=4,column=0,padx=75,pady=20)
       
        check = ctk.IntVar(value=0)
        checkbox = ctk.CTkCheckBox(self.root2, text="Enable Autosaves", variable=check, onvalue=1, offvalue=0)
        checkbox.grid(row=0,column=1,pady=20)
       
        button1 = ctk.CTkButton(self.root2, text="Continue",
                                     command=lambda: self.continue_main_game(combobox1,combobox2,combobox3,combobox4,checkbox))
        button1.grid(row=5, column=0, columnspan=2, pady=40)
       
        self.root2.mainloop()
    def continue_main_game(self,entry1,entry2,entry3,entry4,entry5):
        x1,x2,x3,x4,x5 = entry1.get(), entry2.get(), entry3.get(), entry4.get(), entry5.get()
        self.root2.destroy()
        x = simulation_window(x1,x2,x3,x4,x5)
class maingame(user_database, saves_database):
    def __init__(self, root_window):
        super().__init__()
        self.root2 = root_window
        print("hi")
        self.root = ctk.CTk()
        self.root.title("main game")
        self.root.geometry("300x400")
        self.root.focus()
       
        self.button1 = ctk.CTkButton(self.root, text="New Game",
                                     command=self.new_game).pack(pady=20)
        self.button2 = ctk.CTkButton(self.root, text="Load Save",
                                     command=self.load_game).pack(pady=20)
        self.button3 = ctk.CTkButton(self.root, text="Info Tabs",
                                     command=info_tab).pack(pady=20)
        self.button4 = ctk.CTkButton(self.root, text="Sign Out",
                                    command=self.sign_out).pack(pady=20)
       
        self.root2.destroy()
        self.root.mainloop()
       
    def new_game(self):
        #self.root.destroy()
        specifications = get_specifications()
        #specification.returnspecs()
    def load_game(self):
        save_names_fetched = self.fetch_names()
        #Coolants, ControlRod, Moderator, Fuel_type, 1 (autosave)
       
        self.root3 = ctk.CTk()
        self.save1 = ctk.CTkButton(self.root3, text=save_names_fetched[0][0], command=lambda: self.continue_old_save(save_names_fetched[0][0]))
        self.save1.grid(row=0,column=0)
        self.save2 = ctk.CTkButton(self.root3, text=save_names_fetched[1][0], command=lambda: self.continue_old_save(save_names_fetched[1][0]))
        self.save2.grid(row=0,column=1)
        self.save3 = ctk.CTkButton(self.root3, text=save_names_fetched[2][0], command=lambda: self.continue_old_save(save_names_fetched[2][0]))
        self.save3.grid(row=1,column=0)
        self.save4 = ctk.CTkButton(self.root3, text=save_names_fetched[3][0], command=lambda: self.continue_old_save(save_names_fetched[3][0]))
        self.save4.grid(row=1,column=1)
        self.save5 = ctk.CTkButton(self.root3, text=save_names_fetched[4][0], command=lambda: self.continue_old_save(save_names_fetched[4][0]))
        self.save5.grid(row=2,column=0)
        self.save6 = ctk.CTkButton(self.root3, text=save_names_fetched[5][0], command=lambda: self.continue_old_save(save_names_fetched[5][0]))
        self.save6.grid(row=2,column=1)
        self.save7 = ctk.CTkButton(self.root3, text=save_names_fetched[6][0], command=lambda: self.continue_old_save(save_names_fetched[6][0]))
        self.save7.grid(row=3,column=0)
        self.save8 = ctk.CTkButton(self.root3, text=save_names_fetched[7][0], command=lambda: self.continue_old_save(save_names_fetched[7][0]))
        self.save8.grid(row=3,column=1)
        self.save9 = ctk.CTkButton(self.root3, text=save_names_fetched[8][0], command=lambda: self.continue_old_save(save_names_fetched[8][0]))
        self.save9.grid(row=4,column=0)
        self.save10 = ctk.CTkButton(self.root3, text=save_names_fetched[9][0], command=lambda: self.continue_old_save(save_names_fetched[9][0]))
        self.save10.grid(row=4,column=1)
       
        self.quit3 = ctk.CTkButton(self.root3, text="Exit", command=self.quit_saves)
        self.quit3.grid(row=5,column=0,columnspan=2,pady=20)
       
        self.root3.mainloop()
    def continue_old_save(self, save_name):
        specs = self.get_save_specs(save_name)
        self.root3.destroy()
        x = simulation_window(specs[0][0],specs[0][1],specs[0][2],specs[0][3],1)
    def quit_saves(self):
        x = maingame(self.root3)
    def sign_out(self):
        #Change user database to logged out
        self.log_out_db()
        self.root.destroy()
        x = main_menu()
class sign_up(user_database):
    def __init__(self):
        super().__init__()
        self.TopLevel = ctk.CTkToplevel()
        self.TopLevel.title("Sign Up")
        self.TopLevel.geometry("600x300")
        self.frame1 = ctk.CTkFrame(master=self.TopLevel, width=500, height=200, fg_color = "transparent")
       
        self.label = ctk.CTkLabel(self.frame1, text="Sign Up").grid(row=0,column=0,columnspan=2, pady=20)
        self.label1 = ctk.CTkLabel(self.frame1, text="Username").grid(row=1,column=0, pady=20,padx=5)
        entry1 = ctk.CTkEntry(self.frame1,placeholder_text="Enter Username...")
        entry1.grid(row=1,column=1, pady=20)
        self.label2 = ctk.CTkLabel(self.frame1, text="Password").grid(row=2,column=0, pady=20,padx=5)
        #self.label2 = ctk.CTkLabel(self.frame1, text="Password", show="*").grid(row=2,column=0)
        entry2 = ctk.CTkEntry(self.frame1, placeholder_text="Enter Password...", show="*")
        entry2.grid(row=2,column=1, pady=20)
        self.button = ctk.CTkButton(self.frame1,width = 2,text="Sign Up", command=lambda: self.sign_up(entry1, entry2)).grid(row=3,column=0,columnspan=2, pady=20)
       
        self.frame1.pack()
        self.frame1.mainloop()
    def sign_up(self, entry1, entry2):
        print(entry1.get(), entry2.get())
        if self.check_signup_valid(entry1.get(),entry2.get()):
            self.sign_up_db(entry1.get(),entry2.get())
            self.display_database()
            self.close()
        else:
            self.label5 = ctk.CTkLabel(self.frame1, text="    Invalid Details!").grid(row=1,column=2)
            self.label6 = ctk.CTkLabel(self.frame1, text="    Invalid Details!").grid(row=2,column=2)
       
    def close(self):
        self.TopLevel.destroy()
        self.TopLevel.update()
class log_in(user_database):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.TopLevel2 = ctk.CTkToplevel()
        self.TopLevel2.title("Log In")
        self.TopLevel2.geometry("600x300")
        self.frame2 = ctk.CTkFrame(master=self.TopLevel2, width=500, height=200, fg_color = "transparent")
       
        self.label = ctk.CTkLabel(self.frame2, text="Login").grid(row=0,column=0,columnspan=2, pady=20)
        self.label1 = ctk.CTkLabel(self.frame2, text="Username").grid(row=1,column=0,pady=20,padx=5)
        entry1 = ctk.CTkEntry(self.frame2, placeholder_text="Enter Username...")
        entry1.grid(row=1,column=1,pady=20)
        self.label2 = ctk.CTkLabel(self.frame2, text="Password").grid(row=2,column=0,pady=20,padx=5)
        #self.label2 = ctk.CTkLabel(self.frame2, text="Password", show="*").grid(row=2,column=0)
        entry2 = ctk.CTkEntry(self.frame2, placeholder_text="Enter Password...", show="*")
        entry2.grid(row=2,column=1,pady=20)
       
        self.button = ctk.CTkButton(self.frame2,width = 2,
                                    text="Login", command=lambda: self.login(entry1, entry2)).grid(row=3,column=0,columnspan=2, pady=20)
       
        self.frame2.pack()
        self.frame2.mainloop()
    def login(self, entry1, entry2):
        #if entry1.get() == username and entry2.get() == password:
        if self.validate_login(entry1.get(),entry2.get()):
            print(entry1.get(), entry2.get())
            self.TopLevel2.destroy()
            self.TopLevel2.update()
            #main_menu.quit(self)
            self.display_database()
            maingame(self.root)
        else:
            self.label5 = ctk.CTkLabel(self.frame2, text="    Incorrect Details!").grid(row=1,column=2)
            self.label6 = ctk.CTkLabel(self.frame2, text="    Incorrect Details!").grid(row=2,column=2)

class main_menu():
    def __init__(self):
        backup = ctk.CTk()
        backup.geometry("1x1")
        self.signed_in = False
        self.window3 = ctk.CTk(fg_color="#333521")
        self.window3.title("Starting Menu")
        self.window3.geometry("325x200")
        self.label = ctk.CTkLabel(self.window3,
                                  text_color='white',
                                  text="Main Menu",
                                  font=('bold',20)).grid(row=0,column=0,columnspan=2,pady=10)
        self.button1 = ctk.CTkButton(self.window3, height=100, text="Sign Up",
                                     command=lambda: sign_up()).grid(row=5,column=0,pady=20,padx=10)

        self.button2 = ctk.CTkButton(self.window3, text="Log In", height=100,
                                     command=lambda: log_in(self.window3)).grid(row=5,column=1,pady=20,padx=10)
       
        #try:
        #    self.root2.destroy()
       
        self.window3.mainloop()
        backup.mainloop()
    def quit(self):
        self.window3.destroy()
        self.window3.update()


       
userd = user_database()
userd.create_table()
#userd.display_database()
       
       
usery = saves_database()
usery.create_table()
#usery.display_database()
       
       
ctk.set_appearance_mode("dark")
x = main_menu()

