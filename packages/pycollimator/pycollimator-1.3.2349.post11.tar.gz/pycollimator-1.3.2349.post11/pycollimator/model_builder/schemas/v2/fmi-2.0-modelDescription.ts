/**
Hand-written typescript definition of the fmi-2.0-modelDescription schema.

This file is the source of truth for Go types and the JSON schemas used in the
openapi definition.
*/

// Reference for XML
// https://fmi-standard.org/ --> 2.0.4
// https://github.com/modelica/fmi-standard/releases/download/v2.0.4/FMI-Specification-2.0.4.pdf

/**
 * @minimum 0
 * @TJS-type integer
 */
type Size = number;

export interface LogCategory {
  name: string;
  description?: string;
}

/** @default "local" */
export type Causality =
  | 'parameter'
  | 'calculatedParameter'
  | 'input'
  | 'output'
  | 'local'
  | 'independent';

/** @default "continuous" */
export type Variability =
  | 'constant'
  | 'fixed'
  | 'tunable'
  | 'discrete'
  | 'continuous';

/** @default "continuous" */
export type Initial = 'exact' | 'approx' | 'calculated';

/**
 * Schema for our modelDescription.json converted from FMI modelDescription.xml
 * generated with `typescript-json-schema fmi-2.0-modelDescription.ts fmiModelDescription > fmi-2.0-modelDescription.schema.json`
 */
export interface fmiModelDescription {
  fmiVersion: '2.0';
  modelName: string;
  description?: string;
  generationTool: string;
  guid: string;

  /**
   * @minimum 0
   * @TJS-type integer
   */
  numberOfEventIndicators: number;
  ModelExchange?: {
    modelIdentifier: string;
    canNotUseMemoryManagementFunctions: boolean;
    canGetAndSetFMUstate: boolean;
    canSerializeFMUstate: boolean;
  };
  CoSimulation?: {
    modelIdentifier: string;
    canHandleVariableCommunicationStepSize: boolean;
    canNotUseMemoryManagementFunctions: boolean;
    canGetAndSetFMUstate: boolean;
    canSerializeFMUstate: boolean;
  };
  LogCategories?: LogCategory[];
  DefaultExperiment?: {
    startTime?: number;
    stopTime?: number;
    tolerance?: number;
    stepSize?: number;
  };
  ModelVariables: ScalarVariable[];
}

// See page 56.
interface ScalarVariable {
  name: string;
  cml_name: string; // mangled and guaranteed to be unique
  valueReference: Size; // integer index
  causality?: Causality;
  variability?: Variability;
  initial?: Initial;
  description?: string;
  Real?: ScalarVariableReal;
  Integer?: ScalarVariableInteger;
  Boolean?: ScalarVariableBoolean;
  String?: ScalarVariableString;
  Enumeration?: ScalarVariableEnumeration;
}

interface ScalarVariableCommon extends Record<string, unknown> {
  quantity?: string;
  unit?: string;
  displayUnit?: string;
  relativeQuantity?: boolean;
  reinit?: boolean;
}

interface ScalarVariableReal extends ScalarVariableCommon {
  min?: number;
  max?: number;
  start?: number;
  nominal?: number;
  unbounded?: boolean;
}

interface ScalarVariableInteger extends ScalarVariableCommon {
  min?: number;
  max?: number;
  start?: number;
}

interface ScalarVariableBoolean extends ScalarVariableCommon {
  start?: boolean;
}

interface ScalarVariableString extends ScalarVariableCommon {
  start?: string;
}

interface ScalarVariableEnumeration extends ScalarVariableCommon {
  Items?: ScalarVariableEnumerationItem[];
}

interface ScalarVariableEnumerationItem {
  name: string;
  value: number;
  description?: string;
}
