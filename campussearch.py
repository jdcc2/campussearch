#!/usr/bin/python3

__author__ = 'jd'
from gi.repository import Gtk, GdkPixbuf, Gdk
import requests
import untangle
import subprocess
import threading

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

        #Playing status

        self.isPlaying = False
        self.playing = ""

        #Create main window
        self.window = Gtk.Window(title="CampusSearch", type=Gtk.WindowType.TOPLEVEL)
        self.window.set_border_width(10)

        #Create background image overlay so we can put widgets on top of background image
        self.overlay = Gtk.Overlay()
        #self.window.add(self.overlay)


        pixbuf = GdkPixbuf.Pixbuf.new_from_file('/home/jd/Pictures/Wallpapers/techcon.jpg')
        #Adjust the size of the image to match the screen

        #Get the size of the monitor (because window.get_size() fails)
        s = self.window.get_screen()
        m = s.get_monitor_at_window(s.get_active_window())
        monitor = s.get_monitor_geometry(m)

        print("Monitor =>  Height: %s, Width: %s" % (monitor.height, monitor.width))

        scaled_pixbuf = pixbuf.scale_simple(monitor.width, monitor.height, GdkPixbuf.InterpType.BILINEAR)



        self.background = Gtk.Image.new_from_pixbuf(scaled_pixbuf)






        #Create top-level layout container
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, opacity=0.5)
        self.vbox.set_name("vbox")


        self.addSearchBox()
        self.addResultList()
        #Apply CSS
        self.applyCSS()


        self.overlay.add(self.background)
        self.overlay.add_overlay(self.vbox)



        self.overlay.show_all()

        #Terminate app on window close
        self.window.connect("delete-event", Gtk.main_quit)



        self.window.show_all()

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
                background-color : orange;



            }

            GtkBox {
                background-color : transparent;
                padding-left : 100px;
                padding-right : 100px;
            }

            GtkLabel {

                padding-left : 100px;
            }

            GtkScrolledWindow {
                background-color : transparent;
                margin-right : 200px;
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

        #Add signal handlers
        self.result_list.connect("keynav-failed", self.listNavFailed)
        #self.result_list.connect("key_press_event", self.resultKeyPress)


    def resetResults(self):
        self.vbox.remove(self.scrollwindow)
        self.addResultList()



    def addSearchBox(self):
        self.searchbox = Gtk.Entry()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        box.pack_start(self.searchbox, True, True, 50)
        self.vbox.pack_start(box, False, False, 30)

        #Add signal handler
        self.searchbox.connect("key_press_event", self.searchKeyPress)

    def addResultItem(self, title, smb_url, share_name):
        row = Gtk.ListBoxRow()
        item = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        item.add(Gtk.Label(title, xalign=0))
        item.add(Gtk.Label(smb_url, xalign=0))
        item.add(Gtk.Label(share_name, xalign=0))
        row.result_data = {"title" : title, "smb_url" : smb_url, "share_name" : share_name}
        row.add(item)
        self.result_list.add(row)

        #add signal handler
        row.connect("key_press_event", self.resultKeyPress)









########Signal Handlers

    def searchKeyPress(self, widget, key_event):
        if key_event.keyval == 65293:
            #print("SearchBox: enter pressed")
            searchstring = widget.get_text()
            #print("Searchstring: " + searchstring)
            widget.set_text("")
            self.doSearch(searchstring)

    def resultKeyPress(self, widget, key_event):

        if key_event.keyval == 65293:
            #print("ResultItem : enter pressed")
            #print(widget.result_data)
            self.doPlay(widget.result_data["smb_url"])


    def listNavFailed(self, widget, direction):
        if direction == Gtk.DirectionType.UP:
            self.searchbox.grab_focus()

########Functions

    def doSearch(self, searchstring):

        print("doSearch")
        #Clear the previous results
        self.resetResults()

        #Make the request
        url = "http://search.student.utwente.nl/api/search"

        params = { "q" : searchstring}
        result = requests.get(url, params=params)

        if result.status_code == requests.codes.ok:
            parsed_xml = untangle.parse(result.text)

            #list of results
            results = parsed_xml.campus_search.result

            print(len(results))
            #Add the results
            for result in results:
                if result.type.cdata == "file":

                    self.addResultItem(result.name.cdata, result.full_path.cdata, result.netbios_name.cdata)


            #Make the results show up
            self.window.show_all()

        else:
            print("Error: sending request to campussearch failed")

    def doPlay(self, smb_url):
        thread = threading.Thread(target=self.playThreaded, args=(smb_url, self.endPlay))
        self.isPlaying = True
        self.playing = smb_url
        thread.start()

    def playThreaded(self, smb_url, on_exit):
        self.process = subprocess.Popen(["mplayer", smb_url])
        self.process.wait()
        on_exit()

    def endPlay(self):
        self.isPlaying = False
        self.playing = ""



if __name__ == "__main__":

    cs = CampusSearch()


    Gtk.main()