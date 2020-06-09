from os.path import expanduser, normpath, abspath, isdir, join
from glob import glob
from os import mkdir
from shutil import copy2

# GUI
MP_SETTINGS_FILENAME = expanduser("~/.mp_gryphon_settings")
RIGAL_SCRATCH = expanduser("~/.mp_gryphon_rigal_scratch")
TRACE_GENERATED_OUTFILE = join(RIGAL_SCRATCH, "_mp_trace_generator_output")

# RIGAL
RIGAL_ROOT = abspath(normpath("../../trace-generator"))
RIGAL_RC = join(RIGAL_ROOT, "RIGAL/rigsc.446/bin/rc")
RIGAL_IC = join(RIGAL_ROOT, "RIGAL/rigsc.446/bin/ic")
RIGAL_CODE = join(RIGAL_ROOT, "Code")

# examples
MP_CODE_EXAMPLES = join(RIGAL_ROOT, "Firebird_Pre_loaded_examples")
MP_CODE_DEFAULT_EXAMPLE = join(MP_CODE_EXAMPLES, "Example03_ATM_withdrawal.mp")

def make_rigal_scratch():
    if not isdir(RIGAL_SCRATCH):
        # make the RIGAL scratch work area
        mkdir(RIGAL_SCRATCH)

    # always put in requisite RIGAL files in case RIGAL was updated
    files = glob(join(RIGAL_CODE, "*.h"))
    files.extend(glob(join(RIGAL_CODE, "*.rig")))
    for f in files:
        copy2(f, RIGAL_SCRATCH)
  
