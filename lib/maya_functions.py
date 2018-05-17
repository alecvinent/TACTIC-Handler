# file maya_functions.py
# Maya Functions Module

import os
from lib.side.Qt import QtWidgets as QtGui

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
try:
    import shiboken as shiboken
except:
    import shiboken2 as shiboken

import tactic_classes as tc
from lib.environment import env_inst
import global_functions as gf


def get_maya_window():
    """
    Get the main Maya window as a QtGui.QMainWindow instance
    @return: QtGui.QMainWindow instance of the Maya windows
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is not None:
        return shiboken.wrapInstance(long(main_window_ptr), QtGui.QMainWindow)


def get_maya_dock_window():
    """
    Get the Maya dock window instance of Tactic Dock Window
    @return: QMayaDockWidget
    """
    maya_dock_instances = get_maya_window().findChildren(QtGui.QMainWindow, 'TacticHandlerDock')
    return maya_dock_instances


def open_scene(file_path, dir_path, all_process):
    # check if scene need saving
    new_scene = mel.eval('saveChanges("file -f -new")')
    if bool(new_scene):
        print('Opening: ' + file_path)
        # set_workspace(dir_path, all_process)
        cmds.file(file_path, open=True, force=True)

        # cmds.file(q=True, location=True)  #prtint current scene path


def import_scene(file_path):
    print('Importing: ' + file_path)
    cmds.file(file_path, i=True)


def reference_scene(file_path):
    print('Referencing: ' + file_path)
    cmds.file(file_path, r=True)


def get_skey_from_scene():
    skey = cmds.getAttr('defaultObjectSet.tacticHandler_skey')
    return skey


def export_selected(project_code, tab_code, wdg_code):

    current_type = cmds.optionVar(q='defaultFileExportActiveType')
    current_ext = cmds.translator(str(current_type), q=True, filter=True)
    current_ext = current_ext.split(';')[0]

    current_checkin_widget = env_inst.get_check_tree(project_code, tab_code, wdg_code)

    current_checkin_widget.save_file(selected_objects=[True, {current_type: current_ext[2:]}])


def save_as(project_code, tab_code, wdg_code):

    current_type = cmds.optionVar(q='defaultFileSaveType')
    current_ext = cmds.translator(str(current_type), q=True, filter=True)
    current_ext = current_ext.split(';')[0]

    current_checkin_widget = env_inst.get_check_tree(project_code, tab_code, wdg_code)

    current_checkin_widget.save_file(selected_objects=[False, {current_type: current_ext[2:]}])


def wrap_export_selected_options(project_code, tab_code, wdg_code):
    mel.eval('proc export_selection_maya(){python("' +
             "main.mf.export_selected('{0}', '{1}', '{2}')".format(project_code, tab_code, wdg_code) +
             '");}fileOptions "ExportActive" "export_selection_maya";')


def wrap_save_options(project_code, tab_code, wdg_code):
    mel.eval('proc save_as_maya(){python("' +
             "main.mf.save_as('{0}', '{1}', '{2}')".format(project_code, tab_code, wdg_code) +
             '");}fileOptions "SaveAs" "save_as_maya";')


def set_info_to_scene(search_key, context):
    # add info about particular scene
    skey_link = 'skey://{0}&context={1}'.format(search_key, context)
    if not cmds.attributeQuery('tacticHandler_skey', node='defaultObjectSet', exists=True):
        cmds.addAttr('defaultObjectSet', longName='tacticHandler_skey', dataType='string')
    cmds.setAttr('defaultObjectSet.tacticHandler_skey', skey_link, type='string')


def get_maya_info_dict():
    import maya.cmds as cmds

    info_dict = {
        'cs': cmds.about(cs=True),
        'uil': cmds.about(uil=True),
        'osv': cmds.about(osv=True),
        'os': cmds.about(os=True),
        'env': cmds.about(env=True),
        'a': cmds.about(a=True),
        'b': cmds.about(b=True),
        'p': cmds.about(p=True),
        'v': cmds.about(v=True),
    }
    return info_dict


def inplace_checkin(virtual_snapshot, repo_name, update_versionless, only_versionless=False, generate_icons=True,
                    selected_objects=False, ext_type='mayaAscii', setting_workspace=False):

    scene_name = virtual_snapshot[0][1]['versioned']['names'][0]
    scene_path = gf.form_path(repo_name['value'][0] + '/' + virtual_snapshot[0][1]['versioned']['paths'][0])
    playblast_name = virtual_snapshot[1][1]['versioned']['names'][0]
    playblast_path = gf.form_path(repo_name['value'][0] + '/' + virtual_snapshot[1][1]['versioned']['paths'][0])

    full_scene_path = scene_path + '/' + ''.join(scene_name)
    full_playblast_path = playblast_path + '/' + ''.join(playblast_name)

    # create dest dirs
    if not os.path.exists(scene_path):
        os.makedirs(scene_path)
    if not os.path.exists(playblast_path):
        os.makedirs(playblast_path)

    # saving maya scene
    try:
        if ext_type in ['mayaAscii', 'mayaBinary']:
            cmds.file(rename=full_scene_path)
        renamed = True
    except:
        renamed = False
    try:
        if selected_objects:
            if ext_type in ['mayaAscii', 'mayaBinary']:
                cmds.file(exportSelected=selected_objects, type=ext_type, pr=True, eur=True)
            else:
                cmds.file(full_scene_path, exportSelected=selected_objects, type=ext_type, pr=True, eur=True)
        else:
            cmds.file(save=True, type=ext_type)
        saved = True
    except:
        saved = False

    check_ok = True

    files_objects_list = []

    if renamed and saved:
        if setting_workspace:
            print 'SETTING WORKSPACE'
            # set_workspace(dest_scene_ver, all_process)

        # isolate selected to create proper playblast
        current_panel = cmds.paneLayout('viewPanes', q=True, pane1=True)
        if selected_objects:
            cmds.isolateSelect(current_panel, state=True)
            mel.eval('enableIsolateSelect {0} 1;'.format(current_panel))

        current_frame = cmds.currentTime(query=True)
        cmds.playblast(
            forceOverwrite=True,
            format='image',
            completeFilename=full_playblast_path,
            showOrnaments=False,
            widthHeight=[960, 540],
            sequenceTime=False,
            frame=[current_frame],
            compression='jpg',
            offScreen=False,
            viewer=False,
            percent=100
        )
        if selected_objects:
            cmds.isolateSelect(current_panel, state=False)
            mel.eval('enableIsolateSelect {0} 0;'.format(current_panel))

        match_template = gf.MatchTemplate(['$FILENAME.$EXT'])
        files_objects_dict = match_template.get_files_objects([full_scene_path, full_playblast_path], sort=False)

        maya_app_info_dict = get_maya_info_dict()
        for fl in files_objects_dict.get('file'):
            fl.set_app_info(maya_app_info_dict)
            files_objects_list.append(fl)

        file_paths = [[full_scene_path], [full_playblast_path]]

        check_ok = tc.inplace_checkin(
            file_paths,
            virtual_snapshot,
            repo_name,
            only_versionless,
            update_versionless,
            generate_icons,
            files_objects_list,
        )

    return check_ok, files_objects_list


def create_workspace(dir_path, all_process):
    # TODO create maya definition editor, with presets
    workspace = ['//Maya 2016 Project Definition\n\n']
    consts_list = {
        'fluidCache': '',
        'images': '',
        'offlineEdit': '',
        'furShadowMap': '',
        'iprImages': '',
        'scripts': '',
        'renderData': '',
        'fileCache': '',
        'eps': '',
        'shaders': '',
        '3dPaintTextures': '',
        'translatorData': '',
        'mel': '',
        'furFiles': '',
        'OBJ': '',
        'particles': '',
        'scene': '',
        'sourceImages': '',
        'furEqualMap': '',
        'clips': '',
        'furImages': '',
        'depth': '',
        'movie': '',
        'audio': '',
        'bifrostCache': '',
        'autoSave': '',
        'mayaAscii': '',
        'move': '',
        'sound': '',
        'diskCache': '',
        'illustrator': '',
        'mayaBinary': '',
        'templates': '',
        'OBJexport': '',
        'furAttrMap': '',
    }

    for const, val in consts_list.iteritems():
        if (const == 'scene') or (const == 'mayaAscii') or (const == 'mayaBinary'):
            for process in all_process:
                val += 'work/{0};'.format(process)
        workspace.append('workspace -fr "{0}" "{1}";\n'.format(const, val))

    workspace_file = open(dir_path + "/workspace.mel", "w")
    workspace_file.writelines(workspace)
    workspace_file.close()


def set_workspace(dir_path, all_process):
    create_workspace(dir_path, all_process)
    # print('Setting Workspace: {0}'.format(dir_path))
    mel.eval('setProject "{0}";'.format(dir_path))
    mel.eval('projectWindow;np_editCurrentProjectCallback;')
