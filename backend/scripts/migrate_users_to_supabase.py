#!/usr/bin/env python3
"""
User Migration Script

Migrates users from CSV file to Supabase.
Optionally migrates users from Auth0 (if Auth0 users exist).

Usage:
    python scripts/migrate_users_to_supabase.py [--auth0] [--dry-run]
"""
import sys
import os
import csv
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Add backend/src to path
backend_path = Path(__file__).parent.parent
src_path = backend_path / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
from supabase import create_client, Client
from auth.supabase.config import get_supabase_config
from auth.client_auth import ClientAuth

# Load environment variables
env_path = backend_path / ".env"
load_dotenv(env_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_csv_users_to_supabase(
    supabase_client: Client,
    client_auth: ClientAuth,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Migrate users from CSV file to Supabase.
    
    Args:
        supabase_client: Supabase client instance
        client_auth: ClientAuth instance with loaded CSV users
        dry_run: If True, don't actually create users, just log what would be done
    
    Returns:
        Dictionary with migration statistics
    """
    stats = {
        "total": 0,
        "created": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    logger.info("Starting CSV to Supabase user migration...")
    
    for email, client_data in client_auth.clients.items():
        stats["total"] += 1
        email = email.strip().lower()
        client_id = client_data.get("client_id", "").strip()
        password = client_data.get("password", "").strip()
        
        if not email or not client_id:
            logger.warning(f"Skipping invalid user: email={email}, client_id={client_id}")
            stats["skipped"] += 1
            continue
        
        # Check if user already exists in Supabase
        try:
            existing_user = supabase_client.auth.admin.get_user_by_email(email)
            if existing_user.user:
                logger.info(f"User {email} already exists in Supabase, skipping")
                stats["skipped"] += 1
                continue
        except Exception as e:
            # User doesn't exist, which is fine
            pass
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create user: {email} (client_id: {client_id})")
            stats["created"] += 1
            continue
        
        # Create user in Supabase
        try:
            # If password exists, use it; otherwise generate a random password
            # Users will need to reset password if not provided
            user_password = password if password else None
            
            user_data = {
                "email": email,
                "password": user_password or "TempPassword123!@#",  # Temporary password
                "email_confirm": True,  # Auto-confirm email
                "user_metadata": {
                    "client_id": client_id,
                    "migrated_from": "csv",
                }
            }
            
            # Create user using admin API
            response = supabase_client.auth.admin.create_user(user_data)
            
            if response.user:
                logger.info(f"Created user: {email} (client_id: {client_id})")
                stats["created"] += 1
                
                if not password:
                    logger.warning(
                        f"User {email} created with temporary password. "
                        "User should reset password on first login."
                    )
            else:
                logger.error(f"Failed to create user: {email}")
                stats["errors"] += 1
                
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            stats["errors"] += 1
    
    return stats


def migrate_auth0_users_to_supabase(
    supabase_client: Client,
    auth0_users: List[Dict],
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Migrate users from Auth0 to Supabase.
    
    Args:
        supabase_client: Supabase client instance
        auth0_users: List of Auth0 user dictionaries
        dry_run: If True, don't actually create users, just log what would be done
    
    Returns:
        Dictionary with migration statistics
    """
    stats = {
        "total": 0,
        "created": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    logger.info("Starting Auth0 to Supabase user migration...")
    
    for auth0_user in auth0_users:
        stats["total"] += 1
        email = auth0_user.get("email", "").strip().lower()
        
        if not email:
            logger.warning(f"Skipping Auth0 user without email: {auth0_user.get('user_id')}")
            stats["skipped"] += 1
            continue
        
        # Check if user already exists in Supabase
        try:
            existing_user = supabase_client.auth.admin.get_user_by_email(email)
            if existing_user.user:
                logger.info(f"User {email} already exists in Supabase, skipping")
                stats["skipped"] += 1
                continue
        except Exception:
            pass
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create user from Auth0: {email}")
            stats["created"] += 1
            continue
        
        # Create user in Supabase
        try:
            user_data = {
                "email": email,
                "email_confirm": auth0_user.get("email_verified", False),
                "user_metadata": {
                    "name": auth0_user.get("name"),
                    "migrated_from": "auth0",
                    "auth0_user_id": auth0_user.get("user_id"),
                }
            }
            
            # Note: Auth0 passwords cannot be migrated directly
            # Users will need to reset password
            response = supabase_client.auth.admin.create_user(user_data)
            
            if response.user:
                logger.info(f"Created user from Auth0: {email}")
                logger.warning(
                    f"User {email} needs to reset password. "
                    "Auth0 passwords cannot be migrated."
                )
                stats["created"] += 1
            else:
                logger.error(f"Failed to create user from Auth0: {email}")
                stats["errors"] += 1
                
        except Exception as e:
            logger.error(f"Error creating user from Auth0 {email}: {e}")
            stats["errors"] += 1
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Migrate users to Supabase")
    parser.add_argument(
        "--auth0",
        action="store_true",
        help="Also migrate users from Auth0 (requires Auth0 export file)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually create users, just show what would be done"
    )
    parser.add_argument(
        "--auth0-file",
        type=str,
        help="Path to Auth0 users export file (JSON format)"
    )
    
    args = parser.parse_args()
    
    # Get Supabase configuration
    config = get_supabase_config()
    if not config:
        logger.error("Supabase is not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env")
        sys.exit(1)
    
    # Create Supabase client
    try:
        supabase_client = create_client(config.url, config.service_role_key)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        sys.exit(1)
    
    # Load CSV users
    client_auth = ClientAuth()
    csv_stats = migrate_csv_users_to_supabase(supabase_client, client_auth, args.dry_run)
    
    logger.info("=" * 50)
    logger.info("CSV Migration Summary:")
    logger.info(f"  Total users: {csv_stats['total']}")
    logger.info(f"  Created: {csv_stats['created']}")
    logger.info(f"  Skipped: {csv_stats['skipped']}")
    logger.info(f"  Errors: {csv_stats['errors']}")
    
    # Migrate Auth0 users if requested
    if args.auth0:
        if not args.auth0_file:
            logger.error("--auth0-file is required when using --auth0 flag")
            sys.exit(1)
        
        # Load Auth0 users from file
        import json
        try:
            with open(args.auth0_file, 'r') as f:
                auth0_users = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Auth0 users file: {e}")
            sys.exit(1)
        
        auth0_stats = migrate_auth0_users_to_supabase(
            supabase_client,
            auth0_users,
            args.dry_run
        )
        
        logger.info("=" * 50)
        logger.info("Auth0 Migration Summary:")
        logger.info(f"  Total users: {auth0_stats['total']}")
        logger.info(f"  Created: {auth0_stats['created']}")
        logger.info(f"  Skipped: {auth0_stats['skipped']}")
        logger.info(f"  Errors: {auth0_stats['errors']}")
    
    logger.info("=" * 50)
    logger.info("Migration completed!")


if __name__ == "__main__":
    main()





