"""
Joshua Tanke, 2017.  Created in CIS 211 course.  This program creates a
simulation of our solar system by calculating the vector position of
each planet and drawing the position on a canvas.  The gravity of each
planet changes the vector positions of the other planets at each time step.
"""

from math import sqrt
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from time import sleep


class Vector:
    """
    A Vector is a 3-tuple of (x,y,z) coordinates.
    """
    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z
    
    def x(self):
        return self._x
    
    def y(self):
        return self._y
    
    def z(self):
        return self._z
        
    def __repr__(self):
        return "({:.3g},{:.3g},{:.3g})".format(self.x(), self.y(), self.z())
    
    def norm(self):
        return sqrt((self.x()**2 + self.y()**2 + self.z()**2))
    
    def __add__(self, other):
        return Vector(self.x() + other.x(), self.y() + other.y(), self.z() + other.z())
    
    def __sub__(self, other):
        return Vector(self.x() - other.x(), self.y() - other.y(), self.z() - other.z())
    
    def __truediv__(self, other):
        return Vector(self.x() / other, self.y() / other, self.z() / other)
    
    def __eq__(self, other):
        if self.x() == other.x() and self.y() == other.y() and self.z() == other.z():
            return True
        return False
        
    def __mul__(self, other):
        return Vector(self.x() * other, self.y() * other, self.z() * other)
    
    def clear(self):
        self._x = 0
        self._y = 0
        self._z = 0
    

G = 6.67E-11

class Body:
    """
    A Body object represents the state of a celestial body.  A body has mass 
    (a scalar), position (a vector), and velocity (a vector).  A third vector, 
    named force, is used when calculating forces acting on a body.  An
    optional name can be attached to use in debugging.
    """
    
    def __init__(self, mass = 0, position = Vector(0,0,0), velocity = Vector(0,0,0), name = None):
        """
        Create a new Body object with the specified mass (a scalar), position (a vector), 
        and velocity (another vector).  A fourth argument is an optional name for the body.
       """
        self._mass = mass
        self._position = position
        self._velocity = velocity
        self._name = name
        self._force = Vector(0, 0, 0)

    def __repr__(self):
        if self._name == None:
            return "{:.3g}kg {} {}".format(self._mass, self._position, self._velocity)
        return "{}: {:.3g}kg {} {}".format(self._name, self._mass, self._position, self._velocity)
    
    def name(self):
        return self._name

    def mass(self):
        return self._mass
        
    def position(self):
        return self._position

    def velocity(self):
        return self._velocity

    def force(self):
        return self._force
        
    def direction(self, other):
        return other.position() - self.position()
    
    def add_force(self, other):
        val = (self.direction(other) * other.mass()) / (self.direction(other).norm()**3)
        self._force += val
        
    def clear_force(self):
        self._force.clear()
                
    def move(self, dt):
        a = self.force() * G
        self._velocity += a * dt
        self._position += self.velocity() * dt 
        

class TkBody(Body):
    """
    A TkBody object visualizes the Body class objects.
    """
    def __init__(self, mass, position, velocity, name, size, color):
        super(TkBody, self).__init__(mass, position, velocity, name)
        self._color = color
        self._size = size
        self._graphic = None
    
    def size(self):
        return self._size
    
    def color(self):
        return self._color
    
    def graphic(self):
        return self._graphic
    
    def set_graphic(self, other):
        self._graphic = other



class SolarSystemCanvas(tk.Canvas):
    """
    A SolarSystemCanvas object creates a Canvas onject that plots the different
    TkBody objects.
    """
    
    def __init__(self, parent, height=600, width=600):
        tk.Canvas.__init__(self, parent, height=height, width=width, background='gray90', highlightthickness=0)
        self._planets = None
        self._outer = None
        self._scale = None
        self._offset = Vector(int(self['width'])/2, int(self['height'])/2, 0)
        
    def set_planets(self, lst):
        self._planets = lst
        self._outer = len(lst)
        self._compute_scale(lst)
        self.view_planets(len(lst))
        
    def view_planets(self, n):
        self._compute_scale(self._planets[:n])
        tk.Canvas.delete(self, "all")
        
        for p in self._planets[:n]:
            
            location = self._compute_loc(p)
            graphic = self.create_oval(location[0]+p.size(), 
                                       location[1]+p.size(), 
                                       location[0]-p.size(), 
                                       location[1]-p.size(),
                                       fill=p.color())
                                                            
            p.set_graphic(graphic)
        
        self._outer = n
        
    def move_planets(self, lst):
        for p in self._planets[:self._outer]:
            x, y = self._current_loc(p)
            x_, y_ = self._compute_loc(p)
            self.coords(p.graphic(), x_+p.size(), y_+p.size(), x_-p.size(), y_-p.size())
            self.create_line(x, y, x_, y_)
        
        
    def _compute_scale(self, bodies):
        p = min(self._offset.x(), self._offset.y())
        pos = (bodies[-1].position() - bodies[0].position()).norm()
        self._scale = p / pos
    
    def _compute_loc(self, p):
        pos = p.position() * self._scale + self._offset
        return pos.x(), pos.y()
    
    def _current_loc(self, p):
        ul, ur, _, _ = self.coords(p.graphic())
        return ul + p.size(), ur + p.size()




