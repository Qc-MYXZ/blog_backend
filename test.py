import sys
sys.path.append('./')
from extends.settings import project_settings

settings = project_settings

print(settings.postgres.uri())