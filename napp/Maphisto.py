from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys, os
from FloorMap import FloorMap
from SObject import SObject
import numpy as np
import cv2
from matplotlib import cm
from pathlib import Path


class EditableMap(QLabel):
    def __init__(self, parent=None):
        super(EditableMap, self).__init__(parent)
        self.edit = False
        self.parent = parent

        self.begin, self.destination, self.pin = QPoint(), QPoint(), QPoint()

    def paintEvent(self, QPaintEvent):
        super(EditableMap, self).paintEvent(QPaintEvent)
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.img)
        painter.setPen(QPen(Qt.gray))
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
            painter.setPen(QPen(Qt.gray))
            rect = QRect(self.begin, self.destination)
            painter.drawRect(rect.normalized())

            pos = [
                self.begin.x(),
                self.begin.y(),
                self.destination.x(),
                self.destination.y(),
            ]
            uvs = [
                [self.begin.y(), self.begin.x()],
                [self.destination.y(), self.destination.x()],
            ]

            currentRoom = self.parent.currentRoom
            currentObjInd = self.parent.currentObjInd
            updateObj = True

            for uv in uvs:
                val = self.parent.floorMap.roomSeg[uv[0], uv[1]]
                if val != currentRoom + 1:
                    updateObj = False

            if updateObj:
                self.parent.floorMap.rooms[currentRoom].objects[
                    currentObjInd
                ].position = pos
            else:
                print("Object not in selected room!")

            self.begin, self.destination = QPoint(), QPoint()
            self.update()


