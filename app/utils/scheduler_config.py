"""APScheduler configuration and job definitions."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app


# Global scheduler instance
scheduler = None


def init_scheduler(app):
    """Initialize the APScheduler with the Flask app.
    
    Args:
        app: Flask application instance
    """
    global scheduler
    
    if scheduler is not None:
        return scheduler
    
    scheduler = BackgroundScheduler()
    
    # Add reminder processing job
    # Run every day at 9:00 AM
    scheduler.add_job(
        func=process_reminders_job,
        trigger=CronTrigger(hour=9, minute=0),
        id='process_reminders',
        name='Process loan reminders',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    app.logger.info('APScheduler started')
    
    # Shutdown scheduler when app shuts down
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler


def process_reminders_job():
    """Job function to process reminders.
    
    This runs in a separate thread, so we need to create an app context.
    """
    from app import create_app
    from app.services.scheduler import ReminderScheduler
    
    app = create_app()
    
    with app.app_context():
        try:
            stats = ReminderScheduler.process_reminders()
            app.logger.info(f'Reminder job completed: {stats}')
        except Exception as e:
            app.logger.error(f'Reminder job failed: {e}')


def run_reminders_now():
    """Manually trigger the reminder job.
    
    Returns:
        Statistics dict from processing
    """
    from app.services.scheduler import ReminderScheduler
    
    try:
        stats = ReminderScheduler.process_reminders()
        current_app.logger.info(f'Manual reminder run completed: {stats}')
        return stats
    except Exception as e:
        current_app.logger.error(f'Manual reminder run failed: {e}')
        raise
