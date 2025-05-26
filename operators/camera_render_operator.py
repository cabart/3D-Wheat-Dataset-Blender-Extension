# Code heavily based on BlenderNerf (https://github.com/maximeraafat/BlenderNeRF/tree/main)

from ..properties.enum_objects import RenderMode
import bpy
import random
from bpy.app.handlers import persistent
from mathutils import Vector, Quaternion
import json
import os
from .. import globals
from tqdm import tqdm
import numpy as np
from PIL import Image
import shutil


CAMERA_NAME = "LPy Camera"  # Camera name used for rendering


class CameraRenderOperator(bpy.types.Operator):
    """Operator to visualize and render cameras for training and testing images using various camera placement strategies

    Uses the animation timeline to render images. When changing to a new frame the camera is updated to the new position according to the sampling strategy (see rendering_camera_update(...)).
    Saves additonal information such as intrinsic camera parameters, extrinsic camera parameters, plant parts labels in a JSON file.
    Saves the 3D mesh of the plants as an OBJ file.
    """

    bl_idname = "lsys.render"
    bl_label = ""
    bl_options = {"REGISTER"}

    def execute(self, context):
        camera_props = bpy.context.scene.CameraRenderProps

        # Check if output directory already exists
        if os.path.exists(camera_props.save_path) and camera_props.render:
            self.report({"ERROR"}, "Output directory already exists!")
            return {"FINISHED"}

        # check if camera is selected : next errors depend on an existing camera
        if context.scene == None:
            self.report({"ERROR"}, "Be sure to have a selected camera!")
            return {"FINISHED"}

        scene = context.scene
        camera = (
            scene.camera
        )  # Camera to be used as a reference for the intrinsic parameters
        camera_props.original_camera = scene.camera.name

        # Setup a collection for visualization of all cameras
        old_collection = bpy.data.collections.get("render_cameras_train", None)
        if old_collection is not None:
            for obj in old_collection.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(old_collection)
        train_camera_collection = bpy.data.collections.new("render_cameras_train")
        bpy.context.scene.collection.children.link(train_camera_collection)

        old_collection = bpy.data.collections.get("render_cameras_test", None)
        if old_collection is not None:
            for obj in old_collection.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(old_collection)
        test_camera_collection = bpy.data.collections.new("render_cameras_test")
        bpy.context.scene.collection.children.link(test_camera_collection)

        # Copy selected camera and use it for rendering (intrinsics might get overwritten in camera sampling)
        rendering_camera = camera.copy()  # Create a copy of the camera object
        rendering_camera.data = (
            camera.data.copy()
        )  # Ensure the camera data (lens, settings) is also duplicated
        rendering_camera.name = CAMERA_NAME
        train_camera_collection.objects.link(rendering_camera)
        scene.camera = rendering_camera

        # Get camera locations and rotations, depends on selected sampling strategy (extrinsic camera parameters, might also change camera intrinsic parameters)
        train_cameras = globals.camera_placements[camera_props.camera_placement_train](
            RenderMode.TRAIN
        )
        test_cameras = globals.camera_placements[camera_props.camera_placement_test](
            RenderMode.TEST
        )

        # Get intrinsic parameters of camera
        output_data_train, colmap_camera = self.get_camera_intrinsics(
            scene, rendering_camera
        )
        output_data_test = output_data_train.copy()
        output_data_transform = output_data_train.copy()

        # Visualize train and test cameras (not used for rendering)
        for i, (camera_location, camera_rotation) in enumerate(train_cameras):
            camera_data = bpy.data.cameras.new(name="Camera" + str(i + 1))
            camera_object = bpy.data.objects.new("Camera" + str(i + 1), camera_data)
            camera_object.location = camera_location
            camera_object.rotation_mode = "QUATERNION"
            camera_object.rotation_quaternion = camera_rotation
            camera_object.data = rendering_camera.data.copy()
            train_camera_collection.objects.link(camera_object)

        for i, (camera_location, camera_rotation) in enumerate(test_cameras):
            camera_data = bpy.data.cameras.new(
                name="Camera" + str(i + 1 + len(train_cameras))
            )
            camera_object = bpy.data.objects.new(
                "Camera" + str(i + 1 + len(train_cameras)), camera_data
            )
            camera_object.location = camera_location
            camera_object.rotation_mode = "QUATERNION"
            camera_object.rotation_quaternion = camera_rotation
            camera_object.data = rendering_camera.data.copy()
            test_camera_collection.objects.link(camera_object)

        # Get extrinsic camera parameters
        camera_props.current_render_mode = RenderMode.TRAIN.value
        colmap_images = ""
        (
            output_data_train["frames"],
            output_data_transform["train_filenames"],
            colmap_images,
            transform_train,
        ) = self.get_camera_extrinsics(scene, rendering_camera, colmap_images)

        camera_props.current_render_mode = RenderMode.TEST.value
        (
            output_data_test["frames"],
            output_data_transform["test_filenames"],
            colmap_images,
            transform_test,
        ) = self.get_camera_extrinsics(
            scene, rendering_camera, colmap_images, test=True
        )

        output_data_transform["frames"] = transform_train + transform_test

        if camera_props.render:
            # Create output directory
            os.makedirs(camera_props.save_path, exist_ok=False)

            camera_props.current_render_mode = RenderMode.TRAIN.value
            for frame in tqdm(
                range(1, camera_props.train_frames_total + 1),
                desc="Rendering training images",
            ):
                bpy.ops.outliner.orphans_purge()
                render_camera(scene, rendering_camera, frame, mode=RenderMode.TRAIN)
            camera_props.current_render_mode = RenderMode.TEST.value
            for frame in tqdm(
                range(1, camera_props.test_frames_total + 1),
                desc="Rendering testing images",
            ):
                bpy.ops.outliner.orphans_purge()
                render_camera(scene, rendering_camera, frame, mode=RenderMode.TEST)

            # Save colmap format, used for creating colmap data format with known camera poses
            colmap_dir = os.path.join(camera_props.save_path, "colmap")
            sparse_dir = os.path.join(colmap_dir, "sparse_known_cameras")
            if not os.path.exists(colmap_dir):
                os.makedirs(colmap_dir)
                os.makedirs(sparse_dir)

            self.save_txt(sparse_dir, "images.txt", colmap_images)
            self.save_txt(sparse_dir, "cameras.txt", colmap_camera)
            self.save_txt(sparse_dir, "points3D.txt", "")

            train_split, test_split = self.create_train_transform_split_files(
                camera_props.train_frames_total, camera_props.test_frames_total
            )
            self.save_txt(colmap_dir, "train_list.txt", train_split)
            self.save_txt(colmap_dir, "test_list.txt", test_split)

            nb_info = {
                "loader": "colmap",
                "type": "object-centric",
                "downscale_factor": 1,
                "downscale_loaded_factor": 1,
            }
            self.save_json(colmap_dir, "nb-info.json", nb_info)

            # Save transforms
            self.save_json(
                camera_props.save_path, "transforms_train.json", output_data_train
            )
            self.save_json(
                camera_props.save_path, "transforms_test.json", output_data_test
            )

            # Save model
            self.save_model(camera_props.save_path, "model.obj", "lpy_collection")

            # Save point cloud
            self.save_point_cloud(
                camera_props.save_path, "points3D.txt", camera_props.point_cloud_samples
            )

            # Save labels dictionary
            self.save_json(camera_props.save_path, "labels.json", globals.plant_labels)

            # Rename test images to correct number
            for i in range(camera_props.test_frames_total, 0, -1):
                os.rename(
                    os.path.join(camera_props.save_path, "test", f"{i:04d}.png"),
                    os.path.join(
                        camera_props.save_path,
                        "test",
                        f"{(i + camera_props.train_frames_total):04d}.png",
                    ),
                )
                os.rename(
                    os.path.join(camera_props.save_path, "masks_test", f"{i:04d}.png"),
                    os.path.join(
                        camera_props.save_path,
                        "masks_test",
                        f"{(i + camera_props.train_frames_total):04d}.png",
                    ),
                )
                os.rename(
                    os.path.join(camera_props.save_path, "depth_test", f"{i:04d}.exr"),
                    os.path.join(
                        camera_props.save_path,
                        "depth_test",
                        f"{(i + camera_props.train_frames_total):04d}.exr",
                    ),
                )

            # Remove '.png' file from train and test folders
            file_path = os.path.join(camera_props.save_path, "train", ".png")
            if os.path.exists(file_path):
                os.remove(file_path)
            file_path = os.path.join(camera_props.save_path, "test", ".png")
            if os.path.exists(file_path):
                os.remove(file_path)

            # Move train and test images to images folder
            os.makedirs(os.path.join(camera_props.save_path, "images"), exist_ok=True)
            os.makedirs(os.path.join(camera_props.save_path, "masks"), exist_ok=True)
            os.makedirs(os.path.join(camera_props.save_path, "depth"), exist_ok=True)
            self.move_files(
                os.path.join(camera_props.save_path, "train"),
                os.path.join(camera_props.save_path, "images"),
            )
            self.move_files(
                os.path.join(camera_props.save_path, "test"),
                os.path.join(camera_props.save_path, "images"),
            )
            self.move_files(
                os.path.join(camera_props.save_path, "masks_train"),
                os.path.join(camera_props.save_path, "masks"),
            )
            self.move_files(
                os.path.join(camera_props.save_path, "masks_test"),
                os.path.join(camera_props.save_path, "masks"),
            )
            self.move_files(
                os.path.join(camera_props.save_path, "depth_train"),
                os.path.join(camera_props.save_path, "depth"),
            )
            self.move_files(
                os.path.join(camera_props.save_path, "depth_test"),
                os.path.join(camera_props.save_path, "depth"),
            )

            os.rmdir(os.path.join(camera_props.save_path, "train"))
            os.rmdir(os.path.join(camera_props.save_path, "test"))
            os.rmdir(os.path.join(camera_props.save_path, "masks_train"))
            os.rmdir(os.path.join(camera_props.save_path, "masks_test"))
            os.rmdir(os.path.join(camera_props.save_path, "depth_train"))
            os.rmdir(os.path.join(camera_props.save_path, "depth_test"))

            # Create nerfbaselines nerfstudio dataloader format
            nerfstudio_path = os.path.join(camera_props.save_path, "nerfstudio")
            os.makedirs(nerfstudio_path, exist_ok=True)
            os.rename(
                os.path.join(camera_props.save_path, "points3D.txt"),
                os.path.join(nerfstudio_path, "points3D.txt"),
            )
            nerfstudio_masks_path = os.path.join(nerfstudio_path, "masks")
            os.makedirs(nerfstudio_masks_path)
            self.make_black_white_masks(
                os.path.join(camera_props.save_path, "masks"), nerfstudio_masks_path
            )

            create_masked_images(
                os.path.join(camera_props.save_path, "images"),
                os.path.join(camera_props.save_path, "masks"),
                os.path.join(nerfstudio_path, "images"),
            )

            self.save_json(nerfstudio_path, "transforms.json", output_data_transform)

            nb_info = {
                "loader": "nerfstudio",
                "type": "object-centric",
                "downscale_factor": 1,
                "downscale_loaded_factor": 1,
            }
            self.save_json(nerfstudio_path, "nb-info.json", nb_info)
        else:
            # Reset camera to original camera
            scene.camera = bpy.data.objects[camera_props.original_camera]

        return {"FINISHED"}

    def move_files(self, src_directory, dst_directory):
        for file_name in os.listdir(src_directory):
            os.rename(
                os.path.join(src_directory, file_name),
                os.path.join(dst_directory, file_name),
            )

    def copy_files(self, src_directory, dst_directory):
        for file_name in os.listdir(src_directory):
            shutil.copyfile(
                os.path.join(src_directory, file_name),
                os.path.join(dst_directory, file_name),
            )

    def make_black_white_masks(self, src_directory, dst_directory):
        for file_name in os.listdir(src_directory):
            image_path = os.path.join(src_directory, file_name)
            output_path = os.path.join(dst_directory, file_name)

            # Open the image in grayscale mode
            image = Image.open(image_path).convert("L")

            # Convert all non-black pixels to white
            bw_image = image.point(lambda p: 255 if p > 0 else 0)

            # Save the processed image
            bw_image.save(output_path)

    def create_train_transform_split_files(self, num_train_frames, num_test_frames):
        train_split = ""
        for i in range(1, num_train_frames + 1):
            train_split += f"{i:04d}.png\n"

        test_split = ""
        for i in range(num_train_frames + 1, num_train_frames + num_test_frames + 1):
            test_split += f"{i:04d}.png\n"

        return train_split, test_split

    def get_camera_intrinsics(self, scene, camera):
        """Get camera intrinsics for the given camera and scene. Return them in nerfstudio and colmap format"""

        camera_angle_x = camera.data.angle_x
        camera_angle_y = camera.data.angle_y

        # camera properties
        f_in_mm = camera.data.lens  # focal length in mm
        scale = scene.render.resolution_percentage / 100
        width_res_in_px = scene.render.resolution_x * scale  # width
        height_res_in_px = scene.render.resolution_y * scale  # height

        optical_center_x = width_res_in_px * (0.5 - camera.data.shift_x)
        optical_center_y = height_res_in_px * (0.5 + camera.data.shift_y)

        # pixel aspect ratios
        size_x = scene.render.pixel_aspect_x * width_res_in_px
        size_y = scene.render.pixel_aspect_y * height_res_in_px
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

        # sensor fit and sensor size (and camera angle swap in specific cases)
        if camera.data.sensor_fit == "AUTO":
            sensor_size_in_mm = (
                camera.data.sensor_height
                if width_res_in_px < height_res_in_px
                else camera.data.sensor_width
            )
            if width_res_in_px < height_res_in_px:
                sensor_fit = "VERTICAL"
                camera_angle_x, camera_angle_y = camera_angle_y, camera_angle_x
            elif width_res_in_px > height_res_in_px:
                sensor_fit = "HORIZONTAL"
            else:
                sensor_fit = "VERTICAL" if size_x <= size_y else "HORIZONTAL"

        else:
            sensor_fit = camera.data.sensor_fit
            if sensor_fit == "VERTICAL":
                sensor_size_in_mm = (
                    camera.data.sensor_height
                    if width_res_in_px <= height_res_in_px
                    else camera.data.sensor_width
                )
                if width_res_in_px <= height_res_in_px:
                    camera_angle_x, camera_angle_y = camera_angle_y, camera_angle_x

        # focal length for horizontal sensor fit
        if sensor_fit == "HORIZONTAL":
            sensor_size_in_mm = camera.data.sensor_width
            s_u = (f_in_mm * width_res_in_px) / sensor_size_in_mm
            s_v = (f_in_mm * width_res_in_px * pixel_aspect_ratio) / sensor_size_in_mm

        # focal length for vertical sensor fit
        if sensor_fit == "VERTICAL":
            s_u = (f_in_mm * (width_res_in_px / pixel_aspect_ratio)) / sensor_size_in_mm
            s_v = (f_in_mm * width_res_in_px) / sensor_size_in_mm

        camera_intr_dict = {
            "camera_angle_x": camera_angle_x,
            "camera_angle_y": camera_angle_y,
            "fl_x": s_u,
            "fl_y": s_v,
            "k1": 0.0,
            "k2": 0.0,
            "k3": 0.0,
            "k4": 0.0,
            "p1": 0.0,
            "p2": 0.0,
            "cx": round(optical_center_x),
            "cy": round(optical_center_y),
            "w": round(width_res_in_px),
            "h": round(height_res_in_px),
        }

        colmap_camera = f"1 PINHOLE {round(width_res_in_px)} {round(height_res_in_px)} {s_u} {s_v} {round(optical_center_x)} {round(optical_center_y)}"

        return camera_intr_dict, colmap_camera

    # camera extrinsics (transform matrices)
    def get_camera_extrinsics(self, scene, camera, colmap_images, test=False):
        # TODO: Rewrite, make flow more clear (camera placement in handler function is very intransparent)
        camera_props = bpy.context.scene.CameraRenderProps

        output_dir = "images"
        if test:
            frames_total = camera_props.test_frames_total
            # output_dir = 'test'
        else:
            frames_total = camera_props.train_frames_total
            # output_dir = 'train'

        scene.frame_start = 1
        scene.frame_step = 1
        scene.frame_end = frames_total

        initFrame = scene.frame_current
        step = scene.frame_step
        end = scene.frame_start + frames_total - 1

        camera_extr_dict = []
        camera_extr_dict_nerfbaselines = []
        split_list = []
        camera_props.dummy_render = True
        for frame in range(scene.frame_start, end + 1, step):
            scene.frame_set(frame)
            if test:
                frame += camera_props.train_frames_total
            filename = os.path.basename(scene.render.frame_path(frame=frame))
            filedir = output_dir

            frame_data = {
                "file_path": str(os.path.join(filedir, filename)).replace("\\", "/"),
                "transform_matrix": self.listify_matrix(camera.matrix_world),
            }

            # Add current image to current split (either train or test)
            split_list.append(str(os.path.join(filedir, filename)).replace("\\", "/"))

            # Create colmap format for known camera extrinsics
            quat_original = camera.matrix_world.to_quaternion()
            Q_colmap = Quaternion(
                (quat_original.x, quat_original.w, quat_original.z, -quat_original.y)
            )
            loc = Vector(camera.matrix_world.translation)
            loc = -(Q_colmap.to_matrix() @ loc)
            colmap_images += f"{frame} {Q_colmap.w} {Q_colmap.x} {Q_colmap.y} {Q_colmap.z} {loc[0]} {loc[1]} {loc[2]} 1 {filename}\n\n"

            camera_extr_dict.append(frame_data)

            # Paths on windows do use backslashes instead of forward slashes
            frame_data_nerfbaselines = {
                "file_path": str(os.path.join(filedir, filename)).replace("\\", "/"),
                "transform_matrix": self.listify_matrix(camera.matrix_world),
                "mask_path": str(os.path.join("masks", filename)).replace("\\", "/"),
            }
            camera_extr_dict_nerfbaselines.append(frame_data_nerfbaselines)

        scene.frame_set(initFrame)  # set back to initial frame
        camera_props.dummy_render = False

        return (
            camera_extr_dict,
            split_list,
            colmap_images,
            camera_extr_dict_nerfbaselines,
        )

    # function from original nerf 360_view.py code for blender
    def listify_matrix(self, matrix):
        matrix_list = []
        for row in matrix:
            matrix_list.append(list(row))
        return matrix_list

    def save_json(self, directory, filename, data, indent=4):
        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as file:
            json.dump(data, file, indent=indent)

    def save_txt(self, directory, filename, data):
        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as file:
            file.write(data)

    def save_model(self, directory, filename, collection_name):
        filepath = os.path.join(directory, filename)

        collection = bpy.data.collections.get(collection_name)

        bpy.ops.object.select_all(action="DESELECT")
        for obj in collection.objects:
            if (
                obj.type == "MESH"
                and obj.name != "GroundPlane"
                and obj.name != "CanopyMesh"
                and obj.name != "CanopyPointCloudMesh"
            ):
                obj.select_set(True)

        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=True,
        )

    def save_point_cloud(self, directory, filename, num_points):
        """
        Create new object joined from all objects of canopy
        Sample points on faces
        Save points in .obj file
        Save points in colmap format
        Cleanup all created objects afterwards
        """
        # Cleanup all created objects
        if bpy.data.objects.get("CanopyPointCloudMesh") is not None:
            bpy.data.objects.remove(
                bpy.data.objects.get("CanopyPointCloudMesh"), do_unlink=True
            )

        bpy.ops.object.add(type="MESH")
        canopy_mesh = bpy.context.active_object
        canopy_mesh.name = "CanopyMesh"

        # Example usage
        select_all_objects_from_collection("lpy_collection")
        # Copy selected objects
        bpy.ops.object.duplicate()

        # Set the empty object as the active object and select it
        canopy_mesh.select_set(True)
        bpy.context.view_layer.objects.active = canopy_mesh

        # Join the selected objects into the new empty object
        bpy.ops.object.join()

        create_point_cloud_with_geometry_nodes(canopy_mesh, num_points)
        bpy.ops.object.modifier_apply(modifier="PointCloud")

        # Reduce number of points to desired amount
        vertices = [
            (canopy_mesh.matrix_world @ vertice.co)
            for vertice in canopy_mesh.data.vertices
        ]
        random.shuffle(vertices)

        selected_vertices = vertices[:num_points]
        # Create random rgb color for each point in range [0, 255]
        colors = np.random.randint(0, 255, (num_points, 3))

        mesh = bpy.data.meshes.new("ReducedPointCloud")
        mesh.from_pydata(selected_vertices, [], [])
        mesh.update()

        # Save points to file
        filepath = os.path.join(directory, "blender_coordinates_" + filename)
        with open(filepath, "w") as file:
            file.write(
                f"# 3D points list in colmap format\n# Number of points: {num_points}\n"
            )
            for i, vertice in enumerate(selected_vertices):
                # x y z r g b error track[]
                file.write(
                    f"{i} {vertice.x} {vertice.y} {vertice.z} {colors[i][0]} {colors[i][1]} {colors[i][2]} 0\n"
                )

        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as file:
            file.write(
                f"# 3D points list in colmap format (x and y are flipped and z is inverted to match nerfbaselines nerfstudio data loader\n# Number of points: {num_points}\n"
            )
            for i, vertice in enumerate(selected_vertices):
                # x y z r g b error track[]
                file.write(
                    f"{i} {vertice.y} {vertice.x} {-vertice.z} {colors[i][0]} {colors[i][1]} {colors[i][2]} 0\n"
                )

        # Make points visible in the scene
        reduced_point_cloud = bpy.data.objects.new("CanopyPointCloudMesh", mesh)
        bpy.context.collection.objects.link(reduced_point_cloud)

        # Remove intermediate object
        bpy.data.objects.remove(bpy.data.objects.get("CanopyMesh"), do_unlink=True)


