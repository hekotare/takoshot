import globals as g


def draw_stage(stage):
    g.graphics.blit(stage.surf, (0, 0))

def draw_player(player):
    x = player.x - player.surf.get_width() * 0.5
    y = player.y - player.surf.get_height() * 0.5
    g.graphics.blit(player.surf, (x, y))