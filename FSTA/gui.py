#!/usr/bin/env python
# -*- coding:utf-8 -*

# Projet : FSTA
#           Un assistant vocale
#
#   gui.py :
#       une interace graphique (pour ajout d'un écran)
#



from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import time, sys

class FstaGui(QMainWindow):
    '''Une interface graphique pour FSTA
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FSTA")
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 480, 320)
        self.UiComponents()
        self.show()

    def UiComponents(self):
        '''Crée les composants
        '''
        #self.showMaximized() #Fullscreen
        self.eyes= Eyes(self, width = self.width(), height = self.height(), pictures = {'normal' : './img/eyes_normal.png', 'bas' : './img/eyes_bas.png'})


class Eyes(QWidget):
    '''Des yeux qui s'animent
    '''
    def __init__(self, parent = None, pictures = None, **kwargs):
        '''pictures : a dict {face : image_file}
        '''
        super().__init__(parent)
        self.pictures = pictures or {}
        self.left = kwargs.get('left',10)
        self.top = kwargs.get('top',10)
        self.width = kwargs.get('width',64*5)
        self.height = kwargs.get('height',43*5)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.label = QLabel(self)
        if self.pictures:
            self.change_etat(list(self.pictures)[0])
        #self.label.adjustSize()

    def set_picture(self, filename):
        '''Set the picture
        '''
        pixmap = QPixmap(filename)
        self.label.setPixmap(pixmap.scaled(self.width, self.height, Qt.KeepAspectRatio))

    def change_etat(self, etat):
        '''Change l'image selon état
        '''
        if self.pictures.get(etat):
            self.set_picture(self.pictures.get(etat))


if __name__ == '__main__':
    app = QApplication([])
    sta = FstaGui()
    while True:
        sta.eyes.change_etat('normal')
        app.processEvents()
        time.sleep(1)
        sta.eyes.change_etat('bas')
        app.processEvents()
        time.sleep(1)
    sys.exit(app.exec_())