def select_all_objects_from_collection(collection_name):
    # Deselect all objects
    bpy.ops.object.select_all(action="DESELECT")

    # Get the collection
    collection = bpy.data.collections.get(collection_name)

    if collection:
        # Select all objects in the collection
        for obj in collection.objects:
            if obj.type == "MESH" and obj.name != "GroundPlane":
                obj.select_set(True)
    else:
        print(f"Collection '{collection_name}' not found")


def create_point_cloud_with_geometry_nodes(obj, num_points):
    # Create a new geometry nodes modifier
    geo_nodes_modifier = obj.modifiers.new(name="PointCloud", type="NODES")

    # Create a new node group and assign it to the modifier
    geo_nodes_tree = bpy.data.node_groups.new(
        name="PointCloudNodeGroup", type="GeometryNodeTree"
    )
    geo_nodes_modifier.node_group = geo_nodes_tree

    # Clear the default nodes
    geo_nodes_tree.nodes.clear()

    # Add input and output nodes
    input_node = geo_nodes_tree.nodes.new(type="NodeGroupInput")
    output_node = geo_nodes_tree.nodes.new(type="NodeGroupOutput")

    geo_nodes_tree.interface.new_socket(
        name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"
    )
    geo_nodes_tree.interface.new_socket(
        name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )

    # Add distribute points on faces node
    distribute_points_node = geo_nodes_tree.nodes.new(
        type="GeometryNodeDistributePointsOnFaces"
    )
    distribute_points_node.inputs["Density"].default_value = 10

    # Add face area node
    face_area_node = geo_nodes_tree.nodes.new(type="GeometryNodeInputMeshFaceArea")

    # Add Attribute Statistic node (for calculating total surface area)
    attribute_statistic_node = geo_nodes_tree.nodes.new(
        type="GeometryNodeAttributeStatistic"
    )

    # Add constant value node for desired number of points
    constant_value_node = geo_nodes_tree.nodes.new(type="ShaderNodeValue")
    constant_value_node.outputs["Value"].default_value = (
        num_points * 2
    )  # Due to rounding error the number of points may be slightly less than the desired number

    # Add a division node
    division_node = geo_nodes_tree.nodes.new(type="ShaderNodeMath")
    division_node.operation = "DIVIDE"

    # Add a points to vertices node
    points_to_vertices_node = geo_nodes_tree.nodes.new(
        type="GeometryNodePointsToVertices"
    )

    # Connect the nodes
    geo_nodes_tree.links.new(
        input_node.outputs["Geometry"], distribute_points_node.inputs["Mesh"]
    )
    geo_nodes_tree.links.new(
        points_to_vertices_node.outputs["Mesh"], output_node.inputs["Geometry"]
    )

    geo_nodes_tree.links.new(
        face_area_node.outputs["Area"], attribute_statistic_node.inputs["Attribute"]
    )
    geo_nodes_tree.links.new(
        input_node.outputs["Geometry"], attribute_statistic_node.inputs["Geometry"]
    )
    geo_nodes_tree.links.new(
        attribute_statistic_node.outputs["Sum"], division_node.inputs[1]
    )
    geo_nodes_tree.links.new(
        constant_value_node.outputs["Value"], division_node.inputs[0]
    )
    geo_nodes_tree.links.new(
        division_node.outputs["Value"], distribute_points_node.inputs["Density"]
    )
    geo_nodes_tree.links.new(
        distribute_points_node.outputs["Points"],
        points_to_vertices_node.inputs["Points"],
    )

    # Position the nodes
    input_node.location = (-800, 0)
    output_node.location = (400, 0)

    face_area_node.location = (-800, 100)
    attribute_statistic_node.location = (-600, 300)
    constant_value_node.location = (-400, 300)
    division_node.location = (-200, 300)
    distribute_points_node.location = (0, 0)
    points_to_vertices_node.location = (200, 0)

    # Update the geometry nodes modifier
    obj.modifiers.update()


