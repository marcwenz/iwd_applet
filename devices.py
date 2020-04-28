import dbus
import collections
from station import Station

bus = dbus.SystemBus()


class Manager:

    def __init__(self):
        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(bus.get_object("net.connman.iwd", "/"), "org.freedesktop.DBus.ObjectManager")
        self.station_path, self.station = self._get_stations()[0] # initialise station to be first
        self.past_nets = self._get_networks()

    def _get_managed_objects(self):
        # Returns object of all managed objects
        return self.manager.GetManagedObjects()

    def _get_networks(self, objects=None, station=None):
        """
        Gets list of dicts containing network information
        """
        if not objects:
            objects = self._get_managed_objects()
        if not station:
            station = self._get_device_station(self.station_path)
        networks = []
        for path3, rssi in station.GetOrderedNetworks():
            networks.append({'path': str(path3), 'rssi': int(rssi)})
            properties2 = objects[path3]['net.connman.iwd.Network']
            for key in properties2:
                val = properties2[key]
                if type(val) == dbus.Boolean:
                    val = True if val else False
                    networks[-1][str(key)] = bool(val)
                else:
                    networks[-1][str(key)] = str(val)
        return networks

    def _get_known_networks(self, objects=None, station=None):
        # gets known networks
        if not objects:
            objects = self._get_managed_objects()
        if not station:
            station = self._get_device_station(self.station_path)
        networks = []
        for path, interfaces in self._get_managed_objects().items():
            if 'net.connman.iwd.KnownNetwork' not in interfaces:
                continue

            network = interfaces['net.connman.iwd.KnownNetwork']
            networks.append({'ssid': str(network['Name']), 'path': str(path)})

            for key in network:
                val = network[key]
                if type(val) == dbus.Boolean:
                    val = True if val else False
                    networks[-1][str(key)] = bool(val)
                else:
                    networks[-1][str(key)] = str(val)
        return networks

    def _query_station(self, station_path, update=False):
        # return ix if station found, otherwise -1
        stations = self._get_stations()
        for ix, (path, station) in enumerate(stations):
            if station_path == path:
                if update:
                    self.station_path, self.station = path, station
                return ix
        return -1

    def _get_stations(self, objects=None):
        dev = []
        if not objects:
            objects = self._get_managed_objects()
        for oo in objects:
            # Loops over all network interfaces
            oo_prop = objects[oo]
            if 'net.connman.iwd.Device' not in oo_prop.keys():
                continue
            dev.append((oo, oo_prop))
        return dev

    def _is_station_connected(self, station):
        # return true if station is connected to a nework
        pass

    def _get_device_device(self, device=None):
        if not device:
            device = self.station
        return device["net.connman.iwd.Device"]

    def _get_device_station_stat(self, device=None):
        if not device:
            device = self.station
        # gets properties Connected NW (path), Scanning (bool), State (connected/...)
        return device["net.connman.iwd.Station"]

    def _get_device_station(self, path=None):
        if not path:
            path = self.station_path
        return dbus.Interface(self.bus.get_object("net.connman.iwd", path),
                                     'net.connman.iwd.Station')

    def _get_current_network(self, station=None):
        # returns current network; -1 as failsafe
        if not station:
            station = self.station
        cn = self._get_device_station_stat(station)['ConnectedNetwork']
        for network in man._get_networks():
            if network['path'] == cn:
                return network
        raise KeyError('Current Network not found')

    def _get_network(self, path=None):
        return dbus.Interface(bus.get_object('net.connman.iwd', path), 'net.connman.iwd.Network')

    def scan(self, station=None):
        if not station:
            station = self._get_device_station()
        station.Scan()
        return 1

    def _net_has_changed(self):
        if (nets := self._get_networks()) != self.past_nets:
            self.past_nets = nets
            return True
        return False

if __name__ == '__main__':
    from time import sleep
    man = Manager()
    print(man.past_nets)
    print(man.scan())
    sleep(1.0)
    nc = man._net_has_changed()
    print(nc)
    print(man.past_nets)

    
# manager = dbus.Interface(bus.get_object("net.connman.iwd", "/"), "org.freedesktop.DBus.ObjectManager")
# objects = manager.GetManagedObjects()
# Obj = collections.namedtuple('Obj', ['interfaces', 'children'])
# tree = Obj({}, {})
# for path in objects:
    # node = tree
    # elems = path.split('/')
    # for subpath in ['/'.join(elems[:l + 1]) for l in range(1, len(elems))]:
        # if subpath not in node.children:
            # node.children[subpath] = Obj({}, {})
        # node = node.children[subpath]
    # node.interfaces.update(objects[path])
# root = tree.children['/net'].children['/net/connman'].children['/net/connman/iwd']

# for path, phy in root.children.items():
    # # Loops over all network interfaces
    # if 'net.connman.iwd.Adapter' not in phy.interfaces:
        # continue

    # properties = phy.interfaces['net.connman.iwd.Adapter']

    # # print("[ %s ]" % path)

    # for key in properties:
        # # Loops ove all properties
        # val = properties[key]
        # if key == 'SupportedModes':
            # val = [str(mode) for mode in val]
        # # print("    %s = %s" % (key, val))

    # # print("    Devices:")

    # for path2, device in phy.children.items():
        # # Loops over all network devices
        # if 'net.connman.iwd.Device' not in device.interfaces:
            # continue

        # print("    [ %s ]" % path2)
        # for interface in device.interfaces:
            # # Loops over macro classes of device
            # name = interface.rsplit('.', 1)[-1]
            # if name not in ('Device', 'Station', 'AccessPoint', 'AdHoc'):
                # continue

            # properties = device.interfaces[interface]
            # for key in properties:
                # # Loops over properties and state
                # val = properties[key]
                # print("        %s.%s = %s" % (name, key, val))

            # if name != 'Station':
                # continue

            # print("        Sorted networks:")

            # station = dbus.Interface(bus.get_object("net.connman.iwd", path2),
                                     # 'net.connman.iwd.Station')
            # # List networks
            # for path3, rssi in station.GetOrderedNetworks():
                # # Loops over all networks in range
                # print("        [ %s ]" % path3)

                # properties2 = objects[path3]['net.connman.iwd.Network']
                # [print(pp, properties2[pp]) for pp in properties2]
                # print("            SSID = %s" % (properties2['Name'],))
                # print("            Signal strength = %i dBm" % (rssi / 100,))
                # print("            Security = %s" % (properties2['Type'],))
