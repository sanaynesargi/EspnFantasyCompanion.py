from PIL import Image, ImageDraw, ImageFont

def draw_title(img, dims, msg):
    fsize = 200
    stroke = ImageFont.truetype('./fonts/stylefont.ttf', fsize)
    W, H = dims
    w, h = img.textsize(msg, font=stroke)
    img.text(((W-w)/2, 500), msg, font=stroke, fill=(0, 0, 0))


def draw_dict(start, interval, dictionary, img, nl):
    fsize = 100
    stroke = ImageFont.truetype('./fonts/statsfont.ttf', fsize)
    x, y = start

    #print((dictionary))
    for k, v in dictionary.items():
        if type(v) == type([]):
            string = f"{k}: "
            for s in v:
                if type(s) == type(dict()):
                    string += "\n    "
                    for key in s:
                        if key != "Week":
                            string += f"{s[key]}, "
                        else:
                            string += f"{key}: {s[key]}"
                    interval += 100
                else:
                    if nl: 
                        string += "\n    "
                        interval += 100
                    string += f"{s}, "

            if string[-2:] == ", ": 
                string = string[0:-2]
            img.text((x,y), string, font=stroke, fill=(0, 0, 0))
        else:
            img.text((x,y), f"{k}: {v}", font=stroke, fill=(0, 0, 0))
        y += interval


def draw_stats(stats, title, output, startx=100, starty=800, nl_on_list=False):
    img = Image.open('./images/back_image.png')
    drawn = ImageDraw.Draw(img)
    draw_title(drawn, img.size, title)
    draw_dict((startx,starty), 120, stats, drawn, nl_on_list)
    img.save(output)
