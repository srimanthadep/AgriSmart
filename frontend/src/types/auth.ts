export interface User {
  id: number
  uuid: string
  email: string
  username: string
  first_name?: string
  last_name?: string
  phone?: string
  location?: string
  latitude?: number
  longitude?: number
  role: 'user' | 'admin' | 'premium'
  is_verified: boolean
  created_at: string
  last_login?: string
}

export interface LoginCredentials {
  email: string
  password: string
  latitude?: number
  longitude?: number
}

export interface RegisterData {
  email: string
  username: string
  password: string
  first_name?: string
  last_name?: string
  phone?: string
  location?: string
  latitude?: number
  longitude?: number
}

export interface AuthResponse {
  success: boolean
  message: string
  data: {
    user: User
    access_token: string
    refresh_token: string
  }
}

export interface ProfileUpdateData {
  first_name?: string
  last_name?: string
  phone?: string
  location?: string
  latitude?: number
  longitude?: number
}
