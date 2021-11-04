from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from math import ceil, floor

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
# substitute bitbang_6800(RS=7, E=8, PINS=[25,24,23,27]) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1306(serial)

# display is 128 x 64
font_size = (6, 8)
# at size 8: 16 chars long 8 lines
chars_per_line = floor(128 / 6)
lines = floor(64 / 8)


def line(draw, row, text, col = 0, invert = False, max_rows = 1, max_cols = chars_per_line, align = "left"):
    fill="white"
    def calc_col_start(col, text_len):
        col_start = (col * font_size[0]) + 1
        if align == "right":
            col_start = ((max_cols - text_len) * font_size[0]) - col
        elif align == "center":
            col_start = (floor(max_cols / 2) - floor(text_len / 2)) * font_size[0]
        if col_start < 1:
            col_start = 1
        return col_start

    row_start = (row * font_size[1]) - 2
    col_start = calc_col_start(col, len(text))
    if row + max_rows > lines:
        print(f"Warning: have allocated for {row + 1 + max_rows} lines but only {lines} line available to display text: {text}")
    if invert:
        text_end = col_start + (len(text) * font_size[0])
        row_end = row_start + (font_size[1] * ceil(len(text) / max_cols))
        draw.rectangle((col_start - 1, row_start + 1, text_end + 1, row_end + 1), fill)
        fill="black"
    
    last_end = 0
    for r in range(max_rows):
        if r > 0:
            col = 0
        if len(text) > last_end:
            end = last_end + (max_cols - col)
            line_text = text[last_end: end]
            last_end = end
            col_start = calc_col_start(col, len(line_text))
            if r + 1 == max_rows and len(text) > last_end: # last row
                line_text = line_text[0: max_cols - col  - 3] + '...'
            draw.text((col_start, row_start + (r * font_size[1])), line_text, fill)


def welcome(**args): 
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, fill="black")
        line(draw, 1, "Welcome", invert=True, align="center")
        line(draw, 3, "Press A to make your first entry", max_rows=2)
        line(draw, 6, "Press D to exit")


def lock(pin, user, failed_login, selected_row, **args):
  with canvas(device) as draw:
    draw.rectangle(device.bounding_box, fill="black")
    line(draw, 0, "1: User", invert = selected_row == 'user')
    line(draw, 1, f"{user}")
    line(draw, 2, "2: Pin", invert = selected_row == 'pin')
    line(draw, 3, ("*" * len(pin)))
    if failed_login:
      line(draw, 4, "Incorrect PIN!", invert = True, align="center")
    elif selected_row == 'user' or selected_row == 'pin':
      line(draw, 4, f"Enter {selected_row}", align="center")
    elif not user:
      line(draw, 4, "Press 1 to input user", align="center")
    elif not pin:
      line(draw, 4, "Press 2 to input pin", align="center")
    if selected_row:
      line(draw, 5, "B:backspace")
    Fn4_text = ''
    if selected_row:
      Fn4_text = 'D:done'
    elif user and pin:
      Fn4_text = 'D:enter'
    if Fn4_text:  
      line(draw, 5, Fn4_text, align="right")
    line(draw, 7, "C+*(hold):power off", align="right")


loading_count = [0]
def loading(loading_message, **args): 
  if not loading_message:
      loading_message = "Loading"
  with canvas(device) as draw:
    draw.rectangle(device.bounding_box, fill="black")
    message = f"{loading_message}{'.' * loading_count[0]}{' ' * (3 - loading_count[0])}"
    line(draw, 3, message, align="center")
    loading_count[0] = (loading_count[0] + 1) % 4

    
def browse(entries, page_entry_indexes, page, n_pages, **args):
  with canvas(device) as draw:
    draw.rectangle(device.bounding_box, fill="black")
    line(draw, 0, f"Page{page + 1}/{n_pages}", align="center")
    nEntries = len(entries)
    for r, row in enumerate(page_entry_indexes):
      if row < nEntries:
        entry = entries[row]
        row_start = (r + 1.5) + r
        line(draw, row_start, f"{r + 1}: ")
        line(draw, row_start, entry['username'], 3, max_cols=chars_per_line - 3)
        line(draw, row_start + 1, entry['service'])
    if page > 0:
        line(draw, 6, "*:prev")
    line(draw, 6, "A:add", align="center")
    if page + 1 < n_pages:
        line(draw, 6, "#:next", align="right")
    line(draw, 7, "B+*(hold):lock", align="right")

def view(selected_entry_index, entries, selected_row, **args):
  entry = entries[selected_entry_index]
  service = entry['service']
  username = entry['username']
  password = entry['password']
  with canvas(device) as draw:
    draw.rectangle(device.bounding_box, fill="black")
    line(draw, 0, "1:", invert=selected_row == 'service')
    line(draw, 0, service, 2)
    line(draw, 1, "2:", invert=selected_row == 'username')
    line(draw, 1, username, 2)
    line(draw, 2, "3:", invert=selected_row == 'password')
    line(draw, 2, password, 2, max_rows=4)
    line(draw, 6, "A+#:edit")
    line(draw, 6, "B:back", align="right")
    if selected_row:
        line(draw, 7, "C+#:transmit", align="right")
    else:
        line(draw, 7, "D+*(hold):delete", align="right")


def edit(service, username, password, selected_row, **args):
  with canvas(device) as draw:
    draw.rectangle(device.bounding_box, fill="black")
    line(draw, 0, "1:", invert=selected_row == 'service')
    line(draw, 0, service, 3)
    line(draw, 1, "2:", invert=selected_row == 'username')
    line(draw, 1, username, 3)
    line(draw, 2, "3:", invert=selected_row == 'password')
    line(draw, 2, password, 3, max_rows=4)
    if selected_row:
        line(draw, 6, "A:generate value")
        line(draw, 7, "B:backspace")
        line(draw, 7, "D:done", align="right")
    else:
        line(draw, 7, "C:cancel")
        line(draw, 7, "D:save", align="right")

def saving(**args): 
    loading("Saving")


def shutdown(**args): 
    loading("Shutting down")

def error(error_message, **args):
  with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    line(draw, 0, f"Error: {error_message}", max_rows=6)
    line(draw, 7, "C:continue")

views = {
  'welcome': welcome,
  'lock': lock,
  'loading': loading,
  'browse': browse,
  'view': view,
  'edit': edit,
  'saving': saving,
  'shutdown': shutdown,
  'error': error
}
