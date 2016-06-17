from __future__ import print_function, unicode_literals

import sys


def kwargs_remove_prefix(kwargs, prefix):
    return {k[len(prefix):]: v for k, v in kwargs.items() if k.startswith(prefix)}


def keys_to_lower(d):
    return {k.lower(): v for k, v in d.items()}


class Options(object):

    _DEFAULT = object()
    # So we can declare the kwargs in DEFAULTS for completeness, but
    # it won't do anything.
    _SKIP = object()

    # Indicates that if an option is not given, it should borrow its
    # value from the specified option.
    class Borrow(object):
        def __init__(self, borrow_from):
            self.borrow_from = borrow_from

    DEFAULTS = {
        'strict': True,

        'flake8_complexity': -1,
        'flake8_strict': Borrow('strict'),
        'flake8_ignore': _SKIP,
        'flake8_lazy': False,

        'isort_strict': Borrow('strict'),
        'isort_force': False,

        'eslint_strict': Borrow('strict'),
        'eslint_path': _SKIP,
    }

    # A dict mapping an option to a pair of (type, fallback). The
    # fallback will be used if the value cannot be converted to the
    # specified type.
    CUSTOM_TYPES = {
        # It turns out that `None` is not a valid default for the
        # complexity as of python3.
        'flake8_complexity': (int, -1),
    }

    def __init__(self, environment_vars, precommit_defaults):
        # Because passing `flake8_strict` or `FLAKE8_STRICT` are both
        # valid, we convert all options to lower case.
        self.environment_vars = keys_to_lower(environment_vars)
        self.precommit_defaults = keys_to_lower(precommit_defaults)

    def get(self, key, default=_DEFAULT):
        """Get a value, working our way through the three different possible
        places.

        """
        key = key.lower()
        val = self.environment_vars.get(key, default)
        if val is not self._DEFAULT:
            return val
        val = self.precommit_defaults.get(key, default)
        if val is not self._DEFAULT:
            return val
        return self.DEFAULTS[key]

    def type_convert(self, key, value):
        """Some keys are more picky about their types. Convert any that are
        the wrong type.

        """
        custom_type, fallback = self.CUSTOM_TYPES.get(key, (None, None))

        if custom_type:
            try:
                return custom_type(value)
            except ValueError:
                print('Invalid value for {}. Ignoring.'.format(key), file=sys.stderr)
                return fallback
            except TypeError:
                # Then it isn't currently set, don't bother printing a
                # message, just use the fallback.
                return fallback
        return value

    def get_kwargs(self, prefix):
        """Get the kwargs, gathering appropriate defaults, and with correct
        types.

        """
        kwargs = {}
        for key in [k for k in self.DEFAULTS if k.startswith(prefix)]:
            value = self.get(key)
            if isinstance(value, self.Borrow):
                kwargs[key] = self.get(value.borrow_from)
            elif value is self._SKIP:
                continue
            else:
                kwargs[key] = value

        # Now apply the type conversions
        typed_kwargs = {}
        for k, v in kwargs.items():
            typed_kwargs[k] = self.type_convert(k, v)

        # Finally remove the prefix. Do this last so we have the full
        # name during processing.
        return kwargs_remove_prefix(typed_kwargs, prefix)
