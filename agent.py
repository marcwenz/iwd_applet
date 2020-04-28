from gi.repository import GLib

import dbus
import dbus.service
import dbus.mainloop.glib
import sys
from random import randrange


class Canceled(dbus.DBusException):
    _dbus_error_name = "net.connman.iwd.Error.Canceled"


class Agent(dbus.service.Object):
    passphrase = None

    @dbus.service.method("net.connman.iwd.Agent",
                         in_signature='', out_signature='')
    def Release(self):
        print("Release")
        mainloop.quit()

    @dbus.service.method("net.connman.iwd.Agent",
                         in_signature='o',
                         out_signature='s')
    def RequestPassphrase(self, path):
        """
        Called when Agent registers a connection to a network
        Invoke the password popup from here
        """
        print("RequestPassphrase (%s)" % (path))

        print("Service credentials requested, type cancel to cancel")
        passphrase = input('Answer: ')

        if not passphrase or passphrase == 'cancel':
            raise Canceled("canceled")

        print("returning (%s)" % (passphrase))
        return passphrase

    @dbus.service.method("net.connman.iwd.Agent",
                         in_signature='o',
                         out_signature='s')
    def RequestPrivateKeyPassphrase(self, path):
        print("RequestPrivateKeyPassphrase (%s)" % (path))

        print("Service credentials requested, type cancel to cancel")
        passphrase = input('Answer: ')

        if not passphrase or passphrase == 'cancel':
            raise Canceled("canceled")

        print("returning (%s)" % (passphrase))
        return passphrase

    @dbus.service.method("net.connman.iwd.Agent",
                         in_signature='o',
                         out_signature='ss')
    def RequestUserNameAndPassword(self, path):
        print("RequestPrivateKeyPassphrase (%s)" % (path))

        print("Service credentials requested, type cancel to cancel")
        user = input('User name: ')

        if not user or user == 'cancel':
            raise Canceled("canceled")

        passwd = input('User password: ')

        if not passwd or passwd == 'cancel':
            raise Canceled("canceled")

        print("returning (%s, %s)" % (user, passwd))
        return (user, passwd)

    @dbus.service.method("net.connman.iwd.Agent",
                         in_signature='s', out_signature='')
    def Cancel(self, reason):
        print("Cancel: " + reason)


def print_usage():
    print("Usage:")
    print("For WPA input:")
    print("%s Passphrase=<passphrase>" % (sys.argv[0]))
    print("Help: %s help" % (sys.argv[0]))
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "help":
        print_usage()

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object('net.connman.iwd',
                                            '/net/connman/iwd'),
                             'net.connman.iwd.AgentManager')

    path = "/test/agent/" + str(randrange(100))
    object = Agent(bus, path)

    if len(sys.argv) >= 2:
        for arg in sys.argv[1:]:
            if arg.startswith("Passphrase="):
                object.passphrase = arg.replace("Passphrase=", "", 1)
            else:
                print_usage()

    try:
        manager.RegisterAgent(path)
    except:
        print("Cannot register iwd agent.")

    mainloop = GLib.MainLoop()
    mainloop.run()
