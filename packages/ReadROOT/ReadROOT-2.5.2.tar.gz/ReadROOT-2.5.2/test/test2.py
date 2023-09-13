from spinmob import egg
from PyQt5 import QtGui, QtCore, QtWidgets
g = egg.gui

w = g.Window("Hallo")
def test():
    val =  QtWidgets.QFileDialog.getExistingDirectory(w._window)
    print(val)
    return val

b = w.place_object(g.Button("Press me!"))
b.signal_clicked.connect(test)

w.show(True)
