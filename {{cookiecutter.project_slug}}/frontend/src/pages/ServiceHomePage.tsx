import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiService from '../services/api';
import { Service, Testimonial } from '../types/serviceBookings';

const ServiceHomePage: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);
  const [status, setStatus] = useState('');
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    service: '',
    date: '',
    time: '',
    notes: '',
    transaction_code: '',
  });
  const [verificationFile, setVerificationFile] = useState<File | null>(null);

  useEffect(() => {
    const load = async () => {
      const [sRes, tRes] = await Promise.all([
        apiService.getServices(),
        apiService.getTestimonials(),
      ]);
      setServices(sRes.data);
      setTestimonials(tRes.data);
      if (sRes.data.length > 0) {
        setFormData((prev) => ({ ...prev, service: String(sRes.data[0].id) }));
      }
    };
    load().catch(() => setStatus('Unable to load content right now.'));
  }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = new FormData();
      Object.entries(formData).forEach(([key, val]) => payload.append(key, val));
      if (verificationFile) payload.append('verification_file', verificationFile);
      await apiService.createBooking(payload);
      setStatus('Reservation submitted successfully.');
      setFormData({
        full_name: '',
        email: '',
        service: services[0] ? String(services[0].id) : '',
        date: '',
        time: '',
        notes: '',
        transaction_code: '',
      });
      setVerificationFile(null);
    } catch {
      setStatus('Failed to submit reservation. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 text-secondary-900 dark:text-secondary-100">
      <header className="border-b border-secondary-200 dark:border-secondary-700 bg-white dark:bg-secondary-800">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Service Offering Website</h1>
          <div className="flex gap-3">
            <Link to="/login" className="text-sm px-3 py-2 rounded bg-secondary-100 dark:bg-secondary-700">Login</Link>
            <Link to="/service-admin" className="text-sm px-3 py-2 rounded bg-primary-600 text-white">Admin</Link>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-10 space-y-10">
        <section>
          <h2 className="text-3xl font-bold mb-2">Clear outcomes, professionally delivered.</h2>
          <p className="text-secondary-600 dark:text-secondary-300">Service presentation, social proof, and direct booking flow.</p>
        </section>

        <section>
          <h3 className="text-2xl font-semibold mb-4">Services</h3>
          <div className="grid md:grid-cols-3 gap-4">
            {services.map((service) => (
              <article key={service.id} className="p-4 rounded-lg border border-secondary-200 dark:border-secondary-700 bg-white dark:bg-secondary-800">
                <h4 className="font-semibold">{service.name}</h4>
                <p className="text-sm text-secondary-600 dark:text-secondary-300 mt-2">{service.description}</p>
                <p className="text-xs mt-3">{service.duration} · {service.price_label}</p>
              </article>
            ))}
          </div>
        </section>

        <section>
          <h3 className="text-2xl font-semibold mb-4">Testimonials</h3>
          <div className="grid md:grid-cols-3 gap-4">
            {testimonials.map((testimonial) => (
              <article key={testimonial.id} className="p-4 rounded-lg border border-secondary-200 dark:border-secondary-700 bg-white dark:bg-secondary-800">
                <p className="text-sm">"{testimonial.quote}"</p>
                <p className="text-xs mt-3 text-secondary-500 dark:text-secondary-300">{testimonial.author_name} {testimonial.author_role ? `· ${testimonial.author_role}` : ''}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="booking">
          <h3 className="text-2xl font-semibold mb-4">Book a Service</h3>
          <form className="grid gap-3 max-w-2xl" onSubmit={onSubmit}>
            <input className="px-3 py-2 rounded border border-secondary-300 bg-white dark:bg-secondary-800" required placeholder="Full name" value={formData.full_name} onChange={(e) => setFormData((p) => ({ ...p, full_name: e.target.value }))} />
            <input className="px-3 py-2 rounded border border-secondary-300 bg-white dark:bg-secondary-800" required type="email" placeholder="Email" value={formData.email} onChange={(e) => setFormData((p) => ({ ...p, email: e.target.value }))} />
            <select className="px-3 py-2 rounded border border-secondary-300 bg-white dark:bg-secondary-800" required value={formData.service} onChange={(e) => setFormData((p) => ({ ...p, service: e.target.value }))}>
              {services.map((service) => <option key={service.id} value={service.id}>{service.name}</option>)}
            </select>
            <div className="grid grid-cols-2 gap-3">
              <input className="px-3 py-2 rounded border border-secondary-300 bg-white dark:bg-secondary-800" required type="date" value={formData.date} onChange={(e) => setFormData((p) => ({ ...p, date: e.target.value }))} />
              <input className="px-3 py-2 rounded border border-secondary-300 bg-white dark:bg-secondary-800" required type="time" value={formData.time} onChange={(e) => setFormData((p) => ({ ...p, time: e.target.value }))} />
            </div>
            <textarea className="px-3 py-2 rounded border border-secondary-300 bg-white dark:bg-secondary-800" placeholder="Notes" value={formData.notes} onChange={(e) => setFormData((p) => ({ ...p, notes: e.target.value }))} />
            <input className="px-3 py-2 rounded border border-secondary-300 bg-white dark:bg-secondary-800" placeholder="Transaction reference" value={formData.transaction_code} onChange={(e) => setFormData((p) => ({ ...p, transaction_code: e.target.value }))} />
            <input className="px-3 py-2 rounded border border-secondary-300 bg-white dark:bg-secondary-800" type="file" onChange={(e) => setVerificationFile(e.target.files?.[0] ?? null)} />
            <button className="px-4 py-2 rounded bg-primary-600 text-white font-medium" type="submit">Submit Reservation</button>
            {status ? <p className="text-sm">{status}</p> : null}
          </form>
        </section>
      </main>
    </div>
  );
};

export default ServiceHomePage;
