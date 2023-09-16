# MeowthPxnk Cxstom logger for python!
---
### How this works:

Logs will be steram to console and save to rollover every hour at 00 minutes:
***savepath ->*** ./Logs/`YYYY-MM-DD`/`HH.00-HH.00`.log

---
### Usage:
```python
import logging

from MeowthLogger import initLogger


initLogger(
    filename="logging.log",
    encoding="utf-8",
    logger_level="INFO"
)

logger = logging.getLogger()

# usage logger ---->

logger.info("INFO")
logger.error("ERROR")
logger.debug("DEBUG")
logger.warning("WARNING")
logger.critical("CRITICAL")
```
---
$XOXO$
*meowthpxnk*