'''
    Monitor Cleaning Tool (MCT)

    Version  : 0.0
    Language : Python 2.7.3
    Date     : 2012-09-10
    Author   : Drew A. French

    License Statement :
        LGPL v3.0

        Copyright 2012, Drew A. French.

        This library is free software: you can redistribute it and/or
        modify it under the terms of the GNU Lesser General Public
        License as published by the Free Software Foundation, either
        version 3 of the License, or (at your option) any later version.

        This library is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
        Lesser General Public License for more details.

        You should have received a copy of the GNU Lesser General Public
        License along with this library.  If not, see
        <http://www.gnu.org/licenses/>.

    Purpose :
            This is the monitor cleaning tool (MCT). This program can be used
        to make your monitor display one solid color; perfect for cleaning
        those irritating smudges!
'''


import sys
import Tkinter as tk
import ttk
import tkColorChooser as colorchooser

class ColorMenu (tk.Menu) :
    ''' The context menu which acts as the main interface. '''

    std_colors = {'black', 'white', 'red', 'green', 'blue', 'cyan', 'magenta',
                  'yellow'}

    options = ['black',
               'white',
               'custom color',
               None,
               'red',
               'green',
               'blue',
               'cyan',
               'magenta',
               'yellow',
               None,
               'fullscreen',
               'alpha',
               None,
               'exit']

    def __init__ (self, par, color='black', activebackground='#202020',
                  *args, **kw) :
        tk.Menu.__init__(self, par, *args, activebackground=activebackground,
                         **kw)
        self.par = par

        self.custom_index = self.options.index('custom color')
        self.var = tk.StringVar()
        self.var_bool = tk.BooleanVar()
        self.var_bool.set(True)

        self._build()

        self.set(color)

    def _build (self) :
        for option in self.options :
            color = 'black'
            active_color = 'white'

            if option is None :
                self.add_separator()
            elif option == 'exit' :
                command = self.par.destroy
                self.add_command(label=option.title(), foreground=color,
                                 activeforeground=active_color,
                                 command=command)
            elif option == 'fullscreen' :
                command = lambda : self.par.fullscreen(self.var_bool.get())
                self.add_checkbutton(label=option.title(), foreground=color,
                                     activeforeground=active_color,
                                     command=command, variable=self.var_bool)
            elif option == 'alpha' :
                self.add_command(label=option.title(), foreground=color,
                                 activeforeground=active_color,
                                 command=self.par.alpha.post)
            else :
                if option == 'custom color' :
                    command = self._custom
                else :
                    command = lambda option=option : self.par.config(bg=option)

                    if option == 'white' or option == 'black' :
                        color = 'black'
                        active_color = 'white'
                    else :
                        color = active_color = option

                self.add_radiobutton(label=option.title(), foreground=color,
                                     activeforeground=active_color,
                                     command=command, variable=self.var)

    def _custom (self, color=None) :
        if color is None :
            try :
                color = self.last_color
            except AttributeError :
                color = 'black'
            else :
                self.par.config(bg=color)
                self.par.update_idletasks()

            color = colorchooser.askcolor(parent=self.par, color=color)
        else :
            if not isinstance(color, (tuple, list)) :
                color = (None, color)

        self._set_custom_color_label_color(color)

    def _set_custom_color_label_color (self, color) :
        try :
            color = color[1]
            self.par.config(bg=color)
        except tk.TclError :
            pass
        else :
            self.entryconfigure(self.custom_index, foreground=color,
                                activeforeground=color)
            self.last_color = color

    def set (self, color) :
        ''' This sets the application's color. '''

        try :
            self.par.config(bg=color)
        except tk.TclError :
            color ='black'
            self.par.config(bg=color)
            success = False
        else :
            success = True

        self.var.set(color.title())

        if self.var.get().lower() not in self.std_colors :
            self.var.set('Custom Color')
            self._custom(color)

        return success

    def post (self, event) :
        ''' This makes the menu appear near the mouse cursor. '''

        tk.Menu.post(self, event.x_root+1, event.y_root+1)

class Alpha (tk.Toplevel) :
    ''' This window allows the user to change the main window's alpha value,
        i.e., its transparency. '''

    def __init__ (self, par, *args, **kw) :
        tk.Toplevel.__init__(self, *args, **kw)
        self.withdraw()
        self.title('')
        self.protocol('WM_DELETE_WINDOW', self.withdraw)

        ''' This attempts to change the window's decorations; this may not work
            on all operating systems. '''
        try :
            self.attributes('-toolwindow', True)
        except tk.TclError :
            pass

        self.par = par
        self.resizable(True, False)

        self.frame = ttk.Labelframe(self, text='Alpha 1.0 :')
        self.frame.pack(padx=10, pady=10, expand=True, fill='both')

        self.scale = ttk.Scale(self.frame, from_=0.0, to=0.999, length=220,
                               command=self._change)
        self.scale.pack(expand=True, fill='both')
        self.scale.set(0.999)

    def _change (self, val) :
        val = float(val)
        self.frame.config(text='Alpha %s :' % str(int(round(val, 2) * 255)))
        self.par.attributes('-alpha', val)

        if val * 255 < 50 :
            ''' This prevents the user from exiting the alpha window, if the
                main window isn't quite opaque enough. '''

            self.protocol('WM_DELETE_WINDOW', lambda : None)
        else :
            self.protocol('WM_DELETE_WINDOW', self.withdraw)

    def post (self) :
        self.deiconify()
        self.transient(self.par)

class MainWin (tk.Tk) :
    ''' This is the main application window. '''

    def __init__ (self, color='Black') :
        tk.Tk.__init__(self)
        self.withdraw()
        self.title('MCT')

        self.alpha = Alpha(self)

        self.menu = self._make_menu(color=color)

        self.fullscreen()
        self.deiconify()

    def _make_menu (self, *args, **kw) :
        menu = ColorMenu(self, tearoff=False, *args, **kw)
        for seq_str in ('2', '3') :
            self.bind('<ButtonRelease-%s>' % seq_str, menu.post)

        return menu

    def fullscreen (self, fill=True) :
        if fill :
            self.update_idletasks()
            self.overrideredirect(True)

            try :
                self.attributes('-topmost', True)
            except tk.TclError :
                pass

            try :
                self.wm_state('zoomed')
            except tk.TclError :
                width  = str(self.winfo_screenwidth())
                height = str(self.winfo_screenheight())
                self.geometry('%sx%s+0+0' % (width, height))
        else :
            self.update_idletasks()
            self.overrideredirect(False)

            try :
                self.attributes('-topmost', False)
            except tk.TclError :
                pass

            self.wm_state('normal')
            self.geometry('200x200+100+100')

def __run__ () :
    ''' This launches the monitor cleaning tool aplication. '''

    try :
        color = sys.argv[1]
    except IndexError :
        color = 'black'

    main_win = MainWin(color=color)
    main_win.mainloop()

if __name__ == '__main__' :
    __run__()

