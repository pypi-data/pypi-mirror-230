# coding: utf-8

"""
Howso API

OpenAPI implementation for interacting with the Howso API. 
"""

try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from howso.openapi.configuration import Configuration


class FeatureBounds(object):
    """
    Auto-generated OpenAPI type.

    Bounds for feature value generation.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'min': 'object',
        'max': 'object',
        'allowed': 'list[object]',
        'allow_null': 'bool'
    }

    attribute_map = {
        'min': 'min',
        'max': 'max',
        'allowed': 'allowed',
        'allow_null': 'allow_null'
    }

    nullable_attributes = [
    ]

    discriminator = None

    def __init__(self, min=None, max=None, allowed=None, allow_null=None, local_vars_configuration=None):  # noqa: E501
        """FeatureBounds - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._min = None
        self._max = None
        self._allowed = None
        self._allow_null = None

        self.min = min
        self.max = max
        if allowed is not None:
            self.allowed = allowed
        if allow_null is not None:
            self.allow_null = allow_null

    @property
    def min(self):
        """Get the min of this FeatureBounds.

        The minimum value to be output. May be a number or date string.

        :return: The min of this FeatureBounds.
        :rtype: object
        """
        return self._min

    @min.setter
    def min(self, min):
        """Set the min of this FeatureBounds.

        The minimum value to be output. May be a number or date string.

        :param min: The min of this FeatureBounds.
        :type min: object
        """

        self._min = min

    @property
    def max(self):
        """Get the max of this FeatureBounds.

        The maximum value to be output. May be a number or date string.

        :return: The max of this FeatureBounds.
        :rtype: object
        """
        return self._max

    @max.setter
    def max(self, max):
        """Set the max of this FeatureBounds.

        The maximum value to be output. May be a number or date string.

        :param max: The max of this FeatureBounds.
        :type max: object
        """

        self._max = max

    @property
    def allowed(self):
        """Get the allowed of this FeatureBounds.

        Explicitly allowed values to be output.

        :return: The allowed of this FeatureBounds.
        :rtype: list[object]
        """
        return self._allowed

    @allowed.setter
    def allowed(self, allowed):
        """Set the allowed of this FeatureBounds.

        Explicitly allowed values to be output.

        :param allowed: The allowed of this FeatureBounds.
        :type allowed: list[object]
        """

        self._allowed = allowed

    @property
    def allow_null(self):
        """Get the allow_null of this FeatureBounds.

        Allow nulls to be output, per their distribution in the data. Defaults to true.

        :return: The allow_null of this FeatureBounds.
        :rtype: bool
        """
        return self._allow_null

    @allow_null.setter
    def allow_null(self, allow_null):
        """Set the allow_null of this FeatureBounds.

        Allow nulls to be output, per their distribution in the data. Defaults to true.

        :param allow_null: The allow_null of this FeatureBounds.
        :type allow_null: bool
        """

        self._allow_null = allow_null

    def to_dict(self, serialize=False, exclude_null=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                elif 'exclude_null' in args:
                    return x.to_dict(serialize, exclude_null)
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            elif value is None and (exclude_null or attr not in self.nullable_attributes):
                continue
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, FeatureBounds):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FeatureBounds):
            return True

        return self.to_dict() != other.to_dict()
