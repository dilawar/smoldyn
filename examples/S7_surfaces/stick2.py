"""Python equivalent of stick2.txt
Note:
    yellow is green in txt file. green and red together is bad idea (since I am
    colorblind).
"""
__author__ = "Dilawar Singh"
__email__ = "dilawars@ncbs.res.in"

import smoldyn as S

S.setBounds(low=[0, 0], high=[100, 100])
red = S.Species("red", color="red", difc=dict(all=3, front=0), display_size=5)
yellow = S.Species("yellow", color="yellow", difc=dict(soln=3, back=1), display_size=5)
blue = S.Species("blue", color="blue", difc=3, display_size=5)

red.addToSolution(100)
yellow.addToSolution(50, pos=(50, 50))
blue.addToSolution(50, pos=(20, 20))

# Construct a closed path in 2D.
p = S.Path2D((0, 0), (100, 0), (100, 100), (0, 100), closed=True)
walls = S.Surface("walls", panels=p.panels)
walls.both.addAction([red, yellow, blue], "reflect")
walls.both.setStyle(color="black")

sph = S.Sphere(center=(50, 50), radius=20, slices=20)
surf = S.Surface("stick", panels=[sph])
surf.setRate(red, "fsoln", "front", rate=1, revrate=0.1)
surf.setRate(yellow, "bsoln", "back", rate=1, revrate=0.1)
surf.setRate(blue, "fsoln", "bsoln", rate=1, revrate=0.1)
surf.front.setStyle(color=(1, 0.7, 0))
surf.back.setStyle(color=(0.6, 0, 0.6))
surf.addMolecules((red, "front"), 100)

sim = S.Simulation(1000, 0.01)
sim.setGraphics("opengl")
sim.addCommand("killmolinsphere red all", "b")
sim.run()