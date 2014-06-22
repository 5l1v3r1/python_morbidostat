from morbidostat_experiment import *
import Tkinter
import threading


class set_up_dialog(Tkinter.Frame):
    def __init__(self, morb):
        self.top= Tkinter.Toplevel()
        self.top.title('Morbidostat Parameters and Set-Up')
        self.morb = morb
        self.vial_selector = vial_selection_dialog(self.morb)

        # scheduling variables
        self.time_variable_names = [('experiment_duration', 'Experiment duration [s]'),
                                    ('cycle_dt', 'Length of cycle [s]'),
                                    ('OD_dt', 'Measurment interval [s]')]
        self.string_variable_names = [('experiment_name', 'Experiment name '),
                                    ('bug', 'Organism'),
                                    ('drugA', 'Drug A'),('drugB', 'Drug B')]

        self.concentration_variable_names = [('target_OD', 'Target OD'),
                                    ('dilution_threshold', 'Dilution Threshold'),
                                    ('dilution_factor', 'Dilution Factor'),
                                    ('drugA_concentration', 'Drug A concentration'),
                                    ('drugB_concentration', 'Drug B concentration')]

        self.variables = {}
        for ttype,var_name in self.time_variable_names + self.string_variable_names + self.concentration_variable_names:
            self.variables[ttype] = Tkinter.StringVar()
            self.variables[ttype].set(str(self.morb.__getattribute__(ttype)))
        self.open_dialog()
        

    def open_dialog(self):
        self.frame= Tkinter.Frame(self.top)
        self.frame.pack()

        grid_counter = 0
        self.fields= {}
        for ti,(ttype, var_name) in enumerate(self.string_variable_names):
            Tkinter.Label(self.frame, text=var_name).grid(row=ti,column = 0, sticky=Tkinter.W)
            self.fields[ttype] = Tkinter.Entry(self.frame, textvariable = str(self.variables[ttype]))
            self.fields[ttype].grid(row=ti+grid_counter, column=1)
        grid_counter+=ti+2

        for ti,(ttype, var_name) in enumerate(self.concentration_variable_names):
            Tkinter.Label(self.frame, text=var_name).grid(row=ti+grid_counter,column = 0, sticky=Tkinter.W)
            self.fields[ttype] = Tkinter.Entry(self.frame, textvariable = str(self.variables[ttype]))
            self.fields[ttype].grid(row=ti+grid_counter, column=1)

        grid_counter+=ti+2
        for ti,(ttype, var_name) in enumerate(self.time_variable_names):
            Tkinter.Label(self.frame, text=var_name).grid(row=ti+grid_counter,column = 0, sticky=Tkinter.W)
            self.fields[ttype] = Tkinter.Entry(self.frame, textvariable = str(self.variables[ttype]))
            self.fields[ttype].grid(row=ti+grid_counter, column=1)

        grid_counter+=ti+2
        done_button = Tkinter.Button(self.frame, text="Done", command = self.read_dialog)        
        done_button.grid(row=grid_counter,column=1)
        vial_selector_button = Tkinter.Button(self.frame, text="Select vials", fg="black", 
                        command=self.vial_selector.open_dialog)
        vial_selector_button.grid(row=grid_counter,column=0)
        

    def read_dialog(self):
        for ttype, var_name in self.time_variable_names:
            self.morb.__setattr__(ttype, int(self.variables[ttype].get()))
        
        for ttype, var_name in self.string_variable_names:
            self.morb.__setattr__(ttype, self.variables[ttype].get())

        for ttype, var_name in self.concentration_variable_names:
            self.morb.__setattr__(ttype, float(self.variables[ttype].get()))

        self.morb.vials = [vi for vi in range(15) if self.vial_selector.vial_selector_variables[vi].get()]
        self.top.destroy()
        

class vial_selection_dialog(Tkinter.Frame):

    def __init__(self,morb):
        # active vials
        self.morb = morb
        self.vial_selector_variables = []
        for xi in xrange(5):
            for yi in xrange(3):
                vi= xi*3+yi
                self.vial_selector_variables.append(Tkinter.IntVar())
                self.vial_selector_variables[-1].set(int(vi in self.morb.vials))

    def open_dialog(self):            
        top = Tkinter.Toplevel()
        top.title('Active vials')
        vial_selector_frame = Tkinter.Frame(top)
        vial_selector_frame.pack()

        vial_selector_buttons = []
        for xi in xrange(5):
            for yi in xrange(3):
                vi= xi*3+yi
                vial_selector_buttons.append(Tkinter.Checkbutton
                                                  (vial_selector_frame, text = str(vi+1),
                                                   var=self.vial_selector_variables[vi]))
                vial_selector_buttons[-1].grid(row=xi,column=yi)
        done_button = Tkinter.Button(vial_selector_frame, text="Done", command = top.destroy)        
        done_button.grid(row=5,column=1)


