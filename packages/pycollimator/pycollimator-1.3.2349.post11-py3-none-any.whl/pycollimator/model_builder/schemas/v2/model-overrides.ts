// TYPE: ModelOverrides
// The first line must contain the name of the top level schema.
//
// Description: Block overrides schema
//
// This schema is used to override the default values of blocks in a model.

// Using name paths instead of UUID paths makes it much easier to work with
// from pycollimator: users can literally just write the name of the signals
// they want. UUIDs would be more robust but for now we base simulations around
// paths by name.

export interface ModelOverrides {
  block_overrides?: BlockOverride[];
  recorded_signals?: RecordedSignals;
  ensemble_config?: EnsembleConfig;
}

// EnsembleConfig defines how to run an ensemble simulation, which is basically
// a (multiple) parameter sweep batch of "child" simulations.
// FIXME: EnsembleConfig does not belong *inside* ModelOverrides, rather
// EnsembleConfig may contain ModelOverrides (eg. for recorded signals). But
// this was the easiest and least intrusive change to pass the request from the
// frontend to simworker.
// Another thing to consider is that ensemble sims should be able to run
// parameter sweeps on block or submodel parameter values (at the instance
// level), not just model parameters. This is close to what BlockOverride
// does, except those need to specify a sweep.
export interface EnsembleConfig {
  sweep_strategy: 'all_combinations';
  model_parameter_sweeps: ParameterSweep[];
}

export interface RecordedSignals {
  signal_ids: SignalID[];
}

// Full human-readable path to the port like:
// - Submodel_1.Group_2.Block_3.out_4
// - Submodel_1.Group_2.Outport_5
// Corresponds to 'signal_id' in toc.json
export type SignalID = string;

export interface BlockOverride {
  path: string;
  parameters?: ParameterOverrides;
  outputs?: PortOverrides;
}

export interface ParameterOverrides {
  [k: string]: ParameterValueOverride;
}

export interface ParameterValueOverride {
  value: string;
  is_string?: boolean;
}

export interface PortOverrides {
  [path: string]: PortOverride;
}

export interface PortOverride {
  parameters?: ParameterOverrides;
}

export interface ParameterSweep {
  parameter_name: string;
  sweep_expression: string;
  default_value: string;
}

// TODO
// export interface BlockParameterSweep {
//   block_path: string;
//   parameter_name: string;
//   values_expression: string;
//   default_value: string;
// }
