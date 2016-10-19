# file ui_drop_plate_classes.py

import os
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
# import lib.environment as env
from lib.environment import env_mode, env_inst
import lib.ui.checkin.ui_drop_plate as ui_drop_plate
# TODO create sequences parsing
# import lib.side.pyseq as pyseq

reload(ui_drop_plate)


# seqs = pyseq.get_sequences('//renderserver/Project/projectName/scenes/ep29/ep29sc27/compose/sequence/tif/v1')
# print(seqs)


def split_files_and_dirs(filename):
    dirs_list = []
    files_list = []
    for single in filename:
        if os.path.isdir(single):
            dirs_list.append(single)
        else:
            files_list.append(extract_filename(single))

    return dirs_list, files_list


def sequences_from_files(files_list):
    print(files_list)


def sequences_from_dirs(files_list):
    print(files_list)


def file_format(ext):
    formats = {
        'ma': 'mayaAscii',
        'mb': 'mayaBinary',
        'hip': 'Houdini',
        '3b': '3D-Coat',
        'max': '3DSMax scene',
        'scn': 'Softimage XSI',
        'mud': 'Mudbox',
        'abc': 'Alembic',
        'obj': 'OBJ',
        '3ds': '3DSMax model',
        'nk': 'Nuke',
        'fbx': 'FBX',
        'dae': 'COLLADA',
        'rs': 'Redshift Proxy',
        'vdb': 'Open VDB',
        'jpg': 'JPEG Image',
        'jpeg': 'JPEG Image',
        'psd': 'Photoshop PSD',
        'tif': 'TIFF Image',
        'tiff': 'TIFF Image',
        'png': 'PNG Image',
        'tga': 'TARGA Image',
        'exr': 'EXR Image',
        'hdr': 'HDR Image',
        'dpx': 'DPX Image',
        'mov': 'MOV Animation',
        'avi': 'AVI Animation',
    }
    if ext in formats.iterkeys():
        return formats[ext]
    else:
        return ext


def extract_extension(filename):
    # TODO Check for file without EXT
    ext = unicode(os.path.basename(filename)).split('.', -1)
    if not os.path.isdir(filename):
        if len(ext) > 1:
            return ext[-1], file_format(ext[-1])
    elif os.path.isdir(filename):
        return filename, 'Folder'


def extract_filename(filename):
    name = unicode(os.path.basename(filename)).split('.', 1)
    if len(name) > 1:
        return name[0] + '.' + name[1]
    else:
        return name[0]


def extract_dirname(filename):
    dir = unicode(os.path.realpath(filename)).split('.', 1)
    if len(dir) == 1 and not os.path.isdir(filename):
        return dir[0]
    else:
        return os.path.dirname(filename)


class Ui_dropPlateWidget(QtGui.QGroupBox, ui_drop_plate.Ui_dropPlateGroupBox):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent=parent)

        self.setupUi(self)

        self.setAcceptDrops(True)

        self.create_drop_plate_ui()
        self.controls_actions()

    def create_drop_plate_ui(self):

        self.setAcceptDrops(True)
        self.dropTreeWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        if env_mode.get_mode() == 'standalone':
            self.fromDropListCheckBox.setHidden(True)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
            self.setSizePolicy(sizePolicy)
            self.setMinimumWidth(300)

    def controls_actions(self):

        self.clearPushButton.clicked.connect(self.clear_tree_widget)
        self.groupCheckinCheckBox.stateChanged.connect(self.enable_group_checkin)

    def enable_group_checkin(self, state):

        if state:
            self.dropTreeWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
            self.keepFileNameCheckBox.setEnabled(False)
        else:
            self.dropTreeWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            self.dropTreeWidget.clearSelection()
            self.keepFileNameCheckBox.setEnabled(True)

    def clear_tree_widget(self):

        self.dropTreeWidget.clear()

    def append_items_to_tree(self, items):

        # file_dir_tuple = split_files_and_dirs(items)
        # print(file_dir_tuple)

        for item in items:
            tree_item = QtGui.QTreeWidgetItem()
            tree_item.setText(0, extract_filename(item))
            tree_item.setText(1, extract_extension(item)[1])
            tree_item.setData(1, QtCore.Qt.UserRole, extract_extension(item)[0])
            tree_item.setText(2, extract_dirname(item))
            self.dropTreeWidget.addTopLevelItem(tree_item)

        self.dropTreeWidget.resizeColumnToContents(0)
        self.dropTreeWidget.resizeColumnToContents(1)
        self.dropTreeWidget.resizeColumnToContents(2)
        self.dropTreeWidget.resizeColumnToContents(3)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(unicode(url.toLocalFile()))
            self.append_items_to_tree(links)
        else:
            event.ignore()