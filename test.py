import cv2 as cv
import numpy as np
from wows.utility import User, Ship
import asyncio
from wows.APIs import api_get_player_ship_data, api_get_play_personal_data
import aiohttp
from PIL import Image, ImageDraw, ImageFont
import time
from io import BytesIO

def render_text_pil(image, text, center_position, font, font_size, text_color):
    # 创建Draw对象
    draw = ImageDraw.Draw(image)

    # 计算文本长度和起始位置
    text_length = draw.textlength(text, font=font)
    x_position = center_position[0] - text_length // 2
    y_position = center_position[1] - 50 // 2

    # 绘制文本
    draw.text((x_position, y_position), text, font=font, fill=text_color)

    return image

def render_text_cv(image, text, center_position, font, font_size, color):
    # 计算字体缩放比例
    font_scale = font_size / 30.0

    # 计算文本大小和起始位置
    text_size, baseline = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, font_scale, thickness=4)
    x_position = center_position[0] - text_size[0] // 2
    y_position = center_position[1] + text_size[1] // 2

    # 绘制文本
    cv.putText(image, text, (x_position, y_position), cv.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness=4, lineType=cv.LINE_AA)

async def image_gen(user: User, ship_id):
    main_data_img = cv.imread('components/main_data.png')
    max_data_img = cv.imread('components/max_main.png')
    pr_bar_img = cv.imread('components/pr_bar.png') 
    ship = user.ship_dic.get(ship_id, None)
    if ship is None:
        raise('没有该船只')
    color_bg = ship.pr.color_background[::-1]
    color_pr = ship.pr.pr_color[::-1]
    pr_bar_img[:,:,0][pr_bar_img[:,:,0] == 222] = color_pr[0]
    pr_bar_img[:,:,1][pr_bar_img[:,:,1] == 222] = color_pr[1]
    pr_bar_img[:,:,2][pr_bar_img[:,:,2] == 222] = color_pr[2]

    main_data_img[:,:,0][main_data_img[:,:,0] == 222] = color_bg[0]
    main_data_img[:,:,1][main_data_img[:,:,1] == 222] = color_bg[1]
    main_data_img[:,:,2][main_data_img[:,:,2] == 222] = color_bg[2]

    max_data_img[:,:,0][max_data_img[:,:,0] == 222] = color_bg[0]
    max_data_img[:,:,1][max_data_img[:,:,1] == 222] = color_bg[1]
    max_data_img[:,:,2][max_data_img[:,:,2] == 222] = color_bg[2]

    font_medium = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 40)
    font_heavy = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 48)

    img = np.full((1900, 1242, 3), 255, dtype=np.uint8)
    img[336:336 + 120, :] = pr_bar_img
    img[483:483 + 650, :] = main_data_img
    img[1160:1160 + 650, :] = max_data_img
    render_text_cv(img, user.clan_tag, (621, 66), font_heavy, 48, user.pr.color_text)
    render_text_cv(img, user.nick_name, (621, 152), font_medium, 48, user.pr.color_text)

    render_text_cv(img, ship.display_battles, (270, 776), font_medium, 32, ship.pr.color_text)
    render_text_cv(img, ship.display_xp, (270, 1026), font_medium, 32, ship.pr.color_text)

    render_text_cv(img, ship.display_winrate, (621, 776), font_medium, 32, ship.pr.color_text)
    render_text_cv(img, ship.display_kd, (621, 1026), font_medium, 32, ship.pr.color_text)

    render_text_cv(img, f'{ship.display_damage}', (970, 776), font_medium, 32, ship.pr.color_text)
    render_text_cv(img, f'{ship.display_accu_rate}', (970, 1026), font_medium, 32, ship.pr.color_text)

    render_text_cv(img, f'{ship.max_damage_dealt}', (215, 1443), font_medium, 32, ship.pr.color_text)
    render_text_cv(img, f'{ship.max_planes_killed}', (215, 1666), font_medium, 32, ship.pr.color_text)

    render_text_cv(img, f'{ship.max_xp}', (621, 1443), font_medium, 32, ship.pr.color_text)
    render_text_cv(img, f'{ship.max_total_agro}', (621, 1666), font_medium, 32, ship.pr.color_text)

    render_text_cv(img, f'{ship.max_frags}', (1025, 1443), font_medium, 32, ship.pr.color_text)
    render_text_cv(img, f'{ship.max_ships_spotted}', (1025, 1666), font_medium, 32, user.pr.color_text)

    img = Image.fromarray(img[..., ::-1])
    render_text_pil(img, ship.ship_name, (621, 265), font_medium, 48, ship.pr.color_text)
    render_text_pil(img, f'{ship.pr.pr_text} {ship.pr.pr_number}', (621, 390), font_medium, 32, ship.pr.color_text)
    
    # bytes_io = BytesIO()
    # img.save(bytes_io, format='JPEG')
    # bytes_io.seek(0)
    # return bytes_io.getvalue()
    img.save("TEST.PNG")



async def main():
    async with aiohttp.ClientSession() as session:
        start = time.time()
        ships_data = await api_get_player_ship_data(session, '2022397176', 0)
        user_data = await api_get_play_personal_data(session, '2022397176', 0)
        user = User()
        user.init_user(user_data['2022397176'], ships_data['2022397176'], 0, None, 'LKA')
        await user.async_init(ships_data['2022397176'])
        user.date = '111'
        await image_gen(user, '4180588496')
        end = time.time()
        print(end - start)
    pass

if __name__ == '__main__':
    asyncio.run(main())
    pass

