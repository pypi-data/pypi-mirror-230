// WebSocketMessage
/* tslint:disable */

import { WebSocketMessageType } from './websocket-message-type';

export interface WebSocketMessage {
  id: string;
  type: WebSocketMessageType;
  payload: unknown;
  jwt?: string;
}
