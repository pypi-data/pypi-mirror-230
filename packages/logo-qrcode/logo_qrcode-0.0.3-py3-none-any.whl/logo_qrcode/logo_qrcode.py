#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""生成带 Logo 的二维码
    python3 create_qrcode.py -h
"""
import os
import argparse
import qrcode
from PIL import Image, ImageDraw


def set_image_radius(image: Image, radius_width: int):
    """设置图片圆角
    Args:
        image (PIL.Image): 目标图片
        radius_width (int): 圆角尺寸
    """
    radius_width = int(min(image.size[0] * 0.5, image.size[1] * 0.5, radius_width))
    border_mask = Image.new("L", image.size, 0)
    border_draw = ImageDraw.Draw(border_mask)
    border_draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius_width, fill=255)
    image.putalpha(border_mask)


def paste_image_center(image1: Image, image2: Image):
    """将 image2 粘贴到 image1 的中心

    Args:
        image1 (PIL.Image): 目标图片
        image2 (PIL.Image): 粘贴的图片
    """
    border_mask = Image.new("L", image2.size, 0)
    border_draw = ImageDraw.Draw(border_mask)
    border_draw.rounded_rectangle((0, 0, image2.size[0], image2.size[0]), int(image2.size[0] * 0.2), fill=255)

    offset_size = int((image1.size[0] - image2.size[0]) * 0.5)
    image1.paste(image2, (offset_size, offset_size), mask=border_mask)


def create_logo_image(logo_path: str, logo_size: int) -> Image:
    """处理 logo 图片

    Args:
        logo_path (str): logo 图片路径
        logo_size (int): logo 目标尺寸

    Returns:
        _type_: _description_
    """
    # 打开 logo 图像
    logo_image = Image.open(logo_path)
    logo_image = logo_image.convert("RGBA").resize((logo_size, logo_size))
    # 设置 logo 圆角
    set_image_radius(logo_image, int(logo_size * 0.2))
    # 白边
    border_size = logo_image.size[0] + 8
    border_color = (255, 255, 255, 255)
    border_image = Image.new("RGBA", (border_size, border_size), border_color)
    set_image_radius(border_image, int(border_size * 0.2))
    paste_image_center(border_image, logo_image)
    # logo
    logo_image = border_image
    # 灰边
    border_size = logo_image.size[0] + 2
    border_color = (220, 220, 220, 255)
    border_image = Image.new("RGBA", (border_size, border_size), border_color)
    set_image_radius(border_image, int(border_size * 0.2))
    paste_image_center(border_image, logo_image)
    # logo
    logo_image = border_image
    return logo_image


def make(data: str, logo_path: str, qr_path="qr_code.png", qr_size=512):
    """生成二维码
    Args:
        data (str): data
        logo_path (str): logo_path
        qr_path (str, optional): qr_path. Defaults to "qr_code.png".
        qr_size (int, optional): qr_size. Defaults to 512.
    """
    print("data:", data)
    print("logo_path:", logo_path)
    print("qr_path:", qr_path)
    print("qr_size:", qr_size)
    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    qr_image = qr_image.resize((qr_size, qr_size))

    if isinstance(logo_path, str) and logo_path.endswith(".png") and os.path.exists(logo_path):
        logo_image = create_logo_image(logo_path, int(qr_size * 0.2))
        paste_image_center(qr_image, logo_image)

    # 显示和保存二维码
    # qr_image.show()
    qr_image.save(qr_path)


def main():
    """main"""
    parser = argparse.ArgumentParser(description="生成带 Logo 的二维码")
    parser.add_argument("--data", dest="data", required=True, help="二维码信息, 例: http://www.xxx.com")
    parser.add_argument("--save", dest="save", default="qr_code.png", help="保存二维码路径, 默认: qr_code.png")
    parser.add_argument("--logo", dest="logo", help="要添加的 logo 图片地址")
    parser.add_argument("--size", dest="size", type=int, default=512, help="二维码尺寸, 默认 512px")
    # 解析参数
    args = parser.parse_args()
    # 生成二维码
    make(args.data, args.logo, args.save, args.size)


if __name__ == "__main__":
    main()
