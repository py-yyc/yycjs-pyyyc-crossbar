

for y in range(16):
    line = ''
    for x in range(16):
        line += '<td id="pixel_{}_{}"><a href="#" onclick="return pixel_click({}, {});"></a></td>'.format(x, y, x, y)
    print('        <tr>{}</tr>'.format(line))
