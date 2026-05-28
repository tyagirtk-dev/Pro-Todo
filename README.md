# MindVault Pro - Professional Notes Management Platform

## Overview
MindVault Pro is a production-ready SaaS application for professional note management with enterprise-grade security, organization features, and a beautiful modern UI.

## Features

### Core Features
- User Authentication & Authorization
- Email Verification
- Password Reset Flow
- Notes CRUD Operations
- Notes Archive/Restore
- Notes Pin/Unpin
- Color-coded Notes
- Full-text Search
- Bulk Operations

### Security Features
- CSRF Protection
- XSS Prevention with Bleach
- SQL Injection Protection
- Rate Limiting
- Secure Password Hashing (scrypt)
- Security Headers
- Session Protection

## Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- SQLite (development) or PostgreSQL (production)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/mindvault-pro.git
cd mindvault-pro