class ViewControl(tk.Frame):
    """
    The ViewControl class creates a controller on the Canvas object that
    manipulates the number of planets and the duration of the simulation.
    """
    def __init__(self, parent, callback):
        tk.Frame.__init__(self, parent)
        
        self['width'] = 100             
        self['height'] = 25             
        self['background'] = 'white'     
           
        
        self._label = tk.Label(self, text='Number of Planets:').grid(row=0, column=0)
        self._spinbox = tk.Spinbox(self, command=callback, width = 3, font = ('Helvetica', 24), state=tk.DISABLED)
        self._spinbox.grid(row=0, column=1)
        
        
    def reset(self, nbodies):
        self._spinbox['to'] = nbodies
        self._spinbox['from_'] = 2
        self._spinbox['state'] = tk.NORMAL
        self._spinbox.delete(0, tk.END)
        self._spinbox.insert(0, nbodies)
        
    def nbodies(self):
        if self._spinbox['state'] == tk.DISABLED:
            return 0
        return int(self._spinbox.get())




class RunFrame(tk.Frame):
    
    def __init__(self, parent, callback):
        tk.Frame.__init__(self, parent)
        
        self['width'] = 200
        self['height'] = 100
        self['background'] = 'white'
        
        self._run_button = tk.Button(self, text='Run', command= callback)
        self._run_button.grid(row=0, column=0)
        
        self._nsteps_entry = tk.Entry(self)
        self._nsteps_entry.grid(row=0, column=2)
        
        self._progress = ttk.Progressbar(self)
        self._progress.grid(row=0, column=3)
        
        self._nsteps_entry.insert(0, '365')
        
        
    def dt(self):
        
        return 86459
    
    def nsteps(self):
        
        return int(self._nsteps_entry.get())
        
    def init_progress(self, n):
        self._progress['value'] = 0
        self._progress['maximum'] = n
        
    def update_progress(self, n):
        self._progress['value'] += n
        
    def clear_progress(self):
        self._progress['value'] = 0




def step_system(bodies, dt=86459, nsteps=1):
    orbits = [[] for x in range(len(bodies))]
    
    
    for k in range(nsteps):
        
        for i in range(len(bodies)):
            for j in range(len(bodies)):
                if i != j:
                    bodies[i].add_force(bodies[j])
     
        for i in range(len(bodies)):
            bodies[i].move(dt)
            orbits[i].append(bodies[i].position())
            bodies[i].clear_force()
            
    return orbits




def read_bodies(filename, cls):
    '''
    Read descriptions of planets, return a list of body objects.  The first
    argument is the name of a file with one planet description per line, the
    second argument is the type of object to make for each planet.
    '''
    if not issubclass(cls, Body):
        raise TypeError('cls must be Body or a subclass of Body')

    bodies = [ ]

    with open(filename) as bodyfile:
        for line in bodyfile:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            name, m, rx, ry, rz, vx, vy, vz, diam, color = line.split()
            args = {
                'mass' : float(m),
                'position' : Vector(float(rx), float(ry), float(rz)),
                'velocity' : Vector(float(vx), float(vy), float(vz)),
            }
            opts = {'name': name, 'color': color, 'size': int(diam)}
            for x in opts:
                if getattr(cls, x, None):
                    args[x] = opts[x]
            bodies.append(cls(**args))

    return bodies




root = tk.Tk()
root.title("Solar System")

bodies = None

def load_cb():
    global bodies
    fn = tk.filedialog.askopenfilename()
    bodies = read_bodies(fn, TkBody)
    canvas.set_planets(bodies)
    view_count.reset(len(bodies))

def view_cb():
    canvas.view_planets(view_count.nbodies())
    
def run_cb():
    
    def time_step():
        nonlocal nsteps
        step_system(bodies, dt)
        canvas.move_planets(bodies)
        run_frame.update_progress(1)
        sleep(0.02)
        if nsteps > 0:
            nsteps -= 1
            canvas.after_idle(time_step)
        else:
            run_frame.clear_progress()
        
    nsteps = run_frame.nsteps()
    run_frame.init_progress(nsteps)
    dt = run_frame.dt()
    canvas.after_idle(time_step)

canvas = SolarSystemCanvas(root)
canvas.grid(row = 0, column = 0, columnspan = 3, padx = 10, pady = 10, sticky="nsew")

tk.Button(root, text='Load', command=load_cb).grid(row=1, column=0, pady = 20)

view_count = ViewControl(root, view_cb)
view_count.grid(row=1, column=2, pady=20)

run_frame = RunFrame(root, run_cb)
run_frame.grid(row=1, column=1, pady=20)





