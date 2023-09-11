# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: qwak/feature_store/features/execution.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n+qwak/feature_store/features/execution.proto\x12%qwak.feature.store.features.execution\"\xcb\x01\n\rExecutionSpec\x12R\n\x10\x63luster_template\x18\x01 \x01(\x0e\x32\x36.qwak.feature.store.features.execution.ClusterTemplateH\x00\x12^\n\x16resource_configuration\x18\x02 \x01(\x0b\x32<.qwak.feature.store.features.execution.ResourceConfigurationH\x00\x42\x06\n\x04spec\"\xcf\x03\n\x16StreamingExecutionSpec\x12Y\n\x17online_cluster_template\x18\x01 \x01(\x0e\x32\x36.qwak.feature.store.features.execution.ClusterTemplateH\x00\x12\x65\n\x1donline_resource_configuration\x18\x02 \x01(\x0b\x32<.qwak.feature.store.features.execution.ResourceConfigurationH\x00\x12Z\n\x18offline_cluster_template\x18\x03 \x01(\x0e\x32\x36.qwak.feature.store.features.execution.ClusterTemplateH\x01\x12\x66\n\x1eoffline_resource_configuration\x18\x04 \x01(\x0b\x32<.qwak.feature.store.features.execution.ResourceConfigurationH\x01\x42\x16\n\x14online_resource_specB\x17\n\x15offline_resource_spec\"\xe5\x01\n\x15\x42\x61\x63kfillExecutionSpec\x12R\n\x10\x63luster_template\x18\x01 \x01(\x0e\x32\x36.qwak.feature.store.features.execution.ClusterTemplateH\x00\x12^\n\x16resource_configuration\x18\x02 \x01(\x0b\x32<.qwak.feature.store.features.execution.ResourceConfigurationH\x00\x42\x18\n\x16\x62\x61\x63kfill_resource_spec\"\xbe\x01\n\x15ResourceConfiguration\x12\x15\n\rdriver_memory\x18\x01 \x01(\t\x12\x14\n\x0c\x64river_cores\x18\x02 \x01(\x05\x12\x19\n\x11initial_executors\x18\x03 \x01(\x05\x12\x15\n\rmin_executors\x18\x04 \x01(\x05\x12\x15\n\rmax_executors\x18\x05 \x01(\x05\x12\x17\n\x0f\x65xecutor_memory\x18\x06 \x01(\t\x12\x16\n\x0e\x65xecutor_cores\x18\x07 \x01(\x05*d\n\x0f\x43lusterTemplate\x12\t\n\x05SMALL\x10\x00\x12\n\n\x06MEDIUM\x10\x01\x12\t\n\x05LARGE\x10\x02\x12\n\n\x06XLARGE\x10\x03\x12\x0b\n\x07XXLARGE\x10\x04\x12\x0c\n\x08XXXLARGE\x10\x05\x12\x08\n\x04NANO\x10\x06\x42[\n&com.qwak.ai.feature.store.features.apiP\x01Z/qwak/featurestore/features;featurestorefeaturesb\x06proto3')

_CLUSTERTEMPLATE = DESCRIPTOR.enum_types_by_name['ClusterTemplate']
ClusterTemplate = enum_type_wrapper.EnumTypeWrapper(_CLUSTERTEMPLATE)
SMALL = 0
MEDIUM = 1
LARGE = 2
XLARGE = 3
XXLARGE = 4
XXXLARGE = 5
NANO = 6


_EXECUTIONSPEC = DESCRIPTOR.message_types_by_name['ExecutionSpec']
_STREAMINGEXECUTIONSPEC = DESCRIPTOR.message_types_by_name['StreamingExecutionSpec']
_BACKFILLEXECUTIONSPEC = DESCRIPTOR.message_types_by_name['BackfillExecutionSpec']
_RESOURCECONFIGURATION = DESCRIPTOR.message_types_by_name['ResourceConfiguration']
ExecutionSpec = _reflection.GeneratedProtocolMessageType('ExecutionSpec', (_message.Message,), {
  'DESCRIPTOR' : _EXECUTIONSPEC,
  '__module__' : 'qwak.feature_store.features.execution_pb2'
  # @@protoc_insertion_point(class_scope:qwak.feature.store.features.execution.ExecutionSpec)
  })
_sym_db.RegisterMessage(ExecutionSpec)

StreamingExecutionSpec = _reflection.GeneratedProtocolMessageType('StreamingExecutionSpec', (_message.Message,), {
  'DESCRIPTOR' : _STREAMINGEXECUTIONSPEC,
  '__module__' : 'qwak.feature_store.features.execution_pb2'
  # @@protoc_insertion_point(class_scope:qwak.feature.store.features.execution.StreamingExecutionSpec)
  })
_sym_db.RegisterMessage(StreamingExecutionSpec)

BackfillExecutionSpec = _reflection.GeneratedProtocolMessageType('BackfillExecutionSpec', (_message.Message,), {
  'DESCRIPTOR' : _BACKFILLEXECUTIONSPEC,
  '__module__' : 'qwak.feature_store.features.execution_pb2'
  # @@protoc_insertion_point(class_scope:qwak.feature.store.features.execution.BackfillExecutionSpec)
  })
_sym_db.RegisterMessage(BackfillExecutionSpec)

ResourceConfiguration = _reflection.GeneratedProtocolMessageType('ResourceConfiguration', (_message.Message,), {
  'DESCRIPTOR' : _RESOURCECONFIGURATION,
  '__module__' : 'qwak.feature_store.features.execution_pb2'
  # @@protoc_insertion_point(class_scope:qwak.feature.store.features.execution.ResourceConfiguration)
  })
_sym_db.RegisterMessage(ResourceConfiguration)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n&com.qwak.ai.feature.store.features.apiP\001Z/qwak/featurestore/features;featurestorefeatures'
  _CLUSTERTEMPLATE._serialized_start=1183
  _CLUSTERTEMPLATE._serialized_end=1283
  _EXECUTIONSPEC._serialized_start=87
  _EXECUTIONSPEC._serialized_end=290
  _STREAMINGEXECUTIONSPEC._serialized_start=293
  _STREAMINGEXECUTIONSPEC._serialized_end=756
  _BACKFILLEXECUTIONSPEC._serialized_start=759
  _BACKFILLEXECUTIONSPEC._serialized_end=988
  _RESOURCECONFIGURATION._serialized_start=991
  _RESOURCECONFIGURATION._serialized_end=1181
# @@protoc_insertion_point(module_scope)
