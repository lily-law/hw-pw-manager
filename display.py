from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106, ws0010

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
# substitute bitbang_6800(RS=7, E=8, PINS=[25,24,23,27]) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1306(serial)

# display is 126 x 64
font_size = 8
# at size 8: 16 chars long 8 lines

def browse(entries, page, n_pages, **args):
  with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    nEntries = len(entries)
    for row in range(6):
      if row < nEntries:
        entry = entries[row]
        draw.text((font_size * row, 0), f"{row}: {entry['service'][0: 6]} | {entry['username'][0: 6]}", fill="white")
    draw.text((font_size * 6, 0), f"Page{page}/{n_pages}", fill="white")
    draw.text((font_size * 6, 128 - (font_size * 7)), f"A:add", fill="white")
    draw.text((font_size * 7, 0), "*:prev", fill="white")
    draw.text((font_size * 7, 128 - (font_size * 8)), "#:next", fill="white")

def view(service, username, password, **args):
  with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((font_size * 0, 0), f"1: {service[0: 13]}", fill="white")
    draw.text((font_size * 1, 0), f"2: {username[0: 13]}", fill="white")
    draw.text((font_size * 2, 0), f"3: {password[0: 13 + 32]}", fill="white")
    draw.text((font_size * 5, 0), "#+A:edit", fill="white")
    draw.text((font_size * 5, 128 - (font_size * 7)), f"B:back", fill="white")
    draw.text((font_size * 6, 0), "#+c:paste", fill="white")
    draw.text((font_size * 7, 0), "*+D(hold):delete", fill="white")

def edit(service, username, password, **args):
  with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((font_size * 0, 0), f"1: {service[0: 13 + 16]}", fill="white")
    draw.text((font_size * 1, 0), f"2: {username[0: 13 + 16]}", fill="white")
    draw.text((font_size * 2, 0), f"3: {password[0: 13 + 16]}", fill="white")
    draw.text((font_size * 6, 0), "A:input", fill="white")
    draw.text((font_size * 6, 128 - (font_size * 8)), "B:select", fill="white")
    draw.text((font_size * 7, 0), "C:gen", fill="white")
    draw.text((font_size * 7, 128 - (font_size * 8)), "D:done", fill="white")

views = {
  'browse': browse,
  'view': view,
  'edit': edit
}