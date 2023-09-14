ont_core_path = "<ont_core dirpath>"
port_path = "<port uri>"
log_path = "<guppy_server_log dirpath>"
input_path = "<input dirpath>"
align_ref = "<align_ref filepath>"
bed_file = "<bed_file filepath>"

# Interface
# ---------

# ``ont-pyguppy-client-lib`` comprises three Python modules:

# **helper_functions** A set of functions for running a Dorado basecall server and
# loading reads from fast5 and/or pod5 files.
# **client_lib** A compiled library which provides direct Python bindings to Dorado's
# C++ GuppyClient API.
# **pyclient** A user-friendly wrapper around **client_lib**. This is what you
# should use to interact with a Dorado basecall server.
from pyguppy_client_lib import client_lib, helper_functions, pyclient

# Documentation and help
# ----------------------
# Information on the methods available may be viewed through Python's help command:

help(pyclient)
help(client_lib)


# Starting a basecall server
# --------------------------
# There must be a Dorado basecall server running in order to communicate with it.
# On most Oxford Nanopore devices a basecall server is always running on port 5555.
# On other devices, or if you want to run a separate basecall server, you must start
# one yourself:

# A basecall server requires:
#  * A location to put log files (on your PC)
#  * An initial config file to load
#  * A port to run on
server_args = [
    "--log_path",
    log_path,
    "--config",
    "dna_r9.4.1_450bps_fast.cfg",
    "--port",
    port_path,
]
# The second argument is the directory where the dorado_basecall_server executable
# is found. Update this as  appropriate.
helper_functions.run_server(server_args, str(ont_core_path / "bin"))


# Basecall and align using PyGuppyClient
# --------------------------------------

print("Starting PyGuppyClient...")
from pyguppy_client_lib.pyclient import PyGuppyClient

client = PyGuppyClient(
    port_path, "dna_r9.4.1_450bps_fast", align_ref=align_ref, bed_file=bed_file
)
client.connect()
print(client)

# Using the client generated in the previous example
print("Basecalling...")
called_reads = helper_functions.basecall_with_pyguppy(client, input_path)

for read in called_reads:
    read_id = read["metadata"]["read_id"]
    alignment_genome = read["metadata"]["alignment_genome"]
    sequence = read["datasets"]["sequence"]
    print(
        f"{read_id} sequence length is {len(sequence)}"
        f"alignment_genome is {alignment_genome}"
    )


# Basecall and get states, moves and modbases using GuppyClient
# -------------------------------------------------------------
# In order to retrieve the ``movement`` dataset, the ``move_and_trace_enabled``
# option must be set to ``True``; analogously, for the ``state_data`` one,
# ``post_out`` must be turned on.
# NOTE: You shouldn't turn on ``post_out`` if you don't need the states, because
# it generates a LOT of extra output data so it can really hurt performance.
# Likewise with ``move_and_trace_enabled``, although that's much less expensive.

print("Starting GuppyClient...")
from pyguppy_client_lib.client_lib import GuppyClient

options = {
    "priority": GuppyClient.high_priority,
    "client_name": "test_client",
    "move_and_trace_enabled": True,
    "post_out": True,
}

client = GuppyClient(port_path, "dna_r9.4.1_e8.1_modbases_5mc_cg_fast")
result = client.set_params(options)
result = client.connect()
print(client)

called_reads = helper_functions.basecall_with_pyguppy(client, input_path)

print("Basecalling...")
for read in called_reads:
    base_mod_context = read["metadata"]["base_mod_context"]
    base_mod_alphabet = read["metadata"]["base_mod_alphabet"]

    sequence = read["datasets"]["sequence"]
    movement = read["datasets"]["movement"]
    state_data = read["datasets"]["state_data"]
    base_mod_probs = read["datasets"]["base_mod_probs"]

    print(
        f"{read_id} sequence length is {len(sequence)}, "
        f"base_mod_context is {base_mod_context}, base_mod_alphabet is {base_mod_alphabet}, "
        f"movement size is {movement.shape}, state_data size is {state_data.shape}, "
        f"base_mod_probs size is {base_mod_probs.shape}"
    )
