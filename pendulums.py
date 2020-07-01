import numpy as np
import cv2
import time
from collections import deque

class Pendulum:
    def __init__(self, origin, angle, length, mass, vel, color = [np.random.randint(50, 256) for _ in range(3)]):
        self.origin = origin
        self.end = [origin[0] * length * np.sin(angle), origin[1] * length * np.cos(angle)]
        self.len = length
        self.aAcc = 0
        self.aVel = vel
        self.angle = angle
        self.color = color
        self.mass = mass
        self.moved = False
        

def get_acc(pen):
    if pen is pen1:
        num1 = -g * (2 * pen1.mass + pen2.mass) * np.sin(pen1.angle)
        num2 = -pen2.mass * g * np.sin(pen1.angle - 2 * pen2.angle)
        num3 = -2 * np.sin(pen1.angle - pen2.angle) * pen2.mass
        num4 = pen2.aVel**2 * pen2.len + pen1.aVel**2 * pen1.len * np.cos(pen1.angle - pen2.angle)
        den  = pen1.len * (2 * pen1.mass + pen2.mass - pen2.mass*np.cos(2*pen1.angle -2*pen2.angle))
        pen1.aAcc = (num1 + num2 + num3*num4) / den
    elif pen is pen2:
        num1 = 2 * np.sin(pen1.angle - pen2.angle)
        num2 = pen1.aVel**2 * pen1.len * (pen1.mass + pen2.mass) + g * (pen1.mass + pen2.mass) * np.cos(pen1.angle)
        num3 = pen2.aVel**2 * pen2.len * pen2.mass * np.cos(pen1.angle - pen2.angle)
        den = pen2.len * (2 * pen1.mass + pen2.mass - pen2.mass*np.cos(2*pen1.angle - 2*pen2.angle))
        pen2.aAcc = (num1*(num2 + num3)) / den

center = [4, 4]
pendulums = [Pendulum(center, np.radians(150), 2, 1, 0, (150, 100, 200))]
for params in ((np.radians(180.835), 1.5, .75, 0, (150, 200, 50)),):
    pendulums.append(Pendulum(pendulums[-1].end, *params))
    # add more pendulums. math will be wildly innacruate but the same used for 2 pendulums.

num_dots = 10000
size = [i*2 for i in center]
scale = 100
g = 0.002206575
canvas = np.zeros((size[0] * scale, size[1]*scale, 3))
fourcc = cv2.VideoWriter_fourcc(*'H265')
out = cv2.VideoWriter('output.mp4', fourcc, 60.0, (1000,1000))

dots = deque()

while cv2.waitKey(1) & 0xFF != ord('q'):
    start = time.time()
    new_canvas = canvas.copy()
    for pen in pendulums:
        pen.moved = False
    for idx, pen1 in enumerate(pendulums[:-1]):
        pen2 = pendulums[idx + 1]
        
        for pen in (pen1, pen2):
            if not pen.moved:
                get_acc(pen)
                pen.angle += pen.aVel + pen.aAcc / 2
                pen.aVel += pen.aAcc
                pen.end[0] = pen.origin[0] + np.sin(pen.angle) * pen.len
                pen.end[1] = pen.origin[1] + np.cos(pen.angle) * pen.len

                cv2.line(new_canvas, tuple([int(i*scale) for i in pen.origin]), tuple([int(i*scale) for i in pen.end]), pen.color)
                cv2.circle(new_canvas, tuple([int(i*scale) for i in pen.end]), 17, pen.color, 1)
                cv2.circle(new_canvas, tuple([int(i*scale) for i in pen.end]), np.clip(abs(int(pen.aVel*200)), 1, 17), np.clip([i*1.5 for i in pen.color], 0, 255).tolist(), -1)
                pen.moved = True
    
    for pen, color in zip(pendulums, ((0, 0, 255), (0, 255, 0))):
        dot_loc = tuple([int(i*scale) for i in pen.end])
        dots.append(dot_loc)
        cv2.circle(canvas, dot_loc, 1, color, -1)
        
    if len(dots) > num_dots:
        for i in range(len(pendulums)):
            cv2.circle(canvas, dots.popleft(), 1, (0, 0, 0), -1)
        
    new_canvas = cv2.resize(new_canvas.astype(np.uint8), (1000, 1000))
    cv2.imshow('img', new_canvas)
    out.write(new_canvas)
out.release()
cv2.destroyAllWindows()
