#!/usr/bin/python3
#NOTE: only works with mplayer2


__author__ = 'jd'
from gi.repository import Gtk, GdkPixbuf, Gdk
import requests
import untangle
import subprocess
import threading



"""
TODO
- style using CSS (improve the looks)
- add youtube support


"""


class CampusSearch():
    def __init__(self):

        #Playing status

        self.isPlaying = False
        self.process = None


        #Create main window
        self.window = Gtk.Window(title="CampusSearch", type=Gtk.WindowType.TOPLEVEL)
        self.window.set_border_width(10)
        #Name for CSS
        self.window.set_name('campussearch')

        #Create background image overlay so we can put widgets on top of background image
        #self.overlay = Gtk.Overlay()
        #self.window.add(self.overlay)


        #pixbuf = GdkPixbuf.Pixbuf.new_from_file('/home/jd/Pictures/Wallpapers/techcon.jpg')
        #Adjust the size of the image to match the screen

        #Get the size of the monitor (because window.get_size() fails)
        #s = self.window.get_screen()
        #m = s.get_monitor_at_window(s.get_active_window())
        #monitor = s.get_monitor_geometry(m)

        #print("Monitor =>  Height: %s, Width: %s" % (monitor.height, monitor.width))

        #scaled_pixbuf = pixbuf.scale_simple(monitor.width, monitor.height, GdkPixbuf.InterpType.BILINEAR)



        #self.background = Gtk.Image.new_from_pixbuf(scaled_pixbuf)

        #Create top-level layout container
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, opacity=0.5)
        self.vbox.set_name("vbox")

        #Add title
        title_label = Gtk.Label("CampusSearch")
        title_label.set_name("title")
        #title_label.set_markup("<b></b>")
        title_label.set_size_request(80,70)
        self.vbox.add(title_label)
        #Create horizontal top row
        self.header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        #self.vbox.pack_start(self.header, True, True, 30)
        self.vbox.add(self.header)

        self.addSearchBox()
        self.addNowPlaying()
        self.addResultList()
        self.addFooter()
        #Apply CSS
        self.applyCSS()

        #self.overlay.add(self.background)
        #self.overlay.add_overlay(self.vbox)

        self.window.add(self.vbox)

        #self.overlay.show_all()

        #Terminate app on window close
        self.window.connect("delete-event", self.shutdown)
        #Add global key handler
        self.vbox.connect("key_press_event", self.globalKeyPress)


        self.window.show_all()

        #Show the window
        self.window.fullscreen()
        self.window.show_all()

        #Focus the searchbox
        self.searchbox.grab_focus()
        self.hideNowPlaying()

