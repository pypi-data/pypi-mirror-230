from ..security.csrf import CSRF
from ..core.branch import Emonic

app = Emonic(__name__)
csrf = CSRF(app)