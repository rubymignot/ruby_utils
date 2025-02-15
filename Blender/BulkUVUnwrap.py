bl_info = {
    "name": "Bulk Smart UV",
    "author": "Ruby Mignot",
    "version": (1, 1),
    "blender": (4, 1, 0),
    "location": "View3D > Sidebar > Bulk Smart UV Panel",
    "description": "Applies Smart UV Project to an object and its children with optional new UV layer creation",
    "warning": "",
    "doc_url": "",
    "category": "UV",
}

import bpy
from bpy.props import BoolProperty, PointerProperty, StringProperty

def update_object_picker(self, context):
    bpy.context.scene.bulk_smart_uv_selected_object = bpy.data.objects[self.object_picker]

class BULKSMARTUV_OT_apply_smart_uv(bpy.types.Operator):
    """Apply Smart UV Project to the selected object and its children"""
    bl_idname = "object.apply_smart_uv"
    bl_label = "Apply Smart UV"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.bulk_smart_uv_selected_object is not None

    def execute(self, context):
        selected_object = context.scene.bulk_smart_uv_selected_object
        self.apply_smart_uv_to_hierarchy(selected_object)
        return {'FINISHED'}
    
    def apply_smart_uv_to_hierarchy(self, obj):
        if obj.type == 'MESH':
            # Optionally create (or switch to) a new UV layer if enabled
            props = bpy.context.scene.bulk_smart_uv_properties
            if props.create_new_uv_layer:
                uv_name = props.new_uv_layer_name.strip()
                if uv_name:
                    bpy.context.view_layer.objects.active = obj
                    # Ensure we're in Object mode when modifying mesh data
                    if obj.mode != 'OBJECT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                    mesh = obj.data
                    if uv_name in mesh.uv_layers:
                        mesh.uv_layers.active = mesh.uv_layers[uv_name]
                    else:
                        new_layer = mesh.uv_layers.new(name=uv_name)
                        mesh.uv_layers.active = new_layer

            try:
                # Store the current active object and mode to restore them later
                original_active_object = bpy.context.view_layer.objects.active
                original_mode = bpy.context.object.mode

                # Set the context to the object we want to work with and enter Edit mode
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                
                # Ensure all geometry is selected
                bpy.ops.mesh.select_all(action='SELECT')
                
                # Apply Smart UV Project
                try:
                    bpy.ops.uv.smart_project()
                except RuntimeError as e:
                    print(f"Failed to execute bpy.ops.uv.smart_project() on {obj.name}: {e}")
                
                # Restore the original mode and active object
                bpy.ops.object.mode_set(mode=original_mode)
                bpy.context.view_layer.objects.active = original_active_object
            except Exception as e:
                print(f"Failed to apply Smart UV to {obj.name}: {e}")

        # Recursively apply to children
        for child in obj.children:
            self.apply_smart_uv_to_hierarchy(child)

class BULKSMARTUV_PT_main_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Bulk Smart UV"
    bl_idname = "BULKSMARTUV_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bulk Smart UV'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bulk_props = scene.bulk_smart_uv_properties

        layout.prop_search(scene, "bulk_smart_uv_selected_object", bpy.data, "objects", text="Object Picker")
        layout.operator("object.apply_smart_uv")

        layout.separator()
        layout.label(text="UV Layer Options:")
        layout.prop(bulk_props, "create_new_uv_layer")
        if bulk_props.create_new_uv_layer:
            layout.prop(bulk_props, "new_uv_layer_name")

class BULKSMARTUVProperties(bpy.types.PropertyGroup):
    object_picker: StringProperty(
        name="Object Picker",
        description="Pick an object to apply Smart UV",
        update=update_object_picker
    )
    create_new_uv_layer: BoolProperty(
        name="Create New UV Layer",
        description="Create a new UV layer before applying Smart UV",
        default=False
    )
    new_uv_layer_name: StringProperty(
        name="New UV Layer Name",
        description="Name of the new UV layer to be created",
        default="UVMap_New"
    )

def register():
    bpy.utils.register_class(BULKSMARTUV_OT_apply_smart_uv)
    bpy.utils.register_class(BULKSMARTUV_PT_main_panel)
    bpy.utils.register_class(BULKSMARTUVProperties)
    bpy.types.Scene.bulk_smart_uv_selected_object = PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.bulk_smart_uv_properties = PointerProperty(type=BULKSMARTUVProperties)

def unregister():
    bpy.utils.unregister_class(BULKSMARTUV_OT_apply_smart_uv)
    bpy.utils.unregister_class(BULKSMARTUV_PT_main_panel)
    bpy.utils.unregister_class(BULKSMARTUVProperties)
    del bpy.types.Scene.bulk_smart_uv_selected_object
    del bpy.types.Scene.bulk_smart_uv_properties

if __name__ == "__main__":
    register()
