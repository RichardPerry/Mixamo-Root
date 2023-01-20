# -*- coding: utf-8 -*-

'''
    Copyright (C) 2022  Richard Perry
    Copyright (C) Average Godot Enjoyer (Johngoss725)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Note that Johngoss725's original contributions were published under a 
    Creative Commons 1.0 Universal License (CC0-1.0) located at
    <https://github.com/Johngoss725/Mixamo-To-Godot>.
'''

# Original Script Created By: Average Godot Enjoyer (Johngoss725)
# Bone Renaming Modifications, File Handling, And Addon By: Richard Perry
import bpy
import os
import logging
from pathlib import Path


log = logging.getLogger(__name__)

# in future remove_prefix should be renamed to rename prefix and a target prefix should be specifiable via ui
def fixBones(remove_prefix=False, name_prefix="mixamorig:"):
    bpy.ops.object.mode_set(mode = 'OBJECT')
        
    if not bpy.ops.object:
        log.warning('[Mixamo Root] Could not find amature object, please select the armature')

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.object.show_in_front = True

    if remove_prefix:
        for rig in bpy.context.selected_objects:
            if rig.type == 'ARMATURE':
                for mesh in rig.children:
                    for vg in mesh.vertex_groups:
                        new_name = vg.name
                        new_name = new_name.replace(name_prefix,"")
                        rig.pose.bones[vg.name].name = new_name
                        vg.name = new_name
                for bone in rig.pose.bones:
                    bone.name = bone.name.replace(name_prefix,"")
        for action in bpy.data.actions:
            fc = action.fcurves
            for f in fc:
                f.data_path = f.data_path.replace(name_prefix,"")
        
def scaleAll():
    bpy.ops.object.mode_set(mode='OBJECT')

    prev_context=bpy.context.area.type
        
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.context.area.type = 'GRAPH_EDITOR'
    bpy.context.space_data.dopesheet.filter_text = "Location"
    bpy.context.space_data.pivot_point = 'CURSOR'
    bpy.context.space_data.dopesheet.use_filter_invert = False
        
    bpy.ops.anim.channels_select_all(action='SELECT')   
        
    bpy.ops.transform.resize(value=(1, 0.01, 1), orient_type='GLOBAL',
    orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    orient_matrix_type='GLOBAL',
    constraint_axis=(False, True, False),
    mirror=True, use_proportional_edit=False,
    proportional_edit_falloff='SMOOTH',
    proportional_size=1,
    use_proportional_connected=False,
    use_proportional_projected=False)


def copyHips(root_bone_name="Root", hip_bone_name="mixamorig:Hips", name_prefix="mixamorig:"):
    bpy.context.area.ui_type = 'FCURVES'
    #SELECT OUR ROOT MOTION BONE 
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.context.object.pose.bones[name_prefix + root_bone_name].bone.select = True
    # SET FRAME TO ZERO
    bpy.ops.graph.cursor_set(frame=0.0, value=0.0)
    #ADD NEW KEYFRAME
    bpy.ops.anim.keyframe_insert_menu(type='Location')
    #SELECT ONLY HIPS AND LOCTAIUON GRAPH DATA
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.context.object.pose.bones[hip_bone_name].bone.select = True        
    bpy.context.area.ui_type = 'DOPESHEET'
    bpy.context.space_data.dopesheet.filter_text = "Location"
    bpy.context.area.ui_type = 'FCURVES'
    #COPY THE LOCATION VALUES OF THE HIPS AND DELETE THEM         
    bpy.ops.graph.copy()
    bpy.ops.graph.select_all(action='DESELECT')
    
    myFcurves = bpy.context.object.animation_data.action.fcurves
        
    for i in myFcurves:
        hip_bone_fcvurve = 'pose.bones["'+hip_bone_name+'"].location'
        if str(i.data_path)==hip_bone_fcvurve:
            myFcurves.remove(i)
                
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.context.object.pose.bones[name_prefix + root_bone_name].bone.select = True
    bpy.ops.graph.paste()        
        
    bpy.context.area.ui_type = 'VIEW_3D'
    bpy.ops.object.mode_set(mode='OBJECT')

    
def deleteArmature(imported_objects=set()):
    armature = None
    if bpy.context.selected_objects:
        armature = bpy.context.selected_objects[0]
    if imported_objects == set():
        log.warning("[Mixamo Root] No armature imported, nothing to delete")
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for obj in imported_objects:
            bpy.data.objects[obj.name].select_set(True)
        
    bpy.ops.object.delete(use_global=False, confirm=False)
    if bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = armature

