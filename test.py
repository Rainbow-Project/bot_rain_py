import cv2 as cv
import numpy as np
from wows.utility import User
import asyncio
from wows.APIs import api_get_player_ship_data, api_get_play_personal_data
import aiohttp
import freetype as ft
from io import BytesIO

def render_text(image, text, center_position, font, font_size, color):
    face = font
    face.set_char_size(font_size * 64)

    slot = face.glyph

    # 计算文本宽度
    text_width = 0
    for c in text:
        face.load_char(c, ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT)
        text_width += slot.advance.x >> 6

    # 计算起始 x 位置以使文本居中
    x_position = center_position[0] - (text_width // 2)

    for i, c in enumerate(text):
        face.load_char(c, ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT)
        bitmap = slot.bitmap

        x_pos = x_position + slot.bitmap_left
        y_pos = center_position[1] - slot.bitmap_top

        img_height, img_width = image.shape[:2]
        glyph_height, glyph_width = bitmap.rows, bitmap.width

        for y in range(glyph_height):
            for x in range(glyph_width):
                if y + y_pos < img_height and x + x_pos < img_width:
                    pixel = image[y + y_pos, x + x_pos]
                    glyph_pixel = bitmap.buffer[y * bitmap.pitch + x]

                    blended_pixel = ((1 - (glyph_pixel / 255.0)) * pixel + (glyph_pixel / 255.0) * np.array(color)).astype(np.uint8)
                    image[y + y_pos, x + x_pos] = blended_pixel

        x_position += slot.advance.x >> 6


async def image_gen(user: User, ship_id: str):
    main_data_img = cv.imread('components/main_data.png')
    max_data_img = cv.imread('components/max_main.png')
    pr_bar_img = cv.imread('components/pr_bar.png') 
    color_bg = user.pr.color_background[::-1]
    color_pr = user.pr.pr_color[::-1]
    pr_bar_img[:,:,0][pr_bar_img[:,:,0] == 222] = color_pr[0]
    pr_bar_img[:,:,1][pr_bar_img[:,:,1] == 222] = color_pr[1]
    pr_bar_img[:,:,2][pr_bar_img[:,:,2] == 222] = color_pr[2]

    main_data_img[:,:,0][main_data_img[:,:,0] == 222] = color_bg[0]
    main_data_img[:,:,1][main_data_img[:,:,1] == 222] = color_bg[1]
    main_data_img[:,:,2][main_data_img[:,:,2] == 222] = color_bg[2]

    max_data_img[:,:,0][max_data_img[:,:,0] == 222] = color_bg[0]
    max_data_img[:,:,1][max_data_img[:,:,1] == 222] = color_bg[1]
    max_data_img[:,:,2][max_data_img[:,:,2] == 222] = color_bg[2]

    font_medium = 'src/font/SourceHanSans-Medium.otf'
    font_heavy = 'src/font/SourceHanSans-Heavy.otf'
    font_medium = ft.Face(font_medium)
    font_heavy = ft.Face(font_heavy)

    img = np.full((1900, 1242, 3), 255, dtype=np.uint8)
    img[336:336 + 120, :] = pr_bar_img
    img[483:483 + 650, :] = main_data_img
    img[1160:1160 + 650, :] = max_data_img
    render_text(img, user.clan_tag, (621, 66), font_heavy, 48, user.pr.color_text)
    render_text(img, user.nick_name, (621, 152), font_medium, 48, user.pr.color_text)

    ship = user.ship_dic[ship_id]

    render_text(img, ship.ship_name, (621, 265), font_medium, 48, ship.pr.color_text)

    render_text(img, f'{ship.pr.pr_text} {ship.pr.pr_number}', (621, 410), font_medium, 32, ship.pr.color_text)

    render_text(img, ship.display_battles, (270, 776), font_medium, 32, ship.pr.color_text)
    render_text(img, ship.display_xp, (270, 1026), font_medium, 32, ship.pr.color_text)

    render_text(img, ship.display_winrate, (621, 776), font_medium, 32, ship.pr.color_text)
    render_text(img, ship.display_kd, (621, 1026), font_medium, 32, ship.pr.color_text)

    render_text(img, f'{ship.display_damage}', (970, 776), font_medium, 32, ship.pr.color_text)
    render_text(img, f'{ship.display_accu_rate}', (970, 1026), font_medium, 32, ship.pr.color_text)

    render_text(img, f'{ship.max_damage_dealt}', (215, 1443), font_medium, 32, ship.pr.color_text)
    render_text(img, f'{ship.max_planes_killed}', (215, 1666), font_medium, 32, ship.pr.color_text)

    render_text(img, f'{ship.max_xp}', (621, 1443), font_medium, 32, ship.pr.color_text)
    render_text(img, f'{ship.max_total_agro}', (621, 1666), font_medium, 32, ship.pr.color_text)

    render_text(img, f'{ship.max_frags}', (1025, 1443), font_medium, 32, ship.pr.color_text)
    render_text(img, f'{ship.max_ships_spotted}', (1025, 1666), font_medium, 32, user.pr.color_text)
    
    # _, buffer = cv.imencode('.jpg', img)
    # bytes_io = BytesIO(buffer)
    # return bytes_io
    cv.imwrite('TEST.PNG', img)

async def main():
    async with aiohttp.ClientSession() as session:
        ships_data = await api_get_player_ship_data(session, '2022397176', 0)
        user_data = await api_get_play_personal_data(session, '2022397176', 0)
        user = User()
        user.init_user(user_data['2022397176'], ships_data['2022397176'], 0, None, 'LKA')
        await user.async_init(ships_data['2022397176'])
        await image_gen(user, '3971888592')
    pass

if __name__ == '__main__':
    asyncio.run(main())
    pass