class Example(QWidget):
    def __init__(self, parent):
        super(Example, self).__init__()
        self.map_name = "data/JMap/JMap.png"
        self.data_folder = os.path.split(os.path.abspath(self.map_name))[0] + "/"
        self.floorMap = FloorMap(self.data_folder + "floor.config")
        self.mode = 5
        self.check_buttons = 2
        self.initUI()

    def initUI(self):

        QToolTip.setFont(QFont("SansSerif", 10))
        # QMainWindow.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 250, 150)
        self.resize(1500, 480)
        self.center()

        self.semMapID = 0
        self.currentRoom = 0
        self.currentObjLabel = 0
        self.currentObjId = -1
        self.currentObjInd = -1
        self.check_on = np.zeros(len(self.floorMap.classes))

        # the map visualization
        self.orig_map = cv2.imread(self.map_name)
        image = QImage(
            self.orig_map,
            self.orig_map.shape[1],
            self.orig_map.shape[0],
            self.orig_map.shape[1] * 3,
            QImage.Format_RGB888,
        )
        self.orig_pix = QPixmap(image)
        self.edit_pix = QPixmap(image)

        self.main_image = EditableMap(self)
        self.main_image.img = self.orig_pix
        self.main_image.setPixmap(self.orig_pix)

        self.main_image.setAlignment(Qt.AlignCenter)
        h, w, c = self.floorMap.map.shape
        self.main_image.setFixedSize(w, h)

        self.highlightSelectedRoom()
        self.semMapID = len(self.floorMap.classes) + 1
        self.drawObjects(self.semMapID)
        self.refresh_selected_objects()

        # refresh map from unsaved stuff
        refresh_map_btn = QPushButton("Refresh")
        refresh_map_btn.clicked.connect(self.refreshmap)

        # file browser for finding maps
        btn_browse = QPushButton("Choose Map")
        btn_browse.clicked.connect(self.browse)

        # room selection combobox
        room_selection = QHBoxLayout()
        room_sel_label = QLabel("Rooms", self)
        self.cb = QComboBox()
        for r in range(len(self.floorMap.rooms)):
            self.cb.addItem(self.floorMap.rooms[r].name + f" [{str(r)}]")

        self.cb.currentIndexChanged.connect(self.roomselectionchange)
        room_selection.addWidget(room_sel_label)
        room_selection.addWidget(self.cb)

        # room name
        btn_set_room_name = QPushButton("Name")
        btn_set_room_name.clicked.connect(self.setRoomName)
        room_name_label = QLabel("Room Name")
        self.room_name_edit = QLineEdit()
        self.room_name_edit.setText(self.floorMap.rooms[self.currentRoom].name)
        box_room_name = QHBoxLayout()
        box_room_name.addWidget(room_name_label)
        box_room_name.addWidget(self.room_name_edit)
        box_room_name.addWidget(btn_set_room_name)

        # room selection combobox
        room_category_selection = QHBoxLayout()
        room_category_label = QLabel("Room Category", self)
        self.cb_cat = QComboBox()
        for cat in self.floorMap.categories:
            self.cb_cat.addItem(cat)

        self.cb_cat.currentIndexChanged.connect(self.roomcategoryselectionchange)
        room_category_selection.addWidget(room_category_label)
        room_category_selection.addWidget(self.cb_cat)
        catID = self.floorMap.rooms[self.currentRoom].purpose
        self.cb_cat.setCurrentIndex(catID)

        # object list
        self.list_objects = QListWidget()
        self.list_objects.setAlternatingRowColors(True)
        for o in range(len(self.floorMap.rooms[self.currentRoom].objects)):
            obj = self.floorMap.rooms[self.currentRoom].objects[o]
            self.list_objects.addItem(
                self.floorMap.classes[obj.semLabel] + " - " + str(obj.id)
            )
        self.list_objects.setWindowTitle("Objects")
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
        sem_class_label = QLabel("Label", self)
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

        # Semantic label check boxes
        self.sem_label_box = QVBoxLayout()
        self.sem_index = []

        # ----Create Checkboxes
        for i in range(len(self.floorMap.classes)):
            self.sem_index.insert(i, QCheckBox(self.floorMap.classes[i]))
            self.sem_label_box.addWidget(self.sem_index[i])
            self.sem_index[i].stateChanged.connect(self.check_clicked)

        # 'All' btn
        self.all_check = QPushButton("All")
        self.all_check.setText("All")
        self.sem_label_box.addWidget(self.all_check)
        self.all_check.clicked.connect(self.btn_clicked)

        # 'None' btn
        none_check = QPushButton("None")
        none_check.setText("None")
        self.sem_label_box.addWidget(none_check)
        none_check.clicked.connect(self.btn_clicked)

        # Layout
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(btn_browse, 0, 0, 1, 2)  # 'Choose Map'
        grid.addLayout(room_selection, 1, 0, 1, 2)  # 'Rooms
        grid.addLayout(box_room_name, 2, 0, 1, 2)  # 'Room Name'
        # grid.addLayout(box_room_purpose, 4, 0, 1, 2)
        grid.addLayout(room_category_selection, 3, 0, 1, 1)  # 'Room Category'
        grid.addLayout(sem_class_selection, 3, 1, 1, 1)  # 'Label'
        grid.addWidget(self.list_objects, 4, 0, 2, 2)  # Box with objects
        grid.addWidget(add_obj_btn, 6, 0, 1, 1)  # 'Add'
        grid.addWidget(remove_obj_btn, 6, 1, 1, 1)  # 'Remove
        grid.addWidget(self.edit_obj_btn, 7, 0, 1, 1)  # 'Edit'
        grid.addWidget(save_obj_btn, 7, 1, 1, 1)  # 'Save'

        grid.addWidget(self.main_image, 1, 2, 6, 1)  # Map
        grid.addWidget(refresh_map_btn, 7, 2, 2, 1)  # 'Refresh'

        grid.addLayout(self.sem_label_box, 2, 3, 7, 1)  # Checkboxes
        self.setLayout(grid)

        self.show()

    def highlightSelectedRoom(self):

        ind = np.where(self.floorMap.roomSeg == self.currentRoom + 1)

        highlight = self.orig_map.copy()

        highlight[ind] = [120, 120, 120]
        self.highlight_map = highlight

        image = QImage(
            self.highlight_map,
            self.highlight_map.shape[1],
            self.highlight_map.shape[0],
            self.highlight_map.shape[1] * 3,
            QImage.Format_RGB888,
        )

        self.edit_pix = QPixmap(image)
        self.main_image.img = self.edit_pix
        self.main_image.setPixmap(self.edit_pix)

    def drawObjects(self, semLabel, objId=-1):
        # Picks a colour for every semantic label
        clr = cm.rainbow(np.linspace(0, 1, len(self.floorMap.classes)))
        self.drawn_map = self.highlight_map.copy()
        noDrawInd = len(self.floorMap.classes) + 1

        if semLabel != noDrawInd:
            for roomID, room in enumerate(self.floorMap.rooms):
                on_array = np.where(self.check_on == 1)
                for obj in room.objects:
                    if obj.semLabel in on_array[0]:
                        color = 255 * clr[obj.semLabel, :3]
                        x1, y1, x2, y2 = obj.position
                        if (objId == obj.id) and (roomID == self.currentRoom):
                            cv2.rectangle(self.drawn_map, (x1, y1), (x2, y2), color, -1)
                        else:
                            cv2.rectangle(self.drawn_map, (x1, y1), (x2, y2), color, 1)

        if semLabel == "All":
            pass

        image = QImage(
            self.drawn_map,
            self.drawn_map.shape[1],
            self.drawn_map.shape[0],
            self.drawn_map.shape[1] * 3,
            QImage.Format_RGB888,
        )
        self.edit_pix = QPixmap(image)
        self.main_image.img = self.edit_pix
        self.main_image.setPixmap(self.edit_pix)

    # Allows selected objects to be visible of the map
    # ---Can be combined with refresh and drawObjects in order to optimize #ToDo
    def refresh_selected_objects(self):
        self.drawn_map = self.highlight_map.copy()

        # Picks a colour for every semantic label
        clr = cm.rainbow(np.linspace(0, 1, len(self.floorMap.classes)))

        for roomID, room in enumerate(self.floorMap.rooms):
            on_array = np.where(self.check_on == 1)
            for obj in room.objects:

                if obj.semLabel in on_array[0]:
                    color = 255 * clr[obj.semLabel, :3]
                    x1, y1, x2, y2 = obj.position
                    # Displays the selected object as a filled-in rectangle
                    if obj.id == self.currentObjId and roomID == self.currentRoom:
                        cv2.rectangle(self.drawn_map, (x1, y1), (x2, y2), color, -1)
                    # Displays the other objects as empty rectangles
                    else:
                        cv2.rectangle(self.drawn_map, (x1, y1), (x2, y2), color, 1)
        image = QImage(
            self.drawn_map,
            self.drawn_map.shape[1],
            self.drawn_map.shape[0],
            self.drawn_map.shape[1] * 3,
            QImage.Format_RGB888,
        )
        self.edit_pix = QPixmap(image)
        self.main_image.img = self.edit_pix
        self.main_image.setPixmap(self.edit_pix)

    def refreshmap(self):

        image = QImage(
            self.orig_map,
            self.orig_map.shape[1],
            self.orig_map.shape[0],
            self.orig_map.shape[1] * 3,
            QImage.Format_RGB888,
        )
        self.orig_pix = QPixmap(image)

        self.main_image.img = self.orig_pix
        self.main_image.setPixmap(self.orig_pix)

        objID = -1
        if len(self.floorMap.rooms[self.currentRoom].objects):
            obj = self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd]
            objID = obj.id

        self.highlightSelectedRoom()
        self.drawObjects(self.semMapID, objID)
        self.refresh_selected_objects()

    def setRoomName(self):
        roomName = self.room_name_edit.text()
        self.floorMap.rooms[self.currentRoom].name = roomName

    def setRoomPurpose(self):

        self.floorMap.rooms[self.currentRoom].purpose = self.room_purpose_edit.text()

    def roomcategoryselectionchange(self, i):
        self.floorMap.rooms[self.currentRoom].purpose = i

    def roomselectionchange(self, i):
        self.currentRoom = i
        self.room_name_edit.setText(self.floorMap.rooms[self.currentRoom].name)
        # self.room_purpose_edit.setText(self.floorMap.rooms[self.currentRoom].purpose)

        catID = self.floorMap.rooms[self.currentRoom].purpose
        self.cb_cat.setCurrentIndex(catID)

        self.list_objects.clear()
        for o in range(len(self.floorMap.rooms[self.currentRoom].objects)):
            obj = self.floorMap.rooms[self.currentRoom].objects[o]
            self.list_objects.addItem(
                self.floorMap.classes[obj.semLabel] + " - " + str(obj.id)
            )

        objID = -1
        if len(self.floorMap.rooms[self.currentRoom].objects):
            self.currentObjInd = 0
            self.list_objects.setCurrentRow(self.currentObjInd)
            obj = self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd]
            self.cb2.setCurrentIndex(obj.semLabel)
            objID = obj.id

        self.highlightSelectedRoom()
        self.drawObjects(self.semMapID, objID)
        self.refresh_selected_objects()

    def semclassselectionchange(self, i):
        self.currentObjLabel = i
        self.floorMap.rooms[self.currentRoom].objects[
            self.currentObjInd
        ].semLabel = self.currentObjLabel

    def browse(self):
        w = QWidget()
        w.resize(320, 240)
        w.setWindowTitle("Select Picture")
        filename = QFileDialog.getOpenFileName(w, "Open File", "/")
        self.map_name = filename[0]

        self.orig_map = cv2.imread(self.map_name)
        image = QImage(
            self.orig_map,
            self.orig_map.shape[1],
            self.orig_map.shape[0],
            self.orig_map.shape[1] * 3,
            QImage.Format_RGB888,
        )
        self.orig_pix = QPixmap(image)
        self.edit_pix = QPixmap(image)

        self.main_image.img = self.orig_pix
        self.main_image.setPixmap(self.orig_pix)

        self.data_folder = os.path.split(os.path.abspath(self.map_name))[0] + "/"
        self.floorMap = FloorMap(self.data_folder + "floor.config")
        h, w, c = self.floorMap.map.shape
        self.main_image.setFixedSize(w, h)

        if len(self.floorMap.rooms):
            self.currentRoom = 0
            self.room_name_edit.setText(self.floorMap.rooms[self.currentRoom].name)
            # self.room_purpose_edit.setText(self.floorMap.rooms[self.currentRoom].purpose)
            catID = self.floorMap.rooms[self.currentRoom].purpose
            self.cb_cat.setCurrentIndex(catID)

            self.cb.clear()
            for r in range(len(self.floorMap.rooms)):
                self.cb.addItem(str(r))

            self.list_objects.clear()
            for o in range(len(self.floorMap.rooms[self.currentRoom].objects)):
                obj = self.floorMap.rooms[self.currentRoom].objects[o]
                self.list_objects.addItem(
                    self.floorMap.classes[obj.semLabel] + " - " + str(obj.id)
                )

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

        self.highlightSelectedRoom()
        self.semMapID = len(self.floorMap.classes) + 1
        self.drawObjects(self.semMapID)
        self.refresh_selected_objects()

    def addobject(self):

        self.floorMap.rooms[self.currentRoom].AddObject()
        objs = self.floorMap.rooms[self.currentRoom].objects

        # self.floorMap.rooms[self.currentRoom].objects.append(obj)
        # objs = self.floorMap.rooms[self.currentRoom].objects
        self.currentObjInd = len(objs) - 1
        obj = objs[self.currentObjInd]
        self.list_objects.addItem(
            self.floorMap.classes[obj.semLabel] + " - " + str(obj.id)
        )
        self.cb2.setCurrentIndex(obj.semLabel)
        self.list_objects.setCurrentRow(self.currentObjInd)

    def removeobject(self):

        self.floorMap.rooms[self.currentRoom].RemoveObject(self.currentObjInd)
        # self.floorMap.rooms[self.currentRoom].objects.pop(self.currentObjInd)
        self.list_objects.takeItem(self.currentObjInd)

        objs = self.floorMap.rooms[self.currentRoom].objects
        self.currentObjInd = len(objs) - 1
        obj = objs[self.currentObjInd]
        self.cb2.setCurrentIndex(obj.semLabel)
        self.list_objects.setCurrentRow(self.currentObjInd)

    def editobject(self):
        if self.currentObjInd != -1:
            self.main_image.edit = not self.main_image.edit
        else:
            print("Select object!")
            self.edit_obj_btn.toggle()

    def saveobject(self):
        print("Saved!")
        self.floorMap.Dump(self.data_folder + "floor.config")

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # Runs when a checkbox is checked
    def check_clicked(self):
        rbtn = self.sender()
        text = rbtn.text()

        if rbtn.isChecked():
            semMapID = self.floorMap.classes.index(text)
            self.check_on[semMapID] = 1
            obj = self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd]
            self.drawObjects(semMapID, obj.id)
            self.refresh_selected_objects()

        else:
            semMapID = self.floorMap.classes.index(text)
            self.check_on[semMapID] = 0
            obj = self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd]
            self.drawObjects(semMapID, obj.id)
            self.refresh_selected_objects()

    # Runs when a 'All' or 'None' is clicked
    def btn_clicked(self, value):
        rbtn = self.sender()
        text = rbtn.text()
        if text == "All":
            # Checks all semantic checkboxes
            self.check_buttons = 1
            for i in range(len(self.floorMap.classes)):
                self.sem_index[i].setChecked(True)
            self.refresh_selected_objects()
        else:
            # Unchecks all semantic checkboxes
            self.check_buttons = 0
            for i in range(len(self.floorMap.classes)):
                self.sem_index[i].setChecked(False)
            self.refresh_selected_objects()

    def object_clicked(self, item):
        self.currentObjInd = self.list_objects.selectedIndexes()[0].row()
        obj = self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd]
        self.cb2.setCurrentIndex(obj.semLabel)
        # Sets self.currentObjId to the id of the selected object
        self.currentObjId = (
            self.floorMap.rooms[self.currentRoom].objects[self.currentObjInd].id
        )
        self.drawObjects(self.semMapID, obj.id)
        self.refresh_selected_objects()


class Maphisto(QMainWindow):
    def __init__(self, parent=None):
        super(Maphisto, self).__init__(parent)
        self.form_widget = Example(self)
        self.setCentralWidget(self.form_widget)

        self.initUI()

    def initUI(self):
        exitAction = QAction(QIcon("exit.png"), "&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(qApp.quit)
        menubar = self.menuBar()
        # fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(exitAction)

        # self.toolbar = self.addToolBar('Exit')
        # self.toolbar.addAction(exitAction)

        # self.statusBar().showMessage('Ready')
        self.setWindowTitle("Maphisto")
        self.setWindowIcon(QIcon(str(Path("data/icons/icon.png"))))

    def closeEvent(self, event):

        reply = QMessageBox.question(
            self, "Message", "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    # Stylesheet
    with open(Path("napp/stylesheets/ubuntu.qss"), "r",) as f:
        style = f.read()
        app.setStyleSheet(style)
    # ex = Example()
    menubar = Maphisto()
    menubar.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
