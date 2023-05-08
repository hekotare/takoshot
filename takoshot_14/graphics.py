import math

import pygame
import pygame.gfxdraw

import globals as g
from geometry import Geometry

clamp_bytes = lambda v: max(0, min(v, 255))


def rotate(img, angle):
    return pygame.transform.rotate(img, angle)

def flip(img):
    return pygame.transform.flip(img, True, False)

def replace(img, replace_data_list):
    
    new_img = img.copy()
    
    ar = pygame.PixelArray(new_img)
    
    for replace_data in replace_data_list:
        ar.replace(replace_data[0], replace_data[1], 0)
    
    del ar

    return new_img

#--------------------------------------------------
# 描画機能
#--------------------------------------------------
def fill(surface, color):
    surface.fill(color)

def calc_arc_points(x, y, radius, from_degree, degree, split, out_list):
    
    for i in range(split + 1):
        deg = from_degree + degree * (i/split)
        rad = deg * math.pi / 180
        
        out_list.append((x + math.sin(rad) * radius, y - math.cos(rad) * radius))

# space_dot     リングを小さくする（ドット指定）
# space_degree  リングを小さくする（角度指定）
def calc_ring_points(x, y, outer_radius, inner_radius, from_degree, degree, split, out_list, **kwargs):
    
    outer_from_degree = inner_from_degree = from_degree
    outer_degree = inner_degree = degree

    # ドット分だけ隙間をあける
    space_dot = kwargs.get('space_dot')
    space_degree = kwargs.get('space_degree')

    if (space_dot):
        outer_from_degree, outer_degree, inner_from_degree, inner_degree = calc_degree_by_dot(outer_radius, inner_radius, from_degree, degree, space_dot)
    elif (space_degree): # 角度ぶんだけ隙間をあける
        outer_from_degree += space_degree * 0.5
        inner_from_degree += space_degree * 0.5
        outer_degree -= space_degree
        inner_degree -= space_degree
    
    calc_arc_points(x, y, outer_radius, outer_from_degree, outer_degree, split, out_list)
    list = []
    calc_arc_points(x, y, inner_radius, inner_from_degree, inner_degree, split, list)
    list.reverse()
    
    out_list.extend(list)

def calc_degree_by_dot(outer_radius, inner_radius, from_degree, degree, dot):

    # 内側の孤
    c0 = 2 * inner_radius * math.pi * (degree / 360) # 内側の孤の長さを計算する
    inner_degree = (c0 - dot) / (2 * inner_radius * math.pi) * 360 # 内側の孤の長さを指定したドット数分だけ小さくして、その角度を求める
    
    # 外側の孤
    c1 = 2 * outer_radius * math.pi * (degree / 360) # 外側の孤の長さを計算する
    outer_degree = (c1 - dot) / (2 * outer_radius * math.pi) * 360 # 外側の孤の長さを指定したドット数分だけ小さくして、その角度を求める

    # 小さくした孤の分だけ開始位置をずらす
    outer_from_degree = from_degree + (degree - outer_degree) * 0.5
    inner_from_degree = from_degree + (degree - inner_degree) * 0.5
    
    return outer_from_degree, outer_degree, inner_from_degree, inner_degree

def calc_pie_points(x, y, radius, from_degree, degree, split, out_list):
    out_list.append((x, y))
    calc_arc_points(x, y, radius, from_degree, degree, split, out_list)

# space_dot     リングを小さくする（ドット指定）
# space_degree  リングを小さくする（角度指定）
def ring(surface, x, y, outer_radius, inner_radius, start_degree, end_degree, split, **kwargs):
    point_list = []
    
    calc_ring_points(x, y, outer_radius, inner_radius, start_degree, end_degree - start_degree, split, point_list, **kwargs)
    polygon(surface, point_list, **kwargs)

# split　分割数（数値が多いほど綺麗な線になる）
def pie(surface, x, y, radius, start_degree, end_degree, split, **kwargs):
    point_list = []
    calc_pie_points(x, y, radius, start_degree, end_degree - start_degree, split, point_list)
    polygon(surface, point_list, **kwargs)

def rectangle(surface, rect, **kwargs):

    fill = kwargs.get('fill')
    if (fill): pygame.draw.rect(surface, fill, rect)
    
    outline = kwargs.get('outline')
    if (outline):
        width = kwargs.get('width') or 1
        pygame.draw.rect(surface, outline, rect, width=width)

