import globals as g


def draw_stage(stage):
    g.graphics.blit(stage.surf, (0, 0))

def draw_player(player):

    surf = player.surf

    if (player.dir.is_left()):
        import graphics as gra
        surf = gra.flip(surf)

    g.graphics.rotate_blit(surf, (player.x, player.y),
        (surf.get_width() * 0.5, surf.get_height() * 0.75), player.posture_to_rotate_degree())

    # debug posture
    if (g.DebugFlags.DISPLAY_PLAYER_POSTURE):
        g.graphics.text((player.x, player.y + 30), f"posture_deg={int(player.posture_degree)}", (255, 255, 255), background=(0, 0, 0), font=g.font_16)
        g.graphics.text((player.x, player.y + 50), f"rotate_deg={int(player.posture_to_rotate_degree())}", (255, 255, 255), background=(0, 0, 0), font=g.font_16)