def render_camera(scene, camera, frame, mode=RenderMode.TRAIN):
    camera_props = bpy.context.scene.CameraRenderProps

    # Set paths for saving
    if mode == RenderMode.TRAIN:
        camera_props.current_render_mode = RenderMode.TRAIN.value
        image_output_path = os.path.join(camera_props.save_path, "train")
        masks_output_path = os.path.join(camera_props.save_path, "masks_train")
        depths_output_path = os.path.join(camera_props.save_path, "depth_train")
    elif mode == RenderMode.TEST:
        camera_props.current_render_mode = RenderMode.TEST.value
        image_output_path = os.path.join(camera_props.save_path, "test")
        masks_output_path = os.path.join(camera_props.save_path, "masks_test")
        depths_output_path = os.path.join(camera_props.save_path, "depth_test")

    # Set rendering properties
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.device = "GPU"
    bpy.context.scene.cycles.samples = camera_props.render_samples

    # Enable object index pass
    bpy.context.view_layer.use_pass_object_index = True

    # Enable depth pass
    bpy.context.view_layer.use_pass_z = True

    # Set up compositor nodes for rendering image and object index pass
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()

    # Create render layers node
    render_layers = tree.nodes.new(type="CompositorNodeRLayers")

    # Create file output node for image
    file_output_image = tree.nodes.new(type="CompositorNodeOutputFile")
    file_output_image.label = "Image Output"
    file_output_image.base_path = image_output_path
    file_output_image.file_slots[0].path = ""
    tree.links.new(render_layers.outputs["Image"], file_output_image.inputs[0])

    # Create file output node for object index pass
    # Create math node to divide index pass by 200
    math_node = tree.nodes.new(type="CompositorNodeMath")
    math_node.operation = "DIVIDE"
    math_node.inputs[1].default_value = 65536  # 2^16
    tree.links.new(render_layers.outputs["IndexOB"], math_node.inputs[0])
    file_output_index = tree.nodes.new(type="CompositorNodeOutputFile")
    file_output_index.label = "Index Output"
    file_output_index.base_path = masks_output_path
    file_output_index.file_slots[0].path = ""
    file_output_index.format.file_format = "PNG"
    file_output_index.format.color_mode = "BW"
    file_output_index.format.color_depth = "16"
    file_output_index.format.compression = 100
    tree.links.new(math_node.outputs["Value"], file_output_index.inputs[0])

    # Create depth mask image
    file_output_depth = tree.nodes.new(type="CompositorNodeOutputFile")
    file_output_depth.label = "Depth Output"
    file_output_depth.base_path = depths_output_path
    file_output_depth.file_slots[0].path = ""
    file_output_depth.format.file_format = "OPEN_EXR"
    file_output_depth.format.color_depth = "32"
    tree.links.new(render_layers.outputs["Depth"], file_output_depth.inputs[0])

    # Set ranges of frames
    scene.frame_start = 1
    scene.frame_end = (
        camera_props.train_frames_total
        if camera_props.current_render_mode == RenderMode.TRAIN.value
        else camera_props.test_frames_total
    )
    if mode == RenderMode.TRAIN:
        scene.render.filepath = os.path.join(image_output_path, "")
    elif mode == RenderMode.TEST:
        scene.render.filepath = os.path.join(image_output_path, "")

    # Set active camera
    bpy.context.scene.camera = bpy.context.scene.objects.get(CAMERA_NAME)

    # Render single frame
    bpy.context.scene.frame_set(frame)
    camera_props.render_in_progress = True  # Don't run lsys.draw() during rendering
    try:
        bpy.ops.render.render(animation=False, write_still=True)
    finally:
        camera_props.render_in_progress = False

    # Set camera to original in post_render function


