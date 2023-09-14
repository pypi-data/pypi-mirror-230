## signup-genius

A library for parsing signup-genius responses from the signup html, as a free alternative to a paid Signup Genius subscription.

### Install

```sh
pip install signup-genius

```

### Usage

```python
from signup_genius import get_signups

signups = get_signups('https://www.signup-genius.com/go/xyz...')

```

The signup objects returned will vary depending on the type of signup genius encountered.

For example for a simple yes/no response with adult / child counts the signup will look like:

```python
class Signup:
    name: str
    response: str
    comments: str = ''
    adult_count: int = 0
    child_count: int = 0

```

Whereas for a signup-genius with Date / Location / Time and multiple slots with capacities, it will look like:

```python
class Signup:
    name: str
    comments: str = ''
    count: int = 0
    slot: Slot

# where the embedded slot object is:

class Slot:
    date: str
    location: str
    time: str
    name: str
    comments: str = ""
    capacity: int = 1
    filled: int = 0
```

### Name Mapping

Often times it is useful to coerce the signup names returned to a known set of names, e.g. a club or organization whose menbers are known but where there may be variations in how those names are entered in the signup genius ... Jeff vs. Jeffrey, amy vs Amy, etc.

2 Options are supported:

#### An explicit mapping from what is entered to the final representation

```python

mapping = {'Jeff Adams': 'Jeffrey Adams'}
signups = get_signups(url, name_mapping=mapping)

```

Where a signup is updated, an *_original_name* attribute will be added to the object allowing you to detect after the fact which signups have been updated

#### Fuzzy matching against a population of names

You can supply a population of known names, and any names not matching this population will be mapped to the closest match (using Levenshtein distance).

```python
known_names = ['Jeffrey Adams', 'John Doe', Amy Malone']
signups = get_signups(url, match_names=known_names)

```

Again the signups that are updated will be annotated with an *_original_name* attribute.


### Signup Genius Variants supported

So far the following variants are supported:

* Yes / No / Maybe responses with guest count
* Yes / No / Maybe responses with adult, child counts
* Date / Time / Slot signups
* Date / Location / Time / Slot signups

The call to get_signups will first inspect the signup genius to interpret the variant, and use the appropriate parser.  If the variant is not known then a *UnsupportedVariant* exception will be raised

