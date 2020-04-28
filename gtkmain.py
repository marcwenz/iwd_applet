from gi.repository import Gtk, GLib, Gdk
import gi
gi.require_version('Gtk', '3.0')
from random import random
from devices import Manager


class MyWindow(Gtk.Window):

    def __init__(self):
        super().__init__(type=Gtk.WindowType.POPUP)
        # self.move((2560-280)/2, y+30)
        self.man = Manager()

        self.init_ui()

        self.set_position(Gtk.WindowPosition.MOUSE)
        ds = self.get_display()
        dm = ds.list_seats()[0]
        _, x, y = dm.get_pointer().get_position()
        mm = ds.get_monitor_at_point(x, y).get_geometry()

        off_x, off_y = self._calc_offset(self.get_size(), (mm.width, mm.height), self._adjust_pt_pos(x, y, mm))

        self.move(x + off_x, y + off_y)


        print(x, y)

    def _calc_offset(self, win_dim, mon_dim, pt_pos):
        # calculates neccessary offset for window
        offs = []
        for win, mon, pt in zip(win_dim, mon_dim, pt_pos):
            if win > mon - pt:
                offs.append(-win)
            else:
                offs.append(0)
        return offs

    def _adjust_pt_pos(self, pt_x, pt_y, mm):
        return (pt_x - mm.x, pt_y - mm.y)

    def init_ui(self):

        self.box = Gtk.Box().new(Gtk.Orientation.VERTICAL, 3)
        self.add(self.box)

        wifi_name = Gtk.Label().new("Network name")
        refresh_btn = Gtk.Button().new_with_label("Refresh")
        refresh_btn.connect("clicked", self.update_net_data)
        top_box = Gtk.Box().new(Gtk.Orientation.HORIZONTAL, 3)
        top_box.pack_start(wifi_name, 0, 0, 0)
        top_box.pack_end(refresh_btn, 0, 0, 0)

        self.wifi_strength = Gtk.ProgressBar().new()
        self.wifi_strength.set_fraction(0.5)

        quit = Gtk.Button().new_with_label("Quit")
        quit.connect("clicked", self.on_button_clicked)

        self.nets = self.update_network_display(networks=self.man.past_nets)

        self.box.pack_start(top_box, 0, 0, 0)
        self.box.pack_start(self.wifi_strength, 0, 0, 0)
        self.box.pack_start(self.nets, 0, 0, 0)
        self.box.pack_end(quit, 0, 0, 0)

        self.set_border_width(10)
        self.set_title("Quit button")
        self.set_default_size(280, 280)
        self.connect("destroy", Gtk.main_quit)

        self.timeout_id = GLib.timeout_add(500, self.on_timeout)

    def on_button_clicked(self, widget):
        Gtk.main_quit()

    def on_timeout(self):
        """
        Update value on the progress bar
        """
        self.wifi_strength.set_fraction(random())
        return True

    def update_net_data(self, w):
        self.man.scan()
        self.update_check = GLib.timeout_add(500, self.check_has_changed)
        # ll = Gtk.Label().new('ttt')
        # self.box.pack_end(ll, 0, 0, 0)

    def check_has_changed(self):
        # Activated by update_net_data, checks whether scan has changed network list
        if self.man._net_has_changed():
            self.nets.destroy()
            self.nets = self.update_network_display(self.man.past_nets)
            self.box.pack_start(self.nets, 0, 0, 0)
            self.show_all()
            return False
        return True

    def update_network_display(self, networks):
        # updates network list
        nets = Gtk.Box().new(Gtk.Orientation.VERTICAL, 3)
        for network in networks:
            ll = Gtk.Label().new(network['Name'] + ', ' + str(network['rssi']))
            if network['Connected']:
                ll.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.0, 1.0, 0.0, 1.0))
            nets.pack_start(ll, 0, 0, 0)
        print('Networks updated')
        return nets

if __name__ == "__main__":
    win = MyWindow()
    win.show_all()
    Gtk.main()
