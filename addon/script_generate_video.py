import bpy
import json

################# ВЕРСИЯ 1 (upgrade) #################

def interpolation_type(obj, inter_type = 'LINEAR'):
    
    #Интерполяция (по стандарту - линейная)
    
    fc = obj.animation_data.action.fcurves
    for index in range(2,11):
        fc_index = fc[index]
        for keyframe in fc_index.keyframe_points:
            keyframe.interpolation = inter_type

    fc_mat = bpy.data.materials[obj.name].node_tree.animation_data.action.fcurves
    for i in range(4):
        fc_mat_i = fc_mat[i]
        for keyframe in fc_mat_i.keyframe_points:
            keyframe.interpolation = inter_type
    return

def add_object(name, verts, faces, edges=[], col_name='Video_col.1'):
    
    #Добавление пользовательского объекта
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(mesh.name, mesh)
    col = bpy.data.collections.get(col_name)
    col.objects.link(obj)
    #bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(verts, edges, faces)
    return obj

def add_basic_object(obj, counter, col_name='Video_col.1'):
    
    #Добавление базового объекта
    
    if obj['type'].lower() == 'cube':
        # Добавляем куб
        bpy.ops.mesh.primitive_cube_add(size=obj['size'], enter_editmode=False, location=(0, 0, 0))
        bpy.context.active_object.name = obj['id']+'.'+counter
        ob = bpy.data.objects[obj['id']+'.'+counter]
        ob.data.name = obj['id']+'.'+counter
        for obj in ob.users_collection[:]:
            obj.objects.unlink(ob)
        col = bpy.data.collections.get(col_name)
        col.objects.link(ob)
    elif obj['type'].lower() == 'parallelepiped': # Пока в разработке
        # Добавляем параллелепипед
        bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=(0, 0, 0))
        bpy.context.active_object.name = obj['id']+'.'+counter
        ob = bpy.data.objects[obj['id']+'.'+counter]
        ob.scale= (obj['scale'][0], obj['scale'][1], obj['scale'][2])
        ob.data.name = obj['id']+'.'+counter
        for obj in ob.users_collection[:]:
            obj.objects.unlink(ob)
        col = bpy.data.collections.get(col_name)
        col.objects.link(ob)
    elif obj['type'].lower() == 'sphere':
        # Добавляем сферу
        bpy.ops.mesh.primitive_uv_sphere_add(radius=obj['size'], enter_editmode=False, location=(0, 0, 0))
        bpy.context.active_object.name = obj['id']+'.'+counter
        bpy.ops.object.shade_smooth()
        ob = bpy.data.objects[obj['id']+'.'+counter]
        ob.data.name = obj['id']+'.'+counter
        for obj in ob.users_collection[:]:
            obj.objects.unlink(ob)
        col = bpy.data.collections.get(col_name)
        col.objects.link(ob)
    elif obj['type'].lower() == 'plane':
        # Добавляем плоскость
        bpy.ops.mesh.primitive_plane_add(size=obj['size'], enter_editmode=False, location=(0, 0, 0))
        bpy.context.active_object.name = obj['id']+'.'+counter
        ob = bpy.data.objects[obj['id']+'.'+counter]
        ob.data.name = obj['id']+'.'+counter
        for obj in ob.users_collection[:]:
            obj.objects.unlink(ob)
        col = bpy.data.collections.get(col_name)
        col.objects.link(ob)
    return ob

def animated_material(obj, color, cur_frame):
    
    #Анимация цвета
    
    #color.append(1)
    if obj.name in bpy.data.materials:
        if bpy.data.materials[obj.name].node_tree.nodes['Diffuse BSDF'].inputs[0].default_value == color:
            return
        else:
            bpy.data.materials[obj.name].node_tree.nodes['Diffuse BSDF'].inputs[0].default_value = color
            bpy.data.materials[obj.name].node_tree.nodes['Diffuse BSDF'].inputs[0].keyframe_insert("default_value", frame= cur_frame)
            #upgrade
            fc_mat = bpy.data.materials[obj.name].node_tree.animation_data.action.fcurves
            for index in range(4):
                fc_mat[index].keyframe_points[-1].interpolation = 'LINEAR'

    else:
        new_material = bpy.data.materials.new( name= obj.name)
        new_material.use_nodes = True
        new_material.node_tree.nodes.remove(new_material.node_tree.nodes.get('Principled BSDF'))
        material_output = new_material.node_tree.nodes.get('Material Output')
        material_output.location = (400,0)
        diffuse_node = new_material.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        diffuse_node.location = (200,0)
        diffuse_node.inputs[0].default_value = color
        diffuse_node.inputs[0].keyframe_insert("default_value", frame= cur_frame)
        new_material.node_tree.links.new(diffuse_node.outputs[0], material_output.inputs[0])
        #bpy.context.object.active_material = new_material
        bpy.data.objects[obj.name].data.materials.append(bpy.data.materials[obj.name])
        #upgrade
        fc_mat = new_material.node_tree.animation_data.action.fcurves
        for index in range(4):
            fc_mat[index].keyframe_points[-1].interpolation = 'LINEAR'

