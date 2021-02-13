Examples
********


Using ``smoldyn.connect``
---------------------------

The Python module add a few new capabilities to Smoldyn. Smoldyn can now call
any arbitrary function ``foo`` during the simulation and can use the return
value of ``foo`` to update one of the it's object. 

In the example below, Smoldyn is calling the function ``generate_spike`` and
uses its value to update the rate of the reaction using a callback function
``update_kf``.


.. code-block:: python

    import smoldyn
    import random
    import math

    r1_ = None
    bouton_ = None

    def generate_spike(t, args):
        x = random.random()
        if x < 0.1:
            x += 1
        return x


    def update_kf(val):
        global r1_, bouton_
        r1_.kf = 1000 ** val
        c = min(1.0, val)
        bouton_.setStyle('both', color=[c, c, c])


    """
    Size of bouton: 1 cubic µm
    diameter of Synaptic Vesicle (SV): 40 nm
    Diff of SV: 0.024 um^2/s (2400 nm^2/s)
    1px = 1nm throughout.
    """
    s = smoldyn.Simulation(low=[-500, -500], high=[1500, 1500])
    sv = s.addSpecies("SV", difc=dict(all=2400, front=10), color="blue", display_size=10)
    sv.addToSolution(100, lowpos=(0, 0), highpos=(1000, 1000))

    # add a reaction with generates the sv at a fixed rate. Its better to
    # split so location of the new sv is inside the box.
    s.addReaction("svgen", [sv], [sv, sv], rate=1e-6)

    # fused vesicle.
    svFused = s.addSpecies("VSOpen", color="blue", display_size=10)

    # neutotransmitter. The concentration has the half-life of 2ms (PMID:
    # 19844813), that is, rate is 0.693/2e-3, k ~ 346 per sec
    trans = s.addSpecies("trans", color="red", difc=10000, display_size=2)
    decay = s.addReaction("decay", subs=[trans], prds=[], rate=math.log(2) / 20e-3)

    # BOUTON
    path = s.addPath2D((1000, 0), (1000, 1000), (0, 1000), (0, 0))
    bouton_ = s.addSurface("bouton", panels=path.panels)
    bouton_.setStyle('both', color="blue")
    bouton_.setAction('both', [sv], "reflect")

    # this is the bottom surface of bouton. This is sticky for synaptic
    # vesciles
    rect1 = smoldyn.Rectangle(corner=(0, 0), dimensions=[1000], axis="+y")
    bottom = s.addSurface("boutonBottom", panels=[rect1])
    bottom.setStyle('both', color="red")
    bottom.setAction('back', trans, "reflect")  # but it reflect neurotranmitter

    # SV stick to bottom of the bouton and also detach back with a smaller
    # rate.
    bottom.setRate(sv, "fsoln", "front", rate=10, revrate=0.001)

    # They move to outside of bouton, this value is dependant on the membrane
    # potential
    bottom.setRate(sv, "front", "bsoln", rate=10, new_species=svFused)

    # Open vesicle turns into 1000 to 2000 or neurotransmitters.
    r1_ = s.addReaction("open2trans", subs=[svFused], prds=[trans] * 200, rate=100.0)
    s.connect(generate_spike, update_kf, step=20)

    s.addGraphics("opengl", iter=10, text_display="time")
    print('[INFO] Starting simulation ...')
    s.run(stop=20, dt=0.001)
    print("Done")


Examples
--------

.. literalinclude:: ../../examples/S15_python/2Dreact.py



.. liternalinlude:: ../../examples/S15_python/2Dreact.py


.. liternalinlude:: ../../examples/S15_python/bistable.py


.. liternalinlude:: ../../examples/S15_python/bounce3.py


.. liternalinlude:: ../../examples/S15_python/bounds1.py


.. liternalinlude:: ../../examples/S15_python/bounds2.py


.. liternalinlude:: ../../examples/S15_python/box.py


.. liternalinlude:: ../../examples/S15_python/change_env.py


.. liternalinlude:: ../../examples/S15_python/cluster.py


.. liternalinlude:: ../../examples/S15_python/cmddata.py


.. liternalinlude:: ../../examples/S15_python/integrate_with_moose.py


.. liternalinlude:: ../../examples/S15_python/intersurface.py


.. liternalinlude:: ../../examples/S15_python/lotvolt.py


.. liternalinlude:: ../../examples/S15_python/port.py


.. liternalinlude:: ../../examples/S15_python/template.py

