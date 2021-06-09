from bpy.props import BoolProperty, FloatProperty
from bpy.types import Operator
from mathutils import Vector
from ..blender_decorator import register_class

@register_class
class OBJECT_OT_connect_selected_bones(Operator):
    """Connect each selected bone to its parent"""
    bl_idname = 'object.connect_selected_bones'
    bl_label = 'Connect Selected Bones'
    bl_options = {'REGISTER', 'UNDO'}

    connected: BoolProperty(name='Connected',
                            default=True,
                            description='Whether the selected bones should be connected or disconnected')

    def execute(self, context):
        for bone in context.selected_editable_bones[:]:
            bone.use_connect = self.connected
        return {'FINISHED'}

@register_class
class OBJECT_OT_connect_bones_by_distance(Operator):
    """Connect bones by distance to parent"""
    bl_idname = 'object.connect_bones_by_distance'
    bl_label = 'Connect Bones By Distance'
    bl_options = {'REGISTER', 'UNDO'}

    connected: BoolProperty(name='Connected',
                            default=True,
                            description='Whether the affected bones should be connected or disconnected')

    threshold: FloatProperty(name='Distance',
                             default=0.001,
                             soft_min=0.001,
                             soft_max=10,
                             step=1,
                             precision=3,
                             unit='LENGTH',
                             subtype='DISTANCE',
                             description="Connect bone when its head is within this distance from the parent's tail")

    def execute(self, context):
        count = 0
        for bone in context.selected_editable_bones[:]:
            parent = bone.parent
            if parent:
                distance = (Vector(bone.head) - Vector(parent.tail)).length
                if distance < self.threshold and bone.use_connect != self.connected:
                    bone.use_connect = self.connected
                    count += 1

        action = 'Connected' if self.connected else 'Disconnected'
        self.report({'INFO'}, f'{action} {count} bone(s)')
        return {'FINISHED'}
