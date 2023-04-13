import globals as g

def draw_stage(stage_surf):
    g.graphics.blit(stage_surf, (0, 0))

def draw_player(player):
    g.graphics.blit(player.surf, (player.x, player.y))