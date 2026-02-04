/**
 * Items Redux slice - State management for the Items module.
 *
 * This module demonstrates Redux Toolkit patterns:
 * - createSlice for defining reducers
 * - createAsyncThunk for API calls
 * - Handling loading and error states
 * - CRUD operations with async thunks
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import {
  Item,
  ItemListItem,
  ItemsState,
  CreateItemRequest,
  UpdateItemRequest,
} from '../types/items';
import apiService from '../services/api';

const initialState: ItemsState = {
  items: [],
  selectedItem: null,
  isLoading: false,
  error: null,
};

// Async thunks for API operations
export const fetchItems = createAsyncThunk(
  'items/fetchItems',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.getItems();
      return response.data;
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to fetch items';
      return rejectWithValue(errorMessage);
    }
  }
);

export const fetchItem = createAsyncThunk(
  'items/fetchItem',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await apiService.getItem(id);
      return response.data;
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to fetch item';
      return rejectWithValue(errorMessage);
    }
  }
);

export const createItem = createAsyncThunk(
  'items/createItem',
  async (data: CreateItemRequest, { rejectWithValue }) => {
    try {
      const response = await apiService.createItem(data);
      return response.data;
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.name?.[0] ||
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to create item';
      return rejectWithValue(errorMessage);
    }
  }
);

export const updateItem = createAsyncThunk(
  'items/updateItem',
  async ({ id, data }: { id: number; data: UpdateItemRequest }, { rejectWithValue }) => {
    try {
      const response = await apiService.updateItem(id, data);
      return response.data;
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to update item';
      return rejectWithValue(errorMessage);
    }
  }
);

export const deleteItem = createAsyncThunk(
  'items/deleteItem',
  async (id: number, { rejectWithValue }) => {
    try {
      await apiService.deleteItem(id);
      return id;
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to delete item';
      return rejectWithValue(errorMessage);
    }
  }
);

export const archiveItem = createAsyncThunk(
  'items/archiveItem',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await apiService.archiveItem(id);
      return response.data;
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to archive item';
      return rejectWithValue(errorMessage);
    }
  }
);

export const activateItem = createAsyncThunk(
  'items/activateItem',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await apiService.activateItem(id);
      return response.data;
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to activate item';
      return rejectWithValue(errorMessage);
    }
  }
);

const itemsSlice = createSlice({
  name: 'items',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearSelectedItem: (state) => {
      state.selectedItem = null;
    },
    setSelectedItem: (state, action: PayloadAction<Item>) => {
      state.selectedItem = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch items
      .addCase(fetchItems.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchItems.fulfilled, (state, action) => {
        state.isLoading = false;
        state.items = action.payload;
        state.error = null;
      })
      .addCase(fetchItems.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch single item
      .addCase(fetchItem.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchItem.fulfilled, (state, action) => {
        state.isLoading = false;
        state.selectedItem = action.payload;
        state.error = null;
      })
      .addCase(fetchItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Create item
      .addCase(createItem.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createItem.fulfilled, (state, action) => {
        state.isLoading = false;
        // Add to list (convert full item to list item format)
        const newItem: ItemListItem = {
          id: action.payload.id,
          name: action.payload.name,
          status: action.payload.status,
          owner_name: `${action.payload.owner.first_name} ${action.payload.owner.last_name}`,
          created_at: action.payload.created_at,
        };
        state.items.unshift(newItem);
        state.error = null;
      })
      .addCase(createItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Update item
      .addCase(updateItem.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateItem.fulfilled, (state, action) => {
        state.isLoading = false;
        state.selectedItem = action.payload;
        // Update in list
        const index = state.items.findIndex((item) => item.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = {
            id: action.payload.id,
            name: action.payload.name,
            status: action.payload.status,
            owner_name: `${action.payload.owner.first_name} ${action.payload.owner.last_name}`,
            created_at: action.payload.created_at,
          };
        }
        state.error = null;
      })
      .addCase(updateItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Delete item
      .addCase(deleteItem.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteItem.fulfilled, (state, action) => {
        state.isLoading = false;
        state.items = state.items.filter((item) => item.id !== action.payload);
        if (state.selectedItem?.id === action.payload) {
          state.selectedItem = null;
        }
        state.error = null;
      })
      .addCase(deleteItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Archive item
      .addCase(archiveItem.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(archiveItem.fulfilled, (state, action) => {
        state.isLoading = false;
        // Update in list
        const index = state.items.findIndex((item) => item.id === action.payload.id);
        if (index !== -1) {
          state.items[index].status = 'archived';
        }
        if (state.selectedItem?.id === action.payload.id) {
          state.selectedItem = action.payload;
        }
        state.error = null;
      })
      .addCase(archiveItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Activate item
      .addCase(activateItem.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(activateItem.fulfilled, (state, action) => {
        state.isLoading = false;
        // Update in list
        const index = state.items.findIndex((item) => item.id === action.payload.id);
        if (index !== -1) {
          state.items[index].status = 'active';
        }
        if (state.selectedItem?.id === action.payload.id) {
          state.selectedItem = action.payload;
        }
        state.error = null;
      })
      .addCase(activateItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, clearSelectedItem, setSelectedItem } = itemsSlice.actions;
export default itemsSlice.reducer;
