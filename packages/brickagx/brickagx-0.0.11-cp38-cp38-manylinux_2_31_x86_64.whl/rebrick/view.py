import agxOSG
import os
import signal
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from brickbundles import bundle_path

# Import useful utilities to access the current simulation, graphics root and application
from agxPythonModules.utils.environment import init_app, simulation, application, root

from rebrick import InputSignalListener, OutputSignalListener, load_brickfile

def parse_args():
    parser = ArgumentParser(description="View brick models", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("brickfile", help="the .brick file to load")
    parser.add_argument("[AGX flags ...]", help="any additional AGX flags", default="", nargs="?")
    # Kept here for future implementation
    # parser.add_argument("--enable-click", help="Enable sending and receiving signals as Click Messages", action="store_true")
    # parser.add_argument("--click-addr", help="Address for Click to listen on, e.g. ipc:///tmp/click.ipc", default="tcp://*:5555")
    parser.add_argument("--bundle-path", help="list of path to bundle dependencies if any. Overrides environment variable BRICK_BUNDLE_PATH.", metavar="<bundle_path>", default=bundle_path())
    return parser.parse_args()

def buildScene():

    args = parse_args()

    brick_scene, assembly = load_brickfile(simulation(), args.brickfile, args.bundle_path, "")

    # Signals are not used yet, but kept here for future click and/or ros2 usage implementation
    # Add a signal listener so that signals are picked up from inputs
    input_signal_listener = InputSignalListener(assembly)
    output_signal_listener = OutputSignalListener(assembly, brick_scene)
    simulation().add(input_signal_listener, InputSignalListener.RECOMMENDED_PRIO)
    simulation().add(output_signal_listener, OutputSignalListener.RECOMMENDED_PRIO)
    simulation().add(assembly.get())

    agxOSG.createVisual(assembly.get(), root())

def handler(signum, frame):
    os._exit(0)

signal.signal(signal.SIGINT, handler)

parse_args()
init = init_app(name=__name__,
                scenes=[(buildScene, '1')],
                autoStepping=True,  # Default: False
                onInitialized=lambda app: print('App successfully initialized.'),
                onShutdown=lambda app: print('App successfully shut down.'))
