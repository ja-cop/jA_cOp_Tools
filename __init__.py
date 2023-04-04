bl_info = {
    'name': "jA_cOp's Tools",
    'blender': (2, 92, 0),
    'version': (0, 2, 0),
    'category': 'Object',
    'author': 'jA_cOp',
    'description': 'Various tools'
}

import bpy
from bpy.props import BoolProperty
from bpy.types import AddonPreferences
from bpy.app.handlers import persistent

from . import menu
from .blender_decorator import register_class

@register_class
class JToolsAddonPreferences(AddonPreferences):
    bl_idname = __package__

    warn_shapekey_edit: BoolProperty(
        name='Warn on editing shape key',
        default=False,
        description='Show a popup warning when entering edit mode on a mesh shape key')

    def draw(self, context):
        self.layout.prop(self, 'warn_shapekey_edit')

def mode_switch():
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    warn = addon_prefs.warn_shapekey_edit
    obj = bpy.context.active_object
    if warn and obj and obj.type == 'MESH' and obj.mode == 'EDIT' and obj.active_shape_key_index != 0:
        def draw(self, context):
            self.layout.label(text=f'Editing shape key "{obj.active_shape_key.name}"')
        bpy.context.window_manager.popup_menu(draw, title='Warning', icon='ERROR')

subscription_owner = object()

@persistent
def subscribe_to_mode_change(dummy):
    bpy.msgbus.clear_by_owner(subscription_owner)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, 'mode'),
        owner=subscription_owner,
        args=(),
        notify=mode_switch,
        options={'PERSISTENT'} # Not sure what this does
    )

def register():
    for cls in blender_decorator.classes:
        bpy.utils.register_class(cls)

    for menu, entry in blender_decorator.menus:
        menu.append(entry)

    bpy.app.handlers.load_post.append(subscribe_to_mode_change)

    # In case the addon is enabled after loading a file, we need to subscribe here
    subscribe_to_mode_change(None)

def unregister():
    bpy.app.handlers.load_post.remove(subscribe_to_mode_change)
    bpy.msgbus.clear_by_owner(subscription_owner)

    for cls in reversed(blender_decorator.classes):
        bpy.utils.unregister_class(cls)

    for menu, entry in reversed(blender_decorator.menus):
        menu.remove(entry)
