# jA_cOp's Tools

Blender addon with various tools.

# Installation

Download the [latest release](https://github.com/ja-cop/jA_cOp_Tools/releases) from Github. In Blender, go to Edit -> Preferences -> Add-ons -> Install, and select the downloaded ZIP file.

# Unity Animations

The addon includes some conveniences for working quickly with simple [Unity](https://en.wikipedia.org/wiki/Unity_(game_engine)) animations. It is not intended as a replacement for the animation support in the FBX format plugin.

## Save/Load Blendshape Animations

Location: `Object Data Properties (Mesh) > Shape Keys > Shape Key Specials > Unity`

The current shape mix can be loaded from the first frame of a Unity animation clip (`.anim` file). Conversely, the current shape mix can be saved to a new, single-frame Unity animation clip.

When loading a clip, blendshape attributes are matched by name to the active mesh's shape keys. Each attribute's path component is ignored: for example, an animation clip that contains blendshape attributes for a Unity object `Foo` can still be applied to a mesh object named `Bar` as long as the blendshapes match the names of `Foo`'s shape keys. Any blendshape attribute with no matching shape key is ignored. Non-blendshape attributes are also ignored.

When saving a clip, each shape key with a non-zero weight is saved as a blendshape attribute with the shape key's name.

Note that Blender shape keys are in the range 0-1, and Unity blendshapes 0-100. When loading a clip with a blendshape of value 60, the matched shape key is set to 0.6, and vice versa when saving a clip.

## Save Toggle Animations

Location: `Object > Unity > Save Toggle Animations`

Two Unity animation clips will be saved in the selected location: one that enables the selected objects, and one that disables them, each with a single frame. Both clips set the `IsActive` attribute for each selected object.

## Unity Attribute Paths

When saving and loading Unity animation clips, the path component of each attribute is constructed by iterating through the parent chain of the affected object, terminating at the first armature object, or the first object with no parent.

For example, if the selected object named `Body` is parented to an armature, the saved attribute path is simply `Body`; if the selected object named `Accessory` is parented to `Body` which is parented to an armature, the path is `Body/Accessory`. In these examples, the saved clip is ready for use on a Unity animator component attached to a parent object of `Body`, compatible with how Unity imports rigged models in FBX files.

When an object is parented to a bone, the bone parent chain is included in the path. For example, if the selected object `Accessory` is parented to a bone `Chest`, with the chain `Chest > Spine > Hips`, on the armature `Armature`, the attribute path is `Accessory/Chest/Spine/Hips/Armature`: this is compatible with how Unity imports bones from rigged models in FBX files.

# Bone Actions

Location: `Armature > Connect Bones`

These actions are useful for setting the "connected" state for bones in bulk. Appropriate use of the "connected" state is required for using Blender's IK.

## Connect Selected Bones

Sets "connected" for each selected bone. Can also be used to disconnect the selected bones.

Note: this can also be accomplished by holding alt while clicking the `Connected` checkbox in bone properties.

## Connect Bones By Distance

For every bone on the armature, sets "connected" if the bone's head is within the specified distance of the parent bone's tail. Useful for connecting bones on an imported rig that has the bones aligned but no bones marked "connected".

# Delete Empty Vertex Groups

Location: `Object Data Properties (Mesh) > Vertex Groups > Vertex Group Specials > Delete Empty Groups`

## All Empty

Deletes empty vertex groups.

Note: vertex groups containing only zero-weights are not counted as empty and are not deleted by this action. To delete such groups, first use `Weights > Clean` with `Subset = All Groups` in weight paint mode, then use this action.

## Unlocked Empty

Same as above, but locked groups are preserved even when they are empty.

# Delete Empty Shape Keys

Location: `Object > Delete Empty Shape Keys`

Delete empty shape keys on all selected mesh objects. A shape key is considered to be "empty" when all vertices are within the provided `threshold` distance (default: `0.0001`) of the shape key's relative key (e.g. `Basis`). Useful for cleaning up shape keys after deleting geometry or splitting meshes. For convenience, there is also an option to ignore muted shape keys.

# Warn on editing shape key

Location: this addon's preferences

When enabled, entering edit mode on a mesh's shape key will show a pop-up warning reminding the user that a shape key is being edited. The warning is not shown when editing the first shape key (aka `Basis`). Useful when working with lots of shape keys but sometimes forgetting to return to `Basis` before making edits not intended for a shape key.