####### GUI setup functions

    def applyCSS(self):
        style_provider = Gtk.CssProvider()

        css = """

            #campussearch {
                background-color : #C8C9F3;

            }

            #campussearch GtkContainer {
                background-color : #C8C9F3;

            }

            #title {
                color : blue;
                padding-top : 50px;
                padding-bottom : 50px;
                font-size : 25px;
                font-weight : bold;
            }

            #footer {
                color : blue;
                font-size : 13px;

            }

            #campussearch .entry {
                border-radius: 3px;
                border-style: solid;
                border-width: 1px;
            }

            #campussearch GtkListBoxRow {
                color : black;
                background-color : transparent;
                



            }

            #campussearch GtkListBoxRow:focus {
                color : blue;
                background-color : #dedfff;
                border-style: inset;
                border-width : 1px;
                transition: 300ms ease-in-out;
            }



            #campussearch GtkBox {
                background-color : transparent;
                padding-left : 100px;
                padding-right : 100px;
                padding-top : 100px;
            }

            #campussearch GtkLabel {

                padding-left : 100px;

            }




            #campussearch GtkScrolledWindow {
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
        #Arguments: widget, expand, fill, padding
        self.vbox.pack_start(self.scrollwindow, True, True, 30)

        #Add signal handlers
        self.result_list.connect("keynav-failed", self.listNavFailed)
        #self.result_list.connect("key_press_event", self.listKeyPress)
        #self.result_list.connect("key_press_event", self.resultKeyPress)






    def addSearchBox(self):
        self.searchbox = Gtk.Entry(width_request=10)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        box.pack_start(self.searchbox, True, True, 30)
        self.header.pack_start(box, True, True, 50)
        #Extra box for spacing
        self.header.pack_start(Gtk.Box(), True, True, 50)
        #Add signal handler
        #box.connect("key_press_event", self.stopPropagation)
        self.searchbox.connect("key_press_event", self.searchKeyPress)

    def addResultItem(self, title, smb_url, share_name):
        row = Gtk.ListBoxRow()
        item = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        item.add(Gtk.Label(title, xalign=0))
        item.add(Gtk.Label(smb_url, xalign=0, selectable=True))
        item.add(Gtk.Label(share_name, xalign=0))
        row.result_data = {"title" : title, "smb_url" : smb_url, "share_name" : share_name}
        row.add(item)
        self.result_list.add(row)

        #add signal handler
        row.connect("key_press_event", self.resultKeyPress)



    def addNowPlaying(self):
        self.nowPlayingBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.nowPlayingLabel = Gtk.Label("", xalign=0)
        self.nowPlayingIcon = Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_PLAY, 2)
        self.nowPlayingBox.add(self.nowPlayingIcon)
        self.nowPlayingBox.add(self.nowPlayingLabel)
        self.header.pack_end(self.nowPlayingBox, False, False, 30)

    def addFooter(self):
        self.footerbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.footerbar.set_name("footer")
        self.footerbar.add(Gtk.Label("Escape: quit/stop"))
        self.footerbar.add(Gtk.Label("Arrow keys: navigate"))
        self.footerbar.add(Gtk.Label("Enter: search/play"))
        self.footerbar.add(Gtk.Label("Other key: type"))
        self.vbox.pack_end(self.footerbar, False, False, 5)




########Signal Handlers


# Keys:
#  - 65307 = escape
#  - 65293 = enter
#  - 65364 = down
#  - 65362 = up
#  - 65288 = backspace


    def searchKeyPress(self, widget, key_event):
        #enter
        if key_event.keyval == 65293:
            #print("SearchBox: enter pressed")
            searchstring = widget.get_text()
            #print("Searchstring: " + searchstring)
            widget.set_text("")
            self.doSearch(searchstring)
        #down
        if key_event.keyval == 65364:
            self.result_list.grab_focus()



    def stopPropagation(self, widget, key_event):
        #Return True to stop further propagation of the event
        return True


    def resultKeyPress(self, widget, key_event):
        #enter
        if key_event.keyval == 65293:
            #print("ResultItem : enter pressed")
            #print(widget.result_data)
            self.doPlay(widget.result_data["smb_url"], widget.result_data["title"])




    #def listKeyPress(self, widget, key_event):
    #    print("list key press event yo")
    #    print(key_event.keyval)

    def globalKeyPress(self, widget, key_event):
        #backspace
        if key_event.keyval == 65288:
            self.endPlay()
        elif key_event.keyval == 65307: # escape
            if self.isPlaying:
                self.endPlay()
            else:
                self.shutdown()
        elif key_event.keyval == 65364: #down
            #do nothing
            pass
        elif key_event.keyval == 65362: #up
            #do nothing
            pass
        else:
            self.searchbox.grab_focus()
            self.searchbox.set_text(key_event.string)
            self.searchbox.set_position(1)
        #elif key_event == 65293: #enter
        #65364 down




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

        params = { "q" : searchstring, 'n' : 500}
        result = requests.get(url, params=params)

        if result.status_code == requests.codes.ok:
            parsed_xml = untangle.parse(result.text)

            #list of results
            try:
                results = parsed_xml.campus_search.result
            except IndexError:
                return


            #Add the results
            for result in results:
                if result.type.cdata == "file":

                    self.addResultItem(result.name.cdata, result.full_path.cdata, result.netbios_name.cdata)


            #Make the results show up
            self.scrollwindow.show_all()

        else:
            print("Error: sending request to campussearch failed")

    def doPlay(self, smb_url, title):
        thread = threading.Thread(target=self.playThreaded, args=(smb_url, self.endPlay))
        self.isPlaying = True
        self.showNowPlaying(title)
        thread.start()

    def playThreaded(self, smb_url, on_exit):
        try:
            self.process = subprocess.Popen(["mpv", "-fs", "--hwdec=vdpau", "--fs-screen=1",  smb_url])
            self.process.wait()
        except FileNotFoundError:
            print("Error: mpv binary not found")
        on_exit()

    def endPlay(self):
        self.isPlaying = False
        if not self.process == None:
            self.process.poll()
            if self.process.returncode == None:
                self.process.terminate()
        self.hideNowPlaying()

    def showNowPlaying(self, title):
        self.nowPlayingLabel.set_text(title)
        self.nowPlayingBox.show_all()


    def hideNowPlaying(self):
        self.nowPlayingBox.hide()


    def resetResults(self):
        self.vbox.remove(self.scrollwindow)
        self.addResultList()

    def shutdown(self, *args):
        if self.isPlaying:
            self.endPlay()

        Gtk.main_quit
        exit(0)



if __name__ == "__main__":
    cs = CampusSearch()


    Gtk.main()
