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
#log.setLevel('DEBUG')

def fixBones(rename_components=False, name_prefix="mixamorig:"):
    bpy.ops.object.mode_set(mode = 'OBJECT')
        
    if not bpy.ops.object:
        log.warning('[Mixamo Root] Could not find amature object, please select the armature')

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.object.show_in_front = True

    if rename_components:
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
                f.data_path = f.data_path.replace("mixamorig:","")
        
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


def copyHips(root_bone_name="RootMotion", hip_bone_name="mixamorig:Hips"):
        
    bpy.context.area.ui_type = 'FCURVES'
    #SELECT OUR ROOT MOTION BONE 
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.context.object.pose.bones[root_bone_name].bone.select = True
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
    bpy.context.object.pose.bones[root_bone_name].bone.select = True
    bpy.ops.graph.paste()        
        
    bpy.context.area.ui_type = 'VIEW_3D'

    
def deleteArmature(imported_objects=set()):
    if imported_objects == set():
        log.warning("No armature imported, nothing to delete")
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for object in imported_objects:
            bpy.data.objects[object.name].select_set(True)
        
    bpy.ops.object.delete(use_global=False, confirm=False)

def import_armature(path):
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.import_scene.fbx(filepath = path,  automatic_bone_orientation=True)
    
def add_root_bone(root_bone_name="RootMotion", hip_bone_name="mixamorig:Hips"):
    armature = bpy.data.objects[0]
    bpy.ops.object.mode_set(mode='EDIT')

    root_bone = armature.data.edit_bones.new(root_bone_name)
    root_bone.tail.y = 25
    # Likely not needed as default is 0. This is rotation about veritcal axis.
    root_bone.roll = 0

    bpy.ops.object.mode_set(mode='EDIT')
    armature.data.edit_bones[hip_bone_name].parent = armature.data.edit_bones[root_bone_name]
    bpy.ops.object.mode_set(mode='OBJECT')


def get_all_anims(source_dir, root_bone_name="RootMotion", hip_bone_name="mixamorig:Hips", rename_components=False, name_prefix="mixamorig:"):
    files = os.listdir(source_dir)
    use_num = len(files)
    counter = 0 
    old_objs = set()
    
    for file in files:
        try:
            old_objects = set(bpy.context.scene.objects)
            use_string = source_dir+"/"+file
            import_armature(use_string)
            print("[Mixamo Root] Now importing: " + str(use_string))
            counter += 1
            bpy.data.objects[0].animation_data.action.name = Path(use_string).resolve().stem
            
            add_root_bone(root_bone_name=root_bone_name, hip_bone_name=hip_bone_name)
            fixBones(rename_components=rename_components, name_prefix=name_prefix)
            scaleAll()
            copyHips(root_bone_name=root_bone_name, hip_bone_name=hip_bone_name)
                
            if  counter != use_num:
                imported_objects = set(bpy.context.scene.objects) - old_objects
                deleteArmature(imported_objects)
            else: 
                pass
        except Exception as e:
            log.error("[Mixamo Root] ERROR get_all_anims raised %s when processing %s" % (str(e), file))
            return -1
    # bpy.context.area.ui_type = 'TEXT_EDITOR'
    bpy.context.scene.frame_start = 0
    bpy.ops.object.mode_set(mode='OBJECT')


def get_anim(source_file, root_bone_name="RootMotion", hip_bone_name="mixamorig:Hips", rename_components=False, name_prefix="mixamorig:"):
    counter = 0
    old_objs = set()

    try:
        old_objects = set(bpy.context.scene.objects)
        import_armature(source_file)
        print("[Mixamo Root] Now importing: " + source_file)
        counter += 1
        bpy.data.objects[0].animation_data.action.name = Path(source_file).resolve().stem
            
        add_root_bone(root_bone_name=root_bone_name, hip_bone_name=hip_bone_name)
        fixBones(rename_components=rename_components, name_prefix=name_prefix)
        scaleAll()
        copyHips(root_bone_name=root_bone_name, hip_bone_name=hip_bone_name)
        imported_objects = set(bpy.context.scene.objects) - old_objects
        deleteArmature(imported_objects)
      
    except Exception as e:
        log.error("[Mixamo Root] ERROR get_anim raised %s when processing %s" % (str(e), source_file))
        return -1
    # bpy.context.area.ui_type = 'TEXT_EDITOR'
    bpy.context.scene.frame_start = 0
    bpy.ops.object.mode_set(mode='OBJECT') 

if __name__ == "__main__":
    dir_path = "" # If using script in place please set this before running.
    get_all_anims(dir_path)
    print("[Mixamo Root] Run as plugin, or copy script in text editor while setting parameter defaults.")
