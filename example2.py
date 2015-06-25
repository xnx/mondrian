from mondrian2 import Canvas

nlines = 25
width, height = 600, 450
minarea = 5000 / (width * height)
canvas = Canvas(width, height)
canvas.make_painting(nlines, minarea, orthogonal=False)
canvas.write_svg('example2.svg')
