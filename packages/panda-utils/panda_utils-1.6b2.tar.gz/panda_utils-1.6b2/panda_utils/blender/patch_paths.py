import os

import bpy


def update_texture_paths():
    for mat in bpy.data.materials:
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    img = node.image
                    if img is not None:
                        img.filepath = img.filepath.replace(os.path.sep, "/").split("/")[-1]


update_texture_paths()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
