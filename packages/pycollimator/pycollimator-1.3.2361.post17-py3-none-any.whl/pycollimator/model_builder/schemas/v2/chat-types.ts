/* tslint:disable */

export enum FinishReason {
  Stop = 'stop',
  Length = 'length',
  FunctionCall = 'function_call',
  ContentFilter = 'content_filter',
}

export enum ChatMessageRole {
  System = 'system',
  User = 'user',
  Assistant = 'assistant',
  Function = 'function',
}

export interface FunctionCall {
  name: string;
  arguments: string;
}

export type GptFunctionName =
  | 'run_simulation'
  | 'validate_user_model'
  | 'execute_python'
  | 'build_model'
  | 'build_group'
  | 'build_submodel'
  | 'plot'
  | 'get_user_model'
  | 'search_blocks'
  | 'add_parameter'
  | 'add_block'
  | 'remove_block'
  | 'add_link'
  | 'remove_link'
  | 'clear_model';

export interface ChatMessage {
  role: ChatMessageRole;
  content: string;

  originalUserContent?: string;
  automaticMessageContent?: string;

  functionName?: GptFunctionName;
  functionArgs?: string;
  functionResult?: string;
  functionHasError?: boolean;
}

export interface ChatCompleteRequestPayload {
  messages: ChatMessage[];
  temperature: number;
  model: string;
}

export interface ChatCompleteResponsePayload {
  streamUuid: string;
  content?: string;
  finishReason?: FinishReason;
  functionCall?: FunctionCall;
}

export enum ChatCompleteErrorTypes {
  ChatNotAvailable = 'CHAT_NOT_AVAILABLE',
  JsonError = 'JSON_ERROR',
  OpenAiKeyNotFound = 'OPENAI_KEY_NOT_FOUND',
  ChatCallCountExceeded = 'CHAT_CALL_COUNT_EXCEEDED',
  ChatInternalError = 'CHAT_INTERNAL_ERROR',
}

export interface ChatCompleteErrorPayload {
  error: string;
  type: ChatCompleteErrorTypes;
}

export interface Plot {
  id: string;
  value: string; // b64 encoded png
}

// snake_case because it's used in the API
export interface ChatSession {
  session_id: string;
  messages: ChatMessage[];
  plots?: Plot[];
}
