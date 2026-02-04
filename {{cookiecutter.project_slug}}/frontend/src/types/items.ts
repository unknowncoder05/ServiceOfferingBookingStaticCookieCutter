/**
 * Item types - TypeScript interfaces for the Items module.
 *
 * This module demonstrates common type patterns:
 * - Interface definitions for API responses
 * - Status enums
 * - State interface for Redux
 */

export type ItemStatus = 'draft' | 'active' | 'archived';

export interface Item {
  id: number;
  name: string;
  description: string;
  status: ItemStatus;
  owner: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ItemListItem {
  id: number;
  name: string;
  status: ItemStatus;
  owner_name: string;
  created_at: string;
}

export interface CreateItemRequest {
  name: string;
  description?: string;
  status?: ItemStatus;
  metadata?: Record<string, unknown>;
}

export interface UpdateItemRequest {
  name?: string;
  description?: string;
  status?: ItemStatus;
  metadata?: Record<string, unknown>;
}

export interface ItemsState {
  items: ItemListItem[];
  selectedItem: Item | null;
  isLoading: boolean;
  error: string | null;
}
