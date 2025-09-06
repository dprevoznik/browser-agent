from functools import partial

import asyncer

syncify = partial(asyncer.syncify, raise_sync_error=False)
asyncify = partial(asyncer.asyncify, abandon_on_cancel=True)
