bl_info = {
    "name": "Sync Render Visibility",
    "blender": (4, 1, 0),
    "category": "Object",
}

import bpy

class OBJECT_OT_toggle_render_visibility(bpy.types.Operator):
    """Sync Render Visibility"""
    bl_idname = "object.toggle_render_visibility"
    bl_label = "Sync With Viewport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        count = 0  # Compteur pour le nombre d'objets affectés

        # Function to toggle render visibility based on viewport visibility for objects
        def toggle_render_visibility_objects(count):
            for obj in bpy.context.scene.objects:
                if not obj.visible_get():
                    obj.hide_render = True
                else:
                    obj.hide_render = False
                count += 1  # Incrémenter le compteur pour chaque objet traité
            return count


        # Function to toggle render visibility based on viewport visibility for modifiers
        def toggle_render_visibility_modifiers():
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    for mod in obj.modifiers:
                        # If the modifier is not visible in the viewport, hide it in render too
                        if not mod.show_viewport:
                            mod.show_render = False
                        else:
                            mod.show_render = True

        # Call the functions to apply the changes
        count = toggle_render_visibility_objects(count)
        toggle_render_visibility_modifiers()
        
        self.report({'INFO'}, f"Visibility toggled successfully for {count} objects")
        return {'FINISHED'}

class VIEW3D_PT_CustomPanel_visibilty(bpy.types.Panel):
    """Crée un panneau dans la catégorie Objets"""
    bl_label = "Sync Render Visibility"
    bl_idname = "VIEW3D_PT_custom_panel_visibilty"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_toggle_render_visibility.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_toggle_render_visibility)
    bpy.utils.register_class(VIEW3D_PT_CustomPanel_visibilty)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_CustomPanel_visibilty)
    bpy.utils.unregister_class(OBJECT_OT_toggle_render_visibility)

if __name__ == "__main__":
    register()