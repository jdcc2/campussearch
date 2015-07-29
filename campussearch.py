#!/usr/bin/python3

__author__ = 'jd'
from gi.repository import Gtk
import requests

"""
TODO
- Catch keyboard events
- Handle arrow down on searchbox
- Check if keynav-failed event gets emitted on arrow up on upper boundary of list, if yes catch that event

"""


class CampusSearch(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="CampusSearch")
        self.set_border_width(10)

        #overlay so we can put widgets ontop of background image
        self.overlay = Gtk.Overlay()
        #self.add(self.overlay)
        self.background = Gtk.Image.new_from_file('/home/jd/Pictures/Wallpapers/techcon.jpg')
        #self.overlay.add(self.background)


        self.result_list = Gtk.ListBox()
        #self.searchbox = SearchBox()

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.vbox.pack_start(self.result_list, False, False, 0)
        self.vbox.pack_start(Gtk.Entry(), False, False, 0)
        self.add(self.vbox)
        #self.overlay.add_overlay(self.vbox)

        self.fullscreen()

    def addResultItem(self, title, smb_url, share_name):
        row = Gtk.ListBoxRow()
        item = ResultItem(title, smb_url, share_name)
        row.add(item)
        self.result_list.add(row)


    def resetResults(self):
        self.vbox.remove(self.result_list)
        self.result_list = Gtk.ListBox()
        self.vbox.add(self.result_list)

#class SearchBox(Gtk.Entry):
#
 #   def __init__(self, defaulttext=""):
  #      self.set_text(defaulttext)



class ResultItem(Gtk.Box):
    def __init__(self, title, smb_url, share_name):
        self.add(Gtk.Label(title))
        pass

if __name__ == "__main__":
    win = CampusSearch()

    win.connect("delete-event", Gtk.main_quit)
    win.show_all()


    Gtk.main()