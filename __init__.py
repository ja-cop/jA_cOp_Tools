bl_info = {
    'name': "jA_cOp's Tools",
    'blender': (2, 92, 0),
    'category': 'Object',
    'author': 'jA_cOp',
    'description': 'Various tools'
}

# Reload imports on addon reload
if 'bpy' in locals():
    import importlib
    if 'unity' in locals():
        importlib.reload(unity)

# Blender imports
import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy.types import Operator, Menu, AddonPreferences
from mathutils import Vector

# Standard library imports
import os.path

# Addon imports
from . import unity

class JToolsAddonPreferences(AddonPreferences):
    bl_idname = __package__

    warn_shapekey_edit: BoolProperty(
        name='Warn on editing shape key',
        default=False
    )

    def draw(self, context):
        self.layout.prop(self, 'warn_shapekey_edit')

class OBJECT_OT_connect_selected_bones(Operator):
    """Connect each selected bone to its parent"""
    bl_idname = 'object.connect_selected_bones'
    bl_label = 'Connect Selected Bones'
    bl_options = {'REGISTER', 'UNDO'}

    connected: BoolProperty(name='Connected', default=True)

    def execute(self, context):
        for bone in context.selected_editable_bones[:]:
            bone.use_connect = self.connected
        return {'FINISHED'}

class OBJECT_OT_connect_bones_by_distance(Operator):
    """Connect bones by distance to parent"""
    bl_idname = 'object.connect_bones_by_distance'
    bl_label = 'Connect Bones By Distance'
    bl_options = {'REGISTER', 'UNDO'}

    connected: BoolProperty(name='Connected', default=True)
    threshold: FloatProperty(name='Distance',
                             default=0.001,
                             soft_min=0.001,
                             soft_max=10,
                             step=1,
                             precision=3,
                             unit='LENGTH',
                             subtype='DISTANCE')

    def execute(self, context):
        for bone in context.visible_bones:
            parent = bone.parent
            if parent:
                distance = (Vector(bone.head) - Vector(parent.tail)).length
                if distance < self.threshold:
                    bone.use_connect = self.connected
        return {'FINISHED'}

class OBJECT_MT_connect_bones_menu(Menu):
    bl_idname = 'OBJECT_MT_connect_bones_menu'
    bl_label = 'Connect Bones'

    def draw(self, context):
        self.layout.operator(OBJECT_OT_connect_selected_bones.bl_idname, text='Selected')
        self.layout.operator(OBJECT_OT_connect_bones_by_distance.bl_idname, text='By Distance')

def connect_bones_menu(self, context):
    self.layout.menu(OBJECT_MT_connect_bones_menu.bl_idname)

class OBJECT_OT_load_unity_blendshape_anim(Operator, ImportHelper):
    """Load shape key mix from Unity blendshape animation (from first frame)"""
    bl_idname = 'object.load_unity_blendshape_anim'
    bl_label = 'Load Unity Blendshape Animation'
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = '.anim'

    filter_glob: StringProperty(
        default="*.anim",
        options={'HIDDEN'},
    )

    clear: BoolProperty(name='Clear other shape keys', default=True)

    def execute(self, context):
        obj = context.active_object
        key_blocks = obj.data.shape_keys.key_blocks
        object_path = unity.make_unity_object_path(obj)

        with open(self.filepath) as f:
            # Remove YAML tag
            lines = f.readlines()[3:]
            shape_mix = unity.anim_clip_to_shape_mix('\n'.join(lines), object_path)

        if self.clear:
            bpy.ops.object.shape_key_clear()

        for name, value in shape_mix.items():
            if name in key_blocks:
                key_blocks[name].value = value

        return {'FINISHED'}

class OBJECT_OT_save_unity_blendshape_anim(Operator, ExportHelper):
    """Save shape key mix as Unity blendshape animation"""
    bl_idname = 'object.save_unity_blendshape_anim'
    bl_label = 'Save Unity Blendshape Animation'
    filename_ext = '.anim'

    filter_glob: StringProperty(
        default="*.anim",
        options={'HIDDEN'},
    )

    def execute(self, context):
        obj = context.active_object
        (root, ext) = os.path.splitext(self.filepath)
        clip_name = os.path.basename(root)

        shape_keys = {}
        for key in obj.data.shape_keys.key_blocks:
            if key.value >= 0.01:
                shape_keys[key.name] = key.value

        object_path = unity.make_unity_object_path(obj)
        anim_clip = unity.make_blendshape_anim_clip(clip_name, object_path, shape_keys)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(anim_clip)

        return {'FINISHED'}

