import os.path

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper
from ..blender_decorator import register_class
from .. import unity

@register_class
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

    clear: BoolProperty(name='Clear other shape keys',
                        default=True,
                        description='Set to zero each shape key unaffected by the loaded animation clip')

    unpin_active_shape_key: BoolProperty(name='Unpin active shape key',
                                         default=True,
                                         description='Disable the shape key lock')

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

        if self.unpin_active_shape_key:
            obj.show_only_shape_key = False

        for name, value in shape_mix.items():
            if name in key_blocks:
                key_blocks[name].value = value

        num_changed = len(shape_mix)
        basename = os.path.basename(self.filepath)
        if num_changed > 0:
            self.report({'INFO'}, f'{basename}: loaded {num_changed} shape key weight(s)')
        else:
            self.report({'WARNING'}, f'{basename}: no applicable shape keys found')
        return {'FINISHED'}

@register_class
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

@register_class
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

    enable_anim_filename: StringProperty(name='Enable',
                                         default='Enable.anim',
                                         description='Filename of clip which sets IsActive to true')

    disable_anim_filename: StringProperty(name='Disable',
                                          default='Disable.anim',
                                          description='Filename of clip which sets IsActive to false')

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
