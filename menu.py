import bpy
from bpy.types import Menu

from .operator.bone import *
from .operator.unity import *
from .operator.vertexgroup import *
from .operator.shapekey import *
from .blender_decorator import register_class, register_menu

from .operator.image import *

@register_class
class OBJECT_MT_connect_bones_menu(Menu):
    bl_idname = 'OBJECT_MT_connect_bones_menu'
    bl_label = 'Connect Bones'

    def draw(self, context):
        self.layout.operator(OBJECT_OT_connect_selected_bones.bl_idname, text='Selected')
        self.layout.operator(OBJECT_OT_connect_bones_by_distance.bl_idname, text='By Distance')

@register_menu(bpy.types.VIEW3D_MT_edit_armature)
def connect_bones_menu(self, context):
    self.layout.menu(OBJECT_MT_connect_bones_menu.bl_idname)

@register_class
class OBJECT_MT_unity_blendshape_menu(Menu):
    bl_idname = 'OBJECT_MT_unity_blendshape_menu'
    bl_label = 'Unity'

    def draw(self, context):
        self.layout.operator(OBJECT_OT_load_unity_blendshape_anim.bl_idname, text='Load Blendshape Animation', icon='FILEBROWSER')
        self.layout.operator(OBJECT_OT_save_unity_blendshape_anim.bl_idname, text='Save Blendshape Animation', icon='FILE_TICK')

@register_menu(bpy.types.MESH_MT_shape_key_context_menu)
def unity_blendshape_menu(self, context):
    self.layout.menu(OBJECT_MT_unity_blendshape_menu.bl_idname)

@register_class
class OBJECT_MT_unity_object_menu(Menu):
    bl_idname = 'OBJECT_MT_unity_object_menu'
    bl_label = 'Unity'

    def draw(self, context):
        self.layout.operator(OBJECT_OT_save_unity_toggle_anims.bl_idname, text='Save Toggle Animations', icon='FILE_TICK')

@register_menu(bpy.types.VIEW3D_MT_object)
def unity_object_menu(self, context):
    self.layout.menu(OBJECT_MT_unity_object_menu.bl_idname)

#@register_menu(bpy.types.MESH_MT_shape_key_context_menu)
@register_menu(bpy.types.VIEW3D_MT_object)
def remove_empty_shapekeys_menu(self, context):
    self.layout.operator(OBJECT_OT_shapekey_remove_empty.bl_idname, icon='REMOVE')

@register_class
class OBJECT_MT_remove_empty_vertex_group_menu(Menu):
    bl_idname = 'OBJECT_MT_remove_empty_vertex_group_menu'
    bl_label = 'Remove Empty Groups'

    def draw(self, context):
        all_empty_button = self.layout.operator(
            OBJECT_OT_vertex_group_remove_empty.bl_idname,
            text='All Empty')
        all_empty_button.remove_locked = True

        unlocked_empty_button = self.layout.operator(
            OBJECT_OT_vertex_group_remove_empty.bl_idname,
            icon='UNLOCKED',
            text='Unlocked Empty')
        unlocked_empty_button.remove_locked = False

@register_menu(bpy.types.MESH_MT_vertex_group_context_menu)
def remove_empty_vertex_groups_menu(self, context):
    self.layout.menu(OBJECT_MT_remove_empty_vertex_group_menu.bl_idname, icon='REMOVE')

@register_menu(bpy.types.IMAGE_MT_image)
def list_unsaved_images_menu(self, context):
    self.layout.operator(IMAGE_MT_list_unsaved_images.bl_idname)
