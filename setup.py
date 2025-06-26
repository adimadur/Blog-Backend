#!/usr/bin/env python3
"""
Setup script for Django Blogging Platform
This script helps initialize the project with basic configuration.
"""

import os
import secrets
import subprocess
import sys
from pathlib import Path


def generate_secret_key():
    """Generate a secure secret key for Django."""
    return secrets.token_urlsafe(50)


def create_env_file():
    """Create .env file from template."""
    env_example = Path('env.example')
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  .env file already exists. Skipping...")
        return
    
    if not env_example.exists():
        print("❌ env.example file not found!")
        return
    
    # Read template and replace placeholder secret key
    content = env_example.read_text()
    content = content.replace('your-super-secret-key-change-this-in-production', generate_secret_key())
    
    # Write .env file
    env_file.write_text(content)
    print("✅ Created .env file with secure secret key")


def create_directories():
    """Create necessary directories."""
    directories = ['media', 'staticfiles', 'logs', 'nginx/ssl']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")


def install_dependencies():
    """Install Python dependencies."""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Installed Python dependencies")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    return True


def run_migrations():
    """Run Django migrations."""
    try:
        subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=True)
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ Ran database migrations")
    except subprocess.CalledProcessError:
        print("❌ Failed to run migrations")
        return False
    return True


def create_superuser():
    """Create a superuser account."""
    print("\n🔧 Would you like to create a superuser account? (y/n): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes']:
        try:
            subprocess.run([sys.executable, 'manage.py', 'createsuperuser'], check=True)
            print("✅ Superuser created successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to create superuser")
    else:
        print("⏭️  Skipped superuser creation")


def main():
    """Main setup function."""
    print("🚀 Setting up Django Blogging Platform...\n")
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ manage.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("❌ Setup failed at migrations")
        sys.exit(1)
    
    # Create superuser
    create_superuser()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure your .env file with your specific settings")
    print("2. Run 'python manage.py runserver' to start the development server")
    print("3. Visit http://localhost:8000/admin/ to access the admin interface")
    print("4. For production, use 'docker-compose up --build'")


if __name__ == '__main__':
    main() 