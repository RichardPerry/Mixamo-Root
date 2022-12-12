
'''
    Copyright (C) 2022  Richard Perry
    Copyright (C) Johngoss725 (Average Godot Enjoyer)

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

bl_info = {
    "name": "Mixamo Root",
    "author": "Richard Perry, Johngoss725",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "3D View > UI (Right Panel) > Mixamo Tab",
    "description": ("Script to bake insert root motion bone for Mixamo Animations"),
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/RichardPerry/mixamo_root_bones/wiki",
    "tracker_url": "https://github.com/enziop/mixamo_root_bones/issues" ,
    "category": "Animation"
}

import bpy

try:
    from . import mixamoroot
except SystemError:
    import mixamoroot

if "bpy" in locals():
    from importlib import reload
    if "mixamoroot" in locals():
        reload(mixamoroot)

class MixamoPropertyGroup(bpy.types.PropertyGroup):
    '''Property container for options and paths of Mixamo Root'''
    hip_name: bpy.props.StringProperty(
        name="Hip Bone Name",
        description="Name to identify the hip bone if not MixamoRig:Hips",
        maxlen = 256,
        default = "mixamorig:Hips",
        subtype='NONE')
    root_name: bpy.props.StringProperty(
        name="Root Bone Name",
        description="Name to save the root bone as if not RootMotion",
        maxlen = 256,
        default = "RootMotion",
        subtype='NONE')
    name_prefix: bpy.props.StringProperty(
        name="Name Prefix",
        description="Prefix of armature components to identify if not mixamorig:",
        maxlen = 256,
        default = "mixamorig:",
        subtype='NONE')
    source_directory: bpy.props.StringProperty(
        name="Source Directory",
        description="Path to directory containing mixamo animation files (.fbx)",
        maxlen = 256,
        default = "",
        subtype='DIR_PATH')
    rename_components: bpy.props.BoolProperty(
        name="Remove Prefix",
        description="Remove prefix from armature component names",
        default=False)

class OBJECT_OT_ImportAnimations(bpy.types.Operator):
    '''Operator for importing animations and inserting root bones'''
    bl_idname = "mixamo.importanim"
    bl_label = "Import Animations"
    bl_description = "Imports all mixamo animations from the [Source Directory], insert root bones, and merges into a single armature."

    def execute(self, context):
        mixamo = context.scene.mixamo
        source_directory = mixamo.source_directory
        hip_name = mixamo.hip_name
        root_name = mixamo.root_name
        name_prefix = mixamo.name_prefix
        rename_components = mixamo.rename_components
        if source_directory == '':
            self.report({'ERROR_INVALID_INPUT'}, "Error: no Source Directory set.")
            return{ 'CANCELLED'}
        if hip_name == '':
            self.report({'ERROR_INVALID_INPUT'}, "Error: no Hip Bone Name set.")
            return{ 'CANCELLED'}
        if root_name == '':
            self.report({'ERROR_INVALID_INPUT'}, "Error: no Root Bone Name set.")
            return{ 'CANCELLED'}
        if rename_components == True:
            self.report({'WARNING'}, "Remove Prefix set to true, armature components will have their mixamo prefix removed.")
        mixamoroot.get_all_anims(
            bpy.path.abspath(source_directory),
            root_bone_name=root_name,
            hip_bone_name=hip_name,
            rename_components=rename_components,
            name_prefix=name_prefix)
        return{ 'FINISHED'}

class MIXAMOCONV_VIEW_3D_PT_mixamoroot(bpy.types.Panel):
    """Creates a Tab in the Toolshelve in 3D_View"""
    bl_label = "Mixamo Root"
    bl_idname = "MIXAMOCONV_VIEW_3D_PT_mixamoroot"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mixamo"

    def draw(self, context):
        layout = self.layout

        scene = bpy.context.scene

        box = layout.box()
        # Options for how to do the conversion
        row = box.row()
        row.prop(scene.mixamo, "rename_components", toggle=True)
        row = box.row()
        box.prop(scene.mixamo, "hip_name")
        row = box.row()
        box.prop(scene.mixamo, "root_name")
        row = box.row()
        box.prop(scene.mixamo, "name_prefix")
        # Button for conversion of single Selected rig
        box = layout.box()
        box.label(text="Animation Files")
        row = box.row()
        row.prop(scene.mixamo, "source_directory")
        # button to start batch conversion
        row = box.row()
        row.scale_y = 2.0
        row.operator("mixamo.importanim")
        status_row = box.row()

classes = (
    OBJECT_OT_ImportAnimations,
    MIXAMOCONV_VIEW_3D_PT_mixamoroot,
)

def register():
    bpy.utils.register_class(MixamoPropertyGroup)
    bpy.types.Scene.mixamo = bpy.props.PointerProperty(type=MixamoPropertyGroup)
    for cls in classes:
        bpy.utils.register_class(cls)
    '''
    bpy.utils.register_class(OBJECT_OT_ImportAnimations)
    bpy.utils.unregister_class(MixamorootPanel)
    '''

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(MixamoPropertyGroup)    
    '''
    bpy.utils.unregister_class(MixamoPropertyGroup)
    bpy.utils.register_class(OBJECT_OT_ImportAnimations)
    bpy.utils.unregister_class(MixamorootPanel)
    '''


if __name__ == "__main__":
    register()