def hide_object(obj, fr):
    
    #Скрытие объекта
    
    obj.hide_viewport = True
    obj.keyframe_insert(data_path="hide_viewport", frame=fr)
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_render", frame=fr)

def uncover_object(obj, fr):
    
    #Проявление объекта
    
    obj.hide_viewport = False
    obj.keyframe_insert(data_path="hide_viewport", frame=fr)
    obj.hide_render = False
    obj.keyframe_insert(data_path="hide_render", frame=fr)

def generate_video(input_filepath):
    with open(input_filepath, 'r') as f:
        move = json.load(f)

    # Создание сцены и объекта
    counter = 1
    for i in list(bpy.data.scenes.keys()):
        a = i.split('.')
        if (a[0] == 'Video Creator'):
            counter +=1
    counter = str(counter)
    bpy.context.window.scene = bpy.data.scenes.new(name='Video Creator.'+counter) 
    newCol = bpy.data.collections.new('Video_col.'+counter)
    bpy.context.window.scene.collection.children.link(newCol)
    # ------

    be = [] # Список существующих объектов
    basic_objects = ['cube', 'plane', 'sphere', 'parallelepiped']

    # Расставляем объекты на сцене и прячем
    for time_frame in move:
        for obj in time_frame['objects']:
            if obj['id'] not in be:
                if obj['type'].lower() in basic_objects:
                    ob = add_basic_object(obj, counter, col_name=newCol.name)
                else:
                    ob = add_object(obj['id']+'.'+counter, obj['size']['verts'], obj['size']['faces'],
                                    edges=[], col_name=newCol.name)
                be.append(obj['id'])
                hide_object(ob, 0)
    #-------

    for time_frame in move:
        fr = time_frame['cur_frame']
        be_now = [] # Список существующих объектов в данный момент
        for obj in time_frame['objects']:
            ob = bpy.data.objects[obj['id']+'.'+counter]
            be_now.append(obj['id'])

            uncover_object(ob, fr)
            animated_material(ob, obj['color'], fr)

            ob.location = (obj['location']['x'], obj['location']['y'], obj['location']['z'])
            ob.rotation_euler.x = obj['rotation']['x']
            ob.rotation_euler.y = obj['rotation']['y']
            ob.rotation_euler.z = obj['rotation']['z']
            ob.scale = (obj['scale'][0], obj['scale'][1], obj['scale'][2])

            ob.keyframe_insert(data_path="location", frame=fr, index=-1)
            ob.keyframe_insert("rotation_euler", frame=fr)
            ob.keyframe_insert("scale", frame=fr)

            #upgrade
            fc = ob.animation_data.action.fcurves
            for index in range(2,11):
                fc[index].keyframe_points[-1].interpolation = 'LINEAR'
                   
            #interpolation_type(ob) # Интерполяция
        
        set_be_now = set(be_now)
        set_be = set(be)
        hide_objects = set_be - set_be_now
        for obj in bpy.context.window.scene.objects:
            name = obj.name.split('.')
            if name[0] in hide_objects:
                hide_object(obj, fr)

    return fr


