/**
 * ItemsPage - Main page for managing items.
 *
 * This component demonstrates:
 * - Page-level state management for modals
 * - Routing integration with useNavigate
 * - Composition of child components
 * - Modal pattern for forms
 */
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router-dom';
import { RootState, AppDispatch } from '../store';
import { fetchItem, clearSelectedItem } from '../store/itemsSlice';
import { ItemList, ItemForm } from '../components/items';

type ViewMode = 'list' | 'create' | 'edit' | 'view';

const ItemsPage: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { id } = useParams<{ id?: string }>();
  const { selectedItem, isLoading } = useSelector((state: RootState) => state.items);

  const [viewMode, setViewMode] = useState<ViewMode>('list');

  // Load item if ID is in URL
  useEffect(() => {
    if (id) {
      dispatch(fetchItem(parseInt(id, 10)));
      setViewMode('view');
    } else {
      dispatch(clearSelectedItem());
      setViewMode('list');
    }
  }, [id, dispatch]);

  const handleViewItem = (itemId: number) => {
    navigate(`/items/${itemId}`);
  };

  const handleCreateItem = () => {
    setViewMode('create');
  };

  const handleEditItem = () => {
    setViewMode('edit');
  };

  const handleFormSuccess = () => {
    setViewMode('list');
    navigate('/items');
  };

  const handleFormCancel = () => {
    if (viewMode === 'create') {
      setViewMode('list');
    } else {
      setViewMode('view');
    }
  };

  const handleBackToList = () => {
    dispatch(clearSelectedItem());
    navigate('/items');
  };

  // Render item detail view
  const renderItemDetail = () => {
    if (isLoading && !selectedItem) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    if (!selectedItem) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-500">Item not found</p>
          <button
            onClick={handleBackToList}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Back to Items
          </button>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{selectedItem.name}</h1>
            <span
              className={`inline-block mt-2 px-3 py-1 rounded-full text-sm font-medium ${
                selectedItem.status === 'active'
                  ? 'bg-green-100 text-green-800'
                  : selectedItem.status === 'archived'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {selectedItem.status.charAt(0).toUpperCase() + selectedItem.status.slice(1)}
            </span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleBackToList}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
            >
              Back
            </button>
            <button
              onClick={handleEditItem}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Edit
            </button>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-medium text-gray-500">Description</h3>
            <p className="mt-1 text-gray-900">
              {selectedItem.description || 'No description provided'}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Owner</h3>
              <p className="mt-1 text-gray-900">
                {selectedItem.owner.first_name} {selectedItem.owner.last_name}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Created</h3>
              <p className="mt-1 text-gray-900">
                {new Date(selectedItem.created_at).toLocaleString()}
              </p>
            </div>
          </div>

          {Object.keys(selectedItem.metadata).length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-500">Metadata</h3>
              <pre className="mt-1 p-3 bg-gray-50 rounded text-sm overflow-auto">
                {JSON.stringify(selectedItem.metadata, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {viewMode === 'list' && (
        <ItemList onViewItem={handleViewItem} onCreateItem={handleCreateItem} />
      )}

      {viewMode === 'view' && renderItemDetail()}

      {(viewMode === 'create' || viewMode === 'edit') && (
        <div className="max-w-2xl mx-auto">
          <ItemForm
            item={viewMode === 'edit' ? selectedItem : null}
            onSuccess={handleFormSuccess}
            onCancel={handleFormCancel}
          />
        </div>
      )}
    </div>
  );
};

export default ItemsPage;
