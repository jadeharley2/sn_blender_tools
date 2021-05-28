
import bpy, os
from bpy import ops 
bl_info = {
    "name": "SNTools Random skeleton and rigging tools",
	"blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import json
import io
import math
import mathutils
from mathutils import *

class VLV_BoneNameToBlender(bpy.types.Operator):
    """Rename lrig bones to blender style"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.vlvname_toblnd"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Rename lrig bones to blender style"         # Display name in the interface.
    bl_options = {'REGISTER','UNDO'}  
 
    def execute(self, context):    
        bones = bpy.context.active_object.pose.bones 
        for bone in bones:
            if "Lrig_LEG_BL" in bone.name:
                bone.name = bone.name.replace("Lrig_LEG_BL","Lrig_LEG_BX")+".L"
            if "Lrig_LEG_FL" in bone.name:
                bone.name = bone.name.replace("Lrig_LEG_FL","Lrig_LEG_FX")+".L"
            elif "Lrig_LEG_BR" in bone.name:
                bone.name = bone.name.replace("Lrig_LEG_BR","Lrig_LEG_BX")+".R"  
            elif "Lrig_LEG_FR" in bone.name:
                bone.name = bone.name.replace("Lrig_LEG_FR","Lrig_LEG_FX")+".R"  
            elif "Bip01_L_" in bone.name:
                bone.name = bone.name.replace("Bip01_L_","Bip01_X_")+".L"  
            elif "Bip01_R_" in bone.name:
                bone.name = bone.name.replace("Bip01_R_","Bip01_X_")+".R"  
        return {'FINISHED'}  
class VLV_BoneNameToSource(bpy.types.Operator):
    """Rename lrig bones to valve style"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.vlvname_tosourse"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Rename lrig bones to valve style"         # Display name in the interface.
    bl_options = {'REGISTER','UNDO'}  
 
    def execute(self, context):    
        bones = bpy.context.active_object.pose.bones 
        for bone in bones:
            if "Lrig_LEG_BX" in bone.name:
                if ".L" in bone.name:
                    bone.name = bone.name.replace("Lrig_LEG_BX","Lrig_LEG_BL").replace(".L","")
                elif ".R" in bone.name:
                    bone.name = bone.name.replace("Lrig_LEG_BX","Lrig_LEG_BR").replace(".R","")  
            if "Lrig_LEG_FX" in bone.name:
                if ".L" in bone.name:
                    bone.name = bone.name.replace("Lrig_LEG_FX","Lrig_LEG_FL").replace(".L","")
                elif ".R" in bone.name:
                    bone.name = bone.name.replace("Lrig_LEG_FX","Lrig_LEG_FR").replace(".R","")  
            if "Bip01_X_" in bone.name:
                if ".L" in bone.name:
                    bone.name = bone.name.replace("Bip01_X_","Bip01_L_").replace(".L","")
                elif ".R" in bone.name:
                    bone.name = bone.name.replace("Bip01_X_","Bip01_R_").replace(".R","")  
        return {'FINISHED'}  
        
class CreatePointBones(bpy.types.Operator):
    """Create point bones from vertex groups"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.crt_point_bones"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Create point bones from vertex groups"         # Display name in the interface.
    bl_options = {'REGISTER','UNDO'}  
 
    tail_shift = bpy.props.FloatVectorProperty(name="axis",default=(0.01,0,0)) 
    
    def execute(self, context):    
        o =  bpy.context.active_object
        groups = o.vertex_groups 
         
        bpy.ops.object.armature_add(enter_editmode=True,  location= o.location) # align='WORLD', scale=(1, 1, 1),
        arm = bpy.context.active_object
        for grp in groups: 
            #bone.head = grp 
            total_weight = 0
            center = Vector((0,0,0))
            for v in o.data.vertices:
                cweight = 0
                rem_ids = [] 
                for g in v.groups: 
                    if g.group == grp.index:
                        center = center + v.co * g.weight
                        total_weight = total_weight + g.weight
            if total_weight>0: 
                bone = arm.data.edit_bones.new(grp.name)   
                center = center / total_weight
                print(bone.name+" "+str(center))
                bone.head = center 
                bone.tail = center + Vector(self.tail_shift)
                
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}  

class TransferVGWeights(bpy.types.Operator):
    """Transfer vertex group weights to active group"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.vgweights_transfer"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Transfer vertex group weights to active group"         # Display name in the interface.
    bl_options = {'REGISTER'}  # Enable undo for the operator.
 
    def execute(self, context):    

        o = bpy.context.active_object
        activebone = bpy.context.active_pose_bone
        selbones = [k.name for k in bpy.context.selected_pose_bones if k != activebone]
        
        vg_dict = {vgroup.index:vgroup for vgroup in o.vertex_groups}   
        vg_selected = [vg.index for vg in o.vertex_groups if vg.name in selbones]
        vg_active = o.vertex_groups[activebone.name]

        print('weight transfer')
        for vg in selbones: print('from: '+vg)
        print('to: '+activebone.name)

        for v in o.data.vertices:
            cweight = 0
            rem_ids = []
            for g in v.groups:
                if g.group in vg_selected:
                    cweight = cweight + g.weight
                    rem_ids.append(g.group)
            for g in rem_ids: vg_dict[g].remove([v.index])
            if cweight>0:
                vg_active.add([v.index],cweight,'ADD')
                
        
        return {'FINISHED'}  

def menu_func(self, context):
    self.layout.operator(VLV_BoneNameToSource.bl_idname)
    self.layout.operator(VLV_BoneNameToBlender.bl_idname)   
    self.layout.operator(CreatePointBones.bl_idname)  
def menu_func2(self, context): 
    self.layout.operator(TransferVGWeights.bl_idname)

def register(): 
    bpy.utils.register_class(VLV_BoneNameToBlender)
    bpy.utils.register_class(VLV_BoneNameToSource)
    bpy.utils.register_class(TransferVGWeights)
    bpy.utils.register_class(CreatePointBones)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    #bpy.types.VIEW3D_MT_paint_texture.append(menu2_func)

def unregister(): 
    bpy.utils.unregister_class(VLV_BoneNameToBlender)
    bpy.utils.unregister_class(VLV_BoneNameToSource)
    bpy.utils.unregister_class(TransferVGWeights)
    bpy.utils.unregister_class(CreatePointBones)

if __name__ == "__main__":
	register()