class morbidostat_interface(Tkinter.Frame):
    def __init__(self, master, morb):
        self.master = master        
        self.morb = morb
        self.all_good=True
        self.update_status_thread = threading.Thread(target = self.update_status_strings)
        self.run_time_window()

    def call_set_up(self):
        if not morb.running:
            set_up_dialog_window = set_up_dialog(self.morb)
            self.master.wait_window(set_up_dialog_window.top)
        else:
            print "cannot update parameters while running"

    def quit(self):
        self.all_good=False
        self.morb.stop_experiment()
        self.run_time_frame.quit()

    def start(self):
        self.all_good=True
        self.morb.start_experiment()
        self.update_status_strings()

    def interrupt(self):
        self.all_good=True
        self.morb.interrupt_experiment()
        self.update_status_strings()

    def resume(self):
        self.all_good=True
        self.morb.resume_experiment()
        self.update_status_strings()


    def status_str(self):
        if self.morb.running and not self.morb.interrupted:
            return "running"
        elif self.morb.interrupted:
            return "interrupted"
        elif self.morb.stopped:
            return "stopped"
        else:
            return "undefined"

    def remaining_time_str(self):
        remaining_time = (self.morb.n_cycles-self.morb.cycle_counter)*self.morb.cycle_dt
        return self.seconds_to_time_str(remaining_time)
            
    def elapsed_time_str(self):
        remaining_time = (self.morb.cycle_counter)*self.morb.cycle_dt
        return self.seconds_to_time_str(remaining_time)

    def remaining_cycle_time_str(self):
        remaining_time = (self.morb.ODs_per_cycle-self.morb.OD_measurement_counter)*self.morb.OD_dt
        return self.seconds_to_time_str(remaining_time)

    def seconds_to_time_str(self,nsec):
        hours = nsec//3600
        minutes = nsec//60 - hours*60
        seconds = nsec-60*minutes-hours*3600
        return str(hours)+'h:'+format(minutes,'02d')+'m:'+format(seconds,'02d')+'s'        
        

    def run_time_window(self):
        self.run_time_frame = Tkinter.Frame(self.master)
        self.master.title("Morbidostat control")
        self.run_time_frame.pack()
        label_font= 'Helvetica'
        var_font = 'Courier'
        fsize = 16
        self.status_label = Tkinter.Label(self.run_time_frame, text='Status: ', fg="black", anchor=Tkinter.W, height = 2, width= 20, font=(label_font, fsize))
        self.elapsed_time = Tkinter.Label(self.run_time_frame, text  = 'Elapsed time:', fg="black", anchor=Tkinter.W, height = 2, width= 20, font=(label_font, fsize))
        self.remaining_time = Tkinter.Label(self.run_time_frame, text  = 'Remaining time:', fg="black", anchor=Tkinter.W, height = 2, width= 20, font=(label_font, fsize))
        self.remaining_cycle_time = Tkinter.Label(self.run_time_frame, text  = 'Remaining in cycle: ', fg="black", anchor=Tkinter.W, height = 2, width= 20, font=(label_font, fsize))
        self.status_label_val = Tkinter.Label(self.run_time_frame, text=self.status_str(), fg="black", anchor=Tkinter.W, height = 2, width= 10, font=(var_font, fsize))
        self.elapsed_time_val = Tkinter.Label(self.run_time_frame, text  = self.elapsed_time_str(), fg="black", anchor=Tkinter.W, height = 2, width= 10, font=(var_font, fsize))
        self.remaining_time_val = Tkinter.Label(self.run_time_frame, text  = self.remaining_time_str(), fg="black", anchor=Tkinter.W, height = 2, width= 10, font=(var_font, fsize))
        self.remaining_cycle_time_val = Tkinter.Label(self.run_time_frame, text  = self.remaining_cycle_time_str(), fg="black", anchor=Tkinter.W, height = 2, width= 10, font=(var_font, fsize))

        self.set_up_button = Tkinter.Button(self.run_time_frame, text="PARAMETERS", fg="black", 
                                   command=self.call_set_up, height = 2)
        self.refresh_button = Tkinter.Button(self.run_time_frame, text="REFRESH", fg="black", 
                                   command=self.update_status_strings, height = 2)
        self.start_button = Tkinter.Button(self.run_time_frame, text="START", fg="black", 
                                   command=self.start, height = 2)
        self.interrupt_button =Tkinter.Button(self.run_time_frame, text="INTERRUPT", fg="red", 
                                  command=self.interrupt, height = 2)
        self.resume_button = Tkinter.Button(self.run_time_frame, text="RESUME", fg="black", 
                                    command=self.resume, height = 2)
        self.quit_button = Tkinter.Button(self.run_time_frame, text="QUIT", fg="black", 
                                          command=self.quit, height = 2)

        self.status_label.grid(row=0, column=0, columnspan=2)
        self.elapsed_time.grid(row=1, column=0, columnspan=2)
        self.remaining_time.grid(row=2, column=0, columnspan=2)
        self.remaining_cycle_time.grid(row=3, column=0, columnspan=2)
        self.status_label_val.grid(row=0, column=2, columnspan=3)
        self.elapsed_time_val.grid(row=1, column=2, columnspan=3)
        self.remaining_time_val.grid(row=2, column=2, columnspan=3)
        self.remaining_cycle_time_val.grid(row=3, column=2, columnspan=3)
        self.set_up_button.grid(row= 5, column = 0)
        self.refresh_button.grid(row= 5, column = 1)
        self.start_button.grid(row= 5, column = 2)
        self.interrupt_button.grid(row= 5, column = 3)
        self.resume_button.grid(row= 5, column = 4)
        self.quit_button.grid(row= 5, column = 5)

        #self.update_status_thread.start()
    
    def update_status_strings(self):
        self.status_label_val.configure(text=self.status_str())
        self.elapsed_time_val.configure(text  = self.elapsed_time_str())
        self.remaining_time_val.configure(text  = self.remaining_time_str())
        self.remaining_cycle_time_val.configure(text  = self.remaining_cycle_time_str())

def run_GUI(morb):
    root = Tkinter.Tk()
    app=morbidostat_interface(root, morb)
    root.mainloop()
    root.destroy()

if __name__ == '__main__':
    morb = morbidostat()
    gui_thread = threading.Thread(target = run_GUI, args = (morb,))
    gui_thread.start()
    
