from fpdf import FPDF, HTMLMixin
import sqlite3 as sq
import itertools

# print("Enter session info in format 'DD-MM-YYYY<space>Session'")
sessioninfo = "12-04-2023 FN" #input from user
sessioninfo = sessioninfo.split()
Date = sessioninfo[0]
Session = sessioninfo[1]

#Functions
def ranges(i):
    for a, b in itertools.groupby(enumerate(i), lambda pair: pair[1] - pair[0]):
        b = list(b)
        yield b[0][1], b[-1][1]

class PDF(FPDF, HTMLMixin):
    def footer(self):
        # Set position of the footer
        self.set_y(-15)
        
        text_w=pdf.get_string_width("Created by ProtoRes")+6
        self.set_x(((pdf.w - text_w) / 2)+14)

        self.set_font(font, '', 8)
        self.cell(pdf.get_string_width("Created by "), 10, "Created by ")

        self.set_font(font, 'B', 8)
        self.cell(pdf.get_string_width("ProtoRes"), 10, "ProtoRes")

        # Page number
        self.set_font('helvetica', '', 8)
        self.cell(0, 10, f'{self.page_no()}/{{nb}}', align='R')


pdf = PDF('P', 'mm', 'A4')
pdf.set_auto_page_break(auto = True, margin = 15) # Set auto page break
doc_w=pdf.w

# adding fonts
try:
    pdf.add_font('Poppins', '', 'Fonts/Poppins-Regular.ttf')
    pdf.add_font('Poppins', 'B', 'Fonts/Poppins-Bold.ttf')
    font="Poppins"
except:
    print("Poppins font not found. Using Times now.")
    font="Times"



# PACKAGING --------------------------------------------------------------
# for each hall

# code
conn = sq.connect("report.db")
cmd = """SELECT HALL,CLASS,SUBJECT,ROLL
         FROM REPORT
         ORDER BY HALL,CLASS, SUBJECT"""
cursor = conn.execute(cmd)
Q_list = cursor.fetchall()

cmd = """SELECT HALL,COUNT(ROLL)
         FROM REPORT
         GROUP BY HALL"""
cursor = conn.execute(cmd)
R_list = cursor.fetchall()

PDF_list = [["Class", "Subject", "RollNo", "No. of candidates"]]
roll_list = []
hall_name = Q_list[0][0]
class_name = Q_list[0][1]
subject_name = Q_list[0][2]