def create_masked_images(image_dir, mask_dir, output_dir):
    """Create images where the background is masked out using the mask images.

    Args:
        image_dir (_type_): original images directory
        mask_dir (_type_): mask images directory (background is zero)
        output_dir (_type_): output directory for masked images
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get list of image and mask files
    image_files = [f for f in os.listdir(image_dir) if f.endswith(".png")]

    for image_file in image_files:
        # Read the image and corresponding mask
        image_path = os.path.join(image_dir, image_file)
        mask_path = os.path.join(
            mask_dir, image_file
        )  # Assuming mask has the same name as image

        try:
            image = np.array(Image.open(image_path))
            mask_image = np.array(Image.open(mask_path))
        except Exception as e:
            print(f"Could not read image or mask for {image_file}: {e}")
            continue

        # Create a mask from the mask image
        mask = (mask_image > 0).astype(np.uint8)

        # Apply the mask to the image
        masked_image = (
            image * mask[:, :, None]
        )  # Broadcasting mask to match image dimensions

        # Save the masked image
        output_path = os.path.join(output_dir, image_file)
        Image.fromarray(masked_image).save(output_path)

        print(f"Saved masked image to {output_path}")


def sample_camera_placement(scene, mode: RenderMode):
    """Get the camera placement for the current frame. The camera placement is defined by the selected sampling strategy"""
    camera_props = bpy.context.scene.CameraRenderProps
    if mode == RenderMode.TEST:
        samples = globals.camera_placements[camera_props.camera_placement_test](
            RenderMode.TEST
        )
    elif mode == RenderMode.TRAIN:
        samples = globals.camera_placements[camera_props.camera_placement_train](
            RenderMode.TRAIN
        )
    current_sample = samples[scene.frame_current - 1]
    return current_sample


# Update rendering camera for each frame depending on the current rendering mode (train/test)
@persistent
def rendering_camera_update(scene):
    camera_props = bpy.context.scene.CameraRenderProps
    if camera_props.current_render_mode == RenderMode.TEST.value:
        frames_total = camera_props.test_frames_total
        mode = RenderMode.TEST

        if (
            not camera_props.dummy_render
            and camera_props.time_lapse
            and not camera_props.render_in_progress
        ):
            growth_total = scene.PlantProps.derivation_length
            angle = (np.pi / 4.0) + (
                (np.pi / 2.0) * scene.frame_current / frames_total
            )  # Go from pi/2 to 3pi/2
            x = -np.cos(angle)
            z = np.sin(angle)
            scene.world.node_tree.nodes["Sky_normal"].outputs[0].default_value = (
                -x,
                0,
                z,
            )

            scene.PlantProps.iteration_step = int(
                float(growth_total) * scene.frame_current / frames_total
            )
            bpy.ops.lsys.draw()

    elif camera_props.current_render_mode == RenderMode.TRAIN.value:
        frames_total = camera_props.train_frames_total
        mode = RenderMode.TRAIN
    if (
        CAMERA_NAME in scene.objects.keys()
        and scene.frame_current <= frames_total
        and scene.frame_current > 0
    ):
        location, rotation = sample_camera_placement(scene, mode)
        scene.objects[CAMERA_NAME].location = location
        scene.objects[CAMERA_NAME].rotation_mode = "QUATERNION"
        scene.objects[CAMERA_NAME].rotation_quaternion = rotation


@persistent
def post_render(scene):
    # Set camera back to original camera
    camera_props = bpy.context.scene.CameraRenderProps
    scene.camera = bpy.data.objects[camera_props.original_camera]
