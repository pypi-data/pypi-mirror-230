# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: message.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rmessage.proto\x12\tlibpastis\"@\n\rFuzzingEngine\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x12\x10\n\x08pymodule\x18\x03 \x01(\t\"x\n\x0cInputSeedMsg\x12\x0c\n\x04seed\x18\x01 \x01(\x0c\x12.\n\x04type\x18\x02 \x01(\x0e\x32 .libpastis.InputSeedMsg.SeedType\"*\n\x08SeedType\x12\t\n\x05INPUT\x10\x00\x12\t\n\x05\x43RASH\x10\x01\x12\x08\n\x04HANG\x10\x02\"\x17\n\x07\x44\x61taMsg\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t\"\xde\x04\n\x08StartMsg\x12\x17\n\x0f\x62inary_filename\x18\x01 \x01(\t\x12\x0e\n\x06\x62inary\x18\x02 \x01(\x0c\x12\x13\n\x0bsast_report\x18\x03 \x01(\x0c\x12(\n\x06\x65ngine\x18\x04 \x01(\x0b\x32\x18.libpastis.FuzzingEngine\x12/\n\texec_mode\x18\x05 \x01(\x0e\x32\x1c.libpastis.StartMsg.ExecMode\x12/\n\tfuzz_mode\x18\x06 \x01(\x0e\x32\x1c.libpastis.StartMsg.FuzzMode\x12\x31\n\ncheck_mode\x18\x07 \x01(\x0e\x32\x1d.libpastis.StartMsg.CheckMode\x12\x15\n\rcoverage_mode\x18\x08 \x01(\t\x12\x38\n\rseed_location\x18\t \x01(\x0e\x32!.libpastis.StartMsg.SeedInjectLoc\x12\x13\n\x0b\x65ngine_args\x18\n \x01(\t\x12\x14\n\x0cprogram_argv\x18\x0b \x03(\t\":\n\x08\x45xecMode\x12\r\n\tAUTO_EXEC\x10\x00\x12\x0f\n\x0bSINGLE_EXEC\x10\x01\x12\x0e\n\nPERSISTENT\x10\x02\"<\n\x08\x46uzzMode\x12\r\n\tAUTO_FUZZ\x10\x00\x12\x10\n\x0cINSTRUMENTED\x10\x01\x12\x0f\n\x0b\x42INARY_ONLY\x10\x02\"9\n\tCheckMode\x12\r\n\tCHECK_ALL\x10\x00\x12\x0e\n\nALERT_ONLY\x10\x01\x12\r\n\tALERT_ONE\x10\x02\"$\n\rSeedInjectLoc\x12\t\n\x05STDIN\x10\x00\x12\x08\n\x04\x41RGV\x10\x01\"\t\n\x07StopMsg\"\xf1\x01\n\x08HelloMsg\x12.\n\x0c\x61rchitecture\x18\x01 \x01(\x0e\x32\x18.libpastis.HelloMsg.Arch\x12\x0c\n\x04\x63pus\x18\x02 \x01(\r\x12\x0e\n\x06memory\x18\x03 \x01(\x04\x12)\n\x07\x65ngines\x18\x04 \x03(\x0b\x32\x18.libpastis.FuzzingEngine\x12\x10\n\x08hostname\x18\x05 \x01(\t\x12%\n\x08platform\x18\x06 \x01(\x0e\x32\x13.libpastis.Platform\"3\n\x04\x41rch\x12\x07\n\x03X86\x10\x00\x12\n\n\x06X86_64\x10\x01\x12\t\n\x05\x41RMV7\x10\x02\x12\x0b\n\x07\x41\x41RCH64\x10\x03\"\x8b\x01\n\x06LogMsg\x12\x0f\n\x07message\x18\x01 \x01(\t\x12)\n\x05level\x18\x02 \x01(\x0e\x32\x1a.libpastis.LogMsg.LogLevel\"E\n\x08LogLevel\x12\t\n\x05\x44\x45\x42UG\x10\x00\x12\x08\n\x04INFO\x10\x01\x12\x0b\n\x07WARNING\x10\x02\x12\t\n\x05\x45RROR\x10\x03\x12\x0c\n\x08\x43RITICAL\x10\x04\"\xfe\x01\n\x0cTelemetryMsg\x12\x1f\n\x05state\x18\x01 \x01(\x0e\x32\x10.libpastis.State\x12\x14\n\x0c\x65xec_per_sec\x18\x02 \x01(\r\x12\x12\n\ntotal_exec\x18\x03 \x01(\x04\x12\r\n\x05\x63ycle\x18\x04 \x01(\r\x12\x0f\n\x07timeout\x18\x05 \x01(\r\x12\x16\n\x0e\x63overage_block\x18\x06 \x01(\r\x12\x15\n\rcoverage_edge\x18\x07 \x01(\r\x12\x15\n\rcoverage_path\x18\x08 \x01(\r\x12\x17\n\x0flast_cov_update\x18\t \x01(\x04\x12\x11\n\tcpu_usage\x18\n \x01(\x02\x12\x11\n\tmem_usage\x18\x0b \x01(\x02\"\x16\n\x14StopCoverageCriteria\"\xf8\x02\n\x0b\x45nvelopeMsg\x12,\n\tinput_msg\x18\x01 \x01(\x0b\x32\x17.libpastis.InputSeedMsgH\x00\x12&\n\x08\x64\x61ta_msg\x18\x02 \x01(\x0b\x32\x12.libpastis.DataMsgH\x00\x12(\n\tstart_msg\x18\x03 \x01(\x0b\x32\x13.libpastis.StartMsgH\x00\x12&\n\x08stop_msg\x18\x04 \x01(\x0b\x32\x12.libpastis.StopMsgH\x00\x12(\n\thello_msg\x18\x05 \x01(\x0b\x32\x13.libpastis.HelloMsgH\x00\x12$\n\x07log_msg\x18\x06 \x01(\x0b\x32\x11.libpastis.LogMsgH\x00\x12\x30\n\rtelemetry_msg\x18\x07 \x01(\x0b\x32\x17.libpastis.TelemetryMsgH\x00\x12\x38\n\rstop_crit_msg\x18\x08 \x01(\x0b\x32\x1f.libpastis.StopCoverageCriteriaH\x00\x42\x05\n\x03msg*\x1e\n\x05State\x12\x0b\n\x07RUNNING\x10\x00\x12\x08\n\x04IDLE\x10\x01*L\n\x08Platform\x12\x07\n\x03\x41NY\x10\x00\x12\t\n\x05LINUX\x10\x01\x12\x0b\n\x07WINDOWS\x10\x02\x12\t\n\x05MACOS\x10\x03\x12\x0b\n\x07\x41NDROID\x10\x04\x12\x07\n\x03IOS\x10\x05\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'message_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _STATE._serialized_start=1907
  _STATE._serialized_end=1937
  _PLATFORM._serialized_start=1939
  _PLATFORM._serialized_end=2015
  _FUZZINGENGINE._serialized_start=28
  _FUZZINGENGINE._serialized_end=92
  _INPUTSEEDMSG._serialized_start=94
  _INPUTSEEDMSG._serialized_end=214
  _INPUTSEEDMSG_SEEDTYPE._serialized_start=172
  _INPUTSEEDMSG_SEEDTYPE._serialized_end=214
  _DATAMSG._serialized_start=216
  _DATAMSG._serialized_end=239
  _STARTMSG._serialized_start=242
  _STARTMSG._serialized_end=848
  _STARTMSG_EXECMODE._serialized_start=631
  _STARTMSG_EXECMODE._serialized_end=689
  _STARTMSG_FUZZMODE._serialized_start=691
  _STARTMSG_FUZZMODE._serialized_end=751
  _STARTMSG_CHECKMODE._serialized_start=753
  _STARTMSG_CHECKMODE._serialized_end=810
  _STARTMSG_SEEDINJECTLOC._serialized_start=812
  _STARTMSG_SEEDINJECTLOC._serialized_end=848
  _STOPMSG._serialized_start=850
  _STOPMSG._serialized_end=859
  _HELLOMSG._serialized_start=862
  _HELLOMSG._serialized_end=1103
  _HELLOMSG_ARCH._serialized_start=1052
  _HELLOMSG_ARCH._serialized_end=1103
  _LOGMSG._serialized_start=1106
  _LOGMSG._serialized_end=1245
  _LOGMSG_LOGLEVEL._serialized_start=1176
  _LOGMSG_LOGLEVEL._serialized_end=1245
  _TELEMETRYMSG._serialized_start=1248
  _TELEMETRYMSG._serialized_end=1502
  _STOPCOVERAGECRITERIA._serialized_start=1504
  _STOPCOVERAGECRITERIA._serialized_end=1526
  _ENVELOPEMSG._serialized_start=1529
  _ENVELOPEMSG._serialized_end=1905
# @@protoc_insertion_point(module_scope)
