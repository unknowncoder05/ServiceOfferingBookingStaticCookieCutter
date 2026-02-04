/**
 * ItemCard component - Displays a single item in a card format.
 *
 * This component demonstrates:
 * - TypeScript props interface
 * - Conditional rendering based on status
 * - Event handler props for actions
 */
import React from 'react';
import { ItemListItem, ItemStatus } from '../../types/items';

interface ItemCardProps {
  item: ItemListItem;
  onView: (id: number) => void;
  onArchive: (id: number) => void;
  onActivate: (id: number) => void;
  onDelete: (id: number) => void;
}

const statusColors: Record<ItemStatus, string> = {
  draft: 'bg-gray-100 text-gray-800',
  active: 'bg-green-100 text-green-800',
  archived: 'bg-yellow-100 text-yellow-800',
};

const statusLabels: Record<ItemStatus, string> = {
  draft: 'Draft',
  active: 'Active',
  archived: 'Archived',
};

export const ItemCard: React.FC<ItemCardProps> = ({
  item,
  onView,
  onArchive,
  onActivate,
  onDelete,
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900 truncate flex-1">
          {item.name}
        </h3>
        <span
          className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
            statusColors[item.status]
          }`}
        >
          {statusLabels[item.status]}
        </span>
      </div>

      <div className="text-sm text-gray-500 mb-4">
        <p>By {item.owner_name}</p>
        <p>Created {formatDate(item.created_at)}</p>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onView(item.id)}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          View
        </button>

        {item.status !== 'archived' && (
          <button
            onClick={() => onArchive(item.id)}
            className="px-3 py-1 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
          >
            Archive
          </button>
        )}

        {item.status !== 'active' && (
          <button
            onClick={() => onActivate(item.id)}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
          >
            Activate
          </button>
        )}

        <button
          onClick={() => onDelete(item.id)}
          className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
};

export default ItemCard;
