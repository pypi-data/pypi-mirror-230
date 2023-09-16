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


class ReactSeriesResponseContent(object):
    """
    Auto-generated OpenAPI type.

    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'action_features': 'list[str]',
        'series': 'list[list[list[object]]]'
    }

    attribute_map = {
        'action_features': 'action_features',
        'series': 'series'
    }

    nullable_attributes = [
        'action_features', 
        'series', 
    ]

    discriminator = None

    def __init__(self, action_features=None, series=None, local_vars_configuration=None):  # noqa: E501
        """ReactSeriesResponseContent - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._action_features = None
        self._series = None

        self.action_features = action_features
        self.series = series

    @property
    def action_features(self):
        """Get the action_features of this ReactSeriesResponseContent.

        The list of all action features, specified and derived.

        :return: The action_features of this ReactSeriesResponseContent.
        :rtype: list[str]
        """
        return self._action_features

    @action_features.setter
    def action_features(self, action_features):
        """Set the action_features of this ReactSeriesResponseContent.

        The list of all action features, specified and derived.

        :param action_features: The action_features of this ReactSeriesResponseContent.
        :type action_features: list[str]
        """

        self._action_features = action_features

    @property
    def series(self):
        """Get the series of this ReactSeriesResponseContent.

        List of series, where each series is a 2d list of values (rows of data the series), where the values are in the same order as 'action_features'. 

        :return: The series of this ReactSeriesResponseContent.
        :rtype: list[list[list[object]]]
        """
        return self._series

    @series.setter
    def series(self, series):
        """Set the series of this ReactSeriesResponseContent.

        List of series, where each series is a 2d list of values (rows of data the series), where the values are in the same order as 'action_features'. 

        :param series: The series of this ReactSeriesResponseContent.
        :type series: list[list[list[object]]]
        """

        self._series = series

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
        if not isinstance(other, ReactSeriesResponseContent):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReactSeriesResponseContent):
            return True

        return self.to_dict() != other.to_dict()
