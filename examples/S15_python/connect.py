# Shows the use of smoldyn.connect

import smoldyn
import math

def gen_data(t, args):
    x = math.sin(t)
    return x

def update_rate(val):
    global fwd, rev
    fwd.rate = max(0, val)
    print(f'fwd rate={fwd.rate:.3f}, rev binding radius={rev.binding_radius}')

s = smoldyn.Simulation(low=[-500, -500], high=[500, 500])
X = s.addSpecies("X", difc=dict(all=2400, front=10), color="blue", display_size=10)
X.addToSolution(100, lowpos=(-100, -100), highpos=(100, 100))
fwd = s.addReaction("fwd", subs=[X], prds=[X, X], rate=1)
rev = s.addReaction("rev", subs=[X, X], prds=[X], binding_radius=2)
s.connect(gen_data, update_rate, step=10)
s.addGraphics("opengl", iter=10, text_display="time")
s.run(stop=20, dt=0.001)
