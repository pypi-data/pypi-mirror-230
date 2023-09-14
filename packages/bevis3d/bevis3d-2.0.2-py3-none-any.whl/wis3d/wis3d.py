# coding=utf-8
import os
import json
import base64
import trimesh
import numpy as np
from PIL import Image
from io import BytesIO
from typing import overload, Iterable, Dict, Union, Any
from scipy.spatial.transform import Rotation
from shutil import copyfile
import torch
import cv2
from transforms3d import affines, euler
from copy import deepcopy

file_exts = dict(
    point_cloud="ply",
    mesh="ply",
    boxes="json",
    image="png",
    lines="json",
    binVoxel="binvox",
    voxVoxel="vox",
    boxVoxel="json",
    spheres="json",
    camera_trajectory="json",
    correspondences="json",
    planes="json",
    polargrid="json",
)

folder_names = dict(
    point_cloud="point_clouds",
    mesh="meshes",
    boxes="boxes",
    image="images",
    lines="lines",
    binVoxel="voxels",
    voxVoxel="voxels",
    boxVoxel="voxels",
    spheres="spheres",
    camera_trajectory="camera_trajectories",
    correspondences="correspondences",
    planes="planes",
    polargrid="polargrid",
)


def img2url(image: Image.Image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_data = base64.b64encode(buffered.getvalue())
    if not isinstance(img_data, str):
        img_data = img_data.decode()
    return "data:image/png;base64," + img_data


def tensor2ndarray(tensor: Union[np.ndarray, torch.Tensor]) -> np.ndarray:
    if isinstance(tensor, torch.Tensor):
        if tensor.device.type != "cpu":
            tensor = tensor.detach().cpu()
        tensor = tensor.numpy()
    return tensor


class Wis3D:
    def __init__(
        self, out_folder: str, sequence_name: str, xyz_pattern=("x", "y", "z")
    ):
        """
        Initialize Wis3D

        :param out_folder: the folder to store the output files

        :param sequence_name: a subfolder of `out_folder` holding files of the sequence

        :param xyz_pattern: mapping of the three.js coordinate to the target coordinate. Take KITTI coordinate as an example:
        ::

                   three.js:                               KITTI:

            (up: y, right: x, backward:z)         (down: y, right: x, forward:z)
                    y                                     z
                    |                                    /
                    o -- x             -->              o -- x
                   /                                    |
                  z                                     y

                three.js:      x     y     z
                               |     |     |
               xyz_pattern = ['x', '-y', '-z']
                               |     |     |
                  KITTI:       x    -y    -z

        """
        self.scene_id = 0
        self.out_folder = out_folder
        self.sequence_name = sequence_name
        self.three_to_world = self.__get_world_transform(xyz_pattern)
        self.counters = {}
        for key in folder_names:
            self.counters[key] = 0

    def __get_world_transform(self, xyz_pattern=("x", "y", "z")) -> np.ndarray:
        rots = {
            "x": [1, 0, 0],
            "-x": [-1, 0, 0],
            "y": [0, 1, 0],
            "-y": [0, -1, 0],
            "z": [0, 0, 1],
            "-z": [0, 0, -1],
        }
        R = np.array([rots[axis] for axis in xyz_pattern], dtype=np.float32)
        T = np.eye(4)
        T[:3, :3] = R
        return T

    def __get_export_file_name(self, file_type: str, name: str = None) -> str:
        export_dir = os.path.join(
            self.out_folder,
            self.sequence_name,
            "%05d" % self.scene_id,
            folder_names[file_type],
        )
        os.makedirs(export_dir, exist_ok=True)
        if name is None:
            name = "%05d" % self.counters[file_type]

        filename = os.path.join(export_dir, name + "." + file_exts[file_type])
        self.counters[file_type] += 1

        return filename

    def set_scene_id(self, scene_id: int) -> None:
        """
        Set scene ID.

        Use it to create the new scene and add content to different scenes

        :param scene_id: scene ID to be set
        """
        self.scene_id = scene_id

    @overload
    def add_point_cloud(self, path: str, *, name: str = None) -> None:
        """
        Add a point cloud by file path.

        Support importing point clouds from STL, OBJ, PLY, etc.

        :param path: path to the point cloud file

        :param name: output name of the point cloud
        """
        pass

    @overload
    def add_point_cloud(
        self,
        vertices: Union[np.ndarray, torch.Tensor],
        colors: Union[np.ndarray, torch.Tensor] = None,
        *,
        name: str = None
    ) -> None:
        """
        Add a point cloud by point cloud definition.

        :param vertices: points constituting the point cloud, shape: `(n, 3)`

        :param colors: colors of the points, shape: `(n, 3)`

        :param name: output name of the poitn cloud
        """
        pass

    @overload
    def add_point_cloud(self, pcd: trimesh.PointCloud, name: str = None) -> None:
        """
        Add a point cloud loaded by `trimesh`.

        :param pcd: point cloud loaded by `trimesh`

        :param name: output name of the poitn cloud
        """
        pass

    def add_point_cloud(self, vertices, colors=None, *, name=None) -> None:
        if isinstance(vertices, str):
            pcd = trimesh.load_mesh(vertices)
        elif isinstance(vertices, trimesh.PointCloud):
            pcd = vertices
        elif isinstance(vertices, (np.ndarray, torch.Tensor)):
            vertices = tensor2ndarray(vertices)
            colors = tensor2ndarray(colors)
            pcd = trimesh.PointCloud(vertices, colors)
        else:
            raise NotImplementedError()

        pcd.apply_transform(self.three_to_world)
        filename = self.__get_export_file_name("point_cloud", name)
        pcd.export(filename)

    @overload
    def add_mesh(self, path: str, *, name: str = None) -> None:
        """
        Add a mesh by file path.

        Support importing meshes from STL, OBJ, PLY, etc.

        :param path: path to the mesh file

        :param name: output name of the mesh
        """
        pass

    @overload
    def add_mesh(
        self,
        vertices: Union[np.ndarray, torch.Tensor],
        faces: Union[np.ndarray, torch.Tensor],
        vertex_colors: Union[np.ndarray, torch.Tensor],
        *,
        name: str = None
    ) -> None:
        """
        Add a mesh loaded by mesh definition

        :param vertices: vertices of the mesh, shape: `(n, 3)`

        :param faces: faces of the mesh, shape: `(m, 3)`

        :param vertex_colors: vertex colors of the mesh, shape: `(n, 3)`

        :param name: output name of the mesh
        """
        pass

    @overload
    def add_mesh(self, mesh: trimesh.Trimesh, *, name: str = None) -> None:
        """
        Add a mesh loaded by `trimesh`

        :param mesh: mesh loaded by `trimesh`

        :param name: output name of the mesh
        """
        pass

    def add_mesh(self, vertices, faces=None, vertex_colors=None, *, name=None):
        if isinstance(vertices, str):
            mesh = trimesh.load_mesh(vertices)
        elif isinstance(vertices, trimesh.Trimesh):
            mesh = vertices.copy()
        elif isinstance(vertices, (np.ndarray, torch.Tensor)):
            vertices = tensor2ndarray(vertices)
            faces = tensor2ndarray(faces)
            vertex_colors = tensor2ndarray(vertex_colors)
            mesh = trimesh.Trimesh(vertices, faces, vertex_colors=vertex_colors)
        else:
            raise NotImplementedError()

        mesh.apply_transform(self.three_to_world)
        filename = self.__get_export_file_name("mesh", name)
        mesh.export(filename)

    @overload
    def add_image(self, path: str, *, name: str = None) -> None:
        """
        Add an image by file path

        :param path: path to the image file

        :param name: output name of the image
        """
        pass

    @overload
    def add_image(
        self, data: Union[np.ndarray, torch.Tensor], *, name: str = None
    ) -> None:
        """
        Add an image by image definition

        :param data: data of the image

        :param name: output name of the image
        """
        pass

    @overload
    def add_image(self, image: Image.Image, *, name: str = None) -> None:
        """
        Add an image by `PIL.Image.Image`

        :param image: image loaded by `PIL.Image.Image`

        :param name: output name of the image
        """
        pass

    def add_image(self, image, *, name: str = None, scale: int = 1):
        if isinstance(image, str):
            img = Image.open(image)
            img = img.resize((img.size[0]//scale, img.size[1]//scale))
        elif isinstance(image, (np.ndarray, torch.Tensor)):
            image = tensor2ndarray(image)
            img = Image.fromarray(image)
        elif isinstance(image, Image.Image):
            img = image
        else:
            raise NotImplementedError()

        filename = self.__get_export_file_name("image", name)
        img.save(filename)

    @overload
    def add_boxes(
        self,
        corners: Union[np.ndarray, torch.Tensor],
        *,
        order: Iterable[int] = (0, 1, 2, 3, 4, 5, 6, 7),
        labels: Iterable[str] = None,
        name: str = None
    ) -> None:
        """
        Add boxes by corners

        :param corners: eight corners of the boxese, shape: `(n, 8, 3)` or `(8, 3)`

        :param order: order of the corners, the default indices are defined as

        ::

                 4 --- 5        y
                /|   / |        ｜
              7 --- 6  |        ｜
              |  0--|- 1        o —— —— x
              | /   | /        /
              3 --- 2         z

        :param labels: label for each box

        :param name: output name for these boxes
        """
        pass

    @overload
    def add_boxes(
        self,
        positions: Union[np.ndarray, torch.Tensor],
        eulers: Union[np.ndarray, torch.Tensor],
        extents: Union[np.ndarray, torch.Tensor],
        *,
        labels: Iterable[str] = None,
        name: str = None
    ) -> None:
        """
        Add boxes by definition

        :param positions: position for each box, shape: `(n, 3)` or `(3,)`

        :param eulers: euler angles, shape: `(n, 3)` or `(3,)`

        :param extents: extents of the boxes, shape: `(n, 3)` or `(3,)`

        :param labels: label for each box, shape: `(n,)` or `str`

        :param name: output name for these boxes
        """
        pass

    def add_boxes(
        self,
        positions,
        eulers=None,
        extents=None,
        *,
        order=(0, 1, 2, 3, 4, 5, 6, 7),
        labels=None,
        name=None,
        colors=None
    ):
        positions = tensor2ndarray(positions)

        if eulers is None or extents is None:
            positions = np.asarray(positions).reshape(-1, 8, 3)
            corners = deepcopy(positions)
            if order != (0, 1, 2, 3, 4, 5, 6, 7):
                for i, o in enumerate(order):
                    corners[:, o, :] = positions[:, i, :]
            positions = (corners[:, 0, :] + corners[:, 6, :]) / 2
            vector_xs = corners[:, 1, :] - corners[:, 0, :]
            vector_ys = corners[:, 4, :] - corners[:, 0, :]
            vector_zs = corners[:, 3, :] - corners[:, 0, :]

            extent_xs = np.linalg.norm(vector_xs, axis=1).reshape(-1, 1)
            extent_ys = np.linalg.norm(vector_ys, axis=1).reshape(-1, 1)
            extent_zs = np.linalg.norm(vector_zs, axis=1).reshape(-1, 1)
            extents = np.hstack((extent_xs, extent_ys, extent_zs))

            rot_mats = np.stack(
                (vector_xs / extent_xs, vector_ys / extent_ys, vector_zs / extent_zs),
                axis=2,
            )
            Rs = Rotation.from_matrix(rot_mats)
            eulers = Rs.as_euler("XYZ")
        else:
            positions = tensor2ndarray(positions)
            eulers = tensor2ndarray(eulers)
            extents = tensor2ndarray(extents)
            positions = np.asarray(positions).reshape(-1, 3)
            extents = np.asarray(extents).reshape(-1, 3)
            eulers = np.asarray(eulers).reshape(-1, 3)

        boxes = dict()
        for i in range(len(positions)):
            box_def = self.three_to_world @ affines.compose(
                positions[i], euler.euler2mat(*eulers[i]), extents[i]
            )
            T, R, Z, _ = affines.decompose(box_def)
            box = dict(position=T.tolist(), euler=euler.mat2euler(R), extent=Z.tolist())
            if labels is not None:
                if isinstance(labels, str):
                    labels = [labels]
                box.update({"label": labels[i]})
            if colors is not None:
                if isinstance(colors, str):
                    colors = [colors]
                box.update({"color": colors[i]})

            # boxes.append(box)
            if labels[i] in boxes:
                boxes[labels[i]].append(box)
            else:
                boxes[labels[i]] = [box]
        for k,v in boxes.items():
            filename = self.__get_export_file_name("boxes", k)
            with open(filename, "a") as f:
                f.write(json.dumps(v))

        """
        add lidar distance circle 
        radius: 每个圆圈半径为10m的倍数，最大的圆半径为100m
        radials: Radials 或 radial lines 是指一种图形或图像的显示方式，其中线条从中心点向外辐射，类似于圆形或星形图案。默认16根线
        circles：圆圈的个数，默认为10。此时radius为100m，表示每个圆圈之间间隔10m
        division：每个圈默认的分段数，默认100，表示圈是个100边形，约等于一个圆
        """
        # TODO: 所有参数都是可以在Web界面自行调整的，但是无法在这里通过修改超参数进行调整，需要修改前端代码
        filename = self.__get_export_file_name("polargrid", "polargrid")
        with open(filename, "w") as f:
            f.write(json.dumps([{"radius": 100, "radials":16, "circles":10, "divisions":100}]))

            # filename = self.__get_export_file_name("boxes", labels[i])
            # with open(filename, "a") as f:
            #     f.write(json.dumps(boxes))
            #     f.write('\n')
            
            

        # filename = self.__get_export_file_name("boxes", name)
        # with open(filename, "w") as f:
        #     f.write(json.dumps(boxes))

    def add_lines(
        self,
        start_points: Union[np.ndarray, torch.Tensor],
        end_points: Union[np.ndarray, torch.Tensor],
        colors: Union[np.ndarray, torch.Tensor] = None,
        *,
        name: str = None
    ) -> None:
        """
        Add lines by points

        :param start_points: start point of each line, shape: `(n, 3)` or `(3,)`

        :param end_points: end point of each line, shape: `(n, 3)` or `(3,)`

        :param colors: colors of the lines, shape: `(n, 3)`

        :param name: output name for these lines
        """
        start_points = tensor2ndarray(start_points)
        end_points = tensor2ndarray(end_points)
        colors = tensor2ndarray(colors)

        if len(start_points) != len(end_points):
            raise NotImplementedError()

        start_points = np.asarray(start_points).reshape(-1, 3)
        end_points = np.asarray(end_points).reshape(-1, 3)

        n = start_points.shape[0]
        start_points = (
            self.three_to_world @ np.hstack((start_points, np.zeros((n, 1)))).T
        )
        end_points = self.three_to_world @ np.hstack((end_points, np.zeros((n, 1)))).T

        start_points = start_points[:3, :].T
        end_points = end_points[:3, :].T

        if colors is not None:
            if len(colors) != len(start_points):
                raise NotImplementedError()
            colors = np.asarray(colors).reshape(-1, 3)

        lines = []
        for i in range(len(start_points)):
            line = dict(
                start_point=start_points[i].tolist(), end_point=end_points[i].tolist()
            )
            if colors is not None:
                line.update({"color": colors[i].tolist()})

            lines.append(line)

        filename = self.__get_export_file_name("lines", name)
        with open(filename, "w") as f:
            f.write(json.dumps(lines))

    @overload
    def add_voxel(self, path: str, *, name: str = None) -> None:
        """
        Add voxels by binvox/vox file

        @param path: path to the BINVOX or VOX file

        @param name: output name for these lines
        """
        pass

    @overload
    def add_voxel(
        self,
        voxel_centers: Union[np.ndarray, torch.Tensor],
        voxel_size: float,
        colors: Union[np.ndarray, torch.Tensor] = None,
        *,
        name: str = None
    ) -> None:
        """
        Add voxels by boxes

        :param voxel_centers: center for each box, shape: `(n, 3)` or `(3,)`

        :param voxel_size: size of all boxes

        :param colors: colors of each box, shape: `(n, 3)`

        :param name: output name for the voxel
        """
        pass

    def add_voxel(self, voxel_centers, voxel_size=None, colors=None, *, name=None):
        if isinstance(voxel_centers, str):
            file_type = voxel_centers.split(".")[-1]
            if file_type == "binvox":
                filename = self.__get_export_file_name("binVoxel", name)
            elif file_type == "vox":
                filename = self.__get_export_file_name("voxVoxel", name)
            else:
                raise NotImplementedError()

            copyfile(voxel_centers, filename)
        else:
            if voxel_size is None:
                raise NotImplementedError()
            voxel_centers = tensor2ndarray(voxel_centers)
            colors = tensor2ndarray(colors)
            voxel_size = float(voxel_size)
            voxel_centers = np.asarray(voxel_centers).reshape(-1, 3)

            n = voxel_centers.shape[0]
            voxel_centers = (
                self.three_to_world @ np.hstack((voxel_centers, np.zeros((n, 1)))).T
            )
            voxel_centers = voxel_centers[:3, :].T

            if colors is not None:
                colors = np.asarray(colors).reshape(-1, 3)
                if len(colors) != len(voxel_centers):
                    raise NotImplementedError()

            data = []
            data.append(dict(voxel_size=voxel_size))
            boxes = []
            for i in range(len(voxel_centers)):
                box = dict(voxel_center=voxel_centers[i].tolist())
                if colors is not None:
                    box.update({"color": colors[i].tolist()})
                boxes.append(box)
            data.append(dict(voxels=boxes))

            filename = self.__get_export_file_name("boxVoxel", name)
            with open(filename, "w") as f:
                f.write(json.dumps(data))

    def add_spheres(
        self,
        centers: Union[np.ndarray, torch.Tensor],
        radius: Union[float, np.ndarray, torch.Tensor],
        colors=None,
        *,
        name=None
    ) -> None:
        """
        Add spheres

        :param centers: center of each sphere, shape: `(n, 3)` or `(3,)`

        :param radius: radius of each sphere, either float or shape of `(n,)` or `(1,)`

        :param colors: colors of each box, shape: `(n, 3)`

        :param name: output name for the spheres
        """
        centers = tensor2ndarray(centers)
        centers = np.asarray(centers).reshape(-1, 3)
        n = centers.shape[0]
        centers = self.three_to_world @ np.hstack((centers, np.zeros((n, 1)))).T
        centers = centers[:3, :].T

        if colors is not None:
            colors = tensor2ndarray(colors)
            colors = np.asarray(colors).reshape(-1, 3)
            if len(colors) != len(centers):
                raise NotImplementedError()

        spheres = []
        if isinstance(radius, float):
            for i in range(len(centers)):
                sphere = dict(center=centers[i].tolist(), radius=radius)
                if colors is not None:
                    sphere.update({"color": colors[i].tolist()})
                spheres.append(sphere)
        else:
            radius = tensor2ndarray(radius)
            radius = np.asarray(radius).reshape(-1, 1)
            if len(radius) != len(centers):
                raise NotImplementedError()
            for i in range(len(centers)):
                sphere = dict(center=centers[i].tolist(), radius=radius[i].tolist())
                if colors is not None:
                    sphere.update({"color": colors[i].tolist()})
                spheres.append(sphere)

        filename = self.__get_export_file_name("spheres", name)
        with open(filename, "w") as f:
            f.write(json.dumps(spheres))

    def add_camera_trajectory(
        self, poses: Union[np.ndarray, torch.Tensor], *, name: str = None
    ) -> None:
        """
        Add a camera trajectory

        :param poses: transformation matrices of shape `(n, 4, 4)`

        :param name: output name of the camera trajectory
        """
        poses = tensor2ndarray(poses)

        poses = (self.three_to_world @ poses.T).T
        # r = Rotation.from_matrix(poses[:, :3, : 3])
        # eulers = r.as_euler('xyz')
        quats = []
        positions = poses[:, :3, 3].reshape((-1, 3))
        for pose in poses:
            trans_quat = euler.mat2euler(pose[:3, :3])
            quats.append(trans_quat)

        filename = self.__get_export_file_name("camera_trajectory", name)
        with open(filename, "w") as f:
            f.write(json.dumps(dict(eulers=quats, positions=positions.tolist())))

    def add_keypoint_correspondences(
        self,
        img0: Union[Image.Image, np.ndarray, torch.Tensor, str],
        img1: Union[Image.Image, np.ndarray, torch.Tensor, str],
        kpts0: Union[np.ndarray, torch.Tensor],
        kpts1: Union[np.ndarray, torch.Tensor],
        *,
        unmatched_kpts0: Union[np.ndarray, torch.Tensor] = None,
        unmatched_kpts1: Union[np.ndarray, torch.Tensor] = None,
        metrics: Dict[str, Iterable[int]] = None,
        booleans: Dict[str, Iterable[bool]] = None,
        meta: Dict[str, Any] = None,
        name: str = None
    ) -> None:
        """
        Add keypoint correspondences

        :param img0: path to the image or a `PIL.Image.Image` instance or a `numpy.ndarray`

        :param img1: path to the image or a `PIL.Image.Image` instance or a `numpy.ndarray`

        :param kpts0: keypoints of shape `(n, 2)`

        :param kpts1: keypoints of shape `(n, 2)`

        :param unmatched_kpts0: unmatched keypoints of shape `(m, 2)`

        :param unmatched_kpts1: unmatched keypoints of shape `(l, 2)`

        :param metrics: a dictionary of metrics, each with the shape of `(n, )`

        :param booleans: a dictionary of booleans, each with the shape of `(n, )`

        :param meta: a dictionary of meta information of correspondences

        :param name: outputname of the file
        """

        if isinstance(img0, str):
            image0 = Image.open(img0)
        elif isinstance(img0, np.ndarray):
            image0 = Image.fromarray(img0)
        elif isinstance(img0, torch.Tensor):
            image0 = Image.fromarray(tensor2ndarray(img0))
        elif isinstance(img0, Image.Image):
            image0 = img0

        if isinstance(img1, str):
            image1 = Image.open(img1)
        elif isinstance(img1, np.ndarray):
            image1 = Image.fromarray(img1)
        elif isinstance(img1, torch.Tensor):
            image1 = Image.fromarray(tensor2ndarray(img1))
        elif isinstance(img1, Image.Image):
            image1 = img1

        data = {}
        data["img0"] = img2url(image0)
        data["img1"] = img2url(image1)
        kpts0 = tensor2ndarray(kpts0)
        data["kpts0"] = np.asarray(kpts0).tolist()
        kpts1 = tensor2ndarray(kpts1)
        data["kpts1"] = np.asarray(kpts1).tolist()

        if unmatched_kpts0 is not None:
            unmatched_kpts0 = tensor2ndarray(unmatched_kpts0)
            data["unmatched_kpts0"] = np.asarray(unmatched_kpts0).tolist()

        if unmatched_kpts1 is not None:
            unmatched_kpts1 = tensor2ndarray(unmatched_kpts1)
            data["unmatched_kpts1"] = np.asarray(unmatched_kpts1).tolist()

        if metrics is not None and len(dict.keys(metrics)) > 0:
            m = {}
            for k, v in metrics.items():
                m[k] = np.asarray(v).reshape(-1).tolist()
            data["metrics"] = m

        if booleans is not None and len(dict.keys(booleans)) > 0:
            b = {}
            for k, v in booleans.items():
                b[k] = np.asarray(v).reshape(-1).tolist()
            data["booleans"] = b

        if meta is not None:
            data["meta"] = meta

        filename = self.__get_export_file_name("correspondences", name)
        with open(filename, "w") as f:
            f.write(json.dumps(data))
