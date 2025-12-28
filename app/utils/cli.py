"""CLI commands for BookShare application."""
import click
from flask import current_app
from app import db


def register_commands(app):
    """Register CLI commands with the Flask app."""
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database."""
        db.create_all()
        click.echo('Database initialized.')
    
    @app.cli.command('seed-db')
    @click.option('--books', default=1000, help='Number of books to seed')
    @click.option('--borrowers', default=50, help='Number of borrowers to seed')
    @click.option('--loans', default=200, help='Number of loans to seed')
    def seed_db(books, borrowers, loans):
        """Seed the database with sample data."""
        from scripts.seed import seed_data
        seed_data(books, borrowers, loans)
        click.echo(f'Database seeded with {books} books, {borrowers} borrowers, {loans} loans.')
    
    @app.cli.command('rebuild-recs')
    def rebuild_recs():
        """Rebuild TF-IDF recommendation cache."""
        from app.services.recommendations import rebuild_recommendation_cache
        click.echo('Rebuilding recommendation cache...')
        engine = rebuild_recommendation_cache()
        click.echo(f'✓ Built model with {len(engine.book_ids)} books and {engine.tfidf_matrix.shape[1]} features')
        click.echo('✓ Cache saved to disk')
    
    @app.cli.command('test-email')
    def test_email():
        """Test email configuration."""
        from app.services.email import EmailService
        click.echo('Testing email configuration...')
        success = EmailService.test_email_config()
        if success:
            click.echo('✓ Email test successful!')
        else:
            click.echo('✗ Email test failed. Check your SMTP settings in .env')
    
    @app.cli.command('send-reminders')
    def send_reminders_cli():
        """Manually send all pending reminders."""
        from app.services.scheduler import ReminderScheduler
        click.echo('Processing reminders...')
        stats = ReminderScheduler.process_reminders()
        click.echo(f"✓ Sent {stats['before_due']} before-due reminders")
        click.echo(f"✓ Sent {stats['on_due']} on-due reminders")
        click.echo(f"✓ Sent {stats['after_due']} overdue reminders")
        if stats['failed'] > 0:
            click.echo(f"✗ {stats['failed']} reminders failed", err=True)
