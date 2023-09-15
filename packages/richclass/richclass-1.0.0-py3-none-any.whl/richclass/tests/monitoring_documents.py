from richclass import RichPath, RichPathType
import logging
import logging.config
import os

# Set up and configure the logger for this program
LOG_FILE_NAME = "richclass_test.log"

with open('./app/richclass/tests/logging.conf', 'r') as f:
    with open('_logging.conf', 'w') as _f:
        for line in f:
            if "log_name.log" in line:
                line = line.replace('log_name.log', LOG_FILE_NAME)

            _f.write(line)

logging.config.fileConfig('_logging.conf', disable_existing_loggers=False)
os.remove('_logging.conf')

logger = logging.getLogger("root")

# Configure username for directory
WINDOWS_USERNAME = "Family"

dir_documents = RichPath(
    RichPathType.DIRECTORY,
    path_str = "C:/Users/" + WINDOWS_USERNAME,
    req= True,
    logger= logger
)

logger.info(f"created {dir_documents}")

BAD_NAME = "whosagoodboywhosagoodboyyouareyesyouare"

try:
    bad_path = RichPath(
        RichPathType.DIRECTORY,
        path_str = "C:/Users/" + BAD_NAME,
        req= True,
        logger= logger
    )
except:
    logger.info(f"Good, that's not a good directory.")


