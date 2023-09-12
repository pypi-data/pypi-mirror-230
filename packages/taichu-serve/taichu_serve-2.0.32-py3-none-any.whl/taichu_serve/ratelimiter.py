import logging
import threading

from taichu_serve.settings import parse_args

logger = logging.getLogger(__name__)

args = parse_args()

semaphore = threading.Semaphore(value=args.max_concurrent_requests)