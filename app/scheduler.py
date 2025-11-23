"""
Background scheduler for periodic tasks
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings
from app.jobs.alert_generator import generate_alerts_for_all_users

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    """Start the background scheduler"""
    try:
        # Schedule alert generation
        scheduler.add_job(
            func=generate_alerts_for_all_users,
            trigger=IntervalTrigger(minutes=settings.alert_check_interval_minutes),
            id='generate_alerts',
            name='Generate alerts for all users',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        # Don't fail the entire app if scheduler fails


def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()
    logger.info("Background scheduler stopped")

