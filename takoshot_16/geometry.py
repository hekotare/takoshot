import math

import numpy as np
import pygame
from numpy.linalg import inv


class Geometry:
    
    def rotate(x, y, angle_radians):
    
        cos = math.cos(angle_radians)
        sin = math.sin(angle_radians)
        
        return (x * cos - y * sin, x * sin + y * cos)
    
    # ベクトル(0, -1)とベクトル(x, y)の角度を返す
    def vector_to_angle(x, y):
        return -pygame.math.Vector2(0, -1).angle_to(pygame.math.Vector2(x, y).normalize())

# 単位行列の作成
def identity():
    return np.array([[1, 0, 0],
                     [0, 1, 0],
                     [0, 0, 1]])

def scale(mat, scale_x, scale_y):
    return np.dot(scale_mat(scale_x, scale_y), mat)

# 拡大縮小行列の作成
def scale_mat(scale_x, scale_y):
    return np.array([[scale_x, 0, 0],
                     [0, scale_y, 0],
                     [0, 0, 1]])

def rotate(mat, rad):
    return np.dot(rotate_mat(rad), mat)

# 回転行列の作成
def rotate_mat(rad):
    return np.array([[np.cos(rad), -np.sin(rad), 0],
                    [np.sin(rad), np.cos(rad), 0],
                    [0, 0, 1]])

def transform(mat, x, y):
    return np.dot(transform_mat(x, y), mat)

# 移動行列の作成
def transform_mat(x, y):
    return np.array([[1, 0, x],
                     [0, 1, y],
                     [0, 0, 1]])

class Transform:

    @classmethod
    def create_view_point_list(cls, transform, screen_rect):
        return [transform.screen_to_world(screen_rect.left,  screen_rect.top),
                transform.screen_to_world(screen_rect.right, screen_rect.top),
                transform.screen_to_world(screen_rect.right, screen_rect.bottom),
                transform.screen_to_world(screen_rect.left,  screen_rect.bottom)]
    
    # ビュー領域がワールドの外へ出ていたら、
    # ビュー領域がワールド内に収まるためのズームと位置を計算する
    @classmethod
    def calc_viewarea_in_world(self, view_bbox, world_rect):
        
        rate_x = world_rect.width / view_bbox.width
        rate_y = world_rect.height / view_bbox.height
        rate_min = min(rate_x, rate_y)
        
        out_of_world = False
        scale = 1; ofs_x = 0; ofs_y = 0
        
        # ビュー領域がワールドの幅、高さを超えたら
        # まずは大きさをワールドにおさまるようにする
        if (rate_min < 1.0):
        
            out_of_world = True
            scale = rate_min
            
            # ズームを変更したのでビュー領域を変更する
            left, right, top, bottom = \
                (view_bbox.centerx - view_bbox.width * 0.5 * rate_min,
                 view_bbox.centerx + view_bbox.width * 0.5 * rate_min,
                 view_bbox.centery - view_bbox.height * 0.5 * rate_min,
                 view_bbox.centery + view_bbox.height * 0.5 * rate_min)
            
            # pygame.Rectだと整数値しか保持できないので、少数値を扱うためにBBoxクラスを作成
            # 整数値だとカメラがガクガクなるかも
            view_bbox = BBox(left, top, right, bottom)
        
        # ビュー領域が範囲外にいる場合、ワールド内に戻す
        if (view_bbox.left < world_rect.left):
            out_of_world = True
            ofs_x = world_rect.left - view_bbox.left
        if (world_rect.right < view_bbox.right):
            out_of_world = True
            ofs_x = -(view_bbox.right - world_rect.right)
        if (view_bbox.top < world_rect.top):
            out_of_world = True
            ofs_y = world_rect.top - view_bbox.top
        if (world_rect.bottom < view_bbox.bottom):
            out_of_world = True
            ofs_y = -(view_bbox.bottom - world_rect.bottom)
        
        return out_of_world, scale, ofs_x, ofs_y

    def __init__(self, screen_rect):
        self.screen_matrix = Matrix()
        self.screen_matrix.scale(screen_rect[2] * 0.5, screen_rect[3] * 0.5)
        self.screen_matrix.translate(screen_rect[0] + screen_rect[2] * 0.5, screen_rect[1] + screen_rect[3] * 0.5)
        
        self.projection_matrix = Matrix()
        self.projection_matrix.scale(2 / screen_rect[2], 2 / screen_rect[3])
        
        self.view_matrix = Matrix()
        self.view_rotate_rad = 0
        self.view_scale = 1
        
        self.screen_to_world_matrix = Matrix()
        self.world_to_screen_matrix = Matrix()
    
    def calc_transform_from_camera(self, x, y, rotate_rad, scale):

        # 計算誤差でガクガクするから数値を丸めてみる
        x = round(x)
        y = round(y)
        rotate_rad = round(rotate_rad, 4)
        scale = round(scale, 4)
        
        self.view_rotate_rad = rotate_rad
        self.view_scale = scale
        
        self.view_matrix.identity()
        self.view_matrix.translate(-x, -y)
        self.view_matrix.rotate(rotate_rad)
        self.view_matrix.scale(1/scale, 1/scale)
        
        self.world_to_screen_matrix.identity()
        self.world_to_screen_matrix.concat(self.view_matrix.ndarray)
        self.world_to_screen_matrix.concat(self.projection_matrix.ndarray)
        self.world_to_screen_matrix.concat(self.screen_matrix.ndarray)
        
        self.screen_to_world_matrix.identity()
        self.screen_to_world_matrix.concat(self.world_to_screen_matrix.ndarray)
        self.screen_to_world_matrix.invert()
    
    # スクリーン座標をワールド座標に変換する
    def screen_to_world(self, x, y):
        return self.screen_to_world_matrix.transform_point(x, y)
    
    # ワールド値をスクリーン値に変換
    def world_to_screen(self, x, y, rotate_deg, scale):
        return *self.world_to_screen_xy(x, y), self.world_to_screen_rotate_deg(rotate_deg), self.world_to_screen_scale(scale)
    
    # ワールド座標をスクリーン座標に変換する
    def world_to_screen_xy(self, x, y):
        return self.world_to_screen_matrix.transform_point(x, y)
    
    # ワールド座標系の回転値をスクリーン座標系の回転値に変換する
    def world_to_screen_rotate_deg(self, world_rotate_deg):
        return world_rotate_deg - math.degrees(self.view_rotate_rad)
    
    # ワールド座標系のスケールをスクリーン座標系のスケールに変換する
    def world_to_screen_scale(self, world_scale):
        return world_scale / self.view_scale

