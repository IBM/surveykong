from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

# On demand, reusable scheduler.
class _DeferredScheduler:
	def __init__(self):
		self._scheduler = None

	# Create background scheduler that runs up to 30 concurrent jobs.
	# Scheduler will reuse open threads, so never have more than # open at once.
	def scheduler(self):
		if self._scheduler is None:
			self._scheduler = BackgroundScheduler(executors={'default':ThreadPoolExecutor(30)})
			self._scheduler.start()

		return self._scheduler


# Instantiate class instance
_ondemand_scheduler_common = _DeferredScheduler()

# Call this to start and return the class's scheduler which you do .add_job() to.
def commonScheduler():
	return _ondemand_scheduler_common.scheduler()
