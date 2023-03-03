#!/usr/bin/env python

''' A basic GUi to use ImageViewer class to show its functionalities and use cases. '''

from PyQt5 import QtCore, QtWidgets, uic, QtWidgets
from PyQt5.QtWidgets import QKeySequenceEdit, QPushButton, QLabel, QScrollArea, QFormLayout
from PyQt5.QtGui import QKeySequence
from actions import ImageViewer
import sys, os
import shutil

gui = uic.loadUiType("main.ui")[0]     # load UI file designed in Qt Designer
VALID_FORMAT = ('.BMP', '.GIF', '.JPG', '.JPEG', '.PNG', '.PBM', '.PGM', '.PPM', '.TIFF', '.XBM')  # Image formats supported by Qt

def getImages(folder):
    ''' Get the names and paths of all the images in a directory. '''
    image_list = []
    if os.path.isdir(folder):
        for file in os.listdir(folder):
            if file.upper().endswith(VALID_FORMAT):
                im_path = os.path.join(folder, file)
                image_obj = {'name': file, 'path': im_path }
                image_list.append(image_obj)
    return image_list

class Iwindow(QtWidgets.QMainWindow, gui):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.qlabel_image.setFocusPolicy(QtCore.Qt.TabFocus) # set focus policy

        self.cntr, self.numImages = -1, -1  
        self.saved_cntr, self.num_saveImages = -1, -1
        self.saved_folder = None

        self.image_viewer = ImageViewer(self.qlabel_image)
        self.__connectEvents()
        self.showMaximized()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        if e.key() == QtCore.Qt.Key_A:
            self.prevImg()
        if e.key() == QtCore.Qt.Key_S:
            self.nextImg()
        if e.key() == QtCore.Qt.Key_O:
            self.image_viewer.zoomPlus()
        if e.key() == QtCore.Qt.Key_I:
            self.image_viewer.zoomMinus()
        if e.key() == QtCore.Qt.Key_R:
            self.image_viewer.resetZoom()
        if e.key() == QtCore.Qt.Key_D:
            self.saveImg()

    def __connectEvents(self):
        self.open_folder.clicked.connect(self.selectDir)
        self.save_folder.clicked.connect(self.selectsaveDir)
        self.next_im.clicked.connect(self.nextImg)
        self.prev_im.clicked.connect(self.prevImg)
        self.qlist_images.itemClicked.connect(self.item_click)
        # self.qlist_save_images.itemClicked.connect(self.item_click)
        self.save_im.clicked.connect(self.saveImg)

        self.zoom_plus.clicked.connect(self.image_viewer.zoomPlus)
        self.zoom_minus.clicked.connect(self.image_viewer.zoomMinus)
        self.reset_zoom.clicked.connect(self.image_viewer.resetZoom)

        # self.toggle_line.toggled.connect(self.action_line)
        # self.toggle_rect.toggled.connect(self.action_rect)
        self.toggle_move.toggled.connect(self.action_move)

    def selectDir(self):
        ''' Select a directory, make list of images in it and display the first image in the list. '''
        # open 'select folder' dialog box
        self.folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not self.folder:
            QtWidgets.QMessageBox.warning(self, 'No Folder Selected', 'Please select a valid Folder')
            return
        
        self.logs = getImages(self.folder)
        self.numImages = len(self.logs)

        # make qitems of the image names
        self.items = [QtWidgets.QListWidgetItem(log['name']) for log in self.logs]
        self.num_label_1.setText(f'Num: {len(self.items)}')
        self.qlist_images.clear()
        for item in self.items:
            self.qlist_images.addItem(item)

        # display first image and enable Pan 
        self.cntr = 0
        self.image_viewer.enablePan(True)
        self.image_viewer.loadImage(self.logs[self.cntr]['path'])
        self.items[self.cntr].setSelected(True)
        #self.qlist_images.setItemSelected(self.items[self.cntr], True)

        # enable the next image button on the gui if multiple images are loaded
        if self.numImages > 1:
            self.next_im.setEnabled(True)
    
    def selectsaveDir(self):
        ''' Select a directory to save images, make list of images in it and display the first image in the list. '''
        # open 'select folder' dialog box
        self.saved_folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not self.saved_folder:
            self.saved_folder = None
            QtWidgets.QMessageBox.warning(self, 'No Folder Selected', 'Please select a valid Folder')
            return
        
        labelList = []
        buttonList = []
        self.subfolders = os.listdir(self.saved_folder)
        self.num_subfolders = len(self.subfolders)

        self.qformlayout = QFormLayout()

        for i in range(self.num_subfolders):
            labelList.append(QLabel(f"{self.subfolders[i]}"))
            buttonList.append(QPushButton("Save"))
            self.qformlayout.addRow(labelList[i], buttonList[i])
        
        self.groupBox.setLayout(self.qformlayout)


    def saveImg(self):
        if self.saved_folder is not None:
            current_image_path = self.logs[self.cntr]['path']
            f_name = current_image_path.split('/')[-1]
            shutil.copyfile(current_image_path, self.saved_folder + f'/{f_name}')
            # QtWidgets.QMessageBox.warning(self, 'OK', f'You have already saved the image at {self.saved_folder}!')

            #make them appear on the widget
            self.saved_logs = getImages(self.saved_folder)
            self.num_saveImages = len(self.saved_logs)
            self.num_label_2.setText(f'Num: {len(self.saved_logs)}')
            # make qitems of the image names
            self.qlist_save_images.clear()
            self.saved_items = [QtWidgets.QListWidgetItem(log['name']) for log in self.saved_logs]
            for item in self.saved_items:
                self.qlist_save_images.addItem(item)        
        else:
            QtWidgets.QMessageBox.warning(self, 'Sorry', 'You have not choosen a folder to save!')        

    def resizeEvent(self, evt):
        if self.cntr >= 0:
            self.image_viewer.onResize()

    def nextImg(self):
        if self.cntr < self.numImages -1:
            self.cntr += 1
            self.image_viewer.loadImage(self.logs[self.cntr]['path'])
            self.items[self.cntr].setSelected(True)
            #self.qlist_images.setItemSelected(self.items[self.cntr], True)
        else:
            QtWidgets.QMessageBox.warning(self, 'Sorry', 'No more Images!')

    def prevImg(self):
        if self.cntr > 0:
            self.cntr -= 1
            self.image_viewer.loadImage(self.logs[self.cntr]['path'])
            self.items[self.cntr].setSelected(True)
            #self.qlist_images.setItemSelected(self.items[self.cntr], True)
        else:
            QtWidgets.QMessageBox.warning(self, 'Sorry', 'No previous Image!')

    def item_click(self, item):
        self.cntr = self.items.index(item)
        self.image_viewer.loadImage(self.logs[self.cntr]['path'])

    def action_line(self):
        if self.toggle_line.isChecked():
            self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
            self.image_viewer.enablePan(False)

    def action_rect(self):
        if self.toggle_rect.isChecked():
            self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
            self.image_viewer.enablePan(False)

    def action_move(self):
        if self.toggle_move.isChecked():
            self.qlabel_image.setCursor(QtCore.Qt.OpenHandCursor)
            self.image_viewer.enablePan(True)

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))
    app.setPalette(QtWidgets.QApplication.style().standardPalette())
    parentWindow = Iwindow(None)
    sys.exit(app.exec_())

if __name__ == "__main__":
    #print __doc__
    main()