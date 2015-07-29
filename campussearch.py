#!/usr/bin/python3

__author__ = 'jd'
from gi.repository import Gtk, GdkPixbuf, Gdk
import requests

"""
TODO
- Catch keyboard events
- Handle arrow down on searchbox
- Check if keynav-failed event gets emitted on arrow up on upper boundary of list, if yes catch that event
- rescale background image to size of window
- use css to make the background of the layout containers transparent

"""


class CampusSearch():
    def __init__(self):

        #Create main window
        self.window = Gtk.Window(title="CampusSearch", type=Gtk.WindowType.TOPLEVEL)
        self.window.set_border_width(10)

        #Create background image overlay so we can put widgets on top of background image
        self.overlay = Gtk.Overlay()
        #self.window.add(self.overlay)


        pixbuf = GdkPixbuf.Pixbuf.new_from_file('/home/jd/Pictures/LA1.jpg')
        #Adjust the size of the image to match the screen

        #Get the size of the monitor (because window.get_size() fails)
        s = self.window.get_screen()
        m = s.get_monitor_at_window(s.get_active_window())
        monitor = s.get_monitor_geometry(m)

        print("Monitor =>  Height: %s, Width: %s" % (monitor.height, monitor.width))

        scaled_pixbuf = pixbuf.scale_simple(monitor.width - 50, monitor.height- 50, GdkPixbuf.InterpType.BILINEAR)



        self.background = Gtk.Image.new_from_pixbuf(scaled_pixbuf)
        self.overlay.add(self.background)





        #Create top-level layout container
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.vbox.set_name("vbox")

        self.overlay.add_overlay(self.vbox)


        #Terminate app on window close
        self.window.connect("delete-event", Gtk.main_quit)


        #Apply CSS
        self.applyCSS()

        self.addSearchBox()
        self.addResultList()

        for i in range(20):
            self.addResultItem(i ,i*10,i*100)



        self.connectSignals()

        ########WARNING###########
        #The following sequence of statements is the only way in which a background image gets drawn in a fullscreen window


        self.window.add(self.overlay)
        #Show the window
        self.window.fullscreen()
        self.window.show_all()


        #Add the background



        #Redraw to actually show the background
        self.window.show_all()

####### GUI setup functions

        def applyCSS(self):

        style_provider = Gtk.CssProvider()

        css = """


            GtkContainer {
                background-color : transparent;


            }

            GtkBox {
                padding-left : 100px;
                padding-right : 100px;
            }

            GtkLabel {

                padding-left : 100px;
            }


        """



        style_provider.load_from_data(bytes(css.encode()))

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def addResultList(self):
        self.scrollwindow = Gtk.ScrolledWindow()
        self.result_list = Gtk.ListBox()
        self.scrollwindow.add(self.result_list)
        #widget, expand, fill, padding
        self.vbox.pack_start(self.scrollwindow, True, True, 30)

    def resetResults(self):
        self.vbox.remove(self.scrollwindow)
        self.addResultList()



    def addSearchBox(self):
        self.searchbox = Gtk.Entry()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        box.pack_start(self.searchbox, True, True, 50)
        self.vbox.pack_start(box, False, False, 30)

    def addResultItem(self, title, smb_url, share_name):
        row = Gtk.ListBoxRow()
        item = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        item.add(Gtk.Label(title, xalign=0))
        item.add(Gtk.Label(smb_url, xalign=0))
        item.add(Gtk.Label(share_name, xalign=0))
        row.add(item)
        self.result_list.add(row)





    def connectSignals(self):
        self.result_list.connect("keynav-failed", self.listNavFailed)
        self.result_list.connect("key_press_event", self.resultKeyPress)
        self.searchbox.connect("key_press_event", self.searchKeyPress)


########Signal Handlers

    def searchKeyPress(self, widget, key_event):
        if key_event.keyval == 65293:
            print("SearchBox: enter pressed")
            searchstring = widget.get_text()
            print("Searchstring: " + searchstring)
            widget.set_text("")
            self.doSearch(searchstring)

    def resultKeyPress(self, widget, key_event):
        pass

    def listNavFailed(self, widget, direction):
        if direction == Gtk.DirectionType.UP:
            self.searchbox.grab_focus()

########Functions

    def doSearch(self, searchstring):
        pass

    def doAddResults(self, results):






if __name__ == "__main__":
    cs = CampusSearch()
    Gtk.main()