for i in Q_list:
    if hall_name == i[0]:
        # update list

        if class_name == i[1]:

            if subject_name == i[2]:
                roll_list.append(i[3])

            else:
                roll_ = ranges(roll_list)
                no_of_candidates = len(roll_list)
                PDF_list.append([class_name, subject_name, str(list(roll_))[1:-1], no_of_candidates])
                subject_name = i[2]
                roll_list = []
                roll_list.append(i[3])

        else:
            # maybe class name also needs to be rest
            roll_ = ranges(roll_list)
            no_of_candidates = len(roll_list)
            PDF_list.append([class_name, subject_name, str(list(roll_))[1:-1], no_of_candidates])
            class_name = i[1]
            subject_name = i[2]
            roll_list = []
            roll_list.append(i[3])

    else:
        # append , PDF Generate and empty pdf list
        roll_ = ranges(roll_list)
        no_of_candidates = len(roll_list)
        PDF_list.append([class_name, subject_name, str(list(roll_))[1:-1], no_of_candidates])

        # print Packaging PDF on terminal---------------------
        # print()
        # print()
        # print("Packing List for Internal Examination")
        # print("Hall No: ",hall_name,"   Date: ",Date,"   Session: ",Session)
        print(hall_name)
        for j in PDF_list:
            print(j)
        for j in R_list:
            if j[0]==hall_name:
                print("Total: ",j[1])
        print("-------------------------------------------------------------------------")
        # ----------------------------------------------------

        # PDF creation----------------------------------------
        # pdf.add_page()
        #-----------------------------------------------------


        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        pdf.add_page()
        pdf.set_font(font, '', 27)
        text="Marian Engineering College"
        text_w=pdf.get_string_width(text)+6
        doc_w=pdf.w
        pdf.set_x((doc_w - text_w) / 2)
        pdf.cell(text_w, 23, text,  new_x="LMARGIN", new_y="NEXT", align='C')

        pdf.set_font(font, '', 20)
        text="Packing List for Internal Examination"
        text_w=pdf.get_string_width(text)+6
        pdf.set_x((doc_w - text_w) / 2)
        pdf.cell(text_w, 10, text,  new_x="LMARGIN", new_y="NEXT", align='C')

        pdf.set_y(45)
        pdf.set_font(font, '', 18)
        pdf.set_x(30)
        pdf.write_html(f"<align=\"center\">Hall No: <b>{hall_name}</b>      Date: <b>{Date}</b>      Session: <b>{Session}<b/>")
        pdf.cell(0, 15, "", new_x="LMARGIN", new_y="NEXT")

        #Create Table Header
        pdf.set_font(font, 'B', 10)
        pdf.set_y(60)
        class_w=pdf.get_string_width("Class")+8
        pdf.cell(class_w, 20, "Class", align='C', border=True)
        pdf.cell(65, 20, "Subject", align='C', border=True)
        pdf.multi_cell(30, 10, "Roll No.s of\nCandidates", align='C', border=True, new_x="RIGHT")
        y_pos=60
        pdf.set_y(y_pos)
        pdf.set_x(pdf.w-(pdf.w-(18.061+65+30))+10)
        pdf.multi_cell(30, 10, "No of\nCandidates", align='C', border=True)
        pdf.set_y(y_pos)
        pdf.set_x(pdf.w-(pdf.w-(18.061+65+30+30))+10)
        pdf.multi_cell(0, 10, "Roll No.s of\nAbsentees", align='C', border=True, new_x="LMARGIN", new_y="NEXT")

        #Create Table Body
        y_pos=80
        prev_class=""
        PDF_list.pop(0)
        for k in PDF_list:
            rows=1
            if len(k[1])>30:
                rows=2
            height=10*rows
            pdf.set_font(font, '', 10)

            curr_class=k[0]
            if prev_class==curr_class:
                pdf.cell(class_w, height, '"', align='C', border=True)
            else:
                pdf.cell(class_w, height, curr_class, align='C', border=True)
            prev_class=curr_class
            pdf.multi_cell(65, 10, k[1], align='C', border=True)
            pdf.set_y(y_pos)
            pdf.set_x(pdf.w-(pdf.w-(18.061+65))+10)
            pdf.cell(30, height, f"{k[2]}", align='C', border=True)
            pdf.cell(30, height, str(k[3]), align='C', border=True)
            pdf.cell(0, height, "", border=True, new_x="LMARGIN", new_y="NEXT")
            y_pos+=height
        
        pdf.set_font(font, 'B', 10)
        pdf.cell(class_w+65+30, 11, "Total:", border=True, align="C")
        for l in R_list:
            if l[0]==hall_name:
                pdf.cell(30, 11, str(l[1]), border=True, align="C")
        pdf.cell(0, 11, "", border=True, new_x="LMARGIN", new_y="NEXT")

        y_pos+=25
        pdf.set_y(y_pos)
        pdf.set_font(font, '', 15)
        pdf.write_html("<U>Invigilators must</U>:")
        pdf.write_html("<br><br>     1.  Ensure that all candidates have ID-Cards & are in proper uniform.")
        pdf.write_html("<br><br>     2. Announce that mobile phones, smartwatches & other electronic")
        y_pos+=23
        pdf.set_y(y_pos)
        pdf.write_html("<br>         gadgets, pouches, bags, calculator-cover etc. are <B>NOT</B> allowed")
        y_pos+=8
        pdf.set_y(y_pos)
        pdf.write_html("<br>         inside.")


        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
        PDF_list = [["Class", "Subject", "RollNo", "No. of candidates"]]

        hall_name = i[0]
        class_name = i[1]
        roll_list = []
        roll_list.append(i[3])

    if Q_list[-1] == i:
        # PDF Generate
        print(hall_name)
        roll_ = ranges(roll_list)
        print("#",list(roll_list))
        print("#",list(roll_))
        no_of_candidates = len(roll_list)
        PDF_list.append([class_name, subject_name, str(list(roll_))[1:-1], no_of_candidates])

        # print Packaging PDF on terminal---------------------
        # print()
        # print()
        # print("Packing List for Internal Examination")
        # print("Hall No: ",hall_name,"   Date: ",Date,"   Session: ",Session)
        # print()
        for j in PDF_list:
            print(j)
        for j in R_list:
            if j[0]==hall_name:
                print("Total: ",j[1])
        print("-------------------------------------------------------------------------")
        # ----------------------------------------------------

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        pdf.add_page()
        pdf.set_font(font, '', 27)
        text="Marian Engineering College"
        text_w=pdf.get_string_width(text)+6
        doc_w=pdf.w
        pdf.set_x((doc_w - text_w) / 2)
        pdf.cell(text_w, 23, text,  new_x="LMARGIN", new_y="NEXT", align='C')

        pdf.set_font(font, '', 20)
        text="Packing List for Internal Examination"
        text_w=pdf.get_string_width(text)+6
        pdf.set_x((doc_w - text_w) / 2)
        pdf.cell(text_w, 10, text,  new_x="LMARGIN", new_y="NEXT", align='C')

        pdf.set_y(45)
        pdf.set_font(font, '', 18)
        pdf.set_x(30)
        pdf.write_html("Hall No: <b>SJ201</b>      Date: <b>12-04-2022</b>      Session: <b>FN<b/>")

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        PDF_list = []
pdf.add_page()
pdf.output('Packaging List Test.pdf')
##################################################################################################################