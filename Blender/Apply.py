bl_info = {
    "name": "Apply Modifiers",
    "author": "Ruby Mignot",
    "version": (1, 1, 0),
    "blender": (4, 1, 0),
    "category": "Object",
}

import bpy

class OBJECT_OT_apply_modifiers(bpy.types.Operator):
    """Apply Modifiers"""
    bl_idname = "object.apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        self.count = 0
        def apply_and_cleanup_modifiers(obj):
            # Ensure we're in object mode to apply modifiers
            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode='OBJECT')
            
            bpy.context.view_layer.objects.active = obj  # Set the active object
            # Make object data single-user (unique) if there are multiple users
            if obj.data and obj.data.users > 1:
                obj.data = obj.data.copy()
                print(f"Made data for {obj.name} single-user")
            for m in obj.modifiers[:]:  # Iterate through a copy of the modifiers list
                if m.show_viewport:  # Check if the modifier is active
                    try:
                        bpy.ops.object.modifier_apply(modifier=m.name)
                        self.count += 1 
                    except RuntimeError as e:
                        print(f"Error applying {m.name} to {obj.name}. Error: {e}")
                else:  # If the modifier is not active, remove it
                    print(f"Removing non-active modifier {m.name} from {obj.name}.")
                    obj.modifiers.remove(m)

        # Apply and cleanup modifiers on every object in your scene
        for o in bpy.data.objects:
            apply_and_cleanup_modifiers(o)
        self.report({'INFO'}, f"Applied {self.count} modifiers successfully")
        return {'FINISHED'}

class VIEW3D_PT_CustomPanel_applymodifiers(bpy.types.Panel):
    """Crée un panneau dans la catégorie Objets"""
    bl_label = "Apply Modifiers"
    bl_idname = "VIEW3D_PT_custom_panel_applymodifiers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_apply_modifiers.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_apply_modifiers)
    bpy.utils.register_class(VIEW3D_PT_CustomPanel_applymodifiers)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_CustomPanel_applymodifiers)
    bpy.utils.unregister_class(OBJECT_OT_apply_modifiers)

if __name__ == "__main__":
    register()