################# ВЕРСИЯ 2 #################
'''
def add_object(name, verts, faces, edges=[], col_name='Video_col.1'):
    
    #Добавление пользовательского объекта
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(mesh.name, mesh)
    col = bpy.data.collections.get(col_name)
    col.objects.link(obj)
    #bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(verts, edges, faces)
    return obj

def add_basic_object(obj, counter, col_name='Video_col.1'):
    
    #Добавление базового объекта
    
    if obj['type'].lower() == 'cube':
        # Добавляем куб
        bpy.ops.mesh.primitive_cube_add(size=obj['size'], enter_editmode=False, location=(0, 0, 0))
        bpy.context.active_object.name = obj['id']+'.'+counter
        ob = bpy.data.objects[obj['id']+'.'+counter]
        ob.data.name = obj['id']+'.'+counter
        for obj in ob.users_collection[:]:
            obj.objects.unlink(ob)
        col = bpy.data.collections.get(col_name)
        col.objects.link(ob)
    elif obj['type'].lower() == 'parallelepiped': # Пока в разработке
        # Добавляем параллелепипед
        bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=(0, 0, 0))
        bpy.context.active_object.name = obj['id']+'.'+counter
        ob = bpy.data.objects[obj['id']+'.'+counter]
        ob.scale= (obj['scale'][0], obj['scale'][1], obj['scale'][2])
        ob.data.name = obj['id']+'.'+counter
        for obj in ob.users_collection[:]:
            obj.objects.unlink(ob)
        col = bpy.data.collections.get(col_name)
        col.objects.link(ob)
    elif obj['type'].lower() == 'sphere':
        # Добавляем сферу
        bpy.ops.mesh.primitive_uv_sphere_add(radius=obj['size'], enter_editmode=False, location=(0, 0, 0))
        bpy.context.active_object.name = obj['id']+'.'+counter
        bpy.ops.object.shade_smooth()
        ob = bpy.data.objects[obj['id']+'.'+counter]
        ob.data.name = obj['id']+'.'+counter
        for obj in ob.users_collection[:]:
            obj.objects.unlink(ob)
        col = bpy.data.collections.get(col_name)
        col.objects.link(ob)
    elif obj['type'].lower() == 'plane':
        # Добавляем плоскость
        bpy.ops.mesh.primitive_plane_add(size=obj['size'], enter_editmode=False, location=(0, 0, 0))
        bpy.context.active_object.name = obj['id']+'.'+counter
        ob = bpy.data.objects[obj['id']+'.'+counter]
        ob.data.name = obj['id']+'.'+counter
        for obj in ob.users_collection[:]:
            obj.objects.unlink(ob)
        col = bpy.data.collections.get(col_name)
        col.objects.link(ob)
    return ob

def object_animation(obj):
    
    #Анимируем параметры location, rotation, scale
    
    obj.animation_data_create()
    obj.animation_data.action = bpy.data.actions.new(obj.name)
    obj.animation_data.action.fcurves.new(data_path="location",index= 0)
    obj.animation_data.action.fcurves.new(data_path="location",index= 1)
    obj.animation_data.action.fcurves.new(data_path="location",index= 2)

    obj.animation_data.action.fcurves.new(data_path="rotation_euler",index= 0)
    obj.animation_data.action.fcurves.new(data_path="rotation_euler",index= 1)
    obj.animation_data.action.fcurves.new(data_path="rotation_euler",index= 2)

    obj.animation_data.action.fcurves.new(data_path="scale",index= 0)
    obj.animation_data.action.fcurves.new(data_path="scale",index= 1)
    obj.animation_data.action.fcurves.new(data_path="scale",index= 2)


def animated_material(obj, color, cur_frame):
    
    #Анимация цвета
    
    #color.append(1)
    if obj.name in bpy.data.materials:
        if bpy.data.materials[obj.name].node_tree.nodes['Diffuse BSDF'].inputs[0].default_value == color:
            return
        else:
            fc_mat = bpy.data.materials[obj.name].node_tree.animation_data.action.fcurves
            fc_mat[0].keyframe_points.add(1)
            fc_mat[0].keyframe_points[-1].co = cur_frame, color[0]
            fc_mat[0].keyframe_points[-1].interpolation = 'LINEAR'

            fc_mat[1].keyframe_points.add(1)
            fc_mat[1].keyframe_points[-1].co = cur_frame, color[1]
            fc_mat[1].keyframe_points[-1].interpolation = 'LINEAR'

            fc_mat[2].keyframe_points.add(1)
            fc_mat[2].keyframe_points[-1].co = cur_frame, color[2]
            fc_mat[2].keyframe_points[-1].interpolation = 'LINEAR'

            fc_mat[3].keyframe_points.add(1)
            fc_mat[3].keyframe_points[-1].co = cur_frame, color[3]
            fc_mat[3].keyframe_points[-1].interpolation = 'LINEAR'
    else:
        new_material = bpy.data.materials.new( name= obj.name)
        new_material.use_nodes = True

        new_material.node_tree.nodes.remove(new_material.node_tree.nodes.get('Principled BSDF'))
        material_output = new_material.node_tree.nodes.get('Material Output')
        material_output.location = (400,0)

        diffuse_node = new_material.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        diffuse_node.location = (200,0)
        diffuse_node.inputs[0].default_value = color
        diffuse_node.inputs[0].keyframe_insert("default_value", frame= cur_frame)
        new_material.node_tree.links.new(diffuse_node.outputs[0], material_output.inputs[0])
        bpy.data.objects[obj.name].data.materials.append(bpy.data.materials[obj.name])
        
        fc_mat = bpy.data.materials[obj.name].node_tree.animation_data.action.fcurves
        fc_mat[0].keyframe_points[-1].interpolation = 'LINEAR'
        fc_mat[1].keyframe_points[-1].interpolation = 'LINEAR'
        fc_mat[2].keyframe_points[-1].interpolation = 'LINEAR'
        fc_mat[3].keyframe_points[-1].interpolation = 'LINEAR'

def hide_object(obj, fr):
    
    #Скрытие объекта
    
    obj.hide_viewport = True
    obj.keyframe_insert(data_path="hide_viewport", frame=fr)
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_render", frame=fr)

def uncover_object(obj, fr):
    
    #Проявление объекта
    
    obj.hide_viewport = False
    obj.keyframe_insert(data_path="hide_viewport", frame=fr)
    obj.hide_render = False
    obj.keyframe_insert(data_path="hide_render", frame=fr)

def generate_video(input_filepath):
    with open(input_filepath, 'r') as f:
        move = json.load(f)

    # Создание сцены и объекта
    counter = 1
    for i in list(bpy.data.scenes.keys()):
        a = i.split('.')
        if (a[0] == 'videoCreator'):
            counter +=1
    counter = str(counter)
    bpy.context.window.scene = bpy.data.scenes.new(name='videoCreator.'+counter) 
    newCol = bpy.data.collections.new('Video_col.'+counter)
    bpy.context.window.scene.collection.children.link(newCol)
    # ------

    be = [] # Список существующих объектов
    basic_objects = ['cube', 'plane', 'sphere', 'parallelepiped']

    # Расставляем объекты на сцене и прячем
    for time_frame in move:
        for obj in time_frame['objects']:
            if obj['id'] not in be:
                if obj['type'].lower() in basic_objects:
                    ob = add_basic_object(obj, counter, col_name=newCol.name)
                    object_animation(ob) #Анимируем объект 
                else:
                    ob = add_object(obj['id']+'.'+counter, obj['size']['verts'], obj['size']['faces'],
                                    edges=[], col_name=newCol.name)
                    object_animation(ob) #Анимируем объект 
                be.append(obj['id'])
                hide_object(ob, 0)
   

    for time_frame in move:
        fr = time_frame['cur_frame']
        be_now = [] # Список существующих объектов в данный момент
        for obj in time_frame['objects']:
            ob = bpy.data.objects[obj['id']+'.'+counter]
            be_now.append(obj['id'])
            
            uncover_object(ob, fr)
            
            animated_material(ob, obj['color'], fr)

            ob.animation_data.action.fcurves[0].keyframe_points.add(1)
            ob.animation_data.action.fcurves[0].keyframe_points[-1].co = fr, obj['location']['x']
            ob.animation_data.action.fcurves[0].keyframe_points[-1].interpolation = 'LINEAR'
    
            ob.animation_data.action.fcurves[1].keyframe_points.add(1)
            ob.animation_data.action.fcurves[1].keyframe_points[-1].co = fr, obj['location']['y']
            ob.animation_data.action.fcurves[1].keyframe_points[-1].interpolation = 'LINEAR'
    
            ob.animation_data.action.fcurves[2].keyframe_points.add(1)
            ob.animation_data.action.fcurves[2].keyframe_points[-1].co = fr, obj['location']['z']
            ob.animation_data.action.fcurves[2].keyframe_points[-1].interpolation = 'LINEAR'
    
            ob.animation_data.action.fcurves[3].keyframe_points.add(1)
            ob.animation_data.action.fcurves[3].keyframe_points[-1].co = fr, obj['rotation']['x']
            ob.animation_data.action.fcurves[3].keyframe_points[-1].interpolation = 'LINEAR'
    
            ob.animation_data.action.fcurves[4].keyframe_points.add(1)
            ob.animation_data.action.fcurves[4].keyframe_points[-1].co = fr, obj['rotation']['y']
            ob.animation_data.action.fcurves[4].keyframe_points[-1].interpolation = 'LINEAR'
    
            ob.animation_data.action.fcurves[5].keyframe_points.add(1)
            ob.animation_data.action.fcurves[5].keyframe_points[-1].co = fr, obj['rotation']['z']
            ob.animation_data.action.fcurves[5].keyframe_points[-1].interpolation = 'LINEAR'
    
            ob.animation_data.action.fcurves[6].keyframe_points.add(1)
            ob.animation_data.action.fcurves[6].keyframe_points[-1].co = fr, obj['scale'][0]
            ob.animation_data.action.fcurves[6].keyframe_points[-1].interpolation = 'LINEAR'
    
            ob.animation_data.action.fcurves[7].keyframe_points.add(1)
            ob.animation_data.action.fcurves[7].keyframe_points[-1].co = fr, obj['scale'][1]
            ob.animation_data.action.fcurves[7].keyframe_points[-1].interpolation = 'LINEAR'
    
            ob.animation_data.action.fcurves[8].keyframe_points.add(1)
            ob.animation_data.action.fcurves[8].keyframe_points[-1].co = fr, obj['scale'][2]
            ob.animation_data.action.fcurves[8].keyframe_points[-1].interpolation = 'LINEAR'
            
        
        set_be_now = set(be_now)
        set_be = set(be)
        hide_objects = set_be - set_be_now
        for obj in bpy.context.window.scene.objects:
            name = obj.name.split('.')
            if name[0] in hide_objects:
                hide_object(obj, fr)

    return fr

'''