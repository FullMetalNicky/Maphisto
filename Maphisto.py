from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys, os
from FloorMap import FloorMap
from SObject import SObject

class myQLabel(QLabel):
    def __init__(self,parent=None):
        super(myQLabel, self).__init__(parent)
        self.edit = False

        self.begin, self.destination, self.pin = QPoint(), QPoint(), QPoint()   

    def paintEvent(self, QPaintEvent):
        super(myQLabel, self).paintEvent(QPaintEvent)
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.img)
        painter.setPen(QPen(Qt.red))
        rect = QRect(self.begin, self.destination)
        painter.drawRect(rect.normalized())


    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton & self.edit:
            self.begin = event.pos()
            self.destination = self.begin
            self.update()
        elif event.buttons() & Qt.RightButton:
            self.pin = event.pos()
            print("pin object")
            self.update()
        

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton & self.edit:     
            self.destination = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() & Qt.LeftButton & self.edit:
            painter = QPainter(self.img)
            painter.setPen(QPen(Qt.red))
            rect = QRect(self.begin, self.destination)
            painter.drawRect(rect.normalized())

            print(self.begin.x(), self.begin.y(), self.destination.x(), self.destination.y())

            self.begin, self.destination = QPoint(), QPoint()
            self.update()

class Example(QWidget):

    def __init__(self,parent):
        super(Example, self).__init__()
        self.map_name="/home/nickybones/Code/Maphisto/nmap/data/SMap.png"
        self.data_folder = os.path.split(os.path.abspath(self.map_name))[0] + "/"
        self.floorMap = FloorMap(self.data_folder + "floor.config")
        self.mode = 5
        self.initUI()

    def initUI(self):
        
        QToolTip.setFont(QFont('SansSerif', 10))
        #QMainWindow.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 250, 150)
        self.resize(1500, 480)
        self.center()



        self.semMapID = 0
        self.currentRoom = 0
        self.currentObjLabel = 0
        self.currentObjInd = -1

        # the map visualization
        self.main_image = myQLabel(self)
        self.main_image.img = QPixmap(self.map_name)
        self.main_image.setPixmap(QPixmap(self.map_name))
        self.main_image.setAlignment(Qt.AlignCenter)
        h, w, c = self.floorMap.map.shape
        self.main_image.setFixedSize(w, h)

        # refresh map from unsaved stuff
        refresh_map_btn = QPushButton("Refresh")
        refresh_map_btn.clicked.connect(self.refreshmap)

        # file browser for finding maps
        btn_browse = QPushButton("Choose Map")
        btn_browse.clicked.connect(self.browse)
        
        # room selection combobox
        room_selection = QHBoxLayout()
        room_sel_label = QLabel('Rooms', self)
        self.cb = QComboBox()
        for r in range(len(self.floorMap.rooms)):
            self.cb.addItem(str(r))
        
        self.cb.currentIndexChanged.connect(self.roomselectionchange)
        room_selection.addWidget(room_sel_label)
        room_selection.addWidget(self.cb)

        # room name
        btn_set_room_name = QPushButton("Name")
        btn_set_room_name.clicked.connect(self.setRoomName)
        room_name_label = QLabel('Name')
        self.room_name_edit = QLineEdit()
        self.room_name_edit.setText(self.floorMap.rooms[self.currentRoom].name)
        box_room_name = QHBoxLayout()
        box_room_name.addWidget(room_name_label)
        box_room_name.addWidget(self.room_name_edit)
        box_room_name.addWidget(btn_set_room_name)
       

        # room purpose
        btn_set_purpose = QPushButton("Purpose")
        btn_set_purpose.clicked.connect(self.setRoomPurpose)
        room_purpose_label = QLabel('Purpose')
        self.room_purpose_edit = QLineEdit()
        self.room_purpose_edit.setText(self.floorMap.rooms[self.currentRoom].purpose)
        box_room_purpose = QHBoxLayout()
        box_room_purpose.addWidget(room_purpose_label)
        box_room_purpose.addWidget(self.room_purpose_edit)
        box_room_purpose.addWidget(btn_set_purpose)

        # object list
        self.list_objects = QListWidget()
        for o in range(len(self.floorMap.rooms[self.currentRoom].objects)):
            obj = self.floorMap.rooms[self.currentRoom].objects[o]
            self.list_objects.addItem(str(obj.id))
        self.list_objects.setWindowTitle('Objects')
        self.list_objects.itemClicked.connect(self.object_clicked)


        # add object button
        add_obj_btn = QPushButton("Add")
        add_obj_btn.clicked.connect(self.addobject)

        # remove object button
        remove_obj_btn = QPushButton("Remove")
        remove_obj_btn.clicked.connect(self.removeobject)
        # remove object button
        remove_obj_btn = QPushButton("Remove")
        remove_obj_btn.clicked.connect(self.removeobject)
         # edit object button
        self.edit_obj_btn = QPushButton("Edit")
        self.edit_obj_btn.setCheckable(True)
        self.edit_obj_btn.clicked.connect(self.editobject)
        # save object button
        save_obj_btn = QPushButton("Save")
        save_obj_btn.clicked.connect(self.saveobject)



        # sem label selection combobox
        sem_class_selection = QHBoxLayout()
        sem_class_label = QLabel('Label', self)
        self.cb2 = QComboBox()
        for i in range(len(self.floorMap.classes)):
            self.cb2.addItem(self.floorMap.classes[i])
        
        self.cb2.currentIndexChanged.connect(self.semclassselectionchange)
        sem_class_selection.addWidget(sem_class_label)
        sem_class_selection.addWidget(self.cb2)

        if len(self.floorMap.rooms[self.currentRoom].objects):
            self.currentObjInd = 0
            obj = self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd]
            self.cb2.setCurrentIndex(obj.semLabel)
            self.list_objects.setCurrentRow(self.currentObjInd)


        # sem label radio
        sem_label_box = QVBoxLayout()
        sem_label_group = QButtonGroup() # Number group

        for i in range(len(self.floorMap.classes)):
            r=QRadioButton(self.floorMap.classes[i])
            sem_label_group.addButton(r)
            sem_label_box.addWidget(r)
            r.toggled.connect(self.radio_clicked)

       
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(btn_browse, 1 , 0, 1, 2)
        grid.addLayout(room_selection, 2, 0, 1, 2)
        grid.addLayout(box_room_name, 3, 0, 1, 2)
        grid.addLayout(box_room_purpose, 4, 0, 1, 2)
        grid.addWidget(self.list_objects, 5, 0, 4, 1)
        grid.addWidget(add_obj_btn , 5, 1, 1, 1)
        grid.addWidget(remove_obj_btn , 6, 1, 1, 1)
        grid.addWidget(self.edit_obj_btn , 7, 1, 1, 1)
        grid.addWidget(save_obj_btn , 8, 1, 1, 1)


        grid.addLayout(sem_class_selection, 10, 0, 1, 2)

        grid.addWidget(self.main_image, 2, 2, 5, 1)
        grid.addWidget(refresh_map_btn, 7, 2, 1, 1)

        grid.addLayout(sem_label_box, 2, 3, 7, 1)
        self.setLayout(grid)

        self.show()
   
    def refreshmap(self):

        self.main_image.setPixmap(QPixmap(self.map_name))
        self.main_image.img = QPixmap(self.map_name)

    def setRoomName(self):

        self.floorMap.rooms[self.currentRoom].name = self.room_name_edit.text()

    def setRoomPurpose(self):

        self.floorMap.rooms[self.currentRoom].purpose = self.room_purpose_edit.text()

    def roomselectionchange(self, i):
     
        self.currentRoom = i
        self.room_name_edit.setText(self.floorMap.rooms[self.currentRoom].name)
        self.room_purpose_edit.setText(self.floorMap.rooms[self.currentRoom].purpose)
        self.list_objects.clear()
        for o in range(len(self.floorMap.rooms[self.currentRoom].objects)):
            obj = self.floorMap.rooms[self.currentRoom].objects[o]
            self.list_objects.addItem(str(obj.id))

        if len(self.floorMap.rooms[self.currentRoom].objects):
            self.currentObjInd = 0
            self.list_objects.setCurrentRow(self.currentObjInd)
            obj = self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd]
            self.cb2.setCurrentIndex(obj.semLabel)

    def semclassselectionchange(self, i):

        print("Current sem label {} selection changed".format(i))
        self.currentObjLabel = i
        self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd].semLabel = self.currentObjLabel


    def browse(self):
        w = QWidget()
        w.resize(320, 240)
        w.setWindowTitle("Select Picture")
        filename = QFileDialog.getOpenFileName(w, 'Open File', '/')
        self.map_name = filename[0]
        self.main_image.setPixmap(QPixmap(self.map_name))
        self.main_image.img = QPixmap(self.map_name)
        self.data_folder = os.path.split(os.path.abspath(self.map_name))[0] + "/"
        self.floorMap = FloorMap(self.data_folder + "floor.config")
        h, w, c = self.floorMap.map.shape
        self.main_image.setFixedSize(w, h)

        if len(self.floorMap.rooms):
            self.currentRoom = 0
            self.room_name_edit.setText(self.floorMap.rooms[self.currentRoom].name)
            self.room_purpose_edit.setText(self.floorMap.rooms[self.currentRoom].purpose)
            self.list_objects.clear()
            for o in range(len(self.floorMap.rooms[self.currentRoom].objects)):
                obj = self.floorMap.rooms[self.currentRoom].objects[o]
                self.list_objects.addItem(str(obj.id))

            if len(self.floorMap.rooms[self.currentRoom].objects):
                self.currentObjInd = 0
                self.list_objects.setCurrentRow(self.currentObjInd)
                obj = self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd]
                self.cb2.setCurrentIndex(obj.semLabel)
        else:
            self.currentObjInd = 0
            self.list_objects.clear()
            self.cb.clear()
            self.cb2.setCurrentIndex(0)




    def addobject(self):

        obj = self.floorMap.rooms[self.currentRoom].CreateObject()
        self.floorMap.rooms[self.currentRoom].objects.append(obj)
        objs = self.floorMap.rooms[self.currentRoom].objects
        self.currentObjInd = len(objs) - 1
        self.list_objects.addItem(str(obj.id))
        self.cb2.setCurrentIndex(obj.semLabel)
        self.list_objects.setCurrentRow(self.currentObjInd)

    def removeobject(self):

        self.floorMap.rooms[self.currentRoom].objects.pop(self.currentObjInd)
        self.list_objects.takeItem(self.currentObjInd)

        objs = self.floorMap.rooms[self.currentRoom].objects
        self.currentObjInd = len(objs) - 1
        self.cb2.setCurrentIndex(obj.semLabel)
        self.list_objects.setCurrentRow(self.currentObjInd)


    def editobject(self):
        if self.currentObjInd != -1:
            self.main_image.edit = not self.main_image.edit
        else:
            print("Selcet object!")
            self.edit_obj_btn.toggle()


    def saveobject(self):
        print("saved!")
        self.floorMap.Dump(self.data_folder + "floor.config")

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def radio_clicked(self, value):

        rbtn = self.sender()

        if rbtn.isChecked() == True:
            self.semMapID = self.floorMap.classes.index(rbtn.text())


    def object_clicked(self, item):
        #print(self.list_objects.selectedIndexes()[0].row())
        self.currentObjInd = self.list_objects.selectedIndexes()[0].row()
        obj = self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd]
        self.cb2.setCurrentIndex(obj.semLabel)

    # def paintEvent( self, event) :
    #     pass

class Maphisto(QMainWindow):
    def __init__(self, parent=None):
        super(Maphisto, self).__init__(parent)
        self.form_widget = Example(self)
        self.setCentralWidget(self.form_widget)

        self.initUI()

    def initUI(self):
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        menubar = self.menuBar()
        #fileMenu = menubar.addMenu('&File')
        #fileMenu.addAction(exitAction)

        #self.toolbar = self.addToolBar('Exit')
        #self.toolbar.addAction(exitAction)

        #self.statusBar().showMessage('Ready')
        self.setWindowTitle('Maphisto')
        #self.setWindowIcon(QIcon('icon.png'))

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    #ex = Example()
    menubar = Maphisto()
    menubar.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()