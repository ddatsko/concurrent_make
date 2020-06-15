MAKEFILE: str = 'concurrent_makefile'

# Be careful. The path os from this directory (not the one you run the program). You`d better not touch this
HOSTS_FILE: str = 'hosts'

# If files dependencies should be checked and extended by running "$ g++ -M" and
# "$ ldd <library>" for finding out all the libraries, the one depends on
CHECK_MORE_DEPENDENCIES: bool = True

# Timeout (In SECONDS!!) of websocket to receive a complete response. If the server does not respond after
# this timout, connection with it will be closed. None means wait forever.
RECEIVE_TIMEOUT: float or None = None

# If False, libraries with higher versions will substitute ones with lower ones
EXACT_LIB_VERSIONS: bool = False

CHOOSE_HOST_WITH_MORE_LIBS: bool = False

MAX_LOCAL_PROCESSES: int = 0

USE_CXX_M: bool = True
