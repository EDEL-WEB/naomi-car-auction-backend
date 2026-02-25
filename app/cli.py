"""CLI commands for the application"""
import os
import click
from app import db
from app.models.user import User


def register_cli_commands(app):
    """Register CLI commands with the Flask app"""
    
    @app.cli.command('create-admin')
    def create_admin():
        """Create the first admin user from environment variables
        
        Uses ADMIN_EMAIL and ADMIN_PASSWORD from .env
        Will not create admin if one already exists in the database
        """
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if not admin_email or not admin_password:
            click.secho('❌ Error: ADMIN_EMAIL and ADMIN_PASSWORD environment variables must be set', fg='red')
            click.echo('Add to your .env file:')
            click.echo('  ADMIN_EMAIL=admin@example.com')
            click.echo('  ADMIN_PASSWORD=yourSecurePassword123!')
            return
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            click.secho(f'✓ Admin already exists: {existing_admin.email}', fg='yellow')
            return
        
        existing_user = User.query.filter_by(email=admin_email).first()
        if existing_user:
            click.secho(f'❌ Error: User with email "{admin_email}" already exists', fg='red')
            return
        
        try:
            # Create admin user
            admin = User(
                username='admin',
                email=admin_email,
                role='admin',
                approved=True
            )
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            
            click.secho('✓ Admin user created successfully!', fg='green')
            click.echo(f'  Email: {admin_email}')
            click.echo(f'  Username: admin')
            click.echo(f'  Role: admin')
            
        except Exception as e:
            db.session.rollback()
            click.secho(f'❌ Error creating admin: {str(e)}', fg='red')
    
    @app.cli.command('list-users')
    @click.option('--role', default=None, help='Filter by role (admin, seller, buyer)')
    def list_users(role):
        """List all users in the database"""
        try:
            query = User.query
            
            if role:
                query = query.filter_by(role=role)
            
            users = query.order_by(User.created_at.desc()).all()
            
            if not users:
                click.echo('No users found')
                return
            
            click.echo(f'\n{"ID":<5} {"Username":<15} {"Email":<25} {"Role":<10} {"Approved":<10}')
            click.echo('-' * 70)
            
            for user in users:
                approved = '✓' if user.approved else '✗'
                click.echo(
                    f'{user.id:<5} {user.username:<15} {user.email:<25} {user.role:<10} {approved:<10}'
                )
            
            click.echo(f'\nTotal: {len(users)} users\n')
        
        except Exception as e:
            click.secho(f'❌ Error: {str(e)}', fg='red')
    
    @app.cli.command('update-user-role')
    @click.argument('user_id', type=int)
    @click.argument('new_role', type=click.Choice(['admin', 'seller', 'buyer']))
    @click.option('--approved', is_flag=True, default=False, help='Mark seller as approved')
    def update_user_role(user_id, new_role, approved):
        """Update a user's role"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                click.secho(f'❌ User with ID {user_id} not found', fg='red')
                return
            
            old_role = user.role
            user.role = new_role
            
            if new_role == 'seller':
                user.approved = approved
            else:
                user.approved = True
            
            db.session.commit()
            
            click.secho(f'✓ User role updated successfully', fg='green')
            click.echo(f'  User: {user.username} (ID: {user.id})')
            click.echo(f'  Old role: {old_role}')
            click.echo(f'  New role: {new_role}')
            click.echo(f'  Approved: {user.approved}')
        
        except Exception as e:
            db.session.rollback()
            click.secho(f'❌ Error: {str(e)}', fg='red')
    
    @app.cli.command('approve-seller')
    @click.argument('user_id', type=int)
    def approve_seller(user_id):
        """Approve a pending seller"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                click.secho(f'❌ User with ID {user_id} not found', fg='red')
                return
            
            if user.role != 'seller':
                click.secho(f'❌ User is not a seller', fg='red')
                return
            
            if user.approved:
                click.secho(f'ℹ Seller is already approved', fg='yellow')
                return
            
            user.approved = True
            db.session.commit()
            
            click.secho(f'✓ Seller approved successfully', fg='green')
            click.echo(f'  Username: {user.username}')
            click.echo(f'  Email: {user.email}')
        
        except Exception as e:
            db.session.rollback()
            click.secho(f'❌ Error: {str(e)}', fg='red')
