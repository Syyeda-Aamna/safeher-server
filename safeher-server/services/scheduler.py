from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.otp_service import OTPService
from routes.checkin import monitor_missed_checkins
from routes.location import cleanup_expired_shares
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    """Background scheduler service for periodic tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup all scheduled jobs"""
        try:
            # Clean up expired OTPs every 30 minutes
            self.scheduler.add_job(
                OTPService.cleanup_expired_otps,
                trigger=IntervalTrigger(minutes=30),
                id='cleanup_expired_otps',
                name='Clean up expired OTPs',
                replace_existing=True
            )
            
            # Monitor missed check-ins every minute
            self.scheduler.add_job(
                monitor_missed_checkins,
                trigger=IntervalTrigger(minutes=1),
                id='monitor_missed_checkins',
                name='Monitor missed check-ins',
                replace_existing=True
            )
            
            # Clean up expired location shares every hour
            self.scheduler.add_job(
                cleanup_expired_shares,
                trigger=IntervalTrigger(hours=1),
                id='cleanup_expired_shares',
                name='Clean up expired location shares',
                replace_existing=True
            )
            
            logger.info("Scheduled jobs setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup scheduled jobs: {str(e)}")
    
    def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {str(e)}")
    
    def get_job_status(self):
        """Get status of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time,
                "trigger": str(job.trigger)
            })
        return {
            "scheduler_running": self.scheduler.running,
            "total_jobs": len(jobs),
            "jobs": jobs
        }

# Global scheduler instance
scheduler_service = None

def start_scheduler():
    """Initialize and start the global scheduler"""
    global scheduler_service
    try:
        scheduler_service = SchedulerService()
        scheduler_service.start()
        logger.info("Global scheduler started")
    except Exception as e:
        logger.error(f"Failed to start global scheduler: {str(e)}")

def get_scheduler():
    """Get the global scheduler instance"""
    return scheduler_service
