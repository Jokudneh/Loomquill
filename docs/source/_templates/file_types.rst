{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

{% if objname == 'FlyteFile' or  objname == 'FlyteDirectory' %}

.. autoclass:: {{ objname }}

   {% block methods %}
   {% if methods %}

   .. rubric:: {{ _('Methods') }}
   {% for item in methods %}
