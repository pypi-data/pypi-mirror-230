# builtin imports
import logging
from pathlib import Path
import stat
import threading
import time
import tempfile
import hashlib
from typing import List, Union


# Pastis & triton imports
from libpastis import ClientAgent, BinaryPackage, SASTReport
from libpastis.types import CheckMode, CoverageMode, ExecMode, FuzzingEngineInfo, SeedInjectLoc, SeedType, State, \
                            LogLevel, AlertData, FuzzMode

# Local imports
import pastishf
from pastishf.replay import Replay
from pastishf.honggfuzz import HonggfuzzProcess
from pastishf.workspace import Workspace


# Inotify logs are very talkative, set them to ERROR
for logger in (logging.getLogger(x) for x in ["watchdog.observers.inotify_buffer", 'watchdog.observers', "watchdog"]):
    logger.setLevel(logging.ERROR)


class HonggfuzzDriver:

    def __init__(self, agent: ClientAgent, telemetry_frequency: int = 30):

        # Internal objects
        self._agent = agent
        self.workspace = Workspace()
        self.honggfuzz = HonggfuzzProcess()

        # Parameters received through start_received
        self.__exec_mode = None   # SINGLE_RUN, PERSISTENT
        self.__check_mode = None  # CHECK_ALL, ALERT_ONLY
        self.__seed_inj = None    # STDIN or ARGV
        self.__report = None      # SAST report if provided

        # Target data
        self.__package = None
        self.__target_args = None  # Kept for replay

        self.__setup_agent()

        # Configure hookds on workspace
        self.workspace.add_creation_hook(self.workspace.corpus_dir, self.__send_seed)
        self.workspace.add_creation_hook(self.workspace.crash_dir, self.__send_crash)
        self.workspace.add_file_modification_hook(self.workspace.stats_dir, self.__send_telemetry)

        # Telemetry frequency
        self._tel_frequency = telemetry_frequency
        self._tel_last = time.time()

        # Runtime data
        self._tot_seeds = 0
        self._seed_recvs = set()  # Seed received to make sure NOT to send them back

        # Variables for replay
        self._replay_thread = None
        self._queue_to_send = []
        self._started = False

    @staticmethod
    def hash_seed(seed: bytes):
        return hashlib.md5(seed).hexdigest()

    def start(self, package: BinaryPackage, argv: List[str], exmode: ExecMode, fuzzmode: FuzzMode,
              seed_inj: SeedInjectLoc, engine_args: str):
        # Write target to disk.
        self.__package = package
        self.__target_args = argv

        self.workspace.start()  # Start looking at directories

        logging.info("Start process")
        if not self.honggfuzz.start(str(self.__package.executable_path.absolute()),
                             argv,
                             self.workspace,
                             exmode,
                             fuzzmode,
                             seed_inj == SeedInjectLoc.STDIN,
                             engine_args,
                             str(package.dictionary.absolute()) if package.dictionary else None):
            self._agent.send_log(LogLevel.ERROR, "Cannot start target")
        self._started = True

        # Start the replay worker (note that the queue might already have started to be filled by agent thread)
        self._replay_thread = threading.Thread(target=self.replay_worker, daemon=True)
        self._replay_thread.start()

    def stop(self):
        self.honggfuzz.stop()
        self.workspace.stop()
        self._started = False  # should stop the replay thread

    def replay_worker(self):
        while True:
            if not self._started:
                break  # Break when the fuzzer stops
            if self._queue_to_send:
                filename, res = self._queue_to_send.pop(0)
                if not self.__check_seed_alert(filename, is_crash=res):
                    break
            time.sleep(0.05)

    @property
    def started(self):
        return self._started

    def add_seed(self, seed: bytes):
        seed_path = self.workspace.dynamic_input_dir / f"seed-{hashlib.md5(seed).hexdigest()}"
        seed_path.write_bytes(seed)

    def init_agent(self, remote: str = "localhost", port: int = 5555):
        self._agent.register_start_callback(self.start_received)  # Register start because launched manually (not by pastisd)
        self._agent.connect(remote, port)
        self._agent.start()
        # Send initial HELLO message, whick will make the Broker send the START message.
        self._agent.send_hello([FuzzingEngineInfo("HONGGFUZZ", pastishf.__version__, "hfbroker")])

    def run(self):
        self.honggfuzz.wait()

    def __setup_agent(self):
        # Register callbacks.
        self._agent.register_seed_callback(self.__seed_received)
        self._agent.register_stop_callback(self.__stop_received)

    def __send_seed(self, filename: Path):
        self.__send(filename, SeedType.INPUT)

    def __send_crash(self, filename: Path):
        self.__send(filename, SeedType.CRASH)

    def __send(self, filename: Path, typ: SeedType):
        self._tot_seeds += 1
        file = Path(filename)
        raw = file.read_bytes()
        h = self.hash_seed(raw)
        logging.debug(f'[{typ.name}] Sending new: {h} [{self._tot_seeds}]')
        if h not in self._seed_recvs:
            self._agent.send_seed(typ, raw)
        else:
            logging.info("seed (previously sent) do not send it back")
        self._queue_to_send.append((filename, True if typ == SeedType.CRASH else False))

    def __check_seed_alert(self, filename: Path, is_crash: bool) -> bool:
        p = Path(filename)
        # Only rerun the seed if in alert only mode and a SAST report was provided
        if self.__check_mode == CheckMode.ALERT_ONLY and self.__report:

            # Rerun the program with the seed
            run = Replay.run(self.__package.executable_path.absolute(), self.__target_args, stdin_file=filename, timeout=5, cwd=str(self.workspace.target_dir))

            if run.is_hf_iter_crash():
                self.dual_log(LogLevel.ERROR, f"Disable replay engine (because code uses HF_ITER)")
                return False

            # Iterate all covered alerts
            for id in run.alert_covered:
                alert = self.__report.get_alert(id)
                if not alert.covered:
                    alert.covered = True
                    logging.info(f"New alert covered {alert} [{alert.id}]")
                    self._agent.send_alert_data(AlertData(alert.id, alert.covered, False, p.read_bytes()))

            # Check if the target has crashed and if so tell the broker which one
            if run.has_crashed() or run.is_asan_without_crash():  # Also consider ASAN warning as detection
                if not run.crashing_id:
                    self.dual_log(LogLevel.WARNING, f"Crash on {filename.name} but can't link it to a SAST alert")
                else:
                    alert = self.__report.get_alert(run.crashing_id)
                    if not alert.validated:
                        alert.validated = True
                        bugt, aline = run.asan_info()
                        self.dual_log(LogLevel.INFO, f"Honggfuzz new alert validated {alert} [{alert.id}] ({aline})  (asan no crash: {run.is_asan_without_crash()})")
                        self._agent.send_alert_data(AlertData(alert.id, alert.covered, alert.validated, p.read_bytes()))
            else:
                if is_crash:
                    self.dual_log(LogLevel.WARNING, f"crash not reproducible by rerunning seed: {filename.name}")

            if run.has_hanged():  # Honggfuzz does not stores 'hangs' it will have been sent as corpus or crash
                self.dual_log(LogLevel.WARNING, f"Seed {filename} was hanging in replay")
        return True

    def __send_telemetry(self, filename: Path):
        now = time.time()
        if now < (self._tel_last + self._tel_frequency):
            return
        self._tel_last = now

        logging.debug(f'[TELEMETRY] Stats file updated: {filename}')

        with open(filename, 'r') as stats_file:
            try:
                stats = stats_file.readlines()[-1]

                if not stats or stats.startswith("#"):
                    return

                stats = stats.split(',')

                # Stats format:
                #   unix_time, last_cov_update, total_exec, exec_per_sec,
                #   crashes, unique_crashes, hangs, edge_cov, block_cov
                state = State.RUNNING
                last_cov_update = int(stats[1])
                total_exec = int(stats[2])
                exec_per_sec = int(stats[3])
                timeout = int(stats[6])             # aka hangs.
                coverage_edge = int(stats[7])       # aka edge_cov.
                coverage_block = int(stats[8])      # aka block_cov.

                # NOTE: `cycle` and `coverage_path` does not apply for Honggfuzz.
                self._agent.send_telemetry(state=state,
                                           exec_per_sec=exec_per_sec,
                                           total_exec=total_exec,
                                           timeout=timeout,
                                           coverage_block=coverage_block,
                                           coverage_edge=coverage_edge,
                                           last_cov_update=last_cov_update)
            except:
                logging.error(f'Error retrieving stats!')

    def start_received(self, fname: str, binary: bytes, engine: FuzzingEngineInfo, exmode: ExecMode, fuzzmode: FuzzMode, chkmode: CheckMode,
                       _: CoverageMode, seed_inj: SeedInjectLoc, engine_args: str, argv: List[str], sast_report: str = None):
        logging.info(f"[START] bin:{fname} engine:{engine.name} exmode:{exmode.name} fuzzmode:{fuzzmode.name} seedloc:{seed_inj.name} chk:{chkmode.name}")
        if self.started:
            self._agent.send_log(LogLevel.CRITICAL, "Instance already started!")
            return

        if engine.name != "HONGGFUZZ":
            logging.error(f"Wrong fuzzing engine received {engine.name} while I am Honggfuzz")
            self._agent.send_log(LogLevel.ERROR, f"Invalid fuzzing engine received {engine.name} can't do anything")
            return
        if engine.version != pastishf.__version__:
            logging.error(f"Wrong fuzzing engine version {engine.version} received")
            self._agent.send_log(LogLevel.ERROR, f"Invalid fuzzing engine version {engine.version} do nothing")
            return

        # Retrieve package out of the binary received
        try:
            package = BinaryPackage.from_binary(fname, binary, self.workspace.target_dir)
        except FileNotFoundError:
            logging.error("Invalid package received")
            return

        if sast_report:
            logging.info("Loading SAST report")
            self.__report = SASTReport.from_json(sast_report)

        self.__check_mode = chkmode  # CHECK_ALL, ALERT_ONLY

        self.start(package, argv, exmode, fuzzmode, seed_inj, engine_args)

    def __seed_received(self, typ: SeedType, seed: bytes):
        h = self.hash_seed(seed)
        logging.info(f"[SEED] received  {h} ({typ.name})")
        self._seed_recvs.add(h)

        # HACK: Maybe doing it more nicely ?
        if len(seed) > 1024*8: # HF_INPUT_DEFAULT_SIZE
            logging.debug(f"crop seed {h} received to fit 8Kb")
            seed = seed[:1024*8]

        self.add_seed(seed)

    def __stop_received(self):
        logging.info(f"[STOP]")

        self.stop()

    def dual_log(self, level: LogLevel, message: str) -> None:
        """
        Helper function to log message both in the local log system and also
        to the broker.

        :param level: LogLevel message type
        :param message: string message to log
        :return: None
        """
        mapper = {LogLevel.DEBUG: "debug",
                  LogLevel.INFO: "info",
                  LogLevel.CRITICAL: "critical",
                  LogLevel.WARNING: "warning",
                  LogLevel.ERROR: "error"}
        log_f = getattr(logging, mapper[level])
        log_f(message)
        self._agent.send_log(level, message)

    def add_initial_seed(self, file: Union[str, Path]):
        p = Path(file)
        logging.info(f"add initial seed {file.name}")
        # Write seed to disk.
        seed_path = self.workspace.input_dir / p.name
        seed_path.write_bytes(p.read_bytes())

    @staticmethod
    def honggfuzz_available() -> bool:
        return HonggfuzzProcess.hfuzz_environ_check()
