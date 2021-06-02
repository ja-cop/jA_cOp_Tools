import copy
from enum import IntEnum

from . import yaml

# Can pyyaml handle this stuff?
anim_clip_preamble = '''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!74 &7400000
'''

def make_animation_clip(name, curves):
    return anim_clip_preamble + yaml.dump({
        'AnimationClip': {
            'm_Name': name,
            'm_FloatCurves': curves,
            'm_EditorCurves': copy.deepcopy(curves),
            'm_ObjectHideFlags': 0,
            'm_CorrespondingSourceObject': {'fileID': 0},
            'm_PrefabInstance': {'fileID': 0},
            'm_PrefabAsset': {'fileID': 0},
            'serializedVersion': 6,
            'm_Legacy': 0,
            'm_Compressed': 0,
            'm_UseHighQualityCurve': 1,
            'm_RotationCurves': [],
            'm_CompressedRotationCurves': [],
            'm_EulerCurves': [],
            'm_PositionCurves': [],
            'm_ScaleCurves': [],
            'm_PPtrCurves': [],
            'm_SampleRate': 60,
            'm_WrapMode': 0,
            'm_Bounds': {
                'm_Center': {'x': 0, 'y': 0, 'z': 0},
                'm_Extent': {'x': 0, 'y': 0, 'z': 0}
            },
            'm_AnimationClipSettings': {
                'serializedVersion': 2,
                'm_AdditiveReferencePoseClip': {'fileID': 0},
                'm_AdditiveReferencePoseTime': 0,
                'm_StartTime': 0,
                'm_StopTime': 0.016666668,
                'm_OrientationOffsetY': 0,
                'm_Level': 0,
                'm_CycleOffset': 0,
                'm_HasAdditiveReferencePose': 0,
                'm_LoopTime': 1,
                'm_LoopBlend': 0,
                'm_LoopBlendOrientation': 0,
                'm_LoopBlendPositionY': 0,
                'm_LoopBlendPositionXZ': 0,
                'm_KeepOriginalOrientation': 0,
                'm_KeepOriginalPositionY': 1,
                'm_KeepOriginalPositionXZ': 0,
                'm_HeightFromFeet': 0,
                'm_Mirror': 0,
            },
            'm_EulerEditorCurves': [],
            'm_HasGenericRootTransform': 0,
            'm_HasMotionFloatCurves': 0,
            'm_Events': []
        }
    })

def frame(time, value):
    return {
        'serializedVersion': 3,
        'time': time,
        'value': value,
        'inSlope': 0,
        'outSlope': 0,
        'tangentMode': 136,
        'weightedMode': 0,
        'inWeight': 0.33333334,
        'outWeight': 0.33333334,
    }

class UnityClassID(IntEnum):
    GAME_OBJECT = 1
    SKINNED_MESH_RENDERER = 137

def curve(path, class_id, attribute, value):
    return {
        'curve': {
            'serializedVersion': 2,
            'm_Curve': [frame(0, value)],
            'm_PreInfinity': 2,
            'm_PostInfinity': 2,
            'm_RotationOrder': 4
        },
        'attribute': attribute,
        'path': path,
        'classID': int(class_id),
        'script': {'fileID': 0}
    }

def make_blendshape_anim_clip(name, path, shape_keys):
    # Unity blendshape values are integers in range 0-100
    def blendshape_value(blender_value):
        return int(round(blender_value * 100))

    def blendshape_curve(name, value):
        return curve(
        path,
        UnityClassID.SKINNED_MESH_RENDERER,
        'blendShape.' + name,
        blendshape_value(value))

    curves = [blendshape_curve(name, value) for name, value in shape_keys.items()]
    return make_animation_clip(name, curves)

def make_toggle_anim_clip(name, paths, is_active):
    value = 1 if is_active else 0
    curves = [curve(path, UnityClassID.GAME_OBJECT, 'm_IsActive', value) for path in paths]
    return make_animation_clip(name, curves)

def anim_clip_to_shape_mix(anim_clip_src, path_to_mesh_object):
    anim_clip = yaml.safe_load(anim_clip_src)
    curves = anim_clip['AnimationClip']['m_FloatCurves']
    shape_mix = {}
    for curve in curves:
        components = curve['attribute'].split('.')
        if len(components) == 2:
            frames = curve['curve']['m_Curve']
            (attribute_type, attribute_name) = components
            if frames and attribute_type =='blendShape' and curve['path'] == path_to_mesh_object:
                first_frame = frames[0]
                shape_mix[attribute_name] = float(first_frame['value']) / 100
    return shape_mix

def make_unity_bone_path(armature, bone):
    path = bone.name
    b = bone
    while b.parent:
        path = f'{b.parent.name}/{path}'
        b = b.parent
    return f'{armature.name}/{path}'

# Assumes that the root of the path is a top-level object or nearest armature
def make_unity_object_path(obj):
    path = obj.name
    o = obj
    while o.parent:
        if o.parent_type == 'BONE':
            parent_bone = o.parent.data.bones[o.parent_bone]
            bone_path = make_unity_bone_path(o.parent, parent_bone)
            path = f'{bone_path}/{path}'
        elif o.parent.type == 'ARMATURE':
            break
        else:
            path = f'{o.parent.name}/{path}'
        o = o.parent
    return path
