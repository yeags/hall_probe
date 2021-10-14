import sqlite3
from sqlite3 import Error
from tkinter.messagebox import showerror, askyesnocancel, askokcancel, askyesno
from tkinter.simpledialog import askstring
from pathlib import Path
# from hallprobe_gui import ProgramControls
import os

class Session:
    def __init__(self, program_controls_instance, meas_dir):
        self.session_changes = False
        self.measurement_dir = meas_dir
        self.session_dir = None
        self.program_controls = program_controls_instance

    def create_db(self, db_name):
        try:
            self.db = sqlite3.connect(db_name)
            self.__init_tables__(self.db)
        except Error as e:
            showerror('Database Error', e)
    
    def __init_tables__(self):
        sql_part_info = \
            """
            CREATE TABLE IF NOT EXISTS part_info(
                info_id integer PRIMARY KEY AUTOINCREMENT,
                datetime text NOT NULL,
                part_number text NOT NULL,
                revision text NOT NULL,
                notes text
                );
            """
        sql_magnet_temp = \
            """
            CREATE TABLE IF NOT EXISTS magnet_temp(
                magnet_temp_id integer PRIMARY KEY AUTOINCREMENT,
                info_id integer NOT NULL,
                datetime text NOT NULL,
                temp_ai0 real,
                temp_ai1 real,
                temp_ai2 real,
                temp_ai3 real,
                temp_ai4 real,
                temp_ai5 real,
                temp_ai6 real,
                temp_ai7 real,
                FOREIGN KEY (info_id) REFERENCES part_info (info_id)
            );
            """
        sql_scan_point = \
            """
            CREATE TABLE IF NOT EXISTS scan_point(
                point_id integer PRIMARY KEY AUTOINCREMENT,
                info_id integer,
                sp_x real,
                sp_y real,
                sp_z real,
                npy_file text,
                FOREIGN KEY (info_id) REFERENCES part_info (info_id)
            );
            """
        sql_scan_line = \
            """
            CREATE TABLE IF NOT EXISTS scan_line(
                line_id integer PRIMARY KEY AUTOINCREMENT,
                info_id integer,
                sp_x real,
                sp_y real,
                sp_z real,
                ep_x real,
                ep_y real,
                ep_z real,
                pt_density real,
                npy_file text,
                FOREIGN KEY (info_id) REFERENCES part_info (info_id)
            );
            """
        sql_scan_area = \
            """
            CREATE TABLE IF NOT EXISTS scan_area(
                area_id integer PRIMARY KEY AUTOINCREMENT,
                info_id integer,
                sp_x real,
                sp_y real,
                sp_z real,
                sd_x real,
                sd_y real,
                sd_z real,
                pt_density real,
                scan_plane text,
                scan_direction text,
                npy_file text,
                FOREIGN KEY (info_id) REFERENCES part_info (info_id)
            );
            """
        # Create Part Info table
        try:
            c = self.db.cursor()
            c.execute(sql_part_info)
            c.execute(sql_magnet_temp)
            c.execute(sql_scan_point)
            c.execute(sql_scan_line)
            c.execute(sql_scan_area)
            c.close()
        except Error as e:
            showerror('Table Initialization', e)

    def new_session(self):
        if self.session_dir is not None:
            state = askyesno('Warning!', 'Changes will be lost.  Continue?')
            if state:
                dir = askstring('New Session', 'Enter new measurement session name.')
                if dir is not None:
                    self.session_dir = self.measurement_dir / dir
                    os.mkdir(self.session_dir)
                    self.create_db(self.session_dir / 'session.db')
                    self.program_controls.lbl_controls_status.configure(text=f'Created new measurement session.\n{self.session_dir}')
        else:
            dir = askstring('New Session', 'Enter new measurement session name.')
            if dir is not None:
                self.session_dir = self.measurement_dir / dir
                os.mkdir(self.session_dir)
                self.create_db(self.session_dir / 'session.db')
                self.program_controls.lbl_controls_status.configure(text=f'Created new measurement session.\n{self.session_dir}')

    def save_session(self):
        if self.session_changes and self.session_dir is not None:
            pass
        else:
            pass
    
    def load_measurement(self):
        pass

    def load_session(self, filepath: Path):
        if self.session_changes:
            state = askyesnocancel('Save Changes', 'Measurement session has changed.  Save changes?')
            if state:
                pass
            elif state == False:
                pass
            else:
                pass
        else:
            pass

if __name__ == '__main__':
    test = Session()
    test.create_db('test.db')