import numpy as np
import matplotlib.pyplot as plt

p = 1  # proportional scale factor

def compass_p(goal, curr):
    """Proportional control to get to desired heading"""
    dx = curr - goal
    # caculate distance with branch cut
    dx = dx + np.pi
    dx %= 2 * np.pi
    dx -= np.pi
    return p * dx

heading_goal = np.radians(320)

numtest = 300
test_values = np.arange(numtest) / numtest * 2 * np.pi
control_out = compass_p(heading_goal, test_values)

fig, ax = plt.subplots()
ax.plot(np.degrees(test_values), control_out)
ax.set_title('Proportional control of heading')
ax.set_xlabel('compass reading, degrees')
ax.set_ylabel('controller output')
ax.grid()
plt.show(block=False)
