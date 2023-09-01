#!/usr/bin/env python3

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper
from ..blender_decorator import register_class

@register_class
class IMAGE_MT_reload_listed_image(Operator):
    bl_idname = 'image.reload_listed_image'
    bl_label = 'Discard'

    image_name: StringProperty(name='Name', description='Name of image to reload')

    def execute(self, context):
        name = self.image_name
        if name in bpy.data.images:
            bpy.data.images[name].reload()
        return {'FINISHED'}

@register_class
class IMAGE_MT_saveas_listed_image(Operator, ExportHelper):
    """Save image"""
    bl_idname = 'image.saveas_listed_image'
    bl_label = 'Save'
    filename_ext = '.png'

    filter_glob: StringProperty(
        default="*.png",
        options={'HIDDEN'},
    )

    image_name: StringProperty(name='Name', description='Name of image to save', options={'HIDDEN'})

    def execute(self, context):
        image = bpy.data.images[self.image_name]
        image.save(filepath=self.filepath)
        image.filepath = self.filepath
        return {'FINISHED'}

@register_class
class IMAGE_MT_save_listed_image(Operator):
    """Save image"""
    bl_idname = 'image.save_listed_image'
    bl_label = 'Save'

    image_name: StringProperty(name='Name', description='Name of image to save', options={'HIDDEN'})

    def execute(self, context):
        image = bpy.data.images[self.image_name]
        image.save()
        return {'FINISHED'}

@register_class
class IMAGE_MT_list_unsaved_images(Operator):
    """List unsaved (dirty) images"""
    bl_idname = 'image.list_unsaved_images'
    bl_label = 'List Unsaved Images'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return any(i.is_dirty for i in bpy.data.images)

    def draw(self, context):
        dirty_images = [i for i in bpy.data.images if i.is_dirty]
        if dirty_images:
            header = self.layout.split(factor=0.8 * 0.4)
            header.label(text='Name')
            header.label(text='Path')

            box = self.layout.box()
            for image in dirty_images:
                row = box.split(factor=0.8)
                info_cols = row.column().split(factor=0.4)
                info_cols.label(text=image.name, icon='IMAGE')
                info_cols.label(text=image.filepath if image.source == 'FILE' else f"<{image.source.lower()}>")

                button_cols = row.column().row()
                discard = button_cols.operator(IMAGE_MT_reload_listed_image.bl_idname)
                discard.image_name = image.name

                if image.filepath:
                    save = button_cols.operator(IMAGE_MT_save_listed_image.bl_idname)
                    save.image_name = image.name
                else:
                    save = button_cols.operator(IMAGE_MT_saveas_listed_image.bl_idname)
                    save.image_name = image.name
                    save.filepath = image.filepath
        else:
            self.layout.label(text='All images are now saved', icon='CHECKMARK')

    def invoke(self, context, event):
        if any(i.is_dirty for i in bpy.data.images):
            return context.window_manager.invoke_props_dialog(self, width=600)
        else:
            # When a button is pressed in the dialog, invoke() is called again
            # without checking poll()
            self.report({'INFO'}, f'All images are now saved')
            return {'INTERFACE'}

    def execute(self, context):
        return {'FINISHED'}
