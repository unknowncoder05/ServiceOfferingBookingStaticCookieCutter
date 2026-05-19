import React, { useEffect, useState } from 'react';
import apiService from '../services/api';
import { Booking } from '../types/serviceBookings';

const ServiceAdminPage: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const res = await apiService.getBookings();
      setBookings(res.data.results || res.data);
      setError('');
    } catch {
      setError('Failed to load bookings.');
    }
  };

  useEffect(() => {
    load();
  }, []);

  const changeStatus = async (id: number, action: 'confirm' | 'reject') => {
    try {
      if (action === 'confirm') await apiService.confirmBooking(id);
      else await apiService.rejectBooking(id);
      load();
    } catch {
      setError('Failed to update booking status.');
    }
  };

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 p-6 text-secondary-900 dark:text-secondary-100">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Reservations Admin</h1>
        {error ? <p className="mb-4 text-danger-600">{error}</p> : null}
        <div className="overflow-x-auto rounded-lg border border-secondary-200 dark:border-secondary-700 bg-white dark:bg-secondary-800">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-secondary-200 dark:border-secondary-700">
                <th className="p-3 text-left">Created</th>
                <th className="p-3 text-left">Name</th>
                <th className="p-3 text-left">Email</th>
                <th className="p-3 text-left">Service</th>
                <th className="p-3 text-left">Slot</th>
                <th className="p-3 text-left">Status</th>
                <th className="p-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((booking) => (
                <tr key={booking.id} className="border-b border-secondary-100 dark:border-secondary-700">
                  <td className="p-3">{new Date(booking.created_at).toLocaleString()}</td>
                  <td className="p-3">{booking.full_name}</td>
                  <td className="p-3">{booking.email}</td>
                  <td className="p-3">{booking.service_name || booking.service}</td>
                  <td className="p-3">{booking.date} {booking.time}</td>
                  <td className="p-3">{booking.status}</td>
                  <td className="p-3 flex gap-2">
                    <button className="px-3 py-1 rounded bg-success-600 text-white" onClick={() => changeStatus(booking.id, 'confirm')}>Confirm</button>
                    <button className="px-3 py-1 rounded bg-danger-600 text-white" onClick={() => changeStatus(booking.id, 'reject')}>Reject</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ServiceAdminPage;
