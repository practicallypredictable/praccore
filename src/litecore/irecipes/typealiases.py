from typing import (
    Any,
    Callable,
    Hashable,
    Tuple,
)

KeyFunc = Callable[[Any], Any]
HashableKeyFunc = Callable[[Any], Hashable]
FilterFunc = Callable[[Any], bool]
Prioritized = Tuple[int, Any]
Prioritizer = Callable[[Any], Prioritized]
