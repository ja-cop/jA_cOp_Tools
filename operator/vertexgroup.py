import bpy
from bpy.props import BoolProperty
from bpy.types import Operator
from ..blender_decorator import register_class

from collections import namedtuple

VGroup = namedtuple('VGroup', ['group', 'in_use'])

@register_class
class OBJECT_OT_vertex_group_remove_empty(Operator):
    """Delete empty vertex groups"""
    bl_idname = 'object.vertex_group_remove_empty'
    bl_label = 'Delete Empty Groups'
    bl_options = {'REGISTER', 'UNDO'}

    remove_locked: BoolProperty(name='Remove locked empty groups',
                              default=False,
                              description='Remove empty group even if locked')

    def execute(self, context):
        obj = context.active_object
        obj.update_from_editmode()
        groups = [VGroup(group, False) for group in obj.vertex_groups]
        for vertex in obj.data.vertices:
            for group_membership in vertex.groups:
                index = group_membership.group
                groups[index] = VGroup(groups[index].group, True)

        count = 0
        for group in groups:
            if not group.in_use and (self.remove_locked or not group.group.lock_weight):
                obj.vertex_groups.remove(group.group)
                count += 1

        self.report({'INFO'}, f'Deleted {count} empty vertex group(s)')
        return {'FINISHED'}