def import_armature(filepath, root_bone_name="Root", hip_bone_name="mixamorig:Hips", remove_prefix=False, name_prefix="mixamorig:",  insert_root=False, delete_armatures=False):
    old_objs = set(bpy.context.scene.objects)
    if insert_root:
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.import_scene.fbx(filepath = filepath)#,  automatic_bone_orientation=True)
    else:
        bpy.ops.import_scene.fbx(filepath = filepath)#,  automatic_bone_orientation=True)
    
    imported_objects = set(bpy.context.scene.objects) - old_objs
    imported_actions = [x.animation_data.action for x in imported_objects if x.animation_data]
    print("[Mixamo Root] Now importing: " + str(filepath))
    imported_actions[0].name = Path(filepath).resolve().stem # Only reads the first animation associated with an imported armature
    
    if insert_root:
        add_root_bone(root_bone_name, hip_bone_name, remove_prefix, name_prefix)
    
    
def add_root_bone(root_bone_name="Root", hip_bone_name="mixamorig:Hips", remove_prefix=False, name_prefix="mixamorig:"):
    armature = bpy.context.selected_objects[0]
    bpy.ops.object.mode_set(mode='EDIT')

    root_bone = armature.data.edit_bones.new(name_prefix + root_bone_name)
    root_bone.tail.y = 30

    armature.data.edit_bones[hip_bone_name].parent = armature.data.edit_bones[name_prefix + root_bone_name]
    bpy.ops.object.mode_set(mode='OBJECT')

    fixBones(remove_prefix=remove_prefix, name_prefix=name_prefix)
    scaleAll()
    copyHips(root_bone_name=root_bone_name, hip_bone_name=hip_bone_name, name_prefix=name_prefix)

def push(obj, action, track_name=None, start_frame=0):
    # Simulate push :
    # * add a track
    # * add an action on track
    # * lock & mute the track
    # * remove active action from object
    tracks = obj.animation_data.nla_tracks
    new_track = tracks.new(prev=None)
    if track_name:
        new_track.name = track_name
    strip = new_track.strips.new(action.name, start_frame, action)
    obj.animation_data.action = None

def get_all_anims(source_dir, root_bone_name="Root", hip_bone_name="mixamorig:Hips", remove_prefix=False, name_prefix="mixamorig:",  insert_root=False, delete_armatures=False):
    files = os.listdir(source_dir)
    num_files = len(files)
    current_context = bpy.context.area.ui_type
    old_objs = set(bpy.context.scene.objects)
    
    for file in files:
        print("file: " + str(file))
        try:
            filepath = source_dir+"/"+file
            import_armature(filepath, root_bone_name, hip_bone_name, remove_prefix, name_prefix, insert_root, delete_armatures)
            imported_objects = set(bpy.context.scene.objects) - old_objs
            if delete_armatures and num_files > 1:
                deleteArmature(imported_objects)
                num_files -= 1


        except Exception as e:
            log.error("[Mixamo Root] ERROR get_all_anims raised %s when processing %s" % (str(e), file))
            return -1
    bpy.context.area.ui_type = current_context
    bpy.context.scene.frame_start = 0
    bpy.ops.object.mode_set(mode='OBJECT')

def apply_all_anims(delete_applied_armatures=False, control_rig=None, push_nla=False):
    if control_rig and control_rig.type == 'ARMATURE':
        bpy.ops.object.mode_set(mode='OBJECT')

        imported_objects = set(bpy.context.scene.objects)
        imported_armatures = [x for x in imported_objects if x.type == 'ARMATURE' and x.name != control_rig.name]

        for obj in imported_armatures:
            action_name = obj.animation_data.action.name
            bpy.context.scene.mix_source_armature = obj
            bpy.context.view_layer.objects.active = control_rig

            bpy.ops.mr.import_anim_to_rig()

            bpy.context.view_layer.objects.active = control_rig
            selected_action = control_rig.animation_data.action
            selected_action.name = 'ctrl_' + action_name
            # created_actions.append(selected_action)

            if push_nla:
                push(control_rig, selected_action, None, int(selected_action.frame_start))

            if delete_applied_armatures:
                bpy.context.view_layer.objects.active = control_rig
                deleteArmature(set([obj]))


if __name__ == "__main__":
    dir_path = "" # If using script in place please set this before running.
    get_all_anims(dir_path)
    print("[Mixamo Root] Run as plugin, or copy script in text editor while setting parameter defaults.")