class OBJECT_MT_unity_blendshape_menu(Menu):
    bl_idname = 'OBJECT_MT_unity_blendshape_menu'
    bl_label = 'Unity'

    def draw(self, context):
        self.layout.operator(OBJECT_OT_load_unity_blendshape_anim.bl_idname, text='Load Animation', icon='FILEBROWSER')
        self.layout.operator(OBJECT_OT_save_unity_blendshape_anim.bl_idname, text='Save Animation', icon='FILE_TICK')

def unity_blendshape_menu(self, context):
    self.layout.menu(OBJECT_MT_unity_blendshape_menu.bl_idname)

class OBJECT_OT_save_unity_toggle_anims(Operator):
    """Save enable/disable Unity animations"""
    bl_idname = 'object.save_unity_toggle_anims'
    bl_label = 'Save Unity Toggle Animations'
    bl_options = {'REGISTER'}

    # fileselect_add dialog uses these two properties
    directory: StringProperty(
        name="Save Location",
        description="Where to save animation files"
    )
    filter_folder: BoolProperty(default=True, options={'HIDDEN'})

    enable_anim_filename: StringProperty(name='Enable', default='Enable.anim')
    disable_anim_filename: StringProperty(name='Disable', default='Disable.anim')

    def execute(self, context):
        dir_path = self.directory
        objs = context.selected_objects
        object_paths = [unity.make_unity_object_path(obj) for obj in objs]

        (enable_anim_name, _) = os.path.splitext(self.enable_anim_filename)
        enable_anim_path = os.path.join(dir_path, self.enable_anim_filename)
        enable_anim_clip = unity.make_toggle_anim_clip(enable_anim_name, object_paths, is_active=True)
        with open(enable_anim_path, 'w', encoding='utf-8') as f:
            f.write(enable_anim_clip)

        (disable_anim_name, _) = os.path.splitext(self.disable_anim_filename)
        disable_anim_path = os.path.join(dir_path, self.disable_anim_filename)
        disable_anim_clip = unity.make_toggle_anim_clip(disable_anim_name, object_paths, is_active=False)
        with open(disable_anim_path, 'w', encoding='utf-8') as f:
            f.write(disable_anim_clip)

        return {'FINISHED'}

    def invoke(self, context, event):
        active = context.active_object
        if active:
            self.enable_anim_filename = active.name + 'Enable.anim'
            self.disable_anim_filename = active.name + 'Disable.anim'
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class OBJECT_MT_unity_object_menu(Menu):
    bl_idname = 'OBJECT_MT_unity_object_menu'
    bl_label = 'Unity'

    def draw(self, context):
        self.layout.operator(OBJECT_OT_save_unity_toggle_anims.bl_idname, text='Save Toggle Animations', icon='FILE_TICK')

def unity_object_menu(self, context):
    self.layout.menu(OBJECT_MT_unity_object_menu.bl_idname)

class WarningBox(Operator):
    bl_idname = 'message.warningbox'
    bl_label = 'Warning'

    message: StringProperty(default='')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        self.layout.label(text=self.message)

classes = [
    JToolsAddonPreferences,

    OBJECT_OT_connect_selected_bones,
    OBJECT_OT_connect_bones_by_distance,
    OBJECT_MT_connect_bones_menu,

    OBJECT_OT_load_unity_blendshape_anim,
    OBJECT_OT_save_unity_blendshape_anim,
    OBJECT_MT_unity_blendshape_menu,

    OBJECT_OT_save_unity_toggle_anims,
    OBJECT_MT_unity_object_menu,

    WarningBox
]

menu_entries = [
    (bpy.types.VIEW3D_MT_edit_armature, connect_bones_menu),
    (bpy.types.MESH_MT_shape_key_context_menu, unity_blendshape_menu),
    (bpy.types.VIEW3D_MT_object, unity_object_menu)
]

def mode_switch():
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    warn = addon_prefs.warn_shapekey_edit
    obj = bpy.context.active_object
    if warn and obj and obj.type == 'MESH' and obj.mode == 'EDIT' and obj.active_shape_key_index != 0:
        bpy.ops.message.warningbox(
            'INVOKE_DEFAULT',
            message=f'Editing shape key "{obj.active_shape_key.name}"')

subscription_owner = object()

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for menu, entry in menu_entries:
        menu.append(entry)

    bpy.msgbus.clear_by_owner(subscription_owner)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, 'mode'),
        owner=subscription_owner,
        args=(),
        notify=mode_switch,
        options={'PERSISTENT'}
    )

def unregister():
    bpy.msgbus.clear_by_owner(subscription_owner)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for menu, entry in reversed(menu_entries):
        menu.remove(entry)