# 行列
class Matrix:

    def __init__(self):
        self.identity()
    
    def clone(self):
        mat = Matrix()
        mat.ndarray = self.ndarray.copy()
        
        return mat
    
    def identity(self):
        self.ndarray = identity()
    
    def rotate(self, rad):
        self.concat(rotate_mat(rad))
    
    def scale(self, scale_x, scale_y):
        self.concat(scale_mat(scale_x, scale_y))
    
    def translate(self, x, y):
        self.concat(transform_mat(x, y))
    
    def concat(self, mat):
        if not isinstance(mat, (Matrix, np.ndarray)):
            raise TypeError("")
        
        if isinstance(mat, Matrix):
            mat = mat.ndarray
        
        self.ndarray = np.dot(mat, self.ndarray)
    
    def invert(self):
        self.ndarray = inv(self.ndarray)
    
    # x, yに行列を適用する
    def transform_point(self, x, y):
        x, y, _ = np.dot(self.ndarray, (x, y, 1))
        
        return float(x), float(y)

# pygame.Rectは整数値しか持てないので、小数をもてるBBoxクラスを作成
class BBox:
    
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.width = right - left
        self.height = bottom - top
        self.centerx = (left + right) * 0.5
        self.centery = (top + bottom) * 0.5
    
    def to_rect(self):
        
        left = int(self.left)
        right = math.ceil(self.right)
        top = int(self.top)
        bottom = math.ceil(self.bottom)
        
        return pygame.Rect(left, top, right - left, bottom - top)

def create_bounding_box_by_points(points):
    
    x, y = points[0]
    left = right = x
    top = bottom = y
    
    for x, y in points[1:]:
        left = min(left, x)
        right = max(x, right)
        top = min(top, y)
        bottom = max(y, bottom)
    
    return BBox(left, top, right, bottom)
