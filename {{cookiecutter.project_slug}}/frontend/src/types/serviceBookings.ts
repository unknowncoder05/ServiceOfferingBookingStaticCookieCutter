export interface Service {
  id: number;
  name: string;
  description: string;
  duration: string;
  price_label: string;
}

export interface Testimonial {
  id: number;
  quote: string;
  author_name: string;
  author_role: string;
}

export interface Booking {
  id: number;
  full_name: string;
  email: string;
  service: number;
  service_name?: string;
  date: string;
  time: string;
  notes: string;
  transaction_code: string;
  verification_file?: string | null;
  status: 'pending' | 'confirmed' | 'rejected';
  created_at: string;
  updated_at?: string;
}

export interface CreateBookingRequest {
  full_name: string;
  email: string;
  service: number;
  date: string;
  time: string;
  notes?: string;
  transaction_code?: string;
  verification_file?: File | null;
}