def circle(surface, pos, radius, **kwargs):

    fill = kwargs.get('fill')
    if (fill): pygame.draw.circle(surface, fill, pos, radius)
    
    outline = kwargs.get('outline')
    if (outline):
        width = kwargs.get('width') or 1
        pygame.draw.circle(surface, outline, pos, radius, width=width)

def polygon(surface, points, **kwargs):

    fill = kwargs.get('fill')
    if (fill): pygame.draw.polygon(surface, fill, points)
    
    outline = kwargs.get('outline')
    if (outline):
        width = kwargs.get('width') or 1
        pygame.draw.polygon(surface, outline, points, width=width)

def line(surface, color, start_pos, end_pos, width=1):
    return pygame.draw.line(surface, color, start_pos, end_pos, width)

def text(surface, pos, str, color, **kwargs):

    font = kwargs.get('font') or g.default_font
    background = kwargs.get('background')
    
    txt = font.render(str, True, color, background)

    w, h = font.size(str)
    x, y = pos[0], pos[1] # デフォルトではleft

    # 横方向
    align = kwargs.get('textalign')
    
    if (align == 'center'):
        x = x - w * 0.5
    elif (align == 'right'):
        x = x - w
    
    # 縦方向
    align = kwargs.get('valign')

    if (align == 'middle'):
        y = y - h * 0.5
    elif (align == 'bottom'):
        y = y - h
    
    # 影をつける
    shadow_color = kwargs.get('shadow_color')
    
    if (shadow_color is not None):
        shadow_kwargs = kwargs.copy()
        del shadow_kwargs['shadow_color']
        text(surface, (pos[0] + 2, pos[1] + 2), str, shadow_color, **shadow_kwargs)
    
    surface.blit(txt, (x, y))

def blit(surface, img, pos_or_rect, **kwargs):

    alpha = kwargs.get('alpha')
    
    # 透過処理 こんなやり方ありかな？
    if (alpha != None):
        restore_alpha = img.get_alpha()
        img.set_alpha(alpha)
    
    area = kwargs.get('area')
    special_flags = kwargs.get('special_flags') or 0
    
    surface.blit(img, pos_or_rect, area, special_flags = special_flags)
    
    # 元に戻しておく
    if (alpha != None):
        img.set_alpha(restore_alpha)

def rotate_blit(surface, surf, dist_pos, origin_pos, angle_degree, **kwargs):
    # オフセット値の計算
    rad = -math.radians(angle_degree) # pygame.transfate.rotateとGeometry.rotateの回転方向が逆なので、マイナス
    x0, y0 = surf.get_width() * 0.5, surf.get_height() * 0.5  # 画像の真ん中
    x1, y1 = origin_pos # 任意の中心点
    ofs_x, ofs_y = Geometry.rotate(x1-x0, y1-y0, rad)
    
    # 画像を回転
    rotated_surf = pygame.transform.rotate(surf, angle_degree)
    
    # 描画
    blit(surface, rotated_surf, (dist_pos[0] - rotated_surf.get_width() * 0.5 - ofs_x, dist_pos[1] - rotated_surf.get_height() * 0.5 - ofs_y), **kwargs)

class Graphics:

    def __init__(self, surface):
        self.target = surface
    
    def fill(self, color):
        self.target.fill(color)
    
    def ring(self, x, y, outer_radius, inner_radius, start_degree, end_degree, split, **kwargs):
        ring(self.target, x, y, outer_radius, inner_radius, start_degree, end_degree, split, **kwargs)

    # split　分割数（数値が多いほど綺麗な線になる）
    def pie(self, x, y, radius, start, end, split, **kwargs):
        pie(self.target, x, y, radius, start, end, split, **kwargs)

    def rectangle(self, rect, **kwargs):
        rectangle(self.target, rect, **kwargs)
    
    def circle(self, pos, radius, **kwargs):
        circle(self.target, pos, radius, **kwargs)
    
    def polygon(self, points, **kwargs):
        polygon(self.target, points, **kwargs)
    
    def line(self, color, start_pos, end_pos, width=1):
        line(self.target, color, start_pos, end_pos, width)
    
    def text(self, pos, str, color, **kwargs):
        text(self.target, pos, str, color, **kwargs)
    
    def blit(self, img, pos_or_rect, **kwargs):
        blit(self.target, img, pos_or_rect, **kwargs)
    
    def rotate_blit(self, surf, pos_or_rect, origin_pos, angle_degree, **kwargs):
        rotate_blit(self.target, surf, pos_or_rect, origin_pos, angle_degree, **kwargs)