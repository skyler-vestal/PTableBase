import sqlite3 as sql
from bs4 import BeautifulSoup as bs
import urllib.request as req

class PTable:

    table_listings = ['Atomic number', 'Atomic mass', 
        'Electronegativity according to Pauling', 'Density', 
        'Melting point', 'Boiling point', 'Vanderwaals radius', 
        'Ionic radius', 'Isotopes', 'Electronic shell', 
        'Energy of first', 'Energy of second']

    def __init__(self, db_file):
        self.conn = sql.connect(db_file)
        self.c = self.conn.cursor()
        self.elem_data = []
        self.__init_table__()

    def pull_data(self):
        self.__init_data__()
        self.__enter_data__()

    def __init_table__(self):
        self.c.execute(''' CREATE TABLE if not exists elems (
            name text,
            symbol text,
            atom_num text,
            atom_mass text,
            electroneg text,
            density text,
            melting_pt text,
            boiling_pt text,
            vanderwaals text,
            ionic_rad text,
            isotopes text,
            shell text,
            first_ionisation text,
            second_ionisation text
        )''')
        self.conn.commit()

    def __init_data__(self):
        r = req.urlopen('https://www.lenntech.com/periodic/elements/index.htm')
        soup = bs(r.read(), 'html.parser')
        elem_boxes = soup.findAll("div", {"class":"module-body"})
        for elem_box in elem_boxes[0].findAll("a"):
            self.__place_data__(elem_box.get("href"))

    def __place_data__(self, file_url):
        print(f"Accessing {file_url}")
        r = req.urlopen(f'https://www.lenntech.com{file_url}')
        soup = bs(r.read(), 'html.parser')

        page_body = soup.find("div", {"class":"col-md-9"})
        name_info = page_body.find("h1")
        name, symbol = name_info.text.split("-")
        elem_list = [""] * (2 + len(PTable.table_listings))
        elem_list[0], elem_list[1] = name.strip(), symbol.strip()

        elem_table = soup.findAll("table")[0]
        elem_data = elem_table.findAll("tr")[0]
        for tr in elem_data.findAll("tr"):
            data = tr.text.strip().split("   ")
            info_name = data[0]
            for ioniz in PTable.table_listings[-2:]:
                if info_name.startswith(ioniz):
                    info_name = ioniz
            if info_name in PTable.table_listings:
                info_data = ""
                for word in data[1:]:
                    info_data += word             
                if info_name != "Electronic shell":
                    info_data = info_data.split(" ")[0]
                elem_list[PTable.table_listings.index(info_name) + 2] = info_data.strip()
        print(elem_list)
        self.elem_data.append(elem_list)

    def __enter_data__(self):
        for elem in self.elem_data:
            data_string = str(tuple(elem))
            entry_string = f"INSERT INTO elems VALUES {data_string}"
            print(entry_string)
            self.c.execute(entry_string)
            self.conn.commit()