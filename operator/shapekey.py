import bpy
from bpy.props import BoolProperty, FloatProperty
from bpy.types import Operator
from ..blender_decorator import register_class
import numpy as np

@register_class
class OBJECT_OT_shapekey_remove_empty(Operator):
    """Delete empty shape keys"""
    bl_idname = 'object.shapekey_remove_empty'
    bl_label = 'Delete Empty Shape Keys'
    bl_options = {'REGISTER', 'UNDO'}

    remove_muted: BoolProperty(name='Include muted',
                              default=True,
                              description='Remove empty shape key even if muted')

    threshold: FloatProperty(name='Threshold',
                             default=0.0001,
                             soft_min=0.00001,
                             soft_max=0.1,
                             step=0.1,
                             precision=5,
                             unit='LENGTH',
                             subtype='DISTANCE',
                             description="Delete shape keys where all vertices are within this distance from basis")

    def execute(self, context):
        def mesh_with_shapekeys(o):
            return o.type == 'MESH' and o.data.shape_keys and o.data.shape_keys.use_relative

        # Collect unique meshes with shape keys
        meshes = {o.data: o for o in bpy.context.selected_objects if mesh_with_shapekeys(o)}
        if len(meshes) == 0:
            self.report({'WARNING'}, 'no meshes with shape keys in selection')
            return {'CANCELLED'}

        delete_count = 0

        # credit to https://blender.stackexchange.com/a/237611
        for mesh, obj in meshes.items():
            if not mesh.shape_keys: continue
            if not mesh.shape_keys.use_relative: continue

            kbs = mesh.shape_keys.key_blocks
            nverts = len(mesh.vertices)
            to_delete = []

            # Cache locs for rel keys since many keys have the same rel key
            cache = {}

            locs = np.empty(nverts * 3, dtype=np.float32)

            for kb in kbs:
                if kb == kb.relative_key: continue
                if kb.mute and not self.remove_muted: continue

                kb.data.foreach_get("co", locs)

                if kb.relative_key.name not in cache:
                    rel_locs = np.empty(nverts * 3, dtype=np.float32)
                    kb.relative_key.data.foreach_get("co", rel_locs)
                    cache[kb.relative_key.name] = rel_locs
                rel_locs = cache[kb.relative_key.name]

                locs -= rel_locs
                if (np.abs(locs) < self.threshold).all():
                    to_delete.append(kb.name)

            delete_count += len(to_delete)
            for kb_name in to_delete:
                obj.shape_key_remove(mesh.shape_keys.key_blocks[kb_name])
                self.report({'INFO'}, f'{obj.name}: deleted shape key "{kb_name}"')

        self.report({'INFO'}, f'Deleted {delete_count} shape keys')
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
