# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: patient_info.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12patient_info.proto\x12\npitom_data\"\xbd\x02\n\x07Patient\x12\x14\n\x0cproject_type\x18\x01 \x01(\t\x12\x12\n\npatient_id\x18\x02 \x01(\t\x12\x37\n\rconversations\x18\x03 \x03(\x0b\x32 .pitom_data.Patient.Conversation\x1a+\n\tElectrode\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08\x63hecksum\x18\x02 \x01(\t\x1aZ\n\x05\x44\x61tum\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08\x63hecksum\x18\x02 \x01(\t\x12\x31\n\nelectrodes\x18\x03 \x03(\x0b\x32\x1d.pitom_data.Patient.Electrode\x1a\x46\n\x0c\x43onversation\x12\x0c\n\x04name\x18\x01 \x01(\t\x12(\n\x05\x64\x61tum\x18\x02 \x01(\x0b\x32\x19.pitom_data.Patient.Datum\"4\n\x0bPatientInfo\x12%\n\x08patients\x18\x01 \x03(\x0b\x32\x13.pitom_data.Patientb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'patient_info_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PATIENT']._serialized_start=35
  _globals['_PATIENT']._serialized_end=352
  _globals['_PATIENT_ELECTRODE']._serialized_start=145
  _globals['_PATIENT_ELECTRODE']._serialized_end=188
  _globals['_PATIENT_DATUM']._serialized_start=190
  _globals['_PATIENT_DATUM']._serialized_end=280
  _globals['_PATIENT_CONVERSATION']._serialized_start=282
  _globals['_PATIENT_CONVERSATION']._serialized_end=352
  _globals['_PATIENTINFO']._serialized_start=354
  _globals['_PATIENTINFO']._serialized_end=406
# @@protoc_insertion_point(module_scope)
