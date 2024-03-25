bl_info = {
    "name": "Bulk Smart UV",
    "author": "Ruby Mignot",
    "version": (1, 0),
    "blender": (4, 1, 0),
    "location": "View3D > Sidebar > Bulk Smart UV Panel",
    "description": "Applies Smart UV Project to an object and its children",
    "warning": "",
    "doc_url": "",
    "category": "UV",
}

import bpy
from bpy.props import PointerProperty, StringProperty

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
            try:
                # Store the current active object and mode to restore them later
                original_active_object = bpy.context.view_layer.objects.active
                original_mode = bpy.context.object.mode

                # Set the context to the object we want to work with
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                
                # Ensure all geometry is selected
                bpy.ops.mesh.select_all(action='SELECT')
                
                # This is where we need to ensure the context is correct for smart_project
                # Since directly calling bpy.ops.uv.smart_project() can lead to context issues,
                # we perform the operation and catch any exceptions
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

        layout.prop_search(scene, "bulk_smart_uv_selected_object", bpy.data, "objects", text="Object Picker")
        layout.operator("object.apply_smart_uv")

class BULKSMARTUVProperties(bpy.types.PropertyGroup):
    object_picker: StringProperty(
        name="Object Picker",
        description="Pick an object to apply Smart UV",
        update=update_object_picker